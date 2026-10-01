import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/research-manage/scripts/local_git.py'
spec = importlib.util.spec_from_file_location('research_local_git', SCRIPT)
local_git = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_git)


class LocalGitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / 'topic'
        self.root.mkdir()
        self.env = patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull,
                                         'GIT_CONFIG_NOSYSTEM': '1'})
        self.env.start()
        local_git.initialize(self.root)
        local_git.git(self.root, 'config', 'user.name', 'Research Test')
        local_git.git(self.root, 'config', 'user.email', 'test@example.invalid')

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def write(self, name, content='research note\n'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def test_init_preserves_ignore_and_is_idempotent(self):
        ignore = self.root / '.gitignore'
        with ignore.open('a') as stream:
            stream.write('personal-rule/\n')
        before = ignore.read_bytes()
        local_git.initialize(self.root)
        self.assertEqual(ignore.read_bytes(), before)
        self.assertIsNone(local_git.status(self.root)['commit'])

    def test_explicit_checkpoint_leaves_unrelated_files_and_never_pushes(self):
        remote = self.root.parent / 'remote.git'
        subprocess.run(['git', 'init', '--bare', str(remote)], capture_output=True, check=True)
        local_git.git(self.root, 'remote', 'add', 'origin', str(remote))
        self.write('README.md')
        self.write('personal.txt', 'unrelated edits')
        result = local_git.checkpoint(self.root, 'Record topic', ['README.md'])
        self.assertEqual(result['status'], 'committed')
        self.assertEqual(local_git.git(self.root, 'show', 'HEAD:README.md').stdout, 'research note\n')
        self.assertNotIn('personal.txt', local_git.git(self.root, 'ls-files').stdout)
        self.assertEqual(local_git.git(self.root, 'remote', 'get-url', 'origin').stdout.strip(), str(remote))
        self.assertEqual(local_git.git(remote, 'for-each-ref').stdout, '')

    def test_unchanged_checkpoint_and_tracked_deletion(self):
        self.write('README.md')
        first = local_git.checkpoint(self.root, 'Add note', ['README.md'])
        result = local_git.checkpoint(self.root, 'No edit', ['README.md'])
        self.assertEqual(result['status'], 'unchanged')
        self.assertEqual(local_git.status(self.root)['commit'], first['commit'])
        (self.root / 'README.md').unlink()
        self.assertEqual(local_git.checkpoint(self.root, 'Remove note', ['README.md'])['status'], 'committed')
        self.assertEqual(local_git.git(self.root, 'ls-files', 'README.md').stdout, '')

    def test_staged_user_work_is_preserved(self):
        self.write('personal.txt')
        self.write('README.md')
        local_git.git(self.root, 'add', 'personal.txt')
        before = local_git.git(self.root, 'diff', '--cached').stdout
        with self.assertRaisesRegex(local_git.GitError, 'staged'):
            local_git.checkpoint(self.root, 'Record note', ['README.md'])
        self.assertEqual(local_git.git(self.root, 'diff', '--cached').stdout, before)

    def test_paths_assets_and_private_content_are_rejected_before_staging(self):
        self.write('README.md')
        self.write('secret.txt', '-----BEGIN OPENSSH PRIVATE KEY-----\nfixture\n')
        self.write('.env', 'TOKEN=fixture')
        self.write('weights.pt')
        (self.root / 'binary.bin').write_bytes(b'abc\x00def')
        (self.root / 'huge.txt').write_bytes(b'a' * (local_git.MAX_BYTES + 1))
        for name in ('../outside.md', '.', '.env', 'weights.pt', 'secret.txt',
                     'binary.bin', 'huge.txt', 'missing.md'):
            with self.subTest(name=name), self.assertRaises(local_git.GitError):
                local_git.checkpoint(self.root, 'Reject', ['README.md', name])
            self.assertEqual(local_git.git(self.root, 'diff', '--cached', '--name-only').stdout, '')

    def test_no_accidental_parent_or_nested_repository(self):
        child = self.root / 'baselines' / 'method'
        child.mkdir(parents=True)
        with self.assertRaisesRegex(local_git.GitError, 'another repository'):
            local_git.initialize(child)
        subprocess.run(['git', 'init', str(child)], capture_output=True, check=True)
        self.write('baselines/method/model.py')
        with self.assertRaisesRegex(local_git.GitError, 'nested'):
            local_git.checkpoint(self.root, 'Wrong boundary', ['baselines/method/model.py'])

    def test_literal_path_with_spaces_and_brackets_and_unicode_cli(self):
        self.write('results [final].md', 'PSNR 21.4，部分结果\n')
        result = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), 'checkpoint',
                                 '--root', str(self.root), '--message', '记录结果',
                                 '--files', 'results [final].md'],
                                capture_output=True, encoding='utf-8', check=True)
        self.assertIn('committed', result.stdout)
        self.assertIn('21.4', local_git.git(self.root, 'show', 'HEAD:results [final].md').stdout)

    def test_checkpoint_failure_preserves_selected_changes(self):
        self.write('README.md')
        original = local_git.git

        def fail_commit(root, *args, **kwargs):
            if args and args[0] == 'commit':
                raise local_git.GitError('fixture commit failure')
            return original(root, *args, **kwargs)

        with patch.object(local_git, 'git', side_effect=fail_commit):
            with self.assertRaisesRegex(local_git.GitError, 'may remain staged'):
                local_git.checkpoint(self.root, 'Try', ['README.md'])
        self.assertEqual(local_git.git(self.root, 'diff', '--cached', '--name-only').stdout.strip(), 'README.md')

    def test_existing_helper_lock_is_not_removed(self):
        lock = self.root / '.git' / 'research-manage.lock'
        lock.write_text('another operation')
        self.write('README.md')
        with self.assertRaisesRegex(local_git.GitError, 'active'):
            local_git.checkpoint(self.root, 'Try', ['README.md'])
        self.assertEqual(lock.read_text(), 'another operation')

    def test_helper_source_can_be_checkpointed(self):
        (self.root / 'local_git.py').write_bytes(SCRIPT.read_bytes())
        self.assertEqual(local_git.checkpoint(self.root, 'Add helper', ['local_git.py'])['status'], 'committed')

    def test_missing_identity_does_not_stage_or_invent_author(self):
        local_git.git(self.root, 'config', '--unset', 'user.name')
        local_git.git(self.root, 'config', '--unset', 'user.email')
        local_git.git(self.root, 'config', 'user.useConfigOnly', 'true')
        self.write('README.md')
        with self.assertRaises(local_git.GitError):
            local_git.checkpoint(self.root, 'Missing identity', ['README.md'])
        self.assertEqual(local_git.git(self.root, 'diff', '--cached', '--name-only').stdout, '')
        self.assertIsNone(local_git.status(self.root)['commit'])
