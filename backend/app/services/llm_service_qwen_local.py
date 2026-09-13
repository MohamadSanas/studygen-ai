import ollama


class QwenLLMServiceLocal:

    def __init__(self, model_name: str = "qwen2.5:1.5b"):
        self.model_name = model_name

    async def generate(
        self,
        question: str,
        context: str,
        chat_history: list[dict[str, str]] | None = None,
    ) -> str:

        if chat_history is None:
            chat_history = []

        messages = [
            {
                "role": "system",
                "content": (
                    "You are StudyGen AI, a university study assistant. "
                    "Answer questions using the provided lecture material. "
                    "Do not invent information that is not present in the material."
                ),
            }
        ]

        for message in chat_history:
            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": f"""
QUESTION:
{question}

LECTURE MATERIAL:
{context}
""",
            }
        )

        try:
            client = ollama.AsyncClient()

            response = await client.chat(
                model=self.model_name,
                messages=messages,
            )

            return response["message"]["content"]

        except Exception as e:
            raise RuntimeError(
                f"Error calling local Ollama model "
                f"'{self.model_name}': {e}"
            )