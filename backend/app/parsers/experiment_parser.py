import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ExperimentParser:
    """Universal parser for extracting experiments and structured sections from any lab manual PDF."""

    # Keywords commonly found in experiment title headers
    EXPERIMENT_TITLE_KEYWORDS = [
        "estimation", "determination", "preparation", "study", "measurement",
        "verification", "construction", "characteristics", "calibration", "analysis",
        "titration", "synthesis", "dispersive", "newton", "melde", "circuit",
        "magnetic", "energy gap", "torsional", "slit", "diffraction", "electroplating",
        "viscosity", "surface tension", "conductometric", "potentiometric", "ph meter",
        "bakelite", "aspirin", "paracetamol", "edta", "dichrometry", "spectrometer",
        "grating", "pendulum", "viscometer", "stalagmometer", "interferometer", "solar cell"
    ]

    # Explicit experiment patterns
    EXPLICIT_PATTERNS = [
        r"(?:EXPERIMENT|EXP\.?|EXERCISE|PRACTICAL)\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*(\d+[a-z]?)",
        r"\bEXPERIMENT\s+(\d+[a-z]?)\b",
        r"\bEXPERIMENT\s*[-:]\s*(\d+[a-z]?)\b",
        r"\bEXERCISE\s*[-:]?\s*(\d+[a-z]?)\b",
        r"\bPRACTICAL\s*[-:]?\s*(\d+[a-z]?)\b"
    ]

    # Section keywords dictionary
    SECTION_KEYWORDS = {
        "aim": ["aim", "objective", "objectives", "purpose", "aim of experiment"],
        "theory": ["theory", "principle", "introduction", "background", "theoretical background", "description"],
        "equipment": ["apparatus", "equipment", "materials", "materials required", "apparatus required", "chemicals", "chemicals required", "tools", "reagents"],
        "procedure": ["procedure", "method", "steps", "experimental procedure", "methodology", "execution", "preparation"],
        "observations": ["observation", "observations", "tabulation", "readings", "data table", "calculations", "model graph", "observations and calculations"],
        "result": ["result", "results", "conclusion", "inference", "outcome"],
        "safety": ["precaution", "precautions", "safety", "safety measures", "safety precautions", "warnings", "hazards", "code of conduct"],
        "troubleshooting": ["troubleshooting", "common errors", "sources of error", "notes", "faqs", "viva questions", "viva"]
    }

    def parse_experiments(self, full_text: str) -> List[Dict[str, Any]]:
        if not full_text:
            return []

        # Step 1: Strip out Table of Contents / Index blocks to avoid duplicate detection
        clean_search_text = self._filter_table_of_contents(full_text)

        # Step 2: Find experiment boundary candidates
        candidates = self._find_experiment_boundaries(clean_search_text)

        # Step 3: Fallback if no experiments detected -> Parse as master experiment
        if not candidates:
            logger.info("No explicit or numbered experiment headers detected. Parsing full manual as Experiment 1.")
            return [self._parse_single_experiment_block(1, "Laboratory Experiment", full_text)]

        # Step 4: Extract segments and parse each experiment
        experiments = []
        for i, cand in enumerate(candidates):
            exp_num = cand["exp_number"]
            start = cand["start_pos"]
            end = candidates[i + 1]["start_pos"] if i + 1 < len(candidates) else len(clean_search_text)
            segment = clean_search_text[start:end].strip()

            title = cand.get("title") or self._extract_title(segment, exp_num)
            parsed_exp = self._parse_single_experiment_block(exp_num, title, segment)
            experiments.append(parsed_exp)

        return experiments

    def _filter_table_of_contents(self, text: str) -> str:
        """Removes Table of Contents / Index pages from the initial search range."""
        toc_pattern = r"(?:CONTENTS|INDEX|LIST OF EXPERIMENTS|LAB CONTENTS)\b.*?(?=\bCOMMON APPARATUS|\bEXPERIMENT|\b1\.\s+[A-Z]|\Z)"
        # Replace TOC section with whitespace preserving length so string offsets match original text
        match = re.search(toc_pattern, text[:4000], re.IGNORECASE | re.DOTALL)
        if match:
            start, end = match.span()
            return text[:start] + (" " * (end - start)) + text[end:]
        return text

    def _find_experiment_boundaries(self, text: str) -> List[Dict[str, Any]]:
        matches = []

        # 1. Match explicit "EXPERIMENT 1", "EXP. 2" patterns
        for pattern in self.EXPLICIT_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                raw_num = m.group(1).lower()
                num = int(re.sub(r'\D', '', raw_num)) if re.search(r'\d+', raw_num) else 1
                matches.append({
                    "exp_number": num,
                    "start_pos": m.start(),
                    "matched_text": m.group(0)
                })

        # 2. Match numbered title patterns like "1. ESTIMATION OF HARDNESS...", "2. DETERMINATION OF..."
        # Format: newline + number + dot/paren + spaces + Title
        title_pattern = r"(?:\n|^)\s*(\d{1,2})\.\s+([A-Za-z0-9\s\-\(\)\/\,\.]{5,120})(?=\n|\r|AIM|APPARATUS|PRINCIPLE|THEORY|$)"
        for m in re.finditer(title_pattern, text):
            exp_num = int(m.group(1))
            header_text = m.group(2).strip()

            # Verify if header contains experiment keywords or is followed by AIM/APPARATUS/PRINCIPLE
            is_valid_exp = any(kw in header_text.lower() for kw in self.EXPERIMENT_TITLE_KEYWORDS)
            following_snippet = text[m.end():m.end() + 200].lower()
            is_valid_exp = is_valid_exp or any(k in following_snippet for k in ["aim:", "apparatus:", "principle:", "theory:"])

            if is_valid_exp:
                matches.append({
                    "exp_number": exp_num,
                    "start_pos": m.start(),
                    "title": header_text.split('\n')[0].strip(),
                    "matched_text": m.group(0)
                })

        # Sort matches by position
        matches.sort(key=lambda x: x["start_pos"])

        # De-duplicate matches for same experiment number, preserving earliest valid occurrence
        unique_matches = []
        seen_nums = set()
        for match in matches:
            if match["exp_number"] not in seen_nums:
                seen_nums.add(match["exp_number"])
                unique_matches.append(match)

        return unique_matches

    def _extract_title(self, segment: str, exp_num: int) -> str:
        lines = [line.strip() for line in segment.split('\n') if line.strip()]
        for line in lines[:4]:
            cleaned = re.sub(r'^(?:EXPERIMENT|EXP\.?|EXERCISE|PRACTICAL)?\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*\d+[\.\)]?\s*', '', line, flags=re.IGNORECASE).strip()
            if cleaned and len(cleaned) > 3:
                return cleaned[:150]
        return f"Experiment {exp_num}"

    def _parse_single_experiment_block(self, exp_num: int, title: str, segment: str) -> Dict[str, Any]:
        aim = self._extract_section_content(segment, "aim")
        theory = self._extract_section_content(segment, "theory")
        equipment_raw = self._extract_section_content(segment, "equipment")
        procedure_raw = self._extract_section_content(segment, "procedure")
        observations = self._extract_section_content(segment, "observations")
        result = self._extract_section_content(segment, "result")
        safety_raw = self._extract_section_content(segment, "safety")
        troubleshooting = self._extract_section_content(segment, "troubleshooting")

        equipment = self._parse_list_items(equipment_raw)
        procedure = self._parse_procedure_steps(procedure_raw or segment)
        safety = self._parse_list_items(safety_raw)

        return {
            "experiment_number": exp_num,
            "title": title,
            "aim": aim or f"Study and conduct {title}",
            "theory": theory or "Theory section available in manual content.",
            "equipment": equipment,
            "procedure": procedure,
            "observations": observations or "",
            "result": result or "",
            "safety": safety,
            "troubleshooting": troubleshooting or "",
            "raw_content": segment
        }

    def _extract_section_content(self, text: str, section_key: str) -> Optional[str]:
        keywords = self.SECTION_KEYWORDS.get(section_key, [])
        if not keywords:
            return None

        all_stops = []
        for key, kw_list in self.SECTION_KEYWORDS.items():
            if key != section_key:
                all_stops.extend(kw_list)

        pattern = (
            rf"(?:\b(?:{'|'.join(keywords)})\b)\s*[:\-]?\s*"
            rf"(.*?)"
            rf"(?=\b(?:{'|'.join(all_stops)})\b|\Z)"
        )

        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            if len(extracted) > 5:
                return extracted
        return None

    def _parse_procedure_steps(self, raw_procedure: str) -> List[str]:
        if not raw_procedure:
            return []

        steps = []
        num_splits = re.split(r'(?:^|\n|\s+)(?:step\s+)?\d+[.\)]\s*', raw_procedure, flags=re.IGNORECASE)
        for s in num_splits:
            s_clean = s.strip()
            if len(s_clean) > 5 and not any(kw in s_clean.lower() for kw in ["experiment", "apparatus required", "department of"]):
                steps.append(s_clean)

        if len(steps) >= 2:
            return steps[:30]

        sentences = re.split(r'[.!?]+\s+', raw_procedure)
        fallback_steps = [sent.strip() for sent in sentences if len(sent.strip()) > 15]
        return fallback_steps[:25]

    def _parse_list_items(self, raw_text: Optional[str]) -> List[str]:
        if not raw_text:
            return []
        items = []
        tokens = re.split(r'[\n,;•\-]', raw_text)
        for token in tokens:
            cleaned = token.strip()
            cleaned = re.sub(r'^\d+[.\)]\s*', '', cleaned)
            if cleaned and len(cleaned) > 2 and len(cleaned) < 150:
                if cleaned not in items:
                    items.append(cleaned)
        return items[:20]
