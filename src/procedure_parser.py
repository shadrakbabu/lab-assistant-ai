import re
from typing import List, Dict

class ProcedureParser:
    def extract_procedures(self, text: str) -> List[Dict]:
        """Extract step-by-step procedures"""
        procedures = []
        
        # Split by common procedure markers
        steps = re.split(r'(?:Step|step|STEP)\s+(\d+)[:\s-]*', text)
        
        for i in range(1, len(steps), 2):
            if i < len(steps):
                procedures.append({
                    "step_number": steps[i],
                    "description": steps[i+1].split('\n')[0][:200]
                })
        
        return procedures if procedures else self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> List[Dict]:
        """Fallback parsing by sentences"""
        sentences = text.split('.')[:5]
        return [{"step_number": str(i+1), "description": s.strip()} 
                for i, s in enumerate(sentences)]
