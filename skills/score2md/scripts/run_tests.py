#!/usr/bin/env python3
from __future__ import annotations

import io
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from score2md_lib.adapters import AdapterError, find_musescore_binary, find_omr_command, ohsheet_to_musicxml, run_oemer_image
from score2md_lib.detect import detect_source
from score2md_lib.pipeline import convert_to_md


FIXTURE = SCRIPT_DIR.parent / "assets" / "examples" / "simple-piano.musicxml"


KEY_CHANGE_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work><work-title>Key Change Fixture</work-title></work>
  <part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions><key><fifths>1</fifths><mode>minor</mode></key><time><beats>4</beats><beat-type>4</beat-type></time><staves>2</staves></attributes>
      <barline location="left"><repeat direction="forward"/></barline>
      <note><pitch><step>E</step><octave>4</octave></pitch><duration>1</duration><voice>1</voice><staff>1</staff></note>
      <note><chord/><pitch><step>G</step><octave>4</octave></pitch><duration>1</duration><voice>1</voice><staff>1</staff></note>
      <note><chord/><pitch><step>B</step><octave>4</octave></pitch><duration>1</duration><voice>1</voice><staff>1</staff></note>
      <note><rest/><duration>3</duration><voice>1</voice><staff>1</staff></note>
      <backup><duration>4</duration></backup>
      <note><pitch><step>E</step><octave>2</octave></pitch><duration>4</duration><voice>5</voice><staff>2</staff></note>
      <barline location="right"><ending number="1" type="start"/><repeat direction="backward"/></barline>
    </measure>
    <measure number="2">
      <attributes><key><fifths>-4</fifths><mode>minor</mode></key><time><beats>3</beats><beat-type>4</beat-type></time></attributes>
      <note><pitch><step>F</step><octave>4</octave></pitch><duration>3</duration><voice>1</voice><staff>1</staff></note>
      <backup><duration>3</duration></backup>
      <note><pitch><step>F</step><octave>2</octave></pitch><duration>3</duration><voice>5</voice><staff>2</staff></note>
      <barline location="left"><ending number="2" type="start"/></barline>
    </measure>
  </part>
</score-partwise>
"""


class Score2MdTests(unittest.TestCase):
    def test_musicxml_to_markdown_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "score.md"
            result = convert_to_md(FIXTURE, out)
            text = out.read_text(encoding="utf-8")
            self.assertEqual(text.count("```abc"), 1)
            self.assertTrue(text.rstrip().endswith("```"))
            self.assertFalse(re.search(r"K:[^\n]*\n\n", text))
            self.assertIn("%%score {RH LH}", text)
            self.assertIn("[V:RH]", text)
            self.assertIn("[V:LH]", text)
            self.assertIn("[=D=F=A]2", text)
            self.assertEqual(result.verification.status, "verified symbolic conversion")

    def test_mxl_unpacking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mxl = tmp_path / "fixture.mxl"
            xml_bytes = FIXTURE.read_bytes()
            with zipfile.ZipFile(mxl, "w") as archive:
                archive.writestr(
                    "META-INF/container.xml",
                    """<?xml version="1.0"?><container><rootfiles><rootfile full-path="score.musicxml"/></rootfiles></container>""",
                )
                archive.writestr("score.musicxml", xml_bytes)
            out = tmp_path / "score.md"
            result = convert_to_md(mxl, out)
            self.assertEqual(result.source_type, "mxl")
            self.assertIn("[=D=F=A]2", out.read_text(encoding="utf-8"))

    def test_key_time_repeats_and_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "changes.musicxml"
            src.write_text(KEY_CHANGE_FIXTURE, encoding="utf-8")
            out = Path(tmp) / "changes.md"
            result = convert_to_md(src, out, verify="strict")
            text = out.read_text(encoding="utf-8")
            self.assertIn("K:Em", text)
            self.assertIn("K:Fm", text)
            self.assertIn("M:3/4", text)
            self.assertIn("|:", text)
            self.assertIn(":|", text)
            self.assertIn("[1", text)
            self.assertIn("[2", text)
            self.assertEqual(result.verification.key_changes, 1)
            self.assertEqual(result.verification.time_changes, 1)
            self.assertEqual(result.verification.repeats_endings, 4)

    def test_abc_wrapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input.abc"
            src.write_text("X:1\nT:Raw\nM:4/4\nQ:1/4=120\nL:1/8\nK:C\n\nC2 E2 G4 |\n", encoding="utf-8")
            out = Path(tmp) / "raw.md"
            convert_to_md(src, out)
            text = out.read_text(encoding="utf-8")
            self.assertEqual(text.count("```abc"), 1)
            self.assertFalse(re.search(r"K:[^\n]*\n\n", text))
            self.assertTrue(text.rstrip().endswith("```"))

    @patch("score2md_lib.adapters.shutil.which")
    def test_musescore_discovery(self, mock_which: MagicMock) -> None:
        mock_which.side_effect = lambda name: "/usr/bin/MuseScore4" if name == "MuseScore4" else None
        self.assertEqual(find_musescore_binary().as_posix(), "/usr/bin/MuseScore4")

    @patch("score2md_lib.adapters.importlib.util.find_spec")
    @patch("score2md_lib.adapters.shutil.which")
    def test_omr_module_fallback(self, mock_which: MagicMock, mock_find_spec: MagicMock) -> None:
        mock_which.return_value = None
        mock_find_spec.side_effect = lambda name: object() if name == "omr_parser.ete" else None
        command = find_omr_command()
        self.assertEqual(command[-2:], ["-m", "omr_parser.ete"])

    @patch("score2md_lib.adapters.find_omr_command")
    @patch("score2md_lib.adapters.subprocess.run")
    def test_oemer_command_shape(self, mock_run: MagicMock, mock_find_omr: MagicMock) -> None:
        mock_find_omr.return_value = [sys.executable, "-W", "ignore", "-m", "oemer.ete"]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image = tmp_path / "page.png"
            image.write_bytes(b"fake")

            def side_effect(*_args, **kwargs):
                cwd = Path(kwargs["cwd"])
                (cwd / "page.musicxml").write_text("<score-partwise/>", encoding="utf-8")
                return MagicMock()

            mock_run.side_effect = side_effect
            out = run_oemer_image(image, tmp_path / "xml")
            command = mock_run.call_args.args[0]
            self.assertIn("-m", command)
            self.assertIn("oemer.ete", command)
            self.assertTrue(out.exists())

    @patch("score2md_lib.adapters._http_json")
    @patch("score2md_lib.adapters.urllib.request.urlopen")
    def test_ohsheet_youtube_flow(self, mock_urlopen: MagicMock, mock_json: MagicMock) -> None:
        import os

        mock_json.side_effect = [
            {"job_id": "abc"},
            {"status": "succeeded"},
        ]
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"<score-partwise/>"
        mock_urlopen.return_value = response
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["SCORE2MD_OHSHEET_URL"] = "http://localhost:8000"
            out = Path(tmp) / "score.musicxml"
            ohsheet_to_musicxml("https://youtu.be/example", out, is_youtube=True, prefer_clean_source=False)
            self.assertFalse(mock_json.call_args_list[0].kwargs["body"]["prefer_clean_source"])
            self.assertTrue(out.exists())

    @patch("score2md_lib.adapters._http_json")
    @patch("score2md_lib.adapters._http_upload")
    @patch("score2md_lib.adapters.urllib.request.urlopen")
    @patch("score2md_lib.adapters.subprocess.run")
    def test_video_to_audio_to_ohsheet_flow(
        self,
        mock_run: MagicMock,
        mock_urlopen: MagicMock,
        mock_upload: MagicMock,
        mock_json: MagicMock,
    ) -> None:
        import os

        def run_side_effect(args, **_kwargs):
            Path(args[-1]).write_bytes(b"wav")
            return MagicMock()

        mock_run.side_effect = run_side_effect
        mock_upload.return_value = {"uri": "file:///audio.wav", "format": "wav"}
        mock_json.side_effect = [{"job_id": "vid"}, {"status": "succeeded"}]
        response = MagicMock()
        response.__enter__.return_value.read.return_value = FIXTURE.read_bytes()
        mock_urlopen.return_value = response
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["SCORE2MD_OHSHEET_URL"] = "http://localhost:8000"
            src = Path(tmp) / "clip.mp4"
            src.write_bytes(b"video")
            out = Path(tmp) / "score.musicxml"
            ohsheet_to_musicxml(src, out, is_video=True, ffmpeg_path=src)
            self.assertEqual(Path(mock_upload.call_args.args[1]).suffix, ".wav")
            self.assertIn("-vn", mock_run.call_args.args[0])
            self.assertTrue(out.exists())

    def test_ohsheet_requires_configured_service(self) -> None:
        import os

        old_value = os.environ.pop("SCORE2MD_OHSHEET_URL", None)
        try:
            with self.assertRaises(AdapterError):
                ohsheet_to_musicxml("https://youtu.be/example", Path("out.musicxml"), is_youtube=True)
        finally:
            if old_value is not None:
                os.environ["SCORE2MD_OHSHEET_URL"] = old_value

    @patch("score2md_lib.adapters._http_json")
    def test_ohsheet_failed_job_reports_error(self, mock_json: MagicMock) -> None:
        import os

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["SCORE2MD_OHSHEET_URL"] = "http://localhost:8000"
            mock_json.side_effect = [{"job_id": "bad"}, {"status": "failed", "error": "transcription failed"}]
            with self.assertRaisesRegex(AdapterError, "transcription failed"):
                ohsheet_to_musicxml("https://youtu.be/example", Path(tmp) / "score.musicxml", is_youtube=True)

    @patch("score2md_lib.adapters.time.sleep")
    @patch("score2md_lib.adapters.time.time")
    @patch("score2md_lib.adapters._http_json")
    def test_ohsheet_timeout_reports_job(self, mock_json: MagicMock, mock_time: MagicMock, _mock_sleep: MagicMock) -> None:
        import os

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["SCORE2MD_OHSHEET_URL"] = "http://localhost:8000"
            mock_json.side_effect = [{"job_id": "slow"}, {"status": "running"}]
            mock_time.side_effect = [0, 0, 2]
            with self.assertRaisesRegex(AdapterError, "timed out: slow"):
                ohsheet_to_musicxml(
                    "https://youtu.be/example",
                    Path(tmp) / "score.musicxml",
                    is_youtube=True,
                    timeout_sec=1,
                )

    @patch("score2md_lib.pipeline.image_to_musicxml")
    def test_normalized_musicxml_cache_reuse_and_refresh(self, mock_image_to_xml: MagicMock) -> None:
        def fake_image_to_xml(_source, output, **_kwargs):
            Path(output).write_bytes(FIXTURE.read_bytes())
            return Path(output)

        mock_image_to_xml.side_effect = fake_image_to_xml
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "page.png"
            src.write_bytes(b"fake image")
            first = convert_to_md(src, Path(tmp) / "first.md")
            second = convert_to_md(src, Path(tmp) / "second.md")
            third = convert_to_md(src, Path(tmp) / "third.md", refresh_cache=True)
            self.assertFalse(first.used_cache)
            self.assertTrue(second.used_cache)
            self.assertFalse(third.used_cache)
            self.assertEqual(mock_image_to_xml.call_count, 2)

    def test_non_youtube_http_url_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "only supported for YouTube"):
            detect_source("https://example.com/audio.mp3")


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
