#!/usr/bin/env python3
"""caption-resync: batch-fix out-of-sync subtitles from the command line.

Shift, stretch, convert (SRT <-> WebVTT), strip styling tags, renumber and
validate whole folders of subtitle files. Zero dependencies, Python 3.9+.

Typical use: your subtitles lag the audio by a constant offset, so every
cue arrives late. One command fixes the whole season:

    caption-resync --shift -2.5s --dir subtitles/ --glob \"*.srt\"

Outputs land next to the inputs with a ``.resync`` suffix by default, so the
originals are never touched.
"""

from __future__ import annotations

import argparse
import glob as glob_module
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__version__ = "1.0.0"

# A timestamp: [hh:]mm:ss,mmm or [hh:]mm:ss.mmm (1 to 3 millisecond digits).
TS_RE = re.compile(
    r"(?:(\d+):)?(\d{1,2}):(\d{1,2})[,.](\d{1,3})"
)


@dataclass
class ParseIssue:
    """Something the parser noticed while reading a subtitle file."""

    line: int
    severity: str  # "error" or "warning"
    message: str

    def __str__(self) -> str:
        return "line %d [%s] %s" % (self.line, self.severity, self.message)


@dataclass
class Cue:
    """One subtitle cue. Times are integer milliseconds."""

    start: int
    end: int
    text: str
    cue_id: Optional[str] = None
    settings: str = ""  # WebVTT cue settings, e.g. "align:start position:0%"


@dataclass
class SubtitleFile:
    """Parsed subtitle document plus any issues found while parsing."""

    cues: List[Cue] = field(default_factory=list)
    fmt: str = "srt"  # "srt" or "vtt"
    header_blocks: List[str] = field(default_factory=list)  # VTT STYLE/REGION
    notes: List[Tuple[int, str]] = field(default_factory=list)  # (cue_index, text) for NOTE blocks
    issues: List[ParseIssue] = field(default_factory=list)

# ... (rest of the file would be here, but truncated for this example)
