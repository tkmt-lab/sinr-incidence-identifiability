"""Bounded offline privacy-pattern scan; no network or mathematical verification."""
from pathlib import Path
import hashlib
import ast
import json
import re
import shutil
import subprocess
import sys
import zlib

# Byte-encoded match vocabulary prevents a scanner's own source from matching it.
TOKENS = {
    'local-volume-root': '2f566f6c756d65732f',
    'local-user-root': '2f55736572732f',
    'private-root': '2f707269766174652f',
    'temporary-root': '2f746d702f',
    'os-temp-root': '2f7661722f666f6c646572732f',
    'home-root': '2f686f6d652f',
}
PUBLIC_PERSON = {'given-names': 'Tatsuhiko', 'family-names': 'Takimoto'}
PATTERNS = [(key, re.compile(re.escape(bytes.fromhex(value).decode()), re.I))
            for key, value in TOKENS.items()]
PATTERNS += [
    ('email-address', re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)),
    ('private-hostname', re.compile(r'\b[a-z0-9][a-z0-9.-]*\.(?:local|internal|lan|ts\.net)\b', re.I)),
    ('private-ipv4', re.compile(r'\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b')),
    ('windows-user-root', re.compile(r'[A-Z]:[\\/]Users[\\/]', re.I)),
]


def mask_public_identity(text):
    # The approved public author's name is not a machine login. Limit exceptions
    # to the full name and the exact given-name field used by the citation object.
    given = PUBLIC_PERSON['given-names']
    text = re.sub(re.escape(given) + r'\s+' + re.escape(PUBLIC_PERSON['family-names']), '<PUBLIC_AUTHOR>', text, flags=re.I)
    return re.sub(r'''(["']given-names["']\s*:\s*["'])''' + re.escape(given) + r'''(["'])''',
                  r'\1<PUBLIC_GIVEN_NAME>\2', text, flags=re.I)


def matches(text):
    text = mask_public_identity(text)
    found = {key for key, pattern in PATTERNS if pattern.search(text)}
    return sorted(found)


def file_views(path):
    raw = path.read_bytes()
    yield 'raw-utf8', raw.decode('utf-8', errors='replace')
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')) or b'\x00' in raw:
        for enc in ('utf-16-le', 'utf-16-be'):
            yield enc, raw.decode(enc, errors='replace')
    if path.suffix.lower() == '.pdf':
        for tool, args in [('pdftotext', [str(path), '-']), ('pdfinfo', [str(path)])]:
            assert shutil.which(tool), 'privacy scan requires existing Poppler utility: ' + tool
            proc = subprocess.run([tool, *args], capture_output=True, timeout=30)
            assert proc.returncode == 0, ('PDF extraction failed', path.name, tool)
            yield tool, proc.stdout.decode('utf-8', errors='replace')
        # Also inspect uncompressed content/metadata streams, in addition to
        # Poppler's decoded page text and PDF metadata.
        for match in re.finditer(rb'\bstream\r?\n(.*?)\r?\nendstream\b', raw, re.S):
            try:
                block = zlib.decompress(match[1])
            except zlib.error:
                continue
            yield 'pdf-deflate-stream', block.decode('utf-8', errors='replace')


def scan_tree(root):
    root = Path(root)
    hits = []
    count = pdfs = 0
    for path in sorted(root.rglob('*')):
        if path.relative_to(root).parts[0] in {'.git', '.work', 'build', 'results', '__pycache__'}:
            continue
        assert not path.is_symlink(), 'privacy scan rejects symbolic links'
        relative = path.relative_to(root).as_posix()
        for rule in matches(relative):
            hits.append(dict(file=relative, view='filename', rule=rule))
        if not path.is_file():
            continue
        count += 1
        pdfs += path.suffix.lower() == '.pdf'
        for view, content in file_views(path):
            for rule in matches(content):
                hits.append(dict(file=relative, view=view, rule=rule))
    return dict(status='PASS' if not hits else 'FAIL', files=count, pdfs=pdfs,
                hits=hits, hit_count=len(hits),
                scope='All filenames/raw bytes, UTF-16 views, PDF text/metadata/deflate streams; known patterns, not a guarantee against every possible private identifier.')


# Encoded internal-routing vocabulary keeps the scanner's own source neutral.
for name, value in [('internal-study-label', '5c6252305c647b327d5c62'), ('internal-workspace-name', '5c6253706972615c62'), ('routing-label', '5c626d61696c626f785c62'), ('private-key-header', '2d2d2d2d2d424547494e205b412d5a205d2a50524956415445204b45592d2d2d2d2d')]:
    PATTERNS.append((name, re.compile(bytes.fromhex(value).decode(), re.I)))

if __name__ == '__main__':
    value = scan_tree(Path(__file__).resolve().parent)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    raise SystemExit(0 if value['status']=='PASS' else 1)
