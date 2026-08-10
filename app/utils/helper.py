import os

def get_files(path):
    try:
        abs_path = os.path.abspath(path)
        entries = os.listdir(abs_path)
        files = []
        for entry in entries:
            full_path = os.path.join(abs_path, entry)
            icon = get_icon(entry, full_path)
            files.append({
                'name': entry,
                'path': full_path,
                'is_dir': os.path.isdir(full_path),
                'icon': icon
            })
        # Direktori di atas, file di bawah
        return sorted(files, key=lambda x: (not x['is_dir'], x['name'].lower()))
    except Exception:
        return []

def get_icon(name, full_path):
    if os.path.isdir(full_path):
        return 'bi bi-folder'

    ext = os.path.splitext(name)[1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.gif']:
        return 'bi bi-file-image'
    if ext in ['.mp4', '.mkv', '.avi']:
        return 'bi bi-file-play'
    if ext in ['.mp3', '.wav']:
        return 'bi bi-file-music'
    if ext in ['.zip']:
        return 'bi bi-file-zip'
    if ext in ['.txt', '.md', '.json']:
        return 'bi bi-file-text'
    if ext in ['.pdf']:
        return 'bi bi-file-pdf'

    return 'bi bi-file-earmark'