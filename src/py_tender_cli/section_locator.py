from __future__ import annotations

import re

from rapidfuzz.fuzz import token_set_ratio

from .models import Section


DEFAULT_MATCH_THRESHOLD = 70.0

_PAGE_RANGE = re.compile(r"(?P<start>\d+)\s*[-–]\s*(?P<end>\d+)")

_INDEX_NUMBER = re.compile(r"^\s*\|?\s*\d+\.\s*")

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "of",
    "the",
}


def _normalize_text(text: str) -> str:
    """Normalize text for fuzzy matching."""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _remove_stop_words(text: str) -> str:
    """Remove common words that carry little matching information."""

    words = _normalize_text(text).split()

    return " ".join(word for word in words if word not in _STOP_WORDS)


def _match_score(
    requested_title: str,
    index_title: str,
) -> float:
    """Return a fuzzy similarity score between two section titles."""

    requested = _remove_stop_words(
        requested_title,
    )

    index = _remove_stop_words(
        index_title,
    )

    if not requested or not index:
        return 0.0

    return float(
        token_set_ratio(
            requested,
            index,
        )
    )


def _extract_index_entry(
    lines: list[str],
    start: int,
) -> tuple[str, re.Match[str]] | None:
    """Extract an index title and page range."""

    entry_lines: list[str] = []

    for offset in range(start, len(lines)):
        line = lines[offset].strip()

        if not line:
            continue

        # A new numbered entry before finding a page range means
        # this entry is not usable.
        if offset > start and _INDEX_NUMBER.match(line):
            return None

        entry_lines.append(line)

        page_range = _PAGE_RANGE.search(line)

        if page_range is None:
            continue

        combined = " ".join(entry_lines)

        title = _INDEX_NUMBER.sub(
            "",
            combined,
        )

        title = _PAGE_RANGE.sub(
            "",
            title,
        ).strip()

        return title, page_range

    return None


def find_section(
    text: str,
    title: str,
    *,
    threshold: float = DEFAULT_MATCH_THRESHOLD,
) -> Section | None:
    """Find a section's page range from an index.

    The supplied title is treated as a semantic search hint.
    The matching index entry supplies the authoritative page range.
    """

    if not 0.0 <= threshold <= 100.0:
        raise ValueError(
            "threshold must be between 0 and 100",
        )

    lines = text.splitlines()

    best_score = -1.0
    best_section: Section | None = None

    for index, line in enumerate(lines):
        if not _INDEX_NUMBER.match(line.strip()):
            continue

        result = _extract_index_entry(
            lines,
            index,
        )

        if result is None:
            continue

        index_title, page_range = result

        score = _match_score(
            title,
            index_title,
        )

        if score < threshold:
            continue

        if score <= best_score:
            continue

        best_score = score

        best_section = Section(
            title=title,
            page_start=int(
                page_range.group("start"),
            ),
            page_end=int(
                page_range.group("end"),
            ),
        )

    return best_section
