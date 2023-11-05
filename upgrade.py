#!/usr/bin/env python

import os
import pathlib
import subprocess

def update_inter(base_dir, fonts_dir):
    inter_version = '3.19'
    inter_archive = f'Inter-{inter_version}.zip'
    inter_url = f'https://github.com/rsms/inter/releases/download/v{inter_version}/{inter_archive}'
    inter_dir = base_dir / f'inter-{inter_version}'
    subprocess.run(['wget', inter_url], check=True, cwd=base_dir)
    subprocess.run(['unzip', '-d', inter_dir, inter_archive], check=True, cwd=base_dir)
    subprocess.run(['rm', inter_archive], check=True, cwd=base_dir)
    subprocess.run(['mv', inter_dir / 'Inter Web' / 'Inter-Regular.woff2', fonts_dir / 'inter-regular.woff2'], check=True, cwd=base_dir)
    subprocess.run(['mv', inter_dir / 'Inter Web' / 'Inter-Italic.woff2', fonts_dir / 'inter-italic.woff2'], check=True, cwd=base_dir)
    subprocess.run(['rm', '-rf', inter_dir], check=True, cwd=base_dir)

def update_iosevka(base_dir, fonts_dir):
    iosevka_version = '27.3.4'
    iosevka_archive = f'webfont-iosevka-{iosevka_version}.zip'
    iosevka_url = f'https://github.com/be5invis/Iosevka/releases/download/v{iosevka_version}/{iosevka_archive}'
    iosevka_dir = base_dir / f'iosevka-{iosevka_version}'
    subprocess.run(['wget', iosevka_url], check=True, cwd=base_dir)
    subprocess.run(['unzip', '-d', iosevka_dir, iosevka_archive], check=True, cwd=base_dir)
    subprocess.run(['rm', iosevka_archive], check=True, cwd=base_dir)
    subprocess.run(['mv', iosevka_dir / 'woff2' / 'iosevka-regular.woff2', fonts_dir], check=True, cwd=base_dir)
    subprocess.run(['mv', iosevka_dir / 'woff2' / 'iosevka-italic.woff2', fonts_dir], check=True, cwd=base_dir)
    subprocess.run(['rm', '-rf', iosevka_dir], check=True, cwd=base_dir)

def main():
    base_dir = pathlib.Path(__file__).resolve().parent
    fonts_dir = base_dir / 'compeng_gg' / 'static' / 'fonts'
    os.makedirs(fonts_dir, exist_ok=True)

    update_inter(base_dir, fonts_dir)
    update_iosevka(base_dir, fonts_dir)

if __name__ == '__main__':
    main()
