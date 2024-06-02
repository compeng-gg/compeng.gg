#!/usr/bin/env python

import os
import pathlib
import subprocess

BASE_DIR = pathlib.Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / 'venv'
VENV_BIN_DIR = VENV_DIR / 'bin'

def run_venv(args, capture_output=False):
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = VENV_DIR
    env['PATH'] = f"{VENV_BIN_DIR}:{env['PATH']}"
    p = subprocess.run(args,
        capture_output=capture_output, check=True, cwd=BASE_DIR, env=env,
        text=True
    )
    return p

def update_requirements():
    subprocess.run(['rm', '-rf', 'venv'], check=True, cwd=BASE_DIR)
    subprocess.run(['python3', '-m', 'venv', 'venv'], check=True, cwd=BASE_DIR)
    run_venv(['pip', 'install', '-U', 'pip'])
    run_venv([
        'pip', 'install',
        'django',
        'djangorestframework',
        'social-auth-app-django',
    ])
    p = run_venv(['pip', 'freeze'], capture_output=True)
    with open(BASE_DIR / 'requirements.txt', 'w') as f:
        f.write(p.stdout)

def main():
    fonts_dir = BASE_DIR / 'compeng_gg' / 'static' / 'fonts'
    os.makedirs(fonts_dir, exist_ok=True)

    update_requirements()

if __name__ == '__main__':
    main()
