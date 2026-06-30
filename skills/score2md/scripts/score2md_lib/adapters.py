from __future__ import annotations

import json
import os
import http.client
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


class AdapterError(RuntimeError):
    pass


def _find_module(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def find_musescore_binary(custom_path: str | Path | None = None) -> Path | None:
    if custom_path:
        path = Path(custom_path)
        if path.exists():
            return path
    for candidate in ["MuseScore4", "MuseScore3", "mscore", "mscore3", "musescore"]:
        found = shutil.which(candidate)
        if found:
            return Path(found)
    if os.name == "nt":
        candidates = [
            Path(r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"),
            Path(r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe"),
            Path(r"C:\Program Files (x86)\MuseScore 3\bin\MuseScore3.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    return None


def find_ffmpeg_binary(custom_path: str | Path | None = None) -> Path | None:
    path_value = custom_path or os.environ.get("SCORE2MD_FFMPEG_PATH")
    if path_value:
        path = Path(path_value)
        if path.exists():
            return path
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)
    if os.name == "nt":
        candidates = [
            Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
            Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    return None


def video_to_wav(input_path: Path, output_path: Path, ffmpeg_path: str | Path | None = None) -> Path:
    binary = find_ffmpeg_binary(ffmpeg_path)
    if binary is None:
        raise AdapterError("Video conversion requires ffmpeg. Install ffmpeg or pass --ffmpeg-path.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(binary),
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-f",
            "wav",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise AdapterError(f"ffmpeg did not create a usable WAV file at {output_path}")
    return output_path


def find_omr_command(custom_module: str | None = None) -> list[str]:
    configured = custom_module or os.environ.get("SCORE2MD_OMR_MODULE")
    candidates = [configured] if configured else []
    candidates.extend(["oemer.ete", "omr_parser.ete", "oemer", "omr_parser"])

    tried: list[str] = []
    for candidate in candidates:
        if not candidate:
            continue
        candidate = candidate.strip()
        tried.append(candidate)
        candidate_path = Path(candidate)
        if candidate_path.exists():
            return [str(candidate_path)]
        found = shutil.which(candidate)
        if found:
            return [found]
        if _find_module(candidate) and ("." in candidate or _find_module(candidate + ".__main__")):
            return [sys.executable, "-W", "ignore", "-m", candidate]

    raise AdapterError(
        "No OMR command found. Install oemer/omr_parser, or pass --omr-module. "
        f"Tried: {', '.join(tried)}"
    )


def convert_with_musescore(input_path: Path, output_path: Path, musescore_path: str | Path | None = None) -> Path:
    binary = find_musescore_binary(musescore_path)
    if binary is None:
        raise AdapterError("MuseScore CLI not found; install MuseScore or pass --musescore-path.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(binary), "-o", str(output_path), str(input_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    if not output_path.exists():
        raise AdapterError(f"MuseScore did not create {output_path}")
    return output_path


def midi_to_musicxml(input_path: Path, output_path: Path, musescore_path: str | Path | None = None) -> Path:
    try:
        return convert_with_musescore(input_path, output_path, musescore_path)
    except Exception as musescore_error:
        try:
            from music21 import converter  # type: ignore
        except ImportError as exc:
            raise AdapterError(
                "MIDI conversion requires MuseScore CLI or music21. "
                f"MuseScore error: {musescore_error}"
            ) from exc
        score = converter.parse(str(input_path))
        score.write("musicxml", fp=str(output_path))
        return output_path


def run_oemer_image(
    image_path: Path,
    output_dir: Path,
    *,
    omr_module: str | None = None,
    deskew: bool = True,
    use_tf: bool = False,
    save_cache: bool = True,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = find_omr_command(omr_module) + [str(image_path), "-o", str(output_dir)]
    if not deskew:
        command.append("--without-deskew")
    if use_tf:
        command.append("--use-tf")
    if save_cache:
        command.append("--save-cache")
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["ONNXRUNTIME_INTER_OP_NUM_THREADS"] = "1"
    env["ONNXRUNTIME_INTRA_OP_NUM_THREADS"] = "1"
    try:
        subprocess.run(command, cwd=str(output_dir), env=env, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise AdapterError(f"OMR command failed for {image_path}: {detail}") from exc
    expected = output_dir / f"{image_path.stem}.musicxml"
    if expected.exists():
        return expected
    generated = sorted(output_dir.glob("*.musicxml"), key=lambda p: p.stat().st_mtime)
    if not generated:
        raise AdapterError(f"oemer generated no MusicXML for {image_path}")
    generated[-1].replace(expected)
    return expected


def join_musicxml_files(input_dir: Path, output_file: Path) -> Path:
    import xml.etree.ElementTree as ET

    files = sorted(input_dir.glob("*.musicxml"))
    if not files:
        raise AdapterError(f"No MusicXML files found in {input_dir}")
    tree = ET.parse(str(files[0]))
    root = tree.getroot()
    parts = root.findall("part")
    for file_path in files[1:]:
        new_root = ET.parse(str(file_path)).getroot()
        new_parts = new_root.findall("part")
        for index, new_part in enumerate(new_parts):
            if index < len(parts):
                for measure in new_part.findall("measure"):
                    parts[index].append(measure)
            else:
                parts.append(new_part)
                root.append(new_part)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(str(output_file), encoding="UTF-8", xml_declaration=True)
    return output_file


def pdf_to_musicxml(
    pdf_path: Path,
    output_path: Path,
    *,
    omr_workers: int = 2,
    omr_module: str | None = None,
) -> Path:
    try:
        import pypdfium2 as pdfium  # type: ignore
    except ImportError as exc:
        raise AdapterError("PDF conversion requires pypdfium2 and oemer.") from exc
    with tempfile.TemporaryDirectory(prefix="score2md-pdf-") as tmp:
        tmp_dir = Path(tmp)
        images_dir = tmp_dir / "images"
        xml_dir = tmp_dir / "musicxml"
        images_dir.mkdir()
        xml_dir.mkdir()
        pdf = pdfium.PdfDocument(str(pdf_path))
        image_paths: list[Path] = []
        for index in range(len(pdf)):
            page = pdf[index]
            bitmap = page.render(scale=4.1666)
            pil_image = bitmap.to_pil()
            image_path = images_dir / f"page_{index:03d}.png"
            pil_image.save(str(image_path), "PNG")
            image_paths.append(image_path)

        max_workers = max(1, min(4, omr_workers))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(run_oemer_image, image_path, xml_dir, omr_module=omr_module)
                for image_path in image_paths
            ]
            for future in as_completed(futures):
                future.result()
        return join_musicxml_files(xml_dir, output_path)


def image_to_musicxml(image_path: Path, output_path: Path, *, omr_module: str | None = None) -> Path:
    with tempfile.TemporaryDirectory(prefix="score2md-image-") as tmp:
        xml = run_oemer_image(image_path, Path(tmp), omr_module=omr_module)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(xml.read_bytes())
        return output_path


def _http_json(url: str, method: str = "GET", body: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_upload(url: str, file_path: Path, field: str = "file", timeout: int = 120) -> dict:
    boundary = "----score2mdBoundary"
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{file_path.name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    parsed = urllib.parse.urlsplit(url)
    connection_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    path = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    length = len(header) + file_path.stat().st_size + len(footer)
    connection = connection_cls(parsed.netloc, timeout=timeout)
    try:
        connection.putrequest("POST", path)
        connection.putheader("Host", parsed.netloc)
        connection.putheader("Content-Type", f"multipart/form-data; boundary={boundary}")
        connection.putheader("Content-Length", str(length))
        connection.endheaders()
        connection.send(header)
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                connection.send(chunk)
        connection.send(footer)
        response = connection.getresponse()
        payload = response.read()
        if response.status >= 400:
            raise urllib.error.HTTPError(url, response.status, response.reason, response.headers, None)
        return json.loads(payload.decode("utf-8"))
    finally:
        connection.close()


def _load_cached_job(job_cache_path: Path | None) -> str | None:
    if not job_cache_path or not job_cache_path.exists():
        return None
    try:
        data = json.loads(job_cache_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    job_id = data.get("job_id")
    return str(job_id) if job_id else None


def _write_cached_job(job_cache_path: Path | None, job_id: str, body: dict) -> None:
    if not job_cache_path:
        return
    job_cache_path.parent.mkdir(parents=True, exist_ok=True)
    job_cache_path.write_text(
        json.dumps({"job_id": job_id, "request": body, "created_at": time.time()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def ohsheet_to_musicxml(
    source: str | Path,
    output_path: Path,
    *,
    is_youtube: bool = False,
    is_video: bool = False,
    ffmpeg_path: str | Path | None = None,
    timeout_sec: int = 900,
    prefer_clean_source: bool = True,
    job_cache_path: Path | None = None,
    refresh_job: bool = False,
) -> Path:
    base = os.environ.get("SCORE2MD_OHSHEET_URL", "").rstrip("/")
    if not base:
        raise AdapterError("Set SCORE2MD_OHSHEET_URL to use audio, video, or YouTube conversion.")

    job_body: dict = {}
    job_id = None if refresh_job else _load_cached_job(job_cache_path)
    if not job_id:
        if is_youtube:
            job_body = {"title": str(source), "prefer_clean_source": prefer_clean_source}
        else:
            source_path = Path(source)
            with tempfile.TemporaryDirectory(prefix="score2md-video-") if is_video else _null_tempdir() as tmp:
                upload_path = source_path
                if is_video:
                    upload_path = video_to_wav(source_path, Path(tmp) / f"{source_path.stem}.wav", ffmpeg_path)
                audio = _http_upload(f"{base}/v1/uploads/audio", upload_path)
            job_body = {"audio": audio, "title": source_path.stem, "prefer_clean_source": prefer_clean_source}
        job = _http_json(f"{base}/v1/jobs", method="POST", body=job_body)
        job_id = job.get("job_id")
        if job_id:
            _write_cached_job(job_cache_path, str(job_id), job_body)
    if not job_id:
        raise AdapterError("oh-sheet did not return a job_id.")
    deadline = time.time() + max(1, timeout_sec)
    while time.time() < deadline:
        status = _http_json(f"{base}/v1/jobs/{urllib.parse.quote(job_id)}")
        if status.get("status") == "succeeded":
            break
        if status.get("status") == "failed":
            raise AdapterError(f"oh-sheet job failed: {status.get('error')}")
        time.sleep(2)
    else:
        raise AdapterError(f"oh-sheet job timed out: {job_id}")
    artifact_url = f"{base}/v1/artifacts/{urllib.parse.quote(job_id)}/musicxml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(artifact_url, timeout=60) as response:
            output_path.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        raise AdapterError(f"Could not download oh-sheet MusicXML artifact: HTTP {exc.code}") from exc
    return output_path


class _null_tempdir:
    def __enter__(self) -> str:
        return ""

    def __exit__(self, *_args: object) -> None:
        return None
