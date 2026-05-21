GigaVibeMiptCode - консольное приложение-чат для общения с LLM.

Запуск:

1) нужно активировать виртуальное окружение в папке проекта .venv\Scripts\activate

2) установить библиотеки pip install openai pyyaml

3) создать локально свой config.yaml:

api_key: "ollama_secret_token_here"
api_host: "http://localhost:11434/v1/"
limit_message: 11
limit_chars: 2000
temperature: 0.7
system_prompt: "You are a helpful and precise MIPT student assistant."
model: "gemma3:270m"

если используется локальный хост Ollama, нужную модель необходимо скачать

4) далее запустить main.py
