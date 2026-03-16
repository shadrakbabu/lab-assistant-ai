import re
from typing import List, Dict

class ProcedureParser:
    PROCEDURE_START_TERMS = [
        r'procedure',
        r'procedure\s+steps?',
        r'method(?:ology)?',
        r'experimental\s+procedure',
        r'step-by-step',
    ]

    PROCEDURE_END_TERMS = [
        r'precautions?',
        r'observations?',
        r'results?',
        r'outcomes?',
        r'theory',
        r'safety',
        r'discussion',
        r'references?',
        r'conclusions?',
    ]

    def extract_procedures(self, text: str) -> List[Dict]:
        if not text or len(text.strip()) < 10:
            return []

        proc_block = self._extract_procedure_block(text)
        if proc_block:
            steps = self._extract_steps_from_block(proc_block)
            if steps:
                return steps

        # fallback to full text extraction if no explicit procedure block
        steps = self._extract_steps_from_block(text)
        if steps:
            return steps

        return self._fallback_parse(text)

    def extract_precautions(self, text: str) -> str:
        if not text:
            return ""

        lower = text.lower()
        m = re.search(r'^[ \t]*(precautions?|safety)\b', lower, re.MULTILINE)
        if not m:
            return ""

        start = m.start()
        end = len(text)
        for term in self.PROCEDURE_END_TERMS:
            mm = re.search(r'^[ \t]*' + term + r'\b', lower[m.end():], re.MULTILINE)
            if mm:
                candidate = m.end() + mm.start()
                end = min(end, candidate)

        return text[start:end].strip()

    def _extract_procedure_block(self, text: str) -> str:
        lower = text.lower()
        start = None
        for term in self.PROCEDURE_START_TERMS:
            m = re.search(r'^[ \t]*' + term + r'\b', lower, re.MULTILINE)
            if m:
                if start is None or m.start() < start:
                    start = m.start()

        if start is None:
            return ""

        end = len(text)
        for term in self.PROCEDURE_END_TERMS:
            m = re.search(r'^[ \t]*' + term + r'\b', lower[start + 1:], re.MULTILINE)
            if m:
                candidate = start + 1 + m.start()
                end = min(end, candidate)

        return text[start:end].strip()

    def _extract_steps_from_block(self, text: str) -> List[Dict]:
        procedures: List[Dict] = []

        # Step-n style extraction (Step 1:, Step 2., etc.)
        step_pattern = re.compile(
            r'^[ \t]*(?:step|stage)\s+(\d+)\s*[:\.-]?\s*(.+?)(?=^[ \t]*(?:step|stage)\s+\d+\s*[:\.-]?|\Z)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )

        for m in step_pattern.finditer(text):
            step_num = m.group(1).strip()
            desc = m.group(2).strip()
            step_text = self._clean_step_text(desc)
            if step_text:
                procedures.append({"step_number": step_num, "description": step_text})

        if procedures:
            return procedures

        # Numbered list style extraction 1. 2. 3.
        numbered_pattern = re.compile(
            r'^[ \t]*(\d+)[\.)]\s+(.+?)(?=^[ \t]*\d+[\.)]|\Z)',
            re.MULTILINE | re.DOTALL
        )

        for m in numbered_pattern.finditer(text):
            step_num = m.group(1).strip()
            desc = m.group(2).strip()
            step_text = self._clean_step_text(desc)
            if step_text:
                procedures.append({"step_number": step_num, "description": step_text})

        return procedures

    def _clean_step_text(self, text: str) -> str:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        cleaned = []
        for ln in lines:
            low = ln.lower()
            if any(tok in low for tok in ('assistant professor', 'professor', 'dr.', 'department', 'faculty', 'instructor')):
                continue
            if len(ln) < 4:
                continue
            cleaned.append(ln)
        return '\n'.join(cleaned)

    def _fallback_parse(self, text: str) -> List[Dict]:
        parts = re.split(r'\n+', text)
        procedures = []
        for i, part in enumerate(parts):
            cleaned = part.strip()
            if len(cleaned) > 20:
                procedures.append({"step_number": str(i+1), "description": cleaned})
        return procedures
