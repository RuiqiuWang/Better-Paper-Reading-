import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills' / 'read-main'))
import followup
from library import read_index

HTML = '<!doctype html><html><head><title>Paper</title><script>const x="unchanged";</script></head><body><h2 id="method">Method</h2><p id="depth">Depth and disparity are inversely related.</p><p id="formal">Formula <em>d=fB/Z</em>, with positive Z.</p><img src="_cache/figure.png"></body></html>'


def request(source, **kwargs):
    return dict(expected_sha256=hashlib.sha256(source.encode()).hexdigest(), **kwargs)


class FollowupTests(unittest.TestCase):
    def comment(self, source=HTML, **kwargs):
        opts = dict(action='comment', question='Why?', answer='Explanation', anchor_text='Depth and disparity')
        opts.update(kwargs)
        return followup.transform(source, request(source, **opts), 'session-1')

    def test_numbering_global_and_continuation_survive_reload(self):
        source, state = self.comment()
        source, state = self.comment(source, thread='global')
        source, state = self.comment(source, thread='1', question='Then what?')
        source, state = self.comment(source, anchor_id='formal')
        body, restored = followup.unpack(source)
        self.assertEqual(restored, state)
        self.assertEqual([t['id'] for t in state['threads']], ['1', 'global', '2'])
        self.assertEqual(len(state['threads'][0]['messages']), 2)
        self.assertEqual(state['selected'], '2')
        self.assertEqual(body.count('data-pr-open="1"'), 1)
        self.assertEqual(body.count('data-pr-open="2"'), 1)
        self.assertIn('<em>d=fB/Z</em>', body)
        self.assertIn('<script>const x="unchanged";</script>', body)
        self.assertEqual(source.count(followup.START), 1)

    def test_rewrite_preserves_comments_and_refuses_anchor_loss(self):
        source, state = self.comment()
        new, state2 = followup.transform(source, request(source, action='rewrite', old_html='are inversely related.', new_html='are inversely related: doubling depth halves disparity.'), 'session-1')
        self.assertEqual(state['threads'], state2['threads'])
        with self.assertRaisesRegex(ValueError, 'anchor'):
            followup.transform(new, request(new, action='rewrite', old_html='id="pr-anchor-1"', new_html='id="lost"'), 'session-1')

    def test_stale_or_ambiguous_requests_do_not_apply(self):
        with self.assertRaisesRegex(ValueError, 'changed'):
            followup.transform(HTML + ' ', request(HTML, action='rewrite', old_html='Method', new_html='New method'), 's')
        with self.assertRaisesRegex(ValueError, 'match once'):
            self.comment(HTML.replace('Depth and disparity', 'Depth and disparity Depth and disparity'))
        with self.assertRaisesRegex(ValueError, 'Unknown thread'):
            self.comment(thread='99')
        with self.assertRaisesRegex(ValueError, 'unique'):
            followup.transform(HTML, request(HTML, action='rewrite', old_html='MISSING', new_html='New'), 's')

    def test_script_payload_is_inert_and_no_reanchoring_same_text(self):
        source, state = self.comment(question='</script><script>alert(1)</script>', answer='<img src=x onerror=alert(1)>')
        self.assertNotIn('</script><script>alert(1)', source)
        self.assertEqual(followup.unpack(source)[1]['threads'][0]['messages'][0]['answer'], '<img src=x onerror=alert(1)>')
        with self.assertRaisesRegex(ValueError, 'match once'):
            self.comment(source)

    def test_backup_and_same_session_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            (store / 'note.html').write_bytes(HTML.encode())
            entry = dict(id='s', title='Paper', path='note.html', type='read', project='p', pinned=True)
            (store / '_index.json').write_text(json.dumps({'entries': [entry]}))
            updated, state, backup = followup.apply(store, 's', request(HTML, action='comment', thread='global', question='Overall?', answer='Overall explanation.'))
            self.assertEqual(backup.read_bytes(), HTML.encode())
            self.assertEqual(len(read_index(store)['entries']), 1)
            self.assertEqual(updated['project'], 'p')
            self.assertTrue(updated['pinned'])
            self.assertTrue((store / 'index.html').exists())
            self.assertEqual(state['session'], 's')


if __name__ == '__main__':
    unittest.main()
