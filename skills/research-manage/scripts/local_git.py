"""Local-only Git checkpoints for explicitly selected research code/docs (Python 3.8+)."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import subprocess
import sys


IGNORE = """# research-manage: large assets and private/local state
.env
.env.*
*.pem
*.key
__pycache__/
*.pyc
envs/
.venv/
cache/
datasets/
checkpoints/
predictions/
logs/
*.pt
*.pth
*.ckpt
*.safetensors
*.mp4
*.avi
*.mov
"""
BLOCKED_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.npz', '.npy',
                    '.mp4', '.avi', '.mov', '.mkv', '.zip', '.tar', '.gz', '.pem', '.key'}
BLOCKED_PARTS = {'.git', '.ssh', '.aws', '.venv', 'envs', 'cache', 'datasets',
                 'checkpoints', 'predictions', 'logs'}
PRIVATE_NAMES = {'credentials.json', 'openreview_credentials.json', 'id_rsa', 'id_ed25519'}
MAX_BYTES = 5 * 1024 * 1024


class GitError(RuntimeError):
    pass


def git(root, *args, check=True):
    result = subprocess.run(['git', '--literal-pathspecs', '-C', str(root), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding='utf-8', errors='replace')
    if check and result.returncode:
        raise GitError(result.stderr.strip() or result.stdout.strip() or 'Git command failed')
    return result


def repository(root):
    root = Path(root).expanduser().resolve()
    result = git(root, 'rev-parse', '--show-toplevel', check=False)
    if result.returncode:
        raise GitError('No working repository here; initialize the selected topic first.')
    top = Path(result.stdout.strip()).resolve()
    if top != root:
        raise GitError('Requested folder belongs to another repository: ' + str(top))
    return root


@contextmanager
def lock(root):
    # Coordinates this helper only; it is not a global lock against editors or other Git clients.
    path = Path(git(root, 'rev-parse', '--git-path', 'research-manage.lock').stdout.strip())
    if not path.is_absolute():
        path = root / path
    try:
        handle = path.open('x', encoding='utf-8')
    except FileExistsError:
        raise GitError('Another checkpoint may be active; inspect research-manage.lock before retrying.')
    try:
        with handle:
            handle.write('research-manage checkpoint\n')
        yield
    finally:
        path.unlink()


def initialize(root):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise GitError('Topic folder must already exist.')
    existing = git(root, 'rev-parse', '--show-toplevel', check=False)
    if existing.returncode == 0:
        repository(root)  # Refuse accidental nesting inside a parent repository.
    elif (root / '.git').exists():
        raise GitError('Existing .git is not a usable working repository; inspect it before initialization.')
    else:
        git(root, 'init')
    with lock(root):
        ignore = root / '.gitignore'
        if ignore.is_symlink():
            raise GitError('Refusing to modify a linked .gitignore.')
        old = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
        if '# research-manage: large assets and private/local state' not in old:
            with ignore.open('a', encoding='utf-8', newline='\n') as stream:
                stream.write(('\n' if old and not old.endswith('\n') else '') + IGNORE)
    return {'status': 'initialized', 'root': str(root), 'committed': False,
            'note': 'Review .gitignore and select explicit files for a checkpoint. No remote operation performed.'}


def selected_files(root, names):
    selected = []
    for name in names:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise GitError('Use explicit repository-relative files: ' + name)
        candidate = root / relative
        try:
            candidate.resolve().relative_to(root)
        except ValueError:
            raise GitError('Path escapes repository: ' + name)
        for part in (candidate, *candidate.parents):
            if part == root:
                break
            if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
                raise GitError('Linked paths require manual review: ' + name)
            if part.is_dir() and (part / '.git').exists():
                raise GitError('Checkpoint nested repositories separately: ' + name)
        parts = {p.lower() for p in relative.parts}
        basename = relative.name.lower()
        if (parts & BLOCKED_PARTS or basename in PRIVATE_NAMES or basename == '.env'
                or basename.startswith('.env.') or relative.suffix.lower() in BLOCKED_SUFFIXES):
            raise GitError('Large asset or private path is outside checkpoint scope: ' + name)
        if candidate.is_dir():
            raise GitError('Select individual files, not directories: ' + name)
        if candidate.exists():
            if not candidate.is_file() or candidate.stat().st_size > MAX_BYTES:
                raise GitError('Not a small regular file: ' + name)
            data = candidate.read_bytes()
            if b'\0' in data:
                raise GitError('Binary files require separate asset management: ' + name)
            if re.search(br'(?m)^-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----\r?$', data):
                raise GitError('Private key content detected: ' + name)
        elif git(root, 'ls-files', '--error-unmatch', '--', relative.as_posix(), check=False).returncode:
            raise GitError('File does not exist and is not a tracked deletion: ' + name)
        selected.append(relative.as_posix())
    if not selected:
        raise GitError('Select at least one file.')
    return list(dict.fromkeys(selected))


def checkpoint(root, message, files):
    root = repository(root)
    if not message.strip():
        raise GitError('A meaningful commit message is required.')
    with lock(root):
        if git(root, 'diff', '--cached', '--quiet', check=False).returncode:
            raise GitError('Index already contains staged changes; preserve them and resolve ownership first.')
        selected = selected_files(root, files)
        # Do not invent an author or change global/repository identity configuration.
        git(root, 'var', 'GIT_AUTHOR_IDENT')
        git(root, 'var', 'GIT_COMMITTER_IDENT')
        git(root, 'add', '-A', '--', *selected)
        if git(root, 'diff', '--cached', '--quiet', check=False).returncode == 0:
            return {'status': 'unchanged', 'root': str(root)}
        try:
            git(root, 'commit', '--only', '-m', message, '--', *selected)
        except GitError as exc:
            raise GitError('Commit failed; selected changes may remain staged. Do not reset unrelated work. ' + str(exc))
        return {'status': 'committed', 'commit': git(root, 'rev-parse', 'HEAD').stdout.strip(),
                'files': selected, 'root': str(root)}


def status(root):
    root = repository(root)
    head = git(root, 'rev-parse', '--verify', 'HEAD', check=False)
    return {'root': str(root), 'commit': head.stdout.strip() if head.returncode == 0 else None,
            'changes': git(root, 'status', '--short').stdout, 'remote_operation': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'status', 'checkpoint'):
        child = sub.add_parser(command)
        child.add_argument('--root', required=True, type=Path)
        if command == 'checkpoint':
            child.add_argument('--message', required=True)
            child.add_argument('--files', nargs='+', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'init':
            result = initialize(args.root)
        elif args.command == 'status':
            result = status(args.root)
        else:
            result = checkpoint(args.root, args.message, args.files)
        print(json.dumps(result, ensure_ascii=False))
    except (GitError, OSError, UnicodeError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
