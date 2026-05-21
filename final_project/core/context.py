class ContextManager:
    def __init__(
        self,
        system_prompt: str | None = None,
        limit_message: int | None = None,
        limit_chars: int | None = None,
    ):
        self.system_prompt = system_prompt
        self.limit_message = limit_message
        self.limit_chars = limit_chars
        self.messages: list[dict[str, str]] = []
        if self.system_prompt:
            self.messages.append({'role': 'system', 'content': self.system_prompt})

    def add_message(self, role: str, content: str) -> None:
        if self.limit_chars is not None and len(content) > self.limit_chars:
            content = content[-self.limit_chars :]

        self.messages.append({'role': role, 'content': content})
        self.enforce_limits()

    def enforce_limits(self) -> None:
        start_idx = 1 if (self.messages and self.messages[0]['role'] == 'system') else 0
        if self.limit_message is not None:
            while len(self.messages) > self.limit_message:
                if len(self.messages) > start_idx:
                    self.messages.pop(start_idx)
                else:
                    break
        if self.limit_chars is not None:
            while self._get_total_chars() > self.limit_chars:
                if len(self.messages) > start_idx:
                    self.messages.pop(start_idx)
                else:
                    last_msg_idx = len(self.messages) - 1
                    allowed_len = self.limit_chars
                    if last_msg_idx >= start_idx:
                        current_content = self.messages[last_msg_idx]['content']
                        allowed_len -= self._get_total_chars() - len(current_content)
                        if allowed_len > 0:
                            self.messages[last_msg_idx]['content'] = current_content[-allowed_len:]
                        else:
                            self.messages[last_msg_idx]['content'] = ''
                    break

    def _get_total_chars(self) -> int:
        return sum(len(msg['content']) for msg in self.messages)

    def get_messages(self) -> list[dict[str, str]]:
        return self.messages

    def reset(self) -> None:
        self.messages = []
        if self.system_prompt:
            self.messages.append({'role': 'system', 'content': self.system_prompt})
