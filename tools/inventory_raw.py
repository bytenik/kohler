"""Record sizes and SHA-256 hashes of locally retained, unversioned raw evidence."""
import hashlib
import json
from project_paths import CAPTURES, ROOT

files = []
for path in sorted(CAPTURES.rglob('*')):
    if path.suffix not in ('.f64', '.pcap'):
        continue
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    files.append({'path': path.relative_to(ROOT).as_posix(),
                  'size_bytes': path.stat().st_size, 'sha256': digest.hexdigest()})
result = {'raw_files_in_git': False, 'files': files,
          'total_bytes': sum(item['size_bytes'] for item in files)}
(CAPTURES / 'raw-inventory.json').write_text(json.dumps(result, indent=2) + '\n')
print(f"Inventoried {len(files)} raw files, {result['total_bytes']} bytes")
