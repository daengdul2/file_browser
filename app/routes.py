import os
import re
import shutil
from flask import Blueprint, render_template, request, send_file, abort, jsonify, session
from .utils import helper

# Path default jika belum dipilih
DEFAULT_BASE_DIR = os.path.abspath('/storage/emulated/0')

# Folder yang diizinkan untuk dijadikan root
ALLOWED_ROOTS = [
    os.path.abspath('/storage/emulated/0'),
    os.path.abspath('/storage/emulated/0/Download'),
    os.path.abspath('/storage/emulated/0/DCIM')
]

main = Blueprint('main', __name__)

@main.before_app_request
def set_base_dir():
    # Atur base_dir jika belum ada di session
    session_base = session.get('base_dir', DEFAULT_BASE_DIR)
    session['base_dir'] = os.path.abspath(session_base)

def get_base_dir():
    return session.get('base_dir', DEFAULT_BASE_DIR)

@main.route('/')
def index():
    base_dir = get_base_dir()
    path = request.args.get('path', base_dir)
    abs_path = os.path.abspath(path)

    if not abs_path.startswith(base_dir):
        return abort(403)
    if not os.path.isdir(abs_path):
        return abort(404)

    items = helper.get_files(abs_path)
    parent_path = os.path.dirname(abs_path) if abs_path != base_dir else None

    return render_template('index.html', files=items, current_path=abs_path, parent_path=parent_path)

@main.route('/open')
def open_file():
    base_dir = get_base_dir()
    path = request.args.get('path')
    if not path:
        return abort(404)

    abs_path = os.path.abspath(path)
    if not abs_path.startswith(base_dir):
        return abort(403)
    if not os.path.isfile(abs_path) or not os.access(abs_path, os.R_OK):
        return abort(403)

    try:
        return send_file(abs_path)
    except Exception:
        return abort(403)

@main.route('/rename', methods=['POST'])
def rename_file():
    base_dir = get_base_dir()
    path = request.form.get('path')
    new_name = request.form.get('new_name')

    if not path or not new_name:
        return jsonify({'error': 'Path and new name are required'}), 400

    abs_path = os.path.abspath(path)
    if not abs_path.startswith(base_dir):
        return jsonify({'error': 'Forbidden access'}), 403
    if not os.path.exists(abs_path):
        return jsonify({'error': 'File or directory not found'}), 404

    new_path = os.path.join(os.path.dirname(abs_path), new_name)

    try:
        os.rename(abs_path, new_path)
        return jsonify({'success': True, 'new_path': new_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/delete', methods=['POST'])
def delete():
    base_dir = get_base_dir()
    data = request.get_json()
    paths = data.get("paths", [])

    if not paths:
        return jsonify(success=False, error="Tidak ada file yang dipilih")

    try:
        for path in paths:
            abs_path = os.path.abspath(path)

            if not abs_path.startswith(base_dir):
                return jsonify(success=False, error=f"Akses dilarang: {path}")

            if os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
            elif os.path.isfile(abs_path):
                os.remove(abs_path)
            else:
                return jsonify(success=False, error=f"Item tidak ditemukan: {path}")

        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@main.route('/create-folder', methods=['POST'])
def create_folder():
    base_dir = get_base_dir()
    path = request.form.get('path')
    name = request.form.get('name')

    if not path or not name:
        return jsonify(success=False, error="Path atau nama tidak boleh kosong")

    if re.search(r'[\/\\:\*\?"<>\|]', name):
        return jsonify(success=False, error="Nama folder mengandung karakter tidak valid")

    abs_path = os.path.abspath(path)
    full_path = os.path.join(abs_path, name)

    if not abs_path.startswith(base_dir):
        return jsonify(success=False, error="Akses dilarang")
    if os.path.exists(full_path):
        return jsonify(success=False, error="Folder sudah ada")

    try:
        os.makedirs(full_path)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))
        
        
        
        
@main.route('/set-root', methods=['POST'])
def set_root():
    root_path = request.form.get('root_path')

    if not root_path:
        return jsonify(success=False, error="Path tidak boleh kosong")

    abs_path = os.path.abspath(root_path)

    if abs_path not in ALLOWED_ROOTS:
        return jsonify(success=False, error="Path tidak diizinkan")

    if not os.path.isdir(abs_path):
        return jsonify(success=False, error="Path bukan folder yang valid")

    session['base_dir'] = abs_path
    return jsonify(success=True)