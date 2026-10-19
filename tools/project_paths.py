"""Resolve capture identifiers independently of the caller's working directory."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / 'captures'
REPORTS = CAPTURES / 'reports'


def evidence(value):
    """Locate an existing file by current path or its historical identifier."""
    path = Path(value)
    if path.is_file():
        return path.resolve()
    rooted = ROOT / path
    if rooted.is_file():
        return rooted
    mapping = json.loads((CAPTURES / 'path-map.json').read_text())
    mapped = mapping.get(path.as_posix())
    if mapped and (ROOT / mapped).is_file():
        return ROOT / mapped
    matches = list(CAPTURES.rglob(path.name))
    matches = [p for p in matches if p.is_file()]
    if len(matches) != 1:
        raise FileNotFoundError(f'Expected one evidence file for {value}, found {len(matches)}')
    return matches[0]


def capture_base(value):
    """Resolve an existing capture prefix, including bases inside old manifests."""
    for suffix in ('.json', '-manifest.json'):
        try:
            path = evidence(str(value) + suffix)
            return Path(str(path)[:-len(suffix)])
        except FileNotFoundError:
            pass
    raise FileNotFoundError(f'No capture metadata for {value}')


def new_capture_base(value, bus='system'):
    """Place new sessions under captures unless an explicit directory is supplied."""
    path = Path(value)
    if path.parent == Path('.'):
        path = CAPTURES / ('valve' if bus == 'valve' else 'system') / path.name / path.name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.resolve()
