from .ast_analyzer import ASTAnalyzer
from .llm_analyzer import LLMAnalyzer
from .milestone_detector import detect_milestone
from .progress_tracker import ProgressTracker


class AnalyzerService:

    def __init__(self):

        self.llm = LLMAnalyzer()
        self.trackers = {}

    def analyze(
        self,
        session_id: str,
        code: str,
        milestone: str,
    ) -> dict:

        # --------------------------------
        # 1. AST
        # --------------------------------

        ast_result = ASTAnalyzer(
            code
        ).analyze()

        # Empty code
        if ast_result["empty"]:

            return {
                "status": "WAITING",
                "hint_available": False,
                "milestone": milestone,
                "ast": ast_result,
            }

        # Syntax error
        if not ast_result["syntax_valid"]:

            return {
                "status": "TYPING",
                "hint_available": False,
                "milestone": milestone,
                "syntax_error": ast_result[
                    "syntax_error"
                ],
            }

        # --------------------------------
        # 2. LLM
        # --------------------------------

        llm_result = self.llm.analyze(
            code=code,
            milestone=milestone,
            ast_result=ast_result,
        )

        # --------------------------------
        # 3. Milestone
        # --------------------------------

        detected_milestone = detect_milestone(
            features=ast_result["features"]
        )

        # --------------------------------
        # 4. Tracker
        # --------------------------------

        if session_id not in self.trackers:

            self.trackers[session_id] = (
                ProgressTracker()
            )

        tracker = self.trackers[
            session_id
        ]

        tracking = tracker.update(
            code=code,
            analysis=llm_result,
        )

        # --------------------------------
        # 5. Status
        # --------------------------------

        if llm_result["progressing"]:

            status = "PROGRESSING"

        elif not llm_result["relevant"]:

            status = "IRRELEVANT"

        elif llm_result["stuck"]:

            status = "STUCK"

        else:

            status = "NO_PROGRESS"

        return {
            "status": status,
            "hint_available": tracking[
                "hint_available"
            ],
            "milestone": detected_milestone.get("milestone", milestone),
            "llm": llm_result,
            "ast": ast_result,
            "tracking": tracking,
        }

    def reset(self, session_id: str):

        if session_id in self.trackers:

            self.trackers[
                session_id
            ].reset()