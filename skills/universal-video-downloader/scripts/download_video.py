#!/usr/bin/env python3
"""
Universal Multi-Quality Video Downloader
Supports any public media URL (YouTube, Vimeo, Twitch, direct HLS/DASH/MP4 streams).
Enforces conditional 18+ verification only for age-restricted / explicit media.
General audience media downloads immediately without restriction.
"""

import argparse
import sys
import os
import re
import json
import hashlib
import subprocess
import shutil
from datetime import datetime

# Configure UTF-8 on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Import compliance verification helper from sibling script
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from verify_compliance import validate_attestation_token, check_media_age_rating, normalize_url
except ImportError:
    validate_attestation_token = None
    check_media_age_rating = None


def check_prerequisites():
    """Verify that required external binaries (yt-dlp and ffmpeg) are present."""
    has_ytdlp = bool(shutil.which("yt-dlp"))
    has_ffmpeg = bool(shutil.which("ffmpeg"))
    return has_ytdlp, has_ffmpeg


def sanitize_filename(name: str) -> str:
    """Sanitize strings for clean filesystem paths across Windows, macOS, and Linux."""
    clean = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    clean = clean.rstrip(". ")
    clean = re.sub(r"\s+", " ", clean)
    return clean if clean else "downloaded_media"


def compute_file_sha256(filepath: str, block_size: int = 65536) -> str:
    """Compute SHA-256 checksum of completed media file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha.update(block)
    return sha.hexdigest()


def probe_file_streams(filepath: str) -> dict:
    """Probe downloaded media container using ffprobe for codec and geometry verification."""
    if not shutil.which("ffprobe"):
        return {}

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,channels",
        "-show_entries", "format=duration,size",
        "-of", "json",
        filepath
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return json.loads(res.stdout)
    except Exception:
        return {}


def download_with_ffmpeg_fallback(url: str, output_path: str, format_type: str = "mp4") -> str:
    """Direct HLS/DASH or HTML5 media stream fallback using ffmpeg directly."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for direct stream fallback downloads.")

    os.makedirs(output_path, exist_ok=True)
    out_filename = f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
    target_file = os.path.join(output_path, out_filename)

    cmd = [
        "ffmpeg",
        "-y",
        "-headers", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) UniversalVideoDownloader/1.0\r\n",
        "-i", url,
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        target_file
    ]

    print(f"[FALLBACK] Invoking direct ffmpeg stream capture to: {target_file}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg direct stream copy failed: {res.stderr.strip()[:300]}")

    return target_file


def execute_download(
    url: str,
    output_dir: str = "./downloads",
    quality: str = "best",
    format_type: str = "mp4",
    audio_only: bool = False,
    subtitles: bool = False,
    allow_playlist: bool = False,
    concurrent_fragments: int = 4
) -> dict:
    """Execute complete video download with yt-dlp and ffmpeg pipeline."""
    has_ytdlp, has_ffmpeg = check_prerequisites()
    if not has_ytdlp:
        raise RuntimeError("yt-dlp is not installed or not found on PATH. Install via Scoop, Winget, or pip.")

    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android,ios,web"
    ]

    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node"])

    if allow_playlist:
        cmd.extend([
            "--yes-playlist",
            "-o", os.path.join(output_dir, "%(playlist_index)02d - %(title)s.%(ext)s")
        ])
    else:
        cmd.extend([
            "--no-playlist",
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s")
        ])

    if audio_only:
        cmd.extend([
            "-x",
            "--audio-format", "mp3" if format_type == "mp4" else format_type,
            "--audio-quality", "0"
        ])
    else:
        if quality == "best":
            format_spec = "bestvideo+bestaudio/best"
        elif quality == "worst":
            format_spec = "worstvideo+worstaudio/worst"
        else:
            height = quality.replace("p", "")
            format_spec = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        cmd.extend([
            "-f", format_spec,
            "--merge-output-format", format_type
        ])

    if subtitles and not audio_only:
        cmd.extend([
            "--write-subs",
            "--write-auto-subs",
            "--embed-subs",
            "--sub-langs", "all,-live_chat"
        ])

    archive_file = os.path.join(output_dir, ".download_archive.txt")
    cmd.extend([
        "--windows-filenames",
        "--ignore-errors",
        "--retries", "5",
        "--fragment-retries", "5",
        "--concurrent-fragments", str(concurrent_fragments),
        "--download-archive", archive_file,
        "--match-filter", "live_status !=? is_upcoming & !is_live"
    ])

    cmd.append(url)

    print(f"Downloading Media from: {url}")
    print(f"Quality Mode:           {quality}")
    print(f"Container Format:       {format_type if not audio_only else 'mp3 (audio-only)'}")
    print(f"Output Directory:       {os.path.abspath(output_dir)}")
    print(f"Stream Fragments:       {concurrent_fragments} concurrent workers\n")

    expected_file = None
    try:
        p_name = subprocess.run(
            ["yt-dlp", "--windows-filenames", "--print", "filename", "-o", os.path.join(output_dir, "%(title)s.%(ext)s" if not allow_playlist else "%(playlist_index)02d - %(title)s.%(ext)s"), url],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if p_name.returncode == 0 and p_name.stdout.strip():
            expected_file = os.path.basename(p_name.stdout.strip().splitlines()[-1])
    except Exception:
        pass

    initial_files = set(os.listdir(output_dir))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        lower_url = url.lower()
        if ".m3u8" in lower_url or ".mpd" in lower_url or lower_url.endswith(".mp4"):
            print("\n[NOTICE] yt-dlp returned non-zero code. Attempting direct ffmpeg stream fallback...")
            fallback_file = download_with_ffmpeg_fallback(url, output_dir, format_type)
            new_files = [os.path.basename(fallback_file)]
        else:
            raise e

    current_files = set(os.listdir(output_dir))
    new_files = [f for f in (current_files - initial_files) if not f.startswith(".")]

    if not new_files and expected_file and os.path.exists(os.path.join(output_dir, expected_file)):
        new_files = [expected_file]

    results = {
        "status": "success",
        "url": url,
        "output_dir": os.path.abspath(output_dir),
        "quality": quality,
        "format": format_type,
        "files_downloaded": []
    }

    for fname in new_files:
        fpath = os.path.join(output_dir, fname)
        if not os.path.isfile(fpath):
            continue

        size_bytes = os.path.getsize(fpath)
        sha256_hash = compute_file_sha256(fpath)
        stream_meta = probe_file_streams(fpath)

        file_summary = {
            "file_name": fname,
            "file_path": os.path.abspath(fpath),
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "sha256_checksum": sha256_hash,
            "streams": stream_meta.get("streams", [])
        }
        results["files_downloaded"].append(file_summary)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Universal Video Downloader with Multi-Quality, Format Conversion & Conditional 18+ Compliance"
    )
    parser.add_argument("url", help="Target public media or video URL")
    parser.add_argument("-q", "--quality", default="best", choices=["best", "2160p", "1440p", "1080p", "720p", "480p", "360p", "worst"], help="Target video resolution (default: best)")
    parser.add_argument("-f", "--format", default="mp4", choices=["mp4", "mkv", "webm"], help="Output container format (default: mp4)")
    parser.add_argument("-a", "--audio-only", action="store_true", help="Extract audio only (default MP3)")
    parser.add_argument("-s", "--subtitles", action="store_true", help="Embed available subtitles/captions")
    parser.add_argument("-o", "--output", default="./downloads", help="Output directory path (default: ./downloads)")
    parser.add_argument("--playlist", action="store_true", help="Allow downloading entire playlists")
    parser.add_argument("--concurrent-fragments", type=int, default=4, help="Number of concurrent fragment streams for accelerated downloading (default: 4)")
    parser.add_argument("--confirm-adult-18plus", action="store_true", help="Affirm 18+ adult age if the target media is age-restricted")
    parser.add_argument("--signature", type=str, default="", help="Optional signature string")
    parser.add_argument("--attestation", default=None, help="Path to 18+ legal compliance attestation JSON file")
    parser.add_argument("--json", action="store_true", help="Output summary report as JSON")

    args = parser.parse_args()

    # Step 1: Evaluate 18+ Compliance Gate (Conditional)
    adult_confirmed = False
    if args.confirm_adult_18plus:
        adult_confirmed = True
    elif validate_attestation_token:
        candidate_paths = [
            args.attestation,
            "compliance_attestation.json",
            os.path.join(args.output, "compliance_attestation.json")
        ]
        for cp in candidate_paths:
            if cp and os.path.exists(cp):
                is_valid, msg, token_data = validate_attestation_token(cp, args.url)
                if is_valid:
                    adult_confirmed = True
                    break

    # If adult confirmation not supplied, inspect whether media actually requires 18+ verification
    if not adult_confirmed and check_media_age_rating:
        is_restricted, age_limit, title = check_media_age_rating(args.url)
        if is_restricted:
            print("=" * 65, file=sys.stderr)
            print("[AGE RESTRICTION DETECTED: 18+ ADULT CONFIRMATION REQUIRED]", file=sys.stderr)
            print("=" * 65, file=sys.stderr)
            print(f"Target Media: {title}", file=sys.stderr)
            print(f"URL:          {args.url}", file=sys.stderr)
            print(f"Age Limit:    {age_limit}+ (Adult / Age-Gated Content)", file=sys.stderr)
            print("", file=sys.stderr)
            print("Because this media is classified as adult/explicit, you must affirm", file=sys.stderr)
            print("that you are 18 years of age or older in your jurisdiction.", file=sys.stderr)
            print("", file=sys.stderr)
            print("Re-run with adult confirmation:", file=sys.stderr)
            print(f"  python scripts/download_video.py \"{args.url}\" --confirm-adult-18plus", file=sys.stderr)
            print("=" * 65, file=sys.stderr)
            sys.exit(2)
        else:
            print(f"[COMPLIANCE] General Audience media detected (Rating: General). Proceeding directly.\n")
    elif adult_confirmed:
        print("[COMPLIANCE VERIFIED] 18+ Adult Certification confirmed.\n")

    # Step 2: Execute Universal Download
    try:
        summary = execute_download(
            url=args.url,
            output_dir=args.output,
            quality=args.quality,
            format_type=args.format,
            audio_only=args.audio_only,
            subtitles=args.subtitles,
            allow_playlist=args.playlist,
            concurrent_fragments=args.concurrent_fragments
        )

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("\n" + "=" * 65)
            print("  DOWNLOAD COMPLETE: SUMMARY & CRYPTOGRAPHIC VERIFICATION")
            print("=" * 65)
            print(f"Destination Folder: {summary['output_dir']}")
            print(f"Total Files:        {len(summary['files_downloaded'])}")
            for idx, f in enumerate(summary["files_downloaded"], 1):
                print(f"\n  File [{idx}]: {f['file_name']}")
                print(f"    Size:       {f['size_mb']} MB ({f['size_bytes']} bytes)")
                print(f"    SHA-256:    {f['sha256_checksum']}")
                for s in f.get("streams", []):
                    cname = s.get("codec_name", "unknown")
                    w = s.get("width")
                    h = s.get("height")
                    geom = f"{w}x{h}" if w and h else "audio"
                    print(f"    Stream:     {cname:<10} ({geom})")
            print("=" * 65)

        sys.exit(0)
    except Exception as e:
        print(f"\n[DOWNLOAD ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
