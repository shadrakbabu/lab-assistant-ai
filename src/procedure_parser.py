import re
from typing import List, Dict

class ProcedureParser:
    def extract_procedures(self, text: str) -> List[Dict]:
        """Extract step-by-step procedures from text"""
        if not text or len(text.strip()) < 10:
            return []
        
        procedures = []
        
        # Split by common procedure markers
        steps = re.split(r'(?:Step|step|STEP)\s+(\d+)[:\s-]*', text)
        
        if len(steps) > 1:
            # Process matched steps
            for i in range(1, len(steps), 2):
                if i < len(steps):
                    step_num = steps[i]
                    step_text = steps[i+1].strip()
                    # Clean step text from metadata (professor names, short headers)
                    clean_text = self._clean_step_text(step_text)
                    # Get first meaningful line of the step
                    description = (clean_text.split('\n')[0] if clean_text else '').strip()[:250]
                    if description:
                        procedures.append({
                            "step_number": step_num,
                            "description": description
                        })
        
        # If no steps found with Step pattern, try numbered list format
        if not procedures:
            procedures = self._extract_numbered_procedures(text)
        
        # If still nothing, do fallback
        if not procedures:
            procedures = self._fallback_parse(text)
        
        return procedures
    
    def _extract_numbered_procedures(self, text: str) -> List[Dict]:
        """Try to extract procedures from numbered lists"""
        procedures = []
        # Look for lines that start with number followed by period
        lines = text.split('\n')
        for line in lines:
            match = re.match(r'^\s*(\d+)[\.\)\s]+(.*)', line)
            if match:
                desc = self._clean_step_text(match.group(2).strip())
                procedures.append({
                    "step_number": match.group(1),
                    "description": desc.split('\n')[0][:250] if desc else ''
                })
        return procedures[:10]  # Limit to 10 steps

    def _clean_step_text(self, text: str) -> str:
        """Remove common metadata lines (professor names, department lines) from step text."""
        if not text:
            return text
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        cleaned = []
        for ln in lines:
            low = ln.lower()
            # Remove lines that look like author/faculty credits or short noise
            if any(tok in low for tok in ('assistant professor', 'professor', 'dr.', 'department', 'faculty', 'instructor')):
                continue
            # Remove lines that are likely just names with comma and short
            if re.match(r'^[A-Za-z]\.?\s*[A-Za-z]+,\s*(assistant|professor|asst|dept)\b', ln, re.IGNORECASE):
                continue
            # Remove very short lines (noise)
            if len(ln) < 4:
                continue
            cleaned.append(ln)

        return '\n'.join(cleaned)
    
    def _fallback_parse(self, text: str) -> List[Dict]:
        """Fallback parsing by sentences"""
        # Split by punctuation and take meaningful chunks
        sentences = text.split('.')
        procedures = []
        for i, sentence in enumerate(sentences[:5]):
            cleaned = sentence.strip()
            if cleaned and len(cleaned) > 10:
                procedures.append({
                    "step_number": str(i+1),
                    "description": cleaned[:250]
                })
        return procedures
