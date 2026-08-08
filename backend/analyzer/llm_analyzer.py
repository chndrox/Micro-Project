import json
import os

from groq import Groq


MODEL = "llama-3.3-70b-versatile"


class LLMAnalyzer:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set in .env"
            )

        self.client = Groq(api_key=api_key)

    def analyze(
        self,
        code: str,
        milestone: str,
        ast_result: dict,
    ) -> dict:

        prompt = self._build_prompt(
            code,
            milestone,
            ast_result,
        )

        response = self.client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_tokens=400,
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt(),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        text = response.choices[0].message.content.strip()

        return self._parse_response(text)

    def _system_prompt(self) -> str:

        return (
            "You are the code-progress analyzer for ThinkForge AI.\n\n"
            "Your job is to analyze whether a student's code is "
            "relevant to the current learning milestone.\n\n"
            "Do NOT solve the problem.\n"
            "Do NOT provide hints.\n"
            "Do NOT rewrite the student's code.\n\n"
            "Return ONLY valid JSON.\n\n"
            "Required format:\n"
            "{\n"
            '  "relevant": true,\n'
            '  "progressing": true,\n'
            '  "stuck": false,\n'
            '  "milestone": "brute_force",\n'
            '  "confidence": 0.90,\n'
            '  "reason": "short explanation"\n'
            "}\n\n"
            "Rules:\n"
            "1. Random unrelated code is irrelevant.\n"
            "2. Incomplete code is not automatically stuck.\n"
            "3. Syntax errors while typing are not automatically stuck.\n"
            "4. Code that meaningfully moves toward the objective is progressing.\n"
            "5. Relevant code with no meaningful movement can be stuck.\n"
            "6. Keep the reason short.\n"
        )

    def _build_prompt(
        self,
        code: str,
        milestone: str,
        ast_result: dict,
    ) -> str:

        ast_json = json.dumps(
            ast_result,
            indent=2,
        )

        return (
            "Problem: Two Sum\n\n"
            f"Learning milestone: {milestone}\n\n"
            "Student code:\n"
            "```python\n"
            f"{code}\n"
            "```\n\n"
            "Static AST analysis:\n"
            f"{ast_json}\n\n"
            "Determine:\n"
            "- Is the code relevant to Two Sum?\n"
            "- Is it progressing toward the current milestone?\n"
            "- Is the student stuck?\n"
            "- What milestone does the code represent?\n"
            "- How confident are you?\n\n"
            "Return ONLY valid JSON."
        )

    def _parse_response(
        self,
        text: str,
    ) -> dict:

        text = text.strip()

        if text.startswith("```"):
            text = text.replace(
                "```json",
                "",
            )
            text = text.replace(
                "```",
                "",
            )
            text = text.strip()

        try:

            result = json.loads(text)

        except json.JSONDecodeError:

            return {
                "relevant": False,
                "progressing": False,
                "stuck": False,
                "milestone": "unknown",
                "confidence": 0.0,
                "reason": "Unable to parse analyzer response.",
            }

        return {
            "relevant": bool(
                result.get(
                    "relevant",
                    False,
                )
            ),
            "progressing": bool(
                result.get(
                    "progressing",
                    False,
                )
            ),
            "stuck": bool(
                result.get(
                    "stuck",
                    False,
                )
            ),
            "milestone": result.get(
                "milestone",
                "unknown",
            ),
            "confidence": float(
                result.get(
                    "confidence",
                    0.0,
                )
            ),
            "reason": result.get(
                "reason",
                "",
            ),
        }