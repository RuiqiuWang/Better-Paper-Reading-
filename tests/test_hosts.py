import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills' / 'read-main'))
import host_config
spec = importlib.util.spec_from_file_location('paper_installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class HostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {'CODEX_HOME': str(self.home / '.codex'), 'CLAUDE_CONFIG_DIR': str(self.home / '.claude')})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_both_targets_and_repeat_install_backup(self):
        targets = installer.install('both', home=self.home)
        self.assertEqual([host for host, _ in targets], ['codex', 'claude'])
        for host, folder in targets:
            self.assertEqual(json.loads((folder / 'read-main' / 'host.json').read_text())['host'], host)
            for name in installer.SKILLS:
                self.assertTrue((folder / name / 'SKILL.md').exists())
            result = subprocess.run([sys.executable, str(folder / 'read-main' / 'host_config.py')], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)['host'], host)
        codex_dir = targets[0][1]
        (codex_dir / 'read' / 'SKILL.md').write_text('customized prior skill')
        installer.install('both', home=self.home)
        backups = list((codex_dir.parent / 'paper-reading-backups').glob('*/read/SKILL.md'))
        self.assertTrue(any(p.read_text() == 'customized prior skill' for p in backups))

    def test_legacy_upgrade_and_dry_run(self):
        legacy = self.home / '.codex' / 'skills' / 'read'
        legacy.mkdir(parents=True)
        (legacy / 'SKILL.md').write_text('legacy')
        targets = installer.install('codex', home=self.home, dry_run=True)
        self.assertEqual(targets[0][1], legacy.parent)
        self.assertFalse((legacy.parent / 'read-main').exists())
        self.assertFalse((self.home / '.agents').exists())

    def test_research_only_preserves_reading_and_configuration(self):
        folder = self.home / '.codex' / 'skills'
        (folder / 'read-main').mkdir(parents=True)
        (folder / 'read-main' / 'SKILL.md').write_text('personal reading skill')
        host_file = folder / 'read-main' / 'host.json'
        host_file.write_text('{"host":"codex","custom":true}')
        config = self.home / '.codex' / 'paper_reading_config.json'
        config.write_text('{"store_dir":"personal-notes"}')
        targets = installer.install('codex', home=self.home, profile='research')
        self.assertEqual(targets[0][1], folder)
        self.assertEqual(host_file.read_text(), '{"host":"codex","custom":true}')
        self.assertEqual((folder / 'read-main' / 'SKILL.md').read_text(), 'personal reading skill')
        self.assertEqual(config.read_text(), '{"store_dir":"personal-notes"}')
        self.assertTrue((folder / 'research-manage' / 'references' / 'documents.md').exists())
        helper = folder / 'research-manage' / 'scripts' / 'local_git.py'
        result = subprocess.run([sys.executable, str(helper), '--help'], capture_output=True, text=True, check=True)
        self.assertIn('checkpoint', result.stdout)
        self.assertFalse((folder / 'read').exists())

    def test_research_clean_install_both_and_upgrade_backup(self):
        targets = installer.install('both', home=self.home, profile='research')
        for _, folder in targets:
            self.assertTrue((folder / 'research-manage' / 'SKILL.md').exists())
            for source in (ROOT / 'skills' / 'research-evaluate').rglob('*'):
                if source.is_file():
                    installed = folder / 'research-evaluate' / source.relative_to(ROOT / 'skills' / 'research-evaluate')
                    self.assertEqual(installed.read_bytes(), source.read_bytes())
            self.assertFalse((folder / 'read-main').exists())
        codex = targets[0][1]
        (codex / 'research-manage' / 'SKILL.md').write_text('custom research instructions')
        installer.install('codex', home=self.home, profile='research')
        backups = list((codex.parent / 'paper-reading-backups').glob('*/research-manage/SKILL.md'))
        self.assertTrue(any(p.read_text() == 'custom research instructions' for p in backups))

    def test_all_profile_and_research_dry_run(self):
        installer.install('both', home=self.home, profile='research', dry_run=True)
        self.assertFalse((self.home / '.agents').exists())
        self.assertFalse((self.home / '.claude').exists())
        targets = installer.install('both', home=self.home, profile='all')
        for host, folder in targets:
            self.assertTrue((folder / 'research-manage' / 'SKILL.md').exists())
            self.assertEqual(json.loads((folder / 'read-main' / 'host.json').read_text())['host'], host)

    def test_profiles_do_not_split_existing_install_and_reject_unknown(self):
        installer.install('codex', home=self.home, profile='research')
        targets = installer.install('codex', home=self.home)
        self.assertEqual(targets[0][1], self.home / '.agents' / 'skills')
        self.assertFalse((self.home / '.codex' / 'skills').exists())
        with self.assertRaises(ValueError):
            installer.install('codex', home=self.home, profile='typo')

    def test_preferences_are_isolated_and_preserved(self):
        old = self.home / 'old-notes'
        path, data = host_config.update('codex', store=str(old), language='english')
        data.update(dashboard_url='http://127.0.0.1:8898', custom={'keep': True})
        path.write_text(json.dumps(data))
        _, updated = host_config.update('codex', language='chinese')
        self.assertEqual(updated['dashboard_url'], data['dashboard_url'])
        _, moved = host_config.update('codex', store=str(self.home / 'new-notes'))
        self.assertNotIn('dashboard_url', moved)
        self.assertEqual(moved['custom'], {'keep': True})
        self.assertTrue(old.is_dir())
        self.assertEqual(host_config.load('claude')[1], {})

    def test_catalog_rejects_path_escape_and_duplicate_entries(self):
        catalog = self.home / 'catalog.json'
        for bad in ({'reading': ['../read'], 'research': ['research-manage']},
                    {'reading': ['read'], 'research': ['read']},
                    {'reading': [], 'research': ['research-manage']}):
            catalog.write_text(json.dumps(bad), encoding='utf-8')
            with self.assertRaises(ValueError):
                installer.load_catalog(catalog)

    def test_catalog_includes_every_bundled_skill(self):
        bundled = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}
        self.assertEqual(set(installer.PROFILES['all']), bundled)

    def test_malformed_config_is_not_reset(self):
        path = host_config.config_root('codex') / 'paper_reading_config.json'
        path.parent.mkdir(parents=True)
        path.write_text('{broken')
        with self.assertRaises(ValueError):
            host_config.update('codex', language='english')
        self.assertEqual(path.read_text(), '{broken')

    def test_credentials_use_explicit_host_without_printing_secret(self):
        env = dict(os.environ, OPENREVIEW_USERNAME='fixture@example.invalid', OPENREVIEW_PASSWORD='fixture-only-secret')
        result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'skills/read-search/save_credentials.py'), '--host', 'codex'], env=env, capture_output=True, text=True, encoding='utf-8', check=True)
        self.assertNotIn(env['OPENREVIEW_PASSWORD'], result.stdout + result.stderr)
        self.assertTrue((host_config.config_root('codex') / 'openreview_credentials.json').exists())
        self.assertFalse((host_config.config_root('claude') / 'openreview_credentials.json').exists())
