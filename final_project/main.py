import os

from core.config import setup_config
from core.context import ContextManager
from core.file_handler import (
    get_file_chunks,
    parse_chunk_command,
    process_file_attachments,
)
from core.llm_client import LLMClient


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_file_chunk_mode(client: LLMClient, command_input: str) -> None:
    chunk_type, value, auto_confirm = parse_chunk_command(command_input)

    try:
        filepath = input('>>> Введите путь до файла\n>>> ').strip()
        if filepath == '\\q':
            return

        if not os.path.exists(filepath):
            print(f"[Ошибка]: Файл '{filepath}' не существует.")
            return
        prompt_str = '>>> Принято. Что нужно сделать для каждого фрагмента (User Prompt)?\n>>>'
        user_prompt = input(prompt_str).strip()
        if user_prompt == '\\q':
            return

        chunks = get_file_chunks(filepath, chunk_type, value)
        if not chunks:
            print('[Предупреждение]: Файл пуст.')
            return

        print('>>> Принято. Начинаю обработку:')

        for idx, chunk in enumerate(chunks, 1):
            print(f'\n--- Чанк {idx}/{len(chunks)} ---')

            chunk_messages = [
                {
                    'role': 'user',
                    'content': f'{user_prompt}\n\n Текст для обработки:\n{chunk}',
                }
            ]

            print('Бот: ', end='', flush=True)
            full_response = ''
            for chunk_str in client.send_request_stream(chunk_messages):
                print(chunk_str, end='', flush=True)
                full_response += chunk_str
            print()

            if not auto_confirm and idx < len(chunks):
                try:
                    action = input('\n[Нажмите Enter для следующего чанка или \\q для выхода] >>> ')
                    if action.strip() == '\\q':
                        print('Обработка прервана пользователем.')
                        break
                except (KeyboardInterrupt, EOFError):
                    print('\nОбработка прервана.')
                    break

        print('\n>>> Обработка файла завершена.')

    except Exception as e:
        print(f'[Ошибка в режиме почанковой обработки]: {e}')


def main() -> None:
    config = setup_config()
    context = ContextManager(
        system_prompt=config.system_prompt,
        limit_message=config.limit_message,
        limit_chars=config.limit_chars,
    )
    client = LLMClient(config)

    clear_screen()
    print('=== Консольный ИИ-Ассистент GigaVibeMiptCode ===')
    print('Доступные команды: \\q - выход, /reset - очистить чат, /file_chunk - почанковый режим\n')

    if config.system_prompt:
        print(f'[Системный промпт]: {config.system_prompt}\n')

    while True:
        try:
            user_input = input('>>> ').strip()
        except (KeyboardInterrupt, EOFError):
            print('\n Завершение работы.')
            break

        if not user_input:
            continue

        if user_input == '\\q':
            print('Выход из программы.')
            break

        if user_input == '/reset':
            context.reset()
            clear_screen()
            print('=== История чата очищена ===')
            comands_string = 'Доступные команды: \\q - выход,'
            print(comands_string + ' /reset - очистить чат, /file_chunk - почанковый режим\n')
            continue

        if user_input.startswith('/file_chunk'):
            handle_file_chunk_mode(client, user_input)
            continue

        processed_prompt = process_file_attachments(user_input)

        context.add_message('user', processed_prompt)

        print('Бот: ', end='', flush=True)
        full_response = ''

        for chunk in client.send_request_stream(context.get_messages()):
            print(chunk, end='', flush=True)
            full_response += chunk
        print()

        if full_response:
            context.add_message('assistant', full_response)


if __name__ == '__main__':
    main()
