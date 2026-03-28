"""
Experiment Parser Module

Detects and extracts experiment sections from lab manual text.
Uses pattern matching and NLP to identify experiments.
"""

import re
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Experiment:
    """Represents a single experiment."""
    number: int
    title: str
    content: str
    procedure: List[str]
    equipment: List[str]
    safety: List[str]
    start_pos: int
    end_pos: int


class ExperimentParser:
    """Parse and extract experiments from lab manual text."""

    def __init__(self):
        """Initialize the experiment parser."""
        # Regex patterns to detect experiments
        self.exp_patterns = [
            r"experiment\s+(\d+)",  # "Experiment 1"
            r"exp\.?\s+(\d+)",      # "Exp 1" or "Exp. 1"
            r"exp(?:eriment)?\s+#(\d+)",  # "Exp #1"
            r"procedure\s+(\d+)",   # "Procedure 1"
        ]

        # Equipment keywords
        self.equipment_keywords = [
            "apparatus", "equipment", "materials", "tools", "beaker", "flask",
            "thermometer", "scale", "balance", "microscope", "pipette", "burette",
            "reagent", "chemical", "solution", "compound", "acid", "base"
        ]

        # Safety keywords
        self.safety_keywords = [
            "safety", "precaution", "warning", "hazard", "danger", "care",
            "protective", "glove", "goggles", "mask", "ventilation", "caution"
        ]

        # Procedure keywords
        self.procedure_keywords = [
            "step", "procedure", "method", "follow", "add", "mix", "heat",
            "cool", "observe", "measure", "record", "place", "pour"
        ]

    def find_experiments(self, text: str) -> List[Tuple[int, int, int]]:
        """
        Find all experiment start positions in text.

        Args:
            text: The lab manual text

        Returns:
            List of (exp_number, start_pos, end_pos) tuples
        """
        experiments = []

        for pattern in self.exp_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    exp_number = int(match.group(1))
                    start_pos = match.start()
                    experiments.append((exp_number, start_pos, match.group(0)))
                except (IndexError, ValueError):
                    continue

        # Sort by position
        experiments.sort(key=lambda x: x[1])

        # Remove duplicates (same experiment detected multiple times)
        unique_exp = {}
        for exp_num, start_pos, _ in experiments:
            if exp_num not in unique_exp or start_pos < unique_exp[exp_num][1]:
                unique_exp[exp_num] = (exp_num, start_pos)

        return sorted(unique_exp.values(), key=lambda x: x[1])

    def extract_experiment_content(
        self, text: str, exp_number: int, next_exp_pos: int = None
    ) -> str:
        """
        Extract content for a specific experiment.

        Args:
            text: Full text
            exp_number: Experiment number
            next_exp_pos: Position of next experiment (for boundary)

        Returns:
            Experiment content text
        """
        # Find this experiment
        pattern = f"experiment|exp\\.?|procedure"

        matches = list(re.finditer(pattern, text, re.IGNORECASE))

        start_pos = 0
        for i, match in enumerate(matches):
            # Check if this match is followed by the experiment number
            after_match = text[match.end():match.end() + 50]
            if re.search(rf"[#\s]*{exp_number}\b", after_match):
                start_pos = match.start()

                # Find end position (next experiment or end of text)
                if next_exp_pos:
                    end_pos = next_exp_pos
                else:
                    end_pos = len(text)

                return text[start_pos:end_pos].strip()

        return ""

    def extract_title(self, exp_text: str, exp_number: int) -> str:
        """
        Extract experiment title from content.

        Args:
            exp_text: Experiment section text
            exp_number: Experiment number

        Returns:
            Experiment title
        """
        # Look for title after experiment number
        lines = exp_text.split('\n')

        for i, line in enumerate(lines):
            if re.search(rf"experiment|exp", line, re.IGNORECASE):
                # Title is usually in next 1-2 lines
                if i + 1 < len(lines):
                    title = lines[i + 1].strip()
                    if title and len(title) < 200:
                        return title
                elif i + 2 < len(lines):
                    title = lines[i + 2].strip()
                    if title and len(title) < 200:
                        return title

        return f"Experiment {exp_number}"

    def extract_procedures(self, exp_text: str) -> List[str]:
        """
        Extract procedure steps from experiment text.

        Args:
            exp_text: Experiment section text

        Returns:
            List of procedure steps
        """
        procedures = []

        # Look for numbered steps
        step_pattern = r"^[\s]*(?:step\s+)?(\d+)[.\)]\s*(.+?)$"

        for match in re.finditer(step_pattern, exp_text, re.MULTILINE | re.IGNORECASE):
            step_text = match.group(2).strip()
            if step_text:
                procedures.append(step_text)

        # If no numbered steps, split by keywords
        if not procedures:
            sentences = re.split(r'[.!?]+', exp_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and any(kw in sentence.lower() for kw in self.procedure_keywords):
                    procedures.append(sentence)

        return procedures[:20]  # Limit to first 20 steps

    def extract_equipment(self, exp_text: str) -> List[str]:
        """
        Extract equipment/materials from experiment text.

        Args:
            exp_text: Experiment section text

        Returns:
            List of equipment items
        """
        equipment = []

        # Look for equipment section
        equipment_pattern = r"(?:apparatus|equipment|materials|tools)[\s:]*([^.]+?)(?:[.!?]|equipment|procedure|step|safety)"

        for match in re.finditer(equipment_pattern, exp_text, re.IGNORECASE | re.DOTALL):
            equipment_text = match.group(1)
            items = re.split(r'[,\n;]', equipment_text)
            for item in items:
                item = item.strip()
                if item and len(item) < 100 and any(kw in item.lower() for kw in self.equipment_keywords):
                    equipment.append(item)

        return equipment[:15]  # Limit to first 15 items

    def extract_safety(self, exp_text: str) -> List[str]:
        """
        Extract safety precautions from experiment text.

        Args:
            exp_text: Experiment section text

        Returns:
            List of safety precautions
        """
        safety = []

        # Look for safety section
        safety_pattern = r"(?:safety|precaution|warning|danger)[\s:]*([^.]+?)(?:[.!?]|equipment|procedure|step)"

        for match in re.finditer(safety_pattern, exp_text, re.IGNORECASE | re.DOTALL):
            safety_text = match.group(1)
            items = re.split(r'[,\n;]', safety_text)
            for item in items:
                item = item.strip()
                if item and len(item) < 150 and any(kw in item.lower() for kw in self.safety_keywords):
                    safety.append(item)

        return safety[:10]  # Limit to first 10 items

    def parse_experiments(self, text: str) -> Dict[int, Experiment]:
        """
        Parse all experiments from text.

        Args:
            text: Full lab manual text

        Returns:
            Dictionary mapping experiment number to Experiment object
        """
        experiments_dict = {}

        # Find all experiments
        experiment_positions = self.find_experiments(text)

        if not experiment_positions:
            logger.warning("No experiments found in text")
            return {}

        for idx, (exp_num, start_pos) in enumerate(experiment_positions):
            # Determine end position
            if idx + 1 < len(experiment_positions):
                end_pos = experiment_positions[idx + 1][1]
            else:
                end_pos = len(text)

            # Extract content
            content = text[start_pos:end_pos].strip()

            # Parse experiment details
            title = self.extract_title(content, exp_num)
            procedures = self.extract_procedures(content)
            equipment = self.extract_equipment(content)
            safety = self.extract_safety(content)

            # Create experiment object
            experiment = Experiment(
                number=exp_num,
                title=title,
                content=content,
                procedure=procedures,
                equipment=equipment,
                safety=safety,
                start_pos=start_pos,
                end_pos=end_pos
            )

            experiments_dict[exp_num] = experiment
            logger.info(f"Parsed experiment {exp_num}: {title}")

        return experiments_dict

    def get_summary(self, experiments: Dict[int, Experiment]) -> List[Dict]:
        """
        Get summary of all experiments.

        Args:
            experiments: Dictionary of Experiment objects

        Returns:
            List of experiment summaries
        """
        summaries = []

        for exp_num in sorted(experiments.keys()):
            exp = experiments[exp_num]
            summaries.append({
                "number": exp.number,
                "title": exp.title,
                "steps": len(exp.procedure),
                "equipment": len(exp.equipment),
                "safety_items": len(exp.safety),
                "content_length": len(exp.content)
            })

        return summaries
