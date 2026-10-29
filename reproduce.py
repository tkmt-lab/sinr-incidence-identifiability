#!/usr/bin/env python3
"""Offline finite controls. Does not check the all-n prose proof."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
VOLATILE = {'seconds', 'maxrss'}

def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value

def main():
    if not __debug__:
        raise SystemExit('Run without -O: checks use assertions.')
    manifest = ROOT / 'MANIFEST.sha256'
    if not manifest.is_file():
        raise SystemExit('Missing MANIFEST.sha256')
    count = 0
    for line in manifest.read_text().splitlines():
        expected, relative = line.split('  ', 1)
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT):
            raise SystemExit('Manifest path escapes packet')
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f'Hash mismatch: {relative}')
        count += 1
    start = time.perf_counter()
    work = ROOT / '.work'
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='finite-', dir=work) as directory:
        isolated = Path(directory)
        shutil.copytree(ROOT / 'checks', isolated / 'checks')
        shutil.copytree(ROOT / 'baseline', isolated / 'baseline')
        (isolated / 'results').mkdir()
        for name in ('diagnose.py', 'check_jets.py', 'check_algebra.py'):
            result = subprocess.run([sys.executable, '-B', str(isolated/'checks'/name)],
                                    cwd=isolated, capture_output=True, text=True, timeout=600)
            if result.returncode:
                raise SystemExit(result.stdout + result.stderr)
            print(f'PASS {name}', flush=True)
        compared = []
        for baseline in sorted((ROOT/'baseline').glob('*.json')):
            generated = isolated/'results'/baseline.name
            if normalized(json.loads(baseline.read_text())) != normalized(json.loads(generated.read_text())):
                raise SystemExit(f'Baseline mismatch: {baseline.name}')
            compared.append(baseline.name)
    summary = {'status': 'PASS', 'manifest_files': count, 'compared': compared,
               'seconds': time.perf_counter()-start,
               'scope': 'finite n=1..6 controls only',
               'all_n_proof_checked': False, 'this_run_is_independent_agent_review': False}
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/'reproduction.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
