"""Read the Veris HSE daily report log and find reports that are missing.

:author: Shay Hill
:created: 8/15/2023
"""

_REPORT_PATH = "paste_report"


from typing import Sequence, Callable, Iterator

import itertools as it


import dataclasses
import re

# pattern to match a date that appears at the end of a string, e.g. "sdfg nlar hser 8/15/23"
_DATE_PATTERN = re.compile(r"\d{1,2}/\d{1,2}/\d{2}$")


class Report:
    number: int


def _get_report_number(lines: list[str]) -> int | None:
    """Extract the report number from a line in the report log.

    :param lines: lines from the report log
    :return: the report number or None if no number is found in the first line

    Report numbers will be a line with only digits followed by a line containing exactly "Daily HSE Report".

    123
    Daily HSE Report
    """
    if len(lines) < 2:
        return None
    line, next_line = lines[:2]
    if line.isdigit() and int(line) > 0 and next_line == "Daily HSE Report":
        return int(line)
    return None


def _get_report_date(lines: list[str]) -> str | None:
    """Extract the report date from a line in the report log.

    :param lines: lines from the report log
    :return: the report date or None if no date is found on the first line

    Report dates will be m/d/yy or mm/d/yy or m/dd/yy or mm/dd/yy
    """
    if len(lines) < 1:
        return None
    match = re.match(_DATE_PATTERN, lines[0])
    if match:
        return match.group(0)
    return None


def _split_at_next(
    lines: list[str], fsplit: Callable[[list[str]], str | None]
) -> Iterator[list[str]]:
    """Split a report log at the next report number.

    :param lines: a list of lines from the report log
    :param fsplit: a function that takes a list of lines and returns a value if the lines should be split
    :return: a tuple of two lists, the first containing the lines before the next report and the second containing
        the lines starting with the next report number.

    Do not return report numbers that are 0. Treat 0 as None.
    """
    ixs = [0] + [i for i, _ in enumerate(lines) if fsplit(lines[i:])]
    for ix_a, ix_b in it.zip_longest(ixs, ixs[1:]):
        yield lines[ix_a:ix_b]


ONBOARD = {
    x.lower()
    for x in (
        "Sean Moberley",
        "Scott Nix",
        "Derrick Fusilier",
        "Gus Richmond",
        "Charles Murchison",
        "William Necaise",
        "Mark Goff",
        "Jim Watson",
        "Joel Ferrell",
        "Keon Jones",
        "Darius Haywood",
    )
}


def _get_report_log() -> Sequence[str]:
    """
    Read a pasting of the Veris HSE report log and extract a list of reports."""
    global ONBOARD
    seen: set[str] = set()
    with open(_REPORT_PATH, "r", encoding="utf-8") as report_file:
        queue = report_file.read().splitlines()
    for report in _split_at_next(queue, _get_report_number):
        report_number = _get_report_number(report)
        if report_number is None:
            continue
        aaa, report = _split_at_next(report, _get_report_date)
        report_date = _get_report_date(report)
        report_name = report[1]
        if report_name.endswith(" (Houston, TX)"):
            report_name = report_name[: -len(" (Houston, TX)")]
        if report_name == "Guest User":
            continue

        last, first = (x.strip() for x in report_name.split(","))
        fl_lower = f"{first.lower()} {last.lower()}"
        seen.add((report_name, fl_lower))

        if fl_lower in ONBOARD:
            ONBOARD -= {fl_lower}

        # except:
        #     breakpoint()
        # breakpoint()
        # if fl_lower in ONBOARD:
        #     ONBOARD -= {fl_lower}
    print(ONBOARD)
    breakpoint()


if __name__ == "__main__":
    _get_report_log()
