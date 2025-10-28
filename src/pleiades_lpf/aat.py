#
# This file is part of pleiades_lpf
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Getty Art and Architecture Thesaurus (AAT) matcher for FeatureType augmentation.
"""
from collections import defaultdict
import json
from langstring import LangString, MultiLangString
from langcodes.tag_parser import parse_tag
import logging
from pathlib import Path
from pprint import pformat


class AATMatcher:
    """
    Matcher for Getty Art and Architecture Thesaurus (AAT) terms.
    """

    def __init__(self):
        # In a real implementation, this might load AAT data from a file or database
        logger = logging.getLogger(__name__)
        logger.debug("Initializing AATMatcher")

        self._terms = dict()
        self._term_names = dict()

    def match(
        self, label: LangString, aliases: MultiLangString | None = None
    ) -> list[tuple[str, str]]:
        if not self._terms:
            self._load_terms()
        candidates = [label.text.lower().strip()]
        if aliases:
            candidates.extend(
                [alias.text.lower().strip() for alias in aliases.to_langstrings()]
            )
        hits = set()
        for candidate in candidates:
            try:
                term_ids = self._terms[candidate]
            except KeyError:
                continue
            else:
                hits.update(term_ids)
        hits = list(hits)
        return [(hit, self._term_names.get(hit, "")) for hit in hits]

    def _load_terms(self):
        logger = logging.getLogger(__name__)
        logger.debug("Loading AAT terms for matching")
        whence = Path(__file__).parent.parent.parent / "data/aat/aat_terms.json"
        with open(whence, "r", encoding="utf-8") as f:
            raw_terms = json.load(f)
        del f
        for term_id, label_dict_list in raw_terms.items():
            for label_dict in label_dict_list:
                label_text = label_dict.get("text", "").strip().lower()
                if label_text:
                    try:
                        self._terms[label_text]
                    except KeyError:
                        self._terms[label_text] = set()
                    finally:
                        self._terms[label_text].add(term_id)
                    label_lang = label_dict.get("lang")
                    if label_lang == "en":
                        try:
                            self._term_names[term_id]
                        except KeyError:
                            self._term_names[term_id] = label_text
            try:
                self._term_names[term_id]
            except KeyError:
                self._term_names[term_id] = (
                    raw_terms[term_id][0].get("text", "").strip().lower()
                )
