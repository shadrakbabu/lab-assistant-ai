import re
from typing import List, Dict

class ExperimentExtractor:
    def __init__(self):
        self.exp_patterns = [
            r'(?:Exp|Experiment)\s+(\d+)[:\s-]*([^\n]+)',
            r'(\d+)\.\s+([A-Z][^\n]+)',
        ]
    
    def extract_experiments(self, text: str) -> List[Dict]:
        """Extract experiments from text"""
        experiments = []
        for pattern in self.exp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                experiments.append({
                    "number": match.group(1),
                    "title": match.group(2).strip()
                })
        return experiments
