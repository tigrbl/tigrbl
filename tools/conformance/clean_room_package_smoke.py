from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / 'pkgs' / 'core' / 'tigrbl'


def find_entry_points(wheel_path: Path) -> dict[str, str]:
    with ZipFile(wheel_path) as zf:
        entry_name = next(name for name in zf.namelist() if name.endswith('entry_points.txt'))
        text = zf.read(entry_name).decode('utf-8')
    result: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') and line.endswith(']'):
            current = line[1:-1]
            continue
        if current == 'console_scripts' and '=' in line:
            name, value = [part.strip() for part in line.split('=', 1)]
            result[name] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-out', help='optional manifest output path')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        cmd = [sys.executable, '-m', 'build', str(PACKAGE_DIR), '--wheel', '--sdist', '--outdir', str(out_dir)]
        subprocess.run(cmd, check=True, cwd=ROOT)
        wheels = sorted(out_dir.glob('*.whl'))
        sdists = sorted(out_dir.glob('*.tar.gz'))
        if not wheels or not sdists:
            raise SystemExit('clean-room package smoke failed: wheel or sdist missing')
        entry_points = find_entry_points(wheels[0])
        if entry_points.get('tigrbl') != 'tigrbl.cli:console_main':
            raise SystemExit('clean-room package smoke failed: missing tigrbl console entrypoint')
        manifest = {
            'package_dir': str(PACKAGE_DIR.relative_to(ROOT)),
            'wheel': wheels[0].name,
            'sdist': sdists[0].name,
            'console_scripts': entry_points,
        }
        if args.manifest_out:
            out = Path(args.manifest_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
