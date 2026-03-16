import re
from typing import List, Dict


class ExperimentExtractor:
    def __init__(self):
        pass

    def extract_experiments(self, text: str) -> List[Dict]:
        """Extract experiments from text - handles multiple formats including
        a 'List of Experiments' table commonly found in lab manuals."""
        # 1) Try to locate and parse a List of Experiments block
        list_block = self._find_experiments_list(text)
        if list_block:
            parsed = self._parse_experiment_list(list_block)
            if parsed:
                return parsed

        # 2) Fallback to pattern-based extraction
        return self._extract_by_patterns(text)

    def _find_experiments_list(self, text: str) -> str:
        """Return the text block containing 'List of Experiments' if present."""
        match = re.search(r'List of Experiments.*?(?=\n\s*(?:Experiment|Exp)\b|EVALUATION|Evaluation|INDEX|Index|$)', text, re.IGNORECASE | re.DOTALL)
        return match.group(0) if match else ""

    def _parse_experiment_list(self, list_text: str) -> List[Dict]:
        """Parse a List of Experiments block into numbered experiments.

        This handles entries that span multiple lines by using a multiline
        regex that captures from a leading serial number until the next one.
        """
        experiments: List[Dict] = []

        # Normalize whitespace
        block = list_text.strip()

        # Find lines that start with a serial number and capture until next serial
        pattern = re.compile(r'(?m)^\s*(\d+)\b[\s\S]*?(?=^\s*\d+\b|\Z)', re.MULTILINE)
        for m in pattern.finditer(block):
            chunk = m.group(0).strip()
            # Extract the leading number
            mnum = re.match(r'^\s*(\d+)', chunk)
            if not mnum:
                continue
            num = mnum.group(1)

            # Break chunk into lines and remove noise like page ranges or short numeric lines
            lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
            cleaned_lines = []
            for ln in lines:
                # skip pure page ranges like '7 - 11' or single numbers
                if re.match(r'^\d+\s*-\s*\d+$', ln):
                    continue
                if re.match(r'^\d+$', ln):
                    continue
                # skip short uppercase section headers (likely section dividers)
                if ln.isupper() and len(ln) < 60:
                    continue
                cleaned_lines.append(ln)

            # Attempt to detect a page range within the chunk (e.g. '37 - 41')
            start_page = None
            end_page = None
            pr_match = re.search(r'(?P<start>\d+)\s*-\s*(?P<end>\d+)', chunk)
            if pr_match:
                try:
                    start_page = int(pr_match.group('start'))
                    end_page = int(pr_match.group('end'))
                except Exception:
                    start_page = None
                    end_page = None

            # Join remaining lines into a single title string
            title = ' '.join(cleaned_lines)
            # Remove any inline page-range fragments left inside the title
            title = re.sub(r'\s*\d+\s*-\s*\d+\s*', ' ', title).strip()
            # Remove the leading serial from title if still present
            title = re.sub(r'^\s*\d+\s*[:.-]?\s*', '', title).strip()
            # Remove trailing page ranges at end
            title = re.sub(r'\s+\d+\s*-\s*\d+\s*$', '', title).strip()

            # Clean up common header tokens
            if title and len(title) > 3 and not title.lower().startswith(('s.no', 'name of')):
                item = {"number": num, "title": title}
                if start_page and end_page:
                    item.update({"start_page": start_page, "end_page": end_page})
                experiments.append(item)

        return experiments

    def _extract_by_patterns(self, text: str) -> List[Dict]:
        """Fallback extraction using common 'Experiment' headings."""
        experiments: List[Dict] = []
        seen = set()
        patterns = [r'(?:Experiment|Exp)\s+#?(\d+)[:\s-]+([^\n]+)']

        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                num = match.group(1)
                title = match.group(2).strip()
                if num not in seen and self._is_valid_experiment(title):
                    experiments.append({"number": num, "title": title})
                    seen.add(num)

        return experiments

    def _is_valid_experiment(self, title: str) -> bool:
        lower = title.lower()
        for bad in ('professor', 'author', 'department', 'by', 'instructor'):
            if bad in lower:
                return False
        return len(title) > 5

    def extract_experiment_section(self, text: str, exp_number: str, title: str | None = None) -> str:
        """Extract the full section for a given experiment by heading and numbering."""
        if not text:
            return ""

        exp_number_norm = str(exp_number).strip()
        lower_text = text.lower()

        # Start searching after the List of Experiments block to avoid TOC matches.
        list_block = self._find_experiments_list(text)
        search_start = 0
        if list_block:
            search_start = text.find(list_block) + len(list_block)

        # Find all experiment headings in the body.
        heading_regex = re.compile(r'(^|\n)\s*(?:experiment|exp)\s*(?:#\s*)?(\d+)\b[^\n]*', re.IGNORECASE)
        headings = [m for m in heading_regex.finditer(text, search_start)]

        start_idx = None
        for i, m in enumerate(headings):
            if m.group(2).strip() == exp_number_norm:
                start_idx = m.start()
                if i + 1 < len(headings):
                    end_idx = headings[i + 1].start()
                else:
                    end_idx = len(text)
                return text[start_idx:end_idx].strip()

        # Fallback: numeric heading lines like '1.' or '1)' but only if near experiment heading text
        numeric_regex = re.compile(r'(^|\n)\s*(\d+)\s*[\.)]\s*.*', re.MULTILINE)
        matches = [m for m in numeric_regex.finditer(text, search_start)]
        for i, m in enumerate(matches):
            if m.group(2).strip() == exp_number_norm:
                start_idx = m.start()
                end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                return text[start_idx:end_idx].strip()

        # Fallback using title phrase if available
        if title:
            normalized_title = ' '.join(title.split()).lower()
            pos = lower_text.find(normalized_title, search_start)
            if pos != -1:
                next_exp = heading_regex.search(text, pos + len(normalized_title))
                if next_exp:
                    return text[pos:next_exp.start()].strip()
                return text[pos:].strip()

        return ""
