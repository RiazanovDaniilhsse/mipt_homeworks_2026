from core.config import AppConfig
from openai import OpenAI


class LLMClient:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = OpenAI(api_key=self.config.api_key, base_url=self.config.api_host)
        self.model_name = "gemma3:270m"

    def send_request_stream(self, messages: list[dict[str, str]]):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.temperature,
                stream=True,
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except KeyboardInterrupt:
            print("\n\n[Запрос прерван пользователем (Ctrl+C)]")
            return
        except Exception as e:
            print(f"\n\n[Ошибка сервера/API]: Не удалось получить ответ. Подробности: {e}")
            return
