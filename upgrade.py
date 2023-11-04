#!/usr/bin/env python

import os
import pathlib
import subprocess

def main():
    base_dir = pathlib.Path(__file__).resolve().parent
    fonts_dir = base_dir / 'compeng_gg' / 'static' / 'fonts'
    os.makedirs(fonts_dir, exist_ok=True)
    inter_version = '3.19'
    inter_archive = f'Inter-{inter_version}.zip'
    inter_url = f'https://github.com/rsms/inter/releases/download/v{inter_version}/{inter_archive}'
    inter_dir = base_dir / f'inter-{inter_version}'
    subprocess.run(['wget', inter_url], check=True, cwd=base_dir)
    subprocess.run(['unzip', '-d', inter_dir, inter_archive], check=True, cwd=base_dir)
    subprocess.run(['rm', inter_archive], check=True, cwd=base_dir)
    subprocess.run(['mv', inter_dir / 'Inter Web' / 'Inter-Regular.woff2', fonts_dir], check=True, cwd=base_dir)
    subprocess.run(['mv', inter_dir / 'Inter Web' / 'Inter-Regular.woff', fonts_dir], check=True, cwd=base_dir)
    subprocess.run(['mv', inter_dir / 'Inter Web' / 'Inter-Italic.woff2', fonts_dir], check=True, cwd=base_dir)
    subprocess.run(['mv', inter_dir / 'Inter Web' / 'Inter-Italic.woff', fonts_dir], check=True, cwd=base_dir)
    subprocess.run(['rm', '-rf', inter_dir], check=True, cwd=base_dir)

if __name__ == '__main__':
    main()
