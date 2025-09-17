import os
import shutil


def save_file(upload_dir: str, file) -> str:
    file_path = os.path.join(os.getcwd(), upload_dir)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    full_path = os.path.join(file_path, file.filename)
    with open(full_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    
    return full_path
