#!/usr/bin/env python

import os
import pathlib
import subprocess

def update_requirements(base_dir):
    subprocess.run(['rm', '-rf', 'venv'], check=True, cwd=base_dir)
    subprocess.run(['python3', '-m', 'venv', 'venv'], check=True, cwd=base_dir)
    venv_dir = base_dir / 'venv'
    venv_env = os.environ.copy()
    venv_env['VIRTUAL_ENV'] = venv_dir
    venv_env['PATH'] = f"{venv_dir / 'bin'}:{venv_env['PATH']}"
    subprocess.run(['pip', 'install', '-U', 'pip'],
                   check=True, cwd=base_dir, env=venv_env)
    subprocess.run(['pip', 'install', 'django'],
                   check=True, cwd=base_dir, env=venv_env)
    subprocess.run(['pip', 'install', 'social-auth-app-django'],
                   check=True, cwd=base_dir, env=venv_env)
    p = subprocess.run(['pip', 'freeze'],
                       capture_output=True, check=True, cwd=base_dir,
                       env=venv_env, text=True)
    with open(base_dir / 'requirements.txt', 'w') as f:
        f.write(p.stdout)

def main():
    base_dir = pathlib.Path(__file__).resolve().parent
    fonts_dir = base_dir / 'compeng_gg' / 'static' / 'fonts'
    os.makedirs(fonts_dir, exist_ok=True)

    update_requirements(base_dir)

if __name__ == '__main__':
    main()
