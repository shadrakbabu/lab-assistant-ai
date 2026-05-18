import re


class ExperimentIdentifier:

    def identify_experiments(self, text):

        experiments = {}

        # =========================
        # SPLIT INTO EXPERIMENTS
        # =========================
        sections = re.split(
            r'(?=EXPERIMENT\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*\d+)',
            text,
            flags=re.IGNORECASE
        )

        for section in sections:

            if len(section.strip()) < 50:
                continue

            # =========================
            # EXPERIMENT NUMBER
            # =========================
            number_match = re.search(
                r'EXPERIMENT\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*(\d+)',
                section,
                re.IGNORECASE
            )

            if not number_match:
                continue

            exp_number = number_match.group(1)

            # =========================
            # TITLE
            # =========================
            title_match = re.search(
                r'EXPERIMENT\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*\d+\s*[:\-]?\s*(.*)',
                section,
                re.IGNORECASE
            )

            if title_match:

                title = (
                    title_match.group(1)
                    .split("\n")[0]
                    .strip()
                )

            else:

                title = f"Experiment {exp_number}"

            # =========================
            # AIM
            # =========================
            aim_match = re.search(
                r'(AIM|OBJECTIVE)\s*[:\-]?\s*(.*?)(?=THEORY|APPARATUS|EQUIPMENT|PROCEDURE|RESULT|OBSERVATION|$)',
                section,
                re.IGNORECASE | re.DOTALL
            )

            aim = ""

            if aim_match:
                aim = aim_match.group(2).strip()

            # =========================
            # EQUIPMENT
            # =========================
            equipment_match = re.search(
                r'(APPARATUS|EQUIPMENT|MATERIALS REQUIRED)\s*[:\-]?\s*(.*?)(?=PROCEDURE|THEORY|OBSERVATION|RESULT|$)',
                section,
                re.IGNORECASE | re.DOTALL
            )

            equipment = []

            if equipment_match:

                equipment_text = equipment_match.group(2)

                equipment = [
                    item.strip()
                    for item in re.split(
                        r',|\n|•|-',
                        equipment_text
                    )
                    if len(item.strip()) > 2
                ]

            # =========================
            # PROCEDURE
            # =========================
            procedure_match = re.search(
                r'PROCEDURE\s*[:\-]?\s*(.*?)(?=RESULT|OBSERVATION|PRECAUTIONS|VIVA|$)',
                section,
                re.IGNORECASE | re.DOTALL
            )

            procedure = []

            if procedure_match:

                procedure_text = procedure_match.group(1)

                procedure = [
                    step.strip()
                    for step in re.split(
                        r'\n|\d+\.',
                        procedure_text
                    )
                    if len(step.strip()) > 5
                ]

            # =========================
            # SAFETY
            # =========================
            safety_match = re.search(
                r'(PRECAUTIONS|SAFETY)\s*[:\-]?\s*(.*?)(?=RESULT|$)',
                section,
                re.IGNORECASE | re.DOTALL
            )

            safety = []

            if safety_match:

                safety_text = safety_match.group(2)

                safety = [
                    item.strip()
                    for item in re.split(
                        r'\n|•|-',
                        safety_text
                    )
                    if len(item.strip()) > 5
                ]

            # =========================
            # STORE DATA
            # =========================
            experiments[exp_number] = {

                "experiment_number": exp_number,

                "title": title,

                "aim": aim,

                "equipment": equipment,

                "procedure": procedure,

                "safety": safety,

                "content": section
            }

        return experiments