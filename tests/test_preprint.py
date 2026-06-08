"""Tests for the two-pass streaming rewrite of preprint.py.

Each test uses a small synthetic gcode file rather than the 87 MB production
file, so the suite runs quickly and without external dependencies.
"""
import hashlib
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Import the module under test.  preprint.py lives one directory above tests/.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))
import preprint  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fresh_gcode(path: Path, *, with_exclude: bool = True) -> None:
    """Write a minimal OrcaSlicer-style gcode file that has NOT been processed."""
    lines = [
        "; OrcaSlicer generated gcode\n",
        "; filament_colour = #FF0000\n",
        "; filament_type = PLA\n",
        "; filament_max_volumetric_speed = 12\n",
        "; Bambufy: v1.2.3\n",
    ]
    if with_exclude:
        lines.append(
            "EXCLUDE_OBJECT_DEFINE NAME=MyObject"
            " CENTER=100.0000,100.0000"
            " POLYGON=[[90,90],[110,90],[110,110],[90,110]]\n"
        )
    lines += [
        "T0\n",
        "G28\n",
        "G1 X100 Y100 F3000\n",
        "; END OF GCODE\n",
    ]
    path.write_bytes("".join(lines).encode("utf-8"))


def _make_processed_gcode(path: Path) -> None:
    """Write a minimal gcode file that has already been processed.

    Structure: line 1 = MD5 comment, line 2 = _IFS_COLORS comment.
    """
    ifs_body = (
        "_IFS_COLORS START=1 TYPES=PLA E_FEEDRATES=5400"
        " COLORS=FF0000 TOOLS=0 VERSION=1.2.3 EXCLUDE=\"None\"\n"
    )
    ifs_line = "; " + ifs_body
    md5_val = hashlib.md5(("; " + ifs_body).encode("utf-8")).hexdigest()
    lines = [
        f"; MD5:{md5_val}\n",
        ifs_line,
        "; OrcaSlicer generated gcode\n",
        "T0\n",
        "G28\n",
        "; END OF GCODE\n",
    ]
    path.write_bytes("".join(lines).encode("utf-8"))


def _read_lines(path: Path):
    return path.read_bytes().decode("utf-8").splitlines(keepends=True)


# ---------------------------------------------------------------------------
# Test 1: Fresh large file — Pass 1 + Pass 2 run, header injected at line 2,
#          original replaced.
# ---------------------------------------------------------------------------

@patch("preprint.write_to_file")
def test_fresh_file_header_injected(mock_write, tmp_path):
    """A fresh (unprocessed) file gets _IFS_COLORS injected at line 2."""
    gcode = tmp_path / "print.gcode"
    _make_fresh_gcode(gcode, with_exclude=True)

    sys.argv = ["preprint.py", str(gcode)]
    preprint.main()

    lines = _read_lines(gcode)

    # Line 1 — MD5 checksum comment
    assert lines[0].startswith("; MD5:"), (
        f"Expected ''; MD5:'' on line 1, got: {lines[0]!r}"
    )

    # Line 2 — _IFS_COLORS header
    assert lines[1].startswith("; _IFS_COLORS "), (
        f"Expected ''; _IFS_COLORS'' on line 2, got: {lines[1]!r}"
    )

    ifs = lines[1]
    assert "COLORS=FF0000" in ifs, "Filament colour not parsed from header"
    assert "TYPES=PLA" in ifs, "Filament type not parsed from header"
    assert "TOOLS=0" in ifs, "Tool reference not parsed from header"
    assert "VERSION=1.2.3" in ifs, "Bambufy version not parsed from header"
    assert "EXCLUDE_OBJECT_DEFINE" in ifs, (
        "EXCLUDE_OBJECT_DEFINE entry not carried into _IFS_COLORS"
    )

    # Original content must still be present (file grew by the two injected lines)
    full = gcode.read_text(encoding="utf-8")
    assert "; END OF GCODE" in full, "Original gcode content lost after processing"

    # No leftover temp file
    assert not (tmp_path / "print.gcode.tmp").exists(), (
        "Temp file must be removed after successful processing"
    )


# ---------------------------------------------------------------------------
# Test 2: Already-processed file — early exit, file byte-for-byte unchanged.
# ---------------------------------------------------------------------------

@patch("preprint.write_to_file")
def test_already_processed_file_unchanged(mock_write, tmp_path):
    """A file with _IFS_COLORS at line 2 causes an immediate sys.exit(0)."""
    gcode = tmp_path / "print.gcode"
    _make_processed_gcode(gcode)
    original_bytes = gcode.read_bytes()

    sys.argv = ["preprint.py", str(gcode)]
    with pytest.raises(SystemExit) as exc_info:
        preprint.main()

    assert exc_info.value.code == 0, "Expected clean exit (0) for already-processed file"
    assert gcode.read_bytes() == original_bytes, (
        "File must not be modified when already post-processed"
    )


# ---------------------------------------------------------------------------
# Test 3: Interrupted write — temp file cleaned up, original untouched.
# ---------------------------------------------------------------------------

@patch("preprint.write_to_file")
def test_interrupted_write_cleans_up_temp(mock_write, tmp_path):
    """If os.replace() raises, the temp file is deleted and the original survives."""
    gcode = tmp_path / "print.gcode"
    _make_fresh_gcode(gcode, with_exclude=True)
    original_bytes = gcode.read_bytes()

    sys.argv = ["preprint.py", str(gcode)]

    with patch("os.replace", side_effect=OSError("disk full simulation")):
        with pytest.raises(OSError, match="disk full simulation"):
            preprint.main()

    # Original must be completely untouched
    assert gcode.read_bytes() == original_bytes, (
        "Original file must be intact after a failed write"
    )

    # Temp file must have been cleaned up
    temp_file = tmp_path / "print.gcode.tmp"
    assert not temp_file.exists(), (
        "Temp file must be deleted after os.replace() failure"
    )


# ---------------------------------------------------------------------------
# Test 4: No EXCLUDE_OBJECT_DEFINE within scan limit — proceeds without error.
# ---------------------------------------------------------------------------

@patch("preprint.write_to_file")
def test_no_exclude_object_define_proceeds(mock_write, tmp_path):
    """A file without EXCLUDE_OBJECT_DEFINE lines processes without error."""
    gcode = tmp_path / "print.gcode"
    _make_fresh_gcode(gcode, with_exclude=False)

    sys.argv = ["preprint.py", str(gcode)]
    preprint.main()  # Must not raise

    lines = _read_lines(gcode)

    # Must still produce a valid two-line header
    assert lines[0].startswith("; MD5:"), "MD5 line missing"
    assert lines[1].startswith("; _IFS_COLORS "), "_IFS_COLORS line missing"

    # EXCLUDE field should fall back to "None" (matching prior behaviour)
    assert 'EXCLUDE="None"' in lines[1], (
        "EXCLUDE field must fall back to \"None\" when no EXCLUDE_OBJECT_DEFINE found"
    )
