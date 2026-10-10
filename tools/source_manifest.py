"""Verify current source bytes while retaining recorded controller revisions."""


def latest_sources(manifest):
    current = {}
    for item in manifest['sources']:
        path = item['path']
        previous = current.get(path)
        if previous and previous['sha256'] != item['sha256']:
            assert path.startswith('code/controller/') and item.get('revision'), (
                'A changed source needs an explicit maintained-controller revision: ' + path
            )
        current[path] = item
    return current


def verify_sources(root, manifest):
    import hashlib

    current = latest_sources(manifest)
    for path, item in current.items():
        file = root / path
        assert file.is_file(), path
        assert hashlib.sha256(file.read_bytes()).hexdigest() == item['sha256'], path
    return len(current)
