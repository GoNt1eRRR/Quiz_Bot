import os


def get_questions(folder_path: str) -> dict:
    questions = {}

    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder_path, filename)
        with open(path, "r", encoding="KOI8-R") as file:
            content = file.read()

        question_blocks = content.split('\n\n\n')

        for block in question_blocks:
            block = block.strip().split('\n\n')
            question_text, answer_text = None, None

            for part in block:
                if part.startswith("Вопрос"):
                    question_text = part.split("\n", maxsplit=1)[1].replace("\n", " ").strip()
                elif part.startswith("Ответ"):
                    answer_text = part.split("\n", maxsplit=1)[1].replace("\n", " ").strip()

            if question_text and answer_text:
                questions[question_text] = answer_text

    return questions