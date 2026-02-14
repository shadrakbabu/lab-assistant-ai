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
        match = re.search(r'List of Experiments.*?(?=EVALUATION|Evaluation|INDEX|Index|$)', text, re.IGNORECASE | re.DOTALL)
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

    def extract_experiment_section(self, text: str, exp_number: str) -> str:
        """Extract the full section for a given experiment number.

        Searches for headings like "Experiment 6" or "6." and returns the
        content until the next experiment heading.
        """
        # Try multiple patterns to locate the experiment start
        patterns = [
            rf'(?:^|\n)\s*Experiment\s+{re.escape(exp_number)}\b[\s\S]*?(?=(?:\n\s*Experiment\s+\d+\b)|$)',
            rf'(?:^|\n)\s*{re.escape(exp_number)}[.\)\s-]+[\s\S]*?(?=(?:\n\s*\d+[.\)\s-])|$)'
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
            if m:
                # Return the matched block, trimmed
                return m.group(0).strip()

        return ""
