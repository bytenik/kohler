"""Compress and verify raw evidence without changing the original recordings."""
import hashlib
import json
import lzma
import os
from pathlib import Path
import shutil
import subprocess

from project_paths import CAPTURES, ROOT


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def archive(item):
    source = ROOT / item['path']
    target = Path(str(source) + '.xz')
    temporary = Path(str(target) + '.tmp')
    if not target.exists():
        try:
            with temporary.open('wb') as output:
                if shutil.which('xz'):
                    subprocess.run(['xz', '-3', '-T4', '-c', str(source)],
                                   stdout=output, check=True)
                else:
                    with source.open('rb') as raw, lzma.LZMAFile(output, 'wb', preset=3) as compressed:
                        shutil.copyfileobj(raw, compressed, length=1024 * 1024)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    digest = hashlib.sha256()
    size = 0
    with lzma.open(target, 'rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
            size += len(block)
    if size != item['size_bytes'] or digest.hexdigest() != item['sha256']:
        raise ValueError(f'Archive differs from original inventory: {source}')
    return {
        **item, 'archive_path': target.relative_to(ROOT).as_posix(),
        'archive_size_bytes': target.stat().st_size,
        'archive_sha256': sha256(target),
    }


def main():
    inventory = json.loads((CAPTURES / 'raw-inventory.json').read_text())
    results = []
    for item in sorted(inventory['files'], key=lambda entry: entry['size_bytes'], reverse=True):
        result = archive(item)
        results.append(result)
        print(f"Verified {len(results)}/{len(inventory['files'])}: {result['archive_path']}", flush=True)
    report = {
        'raw_files_in_git': False, 'archives_in_git': True,
        'format': 'xz', 'compression_preset': 3, 'lossless_verified': True,
        'files': sorted(results, key=lambda entry: entry['path']),
        'total_original_bytes': sum(entry['size_bytes'] for entry in results),
        'total_archive_bytes': sum(entry['archive_size_bytes'] for entry in results),
    }
    (CAPTURES / 'archive-inventory.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"Original: {report['total_original_bytes']} bytes; archives: {report['total_archive_bytes']} bytes")


if __name__ == '__main__':
    main()
