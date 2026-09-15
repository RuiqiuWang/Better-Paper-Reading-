"""Resolve and update PaperReading's host-specific configuration."""
import argparse
import json
import os
from pathlib import Path
from library import atomic_write


def host_name(explicit=None):
    if explicit:
        if explicit not in ('codex', 'claude'):
            raise ValueError('host must be codex or claude')
        return explicit
    marker = Path(__file__).with_name('host.json')
    if marker.exists():
        return host_name(json.loads(marker.read_text(encoding='utf-8'))['host'])
    parts = Path(__file__).resolve().parts
    return 'codex' if '.codex' in parts or '.agents' in parts else 'claude'


def config_root(host=None):
    host = host_name(host)
    env, folder = ('CODEX_HOME', '.codex') if host == 'codex' else ('CLAUDE_CONFIG_DIR', '.claude')
    return Path(os.environ.get(env, str(Path.home() / folder))).expanduser().resolve()


def default_store():
    if os.name == 'nt' and Path('D:/').is_dir():
        return Path('D:/claude_paper_reading')
    return Path.home() / 'PaperReading'


def load(host=None):
    path = config_root(host) / 'paper_reading_config.json'
    data = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    if not isinstance(data, dict):
        raise ValueError('paper_reading_config.json must be an object')
    return path, data


def update(host=None, store=None, language=None):
    path, data = load(host)
    if store is not None:
        target = Path(store).expanduser().resolve()
        if str(target) != str(Path(data.get('store_dir', default_store())).expanduser().resolve()):
            data.pop('dashboard_url', None)
        (target / '_cache').mkdir(parents=True, exist_ok=True)
        data['store_dir'] = target.as_posix()
    if language is not None:
        if language not in ('chinese', 'english'):
            raise ValueError('Unsupported language')
        data['language'] = language
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return path, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=('codex', 'claude'))
    parser.add_argument('--store')
    parser.add_argument('--language', choices=('chinese', 'english'))
    args = parser.parse_args()
    path, data = update(args.host, args.store, args.language) if args.store is not None or args.language else load(args.host)
    effective = dict(data)
    effective.setdefault('store_dir', default_store().as_posix())
    effective.setdefault('language', 'chinese')
    print(json.dumps({'host': host_name(args.host), 'config_file': str(path), 'config': effective}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
