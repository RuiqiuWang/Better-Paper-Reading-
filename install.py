"""Install Better Research skills for Codex, Claude Code, or both (Python 3.8+)."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent


def load_catalog(path):
    catalog = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(catalog, dict) or set(catalog) != {'reading', 'research'}:
        raise ValueError('Catalog must define reading and research groups.')
    seen = set()
    for names in catalog.values():
        if not isinstance(names, list) or not names:
            raise ValueError('Skill groups must be nonempty lists.')
        for name in names:
            if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', name) or name in seen:
                raise ValueError('Invalid or duplicate skill name in catalog.')
            seen.add(name)
    return catalog


CATALOG = load_catalog(ROOT / 'skill_catalog.json')
SKILLS = tuple(CATALOG['reading'])  # Preserve installer API for reading-only clients.
RESEARCH_SKILLS = tuple(CATALOG['research'])
PROFILES = {'reading': SKILLS, 'research': RESEARCH_SKILLS, 'all': SKILLS + RESEARCH_SKILLS}


def destinations(target, home, skills_dir=None):
    if skills_dir:
        if target == 'both':
            raise ValueError('--skills-dir requires a single target.')
        return [(target, Path(skills_dir).expanduser().resolve())]
    result = []
    if target in ('codex', 'both'):
        modern = home / '.agents' / 'skills'
        legacy = Path(os.environ.get('CODEX_HOME', str(home / '.codex'))) / 'skills'
        existing = [p for p in (modern, legacy) if any((p / s / 'SKILL.md').exists() for s in PROFILES['all'])]
        if len(existing) > 1:
            raise ValueError('Better Research skills exist in both Codex skill directories. Choose one with --target codex --skills-dir PATH to avoid duplicate skills.')
        result.append(('codex', existing[0] if existing else modern))
    if target in ('claude', 'both'):
        result.append(('claude', Path(os.environ.get('CLAUDE_CONFIG_DIR', str(home / '.claude'))) / 'skills'))
    return result


def install(target, home=None, skills_dir=None, dry_run=False, profile='reading'):
    if profile not in PROFILES:
        raise ValueError('Unknown profile: ' + profile)
    selected = PROFILES[profile]
    targets = destinations(target, Path(home or Path.home()).expanduser().resolve(), skills_dir)
    for skill in selected:
        if not (ROOT / 'skills' / skill / 'SKILL.md').is_file():
            raise ValueError('Missing bundled skill: ' + skill)
    for host, directory in targets:
        directory = directory.resolve()
        if directory == (ROOT / 'skills').resolve():
            raise ValueError('Destination must not be the source skills directory.')
        for skill in selected:
            if (directory / skill).is_symlink():
                raise ValueError('Refusing to overwrite a symlinked skill: ' + str(directory / skill))
        print(host + ': ' + str(directory))
        if dry_run:
            continue
        backup = directory.parent / 'paper-reading-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        for skill in selected:
            destination = directory / skill
            if destination.exists():
                shutil.copytree(destination, backup / skill)
            shutil.copytree(ROOT / 'skills' / skill, destination, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if 'read-main' in selected:
            (directory / 'read-main' / 'host.json').write_text(json.dumps({'host': host}) + '\n', encoding='utf-8')
        print('  Installed ' + str(len(selected)) + ' skills (' + profile + '). Existing skills backed up when present: ' + str(backup))
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('codex', 'claude', 'both'), default='both')
    parser.add_argument('--skills-dir', type=Path, help='Override skill directory for one host')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--profile', choices=tuple(PROFILES), default='reading', help='reading (default), research, or all')
    args = parser.parse_args()
    install(args.target, skills_dir=args.skills_dir, dry_run=args.dry_run, profile=args.profile)


if __name__ == '__main__':
    main()
