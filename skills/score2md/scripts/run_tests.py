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

from score2md_lib.adapters import find_musescore_binary, run_oemer_image
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
            convert_to_md(src, out, verify="summary")
            text = out.read_text(encoding="utf-8")
            self.assertIn("K:Em", text)
            self.assertIn("K:Fm", text)
            self.assertIn("M:3/4", text)
            self.assertIn("|:", text)
            self.assertIn(":|", text)
            self.assertIn("[1", text)
            self.assertIn("[2", text)

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

    @patch("score2md_lib.adapters.subprocess.run")
    def test_oemer_command_shape(self, mock_run: MagicMock) -> None:
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
        from score2md_lib.adapters import ohsheet_to_musicxml
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
            ohsheet_to_musicxml("https://youtu.be/example", out, is_youtube=True)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
