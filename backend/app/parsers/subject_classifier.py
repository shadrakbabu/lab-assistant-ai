import re
from typing import Dict


class SubjectClassifier:
    """Classifies lab manual content into subjects based on keyword occurrences."""

    SUBJECT_KEYWORDS = {
        "Physics": [
            "physics", "optics", "circuit", "resistor", "voltmeter", "ammeter", "lens",
            "galvanometer", "wavelength", "pendulum", "velocity", "refractive index",
            "thermodynamics", "magnetic", "frequency", "oscillation", "bet", "surface area",
            "adsorption", "isotherm", "degassing", "pressure", "porosity"
        ],
        "Chemistry": [
            "chemistry", "titration", "acid", "base", "ph", "molarity", "solution",
            "reaction", "reagent", "precipitate", "molar mass", "catalyst", "synthesis",
            "distillation", "organic", "inorganic", "flask", "burette", "pipette", "salt"
        ],
        "Biology": [
            "biology", "microscope", "cell", "tissue", "staining", "enzyme", "dna",
            "protein", "specimen", "organism", "bacteria", "fungi", "photosynthesis",
            "slide", "dissection", "osmosis", "genetics"
        ],
        "Computer Science": [
            "algorithm", "data structure", "array", "binary tree", "sorting", "recursion",
            "python", "java", "c++", "programming", "sql", "database", "graph", "queue",
            "stack", "linked list", "network", "socket", "compilation", "object oriented"
        ]
    }

    @classmethod
    def classify(cls, text: str) -> str:
        if not text:
            return "General Science"

        text_lower = text.lower()
        scores: Dict[str, int] = {subj: 0 for subj in cls.SUBJECT_KEYWORDS}

        for subj, keywords in cls.SUBJECT_KEYWORDS.items():
            for kw in keywords:
                # Count keyword matches
                matches = len(re.findall(rf'\b{re.escape(kw)}\b', text_lower))
                scores[subj] += matches

        best_subject = max(scores, key=scores.get)
        if scores[best_subject] > 2:
            return best_subject

        return "General Science"
