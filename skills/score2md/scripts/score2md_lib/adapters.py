from __future__ import annotations

import json
import os
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
    deskew: bool = True,
    use_tf: bool = False,
    save_cache: bool = True,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-W", "ignore", "-m", "oemer.ete", str(image_path), "-o", str(output_dir)]
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
    subprocess.run(command, cwd=str(output_dir), env=env, check=True, capture_output=True, text=True)
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


def pdf_to_musicxml(pdf_path: Path, output_path: Path, *, omr_workers: int = 2) -> Path:
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
            futures = [executor.submit(run_oemer_image, image_path, xml_dir) for image_path in image_paths]
            for future in as_completed(futures):
                future.result()
        return join_musicxml_files(xml_dir, output_path)


def image_to_musicxml(image_path: Path, output_path: Path) -> Path:
    with tempfile.TemporaryDirectory(prefix="score2md-image-") as tmp:
        xml = run_oemer_image(image_path, Path(tmp))
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
    data = file_path.read_bytes()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{file_path.name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    request = urllib.request.Request(
        url,
        data=header + data + footer,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def ohsheet_to_musicxml(source: str | Path, output_path: Path, *, is_youtube: bool = False) -> Path:
    base = os.environ.get("SCORE2MD_OHSHEET_URL", "").rstrip("/")
    if not base:
        raise AdapterError("Set SCORE2MD_OHSHEET_URL to use audio, video, or YouTube conversion.")
    if is_youtube:
        job_body = {"title": str(source), "prefer_clean_source": True}
    else:
        source_path = Path(source)
        audio = _http_upload(f"{base}/v1/uploads/audio", source_path)
        job_body = {"audio": audio, "title": source_path.stem}
    job = _http_json(f"{base}/v1/jobs", method="POST", body=job_body)
    job_id = job.get("job_id")
    if not job_id:
        raise AdapterError(f"oh-sheet did not return a job_id: {job}")
    deadline = time.time() + 900
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
