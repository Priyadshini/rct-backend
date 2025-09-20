import os
import json
import shutil


def save_file(upload_dir: str, file) -> str:
    file_path = os.path.join(os.getcwd(), upload_dir)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    full_path = os.path.join(file_path, file.filename)
    with open(full_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    
    return full_path


def read_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_json(file_path: str, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)