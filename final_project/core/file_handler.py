import os
import re

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


def process_file_attachments(user_input: str) -> str:
    pattern = r'@::(.*?)::'
    matches = re.findall(pattern, user_input)
    cleaned_text = re.sub(pattern, '', user_input).strip()
    file_contents = []

    for filepath in matches:
        filepath = filepath.strip()
        if not os.path.exists(filepath):
            print(f"\n[Ошибка]: Файл не найден по пути '{filepath}'")
            continue

        try:
            file_size = os.path.getsize(filepath)
            if file_size > MAX_FILE_SIZE_BYTES:
                print(
                    f"\n[Ошибка]: Файл '{filepath}' превышает лимит 5 МБ "
                    f'(размер: {file_size / (1024 * 1024):.2f} МБ). Скипаем.'
                )
                continue
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                file_contents.append(content)
        except Exception as e:
            print(f"\n[Ошибка при чтении файла '{filepath}']: {e}")
            continue

    if file_contents:
        appended_content = '\n'.join(file_contents)
        if cleaned_text:
            return f'{cleaned_text}\n{appended_content}'
        return appended_content

    return cleaned_text


def get_file_chunks(filepath: str, chunk_type: str, value: int) -> list[str]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл '{filepath}' не найден.")

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    if chunk_type == 'len':
        return [text[i : i + value] for i in range(0, len(text), value)]
    else:
        paragraphs = [p for p in text.split('\n') if p.strip()]
        if not paragraphs:
            return []
        chunks = []
        for i in range(0, len(paragraphs), value):
            chunk = '\n'.join(paragraphs[i : i + value])
            chunks.append(chunk)
        return chunks


def parse_chunk_command(command_input: str) -> tuple[str, int, bool]:
    chunk_type = 'paragraph'
    value = 1
    auto_confirm = '-y' in command_input
    cleaned = command_input.replace('-y', '').strip()
    para_match = re.search(r'paragraph=(\d+)', cleaned)
    len_match = re.search(r'len=(\d+)', cleaned)

    if para_match:
        chunk_type = 'paragraph'
        value = int(para_match.group(1))
    elif len_match:
        chunk_type = 'len'
        value = int(len_match.group(1))

    return chunk_type, value, auto_confirm
