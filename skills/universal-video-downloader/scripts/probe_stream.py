#!/usr/bin/env python3
"""
REA-Style Stream & Public Media Evidence Probe
Performs evidence-driven inspection of target media URLs before downloading.
Enumerates yt-dlp streams and probes public HLS/DASH manifests and HTML5 video nodes.
Enforces conditional 18+ adult verification only for age-restricted / explicit media.
"""

import argparse
import sys
import os
import re
import json
import hashlib
import urllib.request
import urllib.parse
import subprocess
import shutil

# Reconfigure console encodings for Windows
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
    from verify_compliance import validate_attestation_token, normalize_url, compute_url_hash
except ImportError:
    validate_attestation_token = None


def probe_ytdlp(url: str) -> dict:
    """Stage 1: Probe media stream metadata via yt-dlp."""
    if not shutil.which("yt-dlp"):
        return {"error": "yt-dlp binary not found on system PATH."}

    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android,ios,web"
    ]
    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node"])
    cmd.append(url)

    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        data = json.loads(res.stdout)
        return {"success": True, "data": data}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr.strip() if e.stderr else str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def probe_public_manifest_url(manifest_url: str) -> dict:
    """Probe an individual discovered manifest or media stream URL for HTTP headers and hash."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UniversalVideoDownloader/1.0"}
    probe_info = {
        "url": manifest_url,
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "sample_sha256": None,
        "is_reachable": False
    }

    try:
        req = urllib.request.Request(manifest_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            probe_info["http_status"] = response.getcode()
            probe_info["content_type"] = response.headers.get("Content-Type")
            probe_info["content_length"] = response.headers.get("Content-Length")
            probe_info["is_reachable"] = (response.getcode() == 200)

            chunk = response.read(65536)
            if chunk:
                probe_info["sample_sha256"] = hashlib.sha256(chunk).hexdigest()
    except Exception as e:
        probe_info["error"] = str(e)

    return probe_info


def probe_html5_manifests(url: str) -> dict:
    """Stage 2: REA Public Web Fallback. Probes HTML5 <video>, <source>, HLS (.m3u8), and DASH (.mpd)."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UniversalVideoDownloader/1.0"}
    results = {
        "page_reachable": False,
        "title": None,
        "discovered_streams": [],
        "manifest_probes": []
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            results["page_reachable"] = (response.getcode() == 200)
            html_text = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        results["error"] = f"Failed to fetch public webpage: {e}"
        return results

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        results["title"] = title_match.group(1).strip()

    m3u8_links = re.findall(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', html_text)
    mpd_links = re.findall(r'(https?://[^\s"\'<>]+\.mpd[^\s"\'<>]*)', html_text)
    mp4_links = re.findall(r'(https?://[^\s"\'<>]+\.(?:mp4|webm|mkv)[^\s"\'<>]*)', html_text)
    video_tag_srcs = re.findall(r'<(?:video|source)[^>]+src=["\']([^"\']+)["\']', html_text, re.IGNORECASE)

    all_candidates = set()
    for link in m3u8_links + mpd_links + mp4_links:
        all_candidates.add(link)

    for src in video_tag_srcs:
        full_url = urllib.parse.urljoin(url, src)
        all_candidates.add(full_url)

    for cand in list(all_candidates)[:5]:
        stream_type = "hls_manifest" if ".m3u8" in cand else ("dash_manifest" if ".mpd" in cand else "direct_media")
        probe_res = probe_public_manifest_url(cand)
        probe_res["stream_type"] = stream_type
        results["discovered_streams"].append(probe_res)

    return results


def compile_evidence_report(url: str, ytdlp_res: dict, html5_res: dict, age_info: dict) -> dict:
    """Compile comprehensive REA-style evidence matrix."""
    evidence = {
        "target_url": url,
        "target_url_sha256": hashlib.sha256(url.strip().encode("utf-8")).hexdigest(),
        "age_rating": age_info,
        "primary_extractor": None,
        "title": None,
        "duration_seconds": None,
        "uploader": None,
        "resolutions_available": [],
        "formats_matrix": [],
        "html5_fallback": html5_res,
        "inferred_recommendation": {}
    }

    if ytdlp_res.get("success"):
        info = ytdlp_res["data"]
        evidence["primary_extractor"] = info.get("extractor", "generic")
        evidence["title"] = info.get("title")
        evidence["duration_seconds"] = info.get("duration")
        evidence["uploader"] = info.get("uploader")

        formats = info.get("formats", [])
        seen_res = set()
        fmt_list = []

        for f in formats:
            height = f.get("height")
            width = f.get("width")
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            fps = f.get("fps")
            ext = f.get("ext", "unknown")
            filesize = f.get("filesize") or f.get("filesize_approx")

            res_label = f"{height}p" if height else (f"{width}x{height}" if width and height else "audio-only")
            if height:
                seen_res.add(height)

            fmt_list.append({
                "format_id": f.get("format_id"),
                "resolution": res_label,
                "fps": fps,
                "vcodec": vcodec,
                "acodec": acodec,
                "ext": ext,
                "filesize_bytes": filesize,
                "filesize_mb": round(filesize / (1024 * 1024), 2) if filesize else None,
                "protocol": f.get("protocol")
            })

        evidence["formats_matrix"] = fmt_list
        sorted_heights = sorted(list(seen_res), reverse=True)
        evidence["resolutions_available"] = [f"{h}p" for h in sorted_heights]

        max_h = sorted_heights[0] if sorted_heights else None
        evidence["inferred_recommendation"] = {
            "highest_resolution": f"{max_h}p" if max_h else "best",
            "is_4k_available": (max_h is not None and max_h >= 2160),
            "is_1080p_available": (max_h is not None and max_h >= 1080),
            "recommended_format": "mp4",
            "recommended_merge_rule": "bestvideo+bestaudio/best"
        }
    else:
        evidence["primary_extractor"] = "html5_public_manifest_fallback"
        evidence["title"] = html5_res.get("title", "Discovered Web Media")
        if html5_res.get("discovered_streams"):
            first_stream = html5_res["discovered_streams"][0]
            evidence["inferred_recommendation"] = {
                "highest_resolution": "direct_manifest",
                "recommended_stream_url": first_stream["url"],
                "stream_type": first_stream.get("stream_type"),
                "recommended_merge_rule": "ffmpeg_stream_copy"
            }

    return evidence


def print_formatted_report(evidence: dict):
    """Print readable REA-style evidence matrix to terminal."""
    age_meta = evidence.get("age_rating", {})
    age_label = "18+ RESTRICTED (Adult Confirmed)" if age_meta.get("is_restricted") else f"General Audience (age_limit: {age_meta.get('age_limit', 0)})"

    print("=" * 70)
    print("  REA STREAM PROBE: PUBLIC MEDIA EVIDENCE REPORT")
    print("=" * 70)
    print(f"Target URL:         {evidence['target_url']}")
    print(f"URL SHA-256:        {evidence['target_url_sha256']}")
    print(f"Age Classification: {age_label}")
    print(f"Extractor Engine:   {evidence['primary_extractor']}")
    print(f"Title:              {evidence['title'] or 'Unknown'}")
    if evidence['duration_seconds']:
        mins = evidence['duration_seconds'] // 60
        secs = evidence['duration_seconds'] % 60
        print(f"Duration:           {mins}m {secs}s ({evidence['duration_seconds']}s)")
    if evidence['uploader']:
        print(f"Uploader / Creator: {evidence['uploader']}")
    print("-" * 70)

    formats = evidence.get("formats_matrix", [])
    if formats:
        print("CONFIRMED STREAMS & FORMAT MATRIX (yt-dlp):")
        print(f"{'ID':<10} {'Resolution':<12} {'FPS':<6} {'V-Codec':<14} {'A-Codec':<12} {'Size (MB)':<10}")
        print("-" * 68)
        displayed = formats[-15:] if len(formats) > 15 else formats
        for f in displayed:
            fid = str(f['format_id'])[:9]
            res = str(f['resolution'])[:11]
            fps = str(f['fps'] or '-')[:5]
            vc = str(f['vcodec'] or 'none')[:13]
            ac = str(f['acodec'] or 'none')[:11]
            sz = f"{f['filesize_mb']} MB" if f['filesize_mb'] else "~"
            print(f"{fid:<10} {res:<12} {fps:<6} {vc:<14} {ac:<12} {sz:<10}")
        print(f"Total stream variants identified: {len(formats)}")
        print(f"Resolutions: {', '.join(evidence.get('resolutions_available', []))}")
    else:
        print("NO DIRECT EXTRACTOR FORMATS FOUND. Probing public HTML5 fallback...")

    html5 = evidence.get("html5_fallback", {})
    streams = html5.get("discovered_streams", [])
    if streams:
        print("\nPUBLIC HTML5 & MANIFEST DISCOVERY (REA Fallback):")
        for idx, s in enumerate(streams, 1):
            status = f"HTTP {s['http_status']}" if s['http_status'] else "Offline"
            ctype = s['content_type'] or "unknown"
            hash_str = s['sample_sha256'][:16] + "..." if s.get('sample_sha256') else "n/a"
            print(f"  [{idx}] Type: {s['stream_type'].upper():<14} Status: {status:<10} Type: {ctype}")
            print(f"      URL:  {s['url']}")
            print(f"      Hash: {hash_str}")

    rec = evidence.get("inferred_recommendation", {})
    print("-" * 70)
    print("INFERRED REA RECOMMENDATIONS:")
    print(f"  Optimal Quality:  {rec.get('highest_resolution', 'best')}")
    print(f"  4K / 2160p:       {'YES (Available)' if rec.get('is_4k_available') else 'NO'}")
    print(f"  Full HD 1080p:    {'YES (Available)' if rec.get('is_1080p_available') else 'NO'}")
    print(f"  Download Rule:    {rec.get('recommended_merge_rule', 'bestvideo+bestaudio/best')}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="REA-Style Stream & Public Media Evidence Probe for Universal Video Downloader"
    )
    parser.add_argument("--url", required=True, help="Target public media URL")
    parser.add_argument("--confirm-adult-18plus", action="store_true", help="Affirm 18+ adult age if media is age-restricted")
    parser.add_argument("--signature", type=str, default="", help="Optional signature string")
    parser.add_argument("--attestation", default="compliance_attestation.json", help="Path to compliance attestation JSON")
    parser.add_argument("--probe-html", action="store_true", help="Force probe public webpage HTML for direct HLS/DASH/HTML5 video streams")
    parser.add_argument("--json", action="store_true", help="Output evidence report as pure JSON")

    args = parser.parse_args()

    # Step 1: Probe metadata without initial blocking
    ytdlp_res = probe_ytdlp(args.url)

    # Determine age rating
    age_limit = 0
    is_restricted = False
    title = "Public Media"
    if ytdlp_res.get("success"):
        info = ytdlp_res["data"]
        age_limit = int(info.get("age_limit") or 0)
        title = info.get("title") or "Public Media"
        is_restricted = (age_limit >= 18)

    # Step 2: Enforce 18+ gate ONLY if media is age-restricted (18+)
    adult_confirmed = False
    if is_restricted:
        if args.confirm_adult_18plus:
            adult_confirmed = True
        elif validate_attestation_token and os.path.exists(args.attestation):
            is_valid, msg, tdata = validate_attestation_token(args.attestation, args.url)
            if is_valid:
                adult_confirmed = True

        if not adult_confirmed:
            print("=" * 65, file=sys.stderr)
            print("[AGE RESTRICTION DETECTED: 18+ ADULT CONFIRMATION REQUIRED]", file=sys.stderr)
            print("=" * 65, file=sys.stderr)
            print(f"Media Title:  {title}", file=sys.stderr)
            print(f"Age Rating:   {age_limit}+ (Adult / Age-Gated Media)", file=sys.stderr)
            print("", file=sys.stderr)
            print("This media stream is classified as explicit or age-restricted.", file=sys.stderr)
            print("Please re-run with confirmation of adult age:", file=sys.stderr)
            print(f"  python scripts/probe_stream.py --url \"{args.url}\" --confirm-adult-18plus", file=sys.stderr)
            print("=" * 65, file=sys.stderr)
            sys.exit(2)
    else:
        # Non-explicit media: automatically confirmed as General Audience
        adult_confirmed = True

    age_info = {
        "is_restricted": is_restricted,
        "age_limit": age_limit,
        "adult_confirmed": adult_confirmed,
        "classification": "18+ Adult" if is_restricted else "General Audience"
    }

    # Step 3: Probing Stage 2 (HTML5 fallback if requested or needed)
    html5_res = {}
    if args.probe_html or not ytdlp_res.get("success"):
        html5_res = probe_html5_manifests(args.url)

    # Step 4: Compile and present evidence
    evidence = compile_evidence_report(args.url, ytdlp_res, html5_res, age_info)

    if args.json:
        print(json.dumps(evidence, indent=2))
    else:
        print_formatted_report(evidence)

    sys.exit(0)


if __name__ == "__main__":
    main()
