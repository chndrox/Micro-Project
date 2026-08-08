class ProgressTracker:

    def __init__(self):

        self.previous_code = ""
        self.previous_progress = 0.0

        self.stuck_count = 0
        self.analysis_count = 0

    def update(
        self,
        code: str,
        analysis: dict,
    ) -> dict:

        self.analysis_count += 1

        progressing = analysis["progressing"]
        stuck = analysis["stuck"]
        relevant = analysis["relevant"]

        code_changed = (
            code != self.previous_code
        )

        if progressing:

            self.stuck_count = 0

        elif stuck and relevant:

            self.stuck_count += 1

        elif not relevant:

            self.stuck_count += 1

        elif not code_changed:

            self.stuck_count += 1

        else:

            self.stuck_count = max(
                0,
                self.stuck_count - 1,
            )

        self.previous_code = code

        hint_available = (
            self.stuck_count >= 3
        )

        return {
            "code_changed": code_changed,
            "stuck_count": self.stuck_count,
            "hint_available": hint_available,
        }

    def reset(self):

        self.previous_code = ""
        self.previous_progress = 0.0
        self.stuck_count = 0
        self.analysis_count = 0