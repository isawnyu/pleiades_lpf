#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
convert AAT TERMS.out file to JSON for lookup use
"""

from airtight.cli import configure_commandline
import csv
import json
import logging
from pathlib import Path
from pleiades_lpf.text import normalize_text
from slugify import slugify

logger = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path("data/aat/TERM.out").resolve()
DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    [
        "-l",
        "--loglevel",
        "NOTSET",
        "desired logging level ("
        + "case-insensitive string: DEBUG, INFO, WARNING, or ERROR",
        False,
    ],
    ["-v", "--verbose", False, "verbose output (logging level == INFO)", False],
    [
        "-w",
        "--veryverbose",
        False,
        "very verbose output (logging level == DEBUG)",
        False,
    ],
    ["-i", "--inputfile", str(DEFAULT_INPUT_PATH), "input AAT TERMS.out file", False],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    input_path = Path(kwargs["inputfile"]).expanduser().resolve()
    terms = dict()
    labels = dict()
    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile, delimiter="\t")
        terms = {}
        for row in reader:
            try:
                id = normalize_text(row[9])
            except IndexError as err:
                logger.warning(f"skipping row with no id: {row}")
                continue

            term = normalize_text(row[10])
            term_parts = [t.strip() for t in term.split(",") if t.strip()]
            if len(term_parts) == 2:
                term = f"{term_parts[1]} {term_parts[0]}"
            slug = slugify(term)
            try:
                terms[slug]
            except KeyError:
                terms[slug] = set()
            terms[slug].add(id)

            try:
                labels[id]
            except KeyError:
                labels[id] = set()
            labels[id].add(term)
    del infile
    out = {
        "terms": dict(),
        "labels": dict(),
    }
    for k, v in terms.items():
        out["terms"][k] = list(v)
    for k, v in labels.items():
        out["labels"][k] = list(v)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
