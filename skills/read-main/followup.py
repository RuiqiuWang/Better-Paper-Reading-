"""Guarded in-place paper rewrites and portable, source-anchored comment threads."""
import argparse
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, urlparse

from library import ASSETS, atomic_write, library_lock, note_path, read_index, save_and_render, script_json

START = '<!-- PAPER-READING-FOLLOWUPS:START -->'
END = '<!-- PAPER-READING-FOLLOWUPS:END -->'
DATA = '<script type="application/json" id="pr-comment-data">'


class Locations(HTMLParser):
    """Record source offsets without reserializing formulas, scripts or markup."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.stack, self.elements, self.texts = source, [], [], []
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.feed(source)

    def source_offset(self):
        row, col = self.getpos()
        return self.lines[row - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            return
        start = self.source_offset()
        self.stack.append({'tag': tag, 'attrs': dict(attrs), 'start': start,
                           'inner': start + len(self.get_starttag_text())})

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1]['tag'] == tag:
            item = self.stack.pop()
            item['close'] = self.source_offset()
            item['end'] = self.source.index('>', item['close']) + 1
            self.elements.append(item)

    def handle_data(self, data):
        if self.stack and not any(x['tag'] in {'script', 'style', 'textarea', 'button', 'a', 'code', 'pre'} or
                                  'data-pr-comment' in x['attrs'] for x in self.stack):
            self.texts.append((self.source_offset(), data))


def unpack(source):
    if START not in source and END not in source:
        return source, {'version': 1, 'next_id': 1, 'selected': 'global', 'threads': []}
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('Malformed follow-up region; restore the last valid HTML before editing.')
    a, b = source.index(START), source.index(END) + len(END)
    region = source[a:b]
    if DATA not in region:
        raise ValueError('Missing comment data.')
    payload = region.split(DATA, 1)[1].split('</script>', 1)[0]
    state = json.loads(payload)
    if state.get('version') != 1 or not isinstance(state.get('threads'), list):
        raise ValueError('Unsupported comment data.')
    return source[:a] + source[b:], state


def pack(source, state):
    closes = list(re.finditer(r'</body\s*>', source, re.I))
    if len(closes) != 1:
        raise ValueError('Expected one closing body tag in the existing HTML.')
    css = (ASSETS / 'comments.css').read_text(encoding='utf-8')
    js = (ASSETS / 'comments.js').read_text(encoding='utf-8')
    region = START + '<style>' + css + '</style>' + DATA + script_json(state) + '</script><script>' + js + '</script>' + END
    at = closes[0].start()
    return source[:at] + region + source[at:]


def anchor(source, number, request):
    parser = Locations(source)
    badge = '<button type="button" class="pr-badge" data-pr-open="%s" aria-label="打开批注 %s">%s</button>' % (number, number, number)
    if request.get('anchor_id'):
        matches = [e for e in parser.elements if e['attrs'].get('id') == request['anchor_id']]
        if len(matches) != 1:
            raise ValueError('anchor_id must identify exactly one closed HTML element.')
        e = matches[0]
        if any(parent['start'] < e['start'] < parent['end'] and 'data-pr-comment' in parent['attrs'] for parent in parser.elements):
            raise ValueError('This passage is inside an existing thread; append to that thread instead.')
        if e['tag'] not in {'p', 'span', 'li', 'h2', 'h3', 'h4', 'div', 'section'}:
            raise ValueError('Choose a paragraph, heading, span or section anchor.')
        if 'data-pr-comment' in e['attrs'] or 'data-pr-comment=' in source[e['inner']:e['close']]:
            raise ValueError('This passage already has a thread; append to that thread instead.')
        source = source[:e['close']] + badge + source[e['close']:]
        at = e['inner'] - 1
        return source[:at] + ' data-pr-comment="%s"' % number + source[at:], request['anchor_id']
    value = request.get('anchor_text', '')
    if not isinstance(value, str) or not value.strip():
        raise ValueError('A new numbered thread needs anchor_id or unique anchor_text; use thread=global for overall questions.')
    matches = []
    for offset, data in parser.texts:
        matches.extend(offset + m.start() for m in re.finditer(re.escape(value), data))
    if len(matches) != 1:
        raise ValueError('anchor_text must match once within one plain text node; use anchor_id for formatted text or formulas.')
    at = matches[0]
    aid = 'pr-anchor-' + str(number)
    if any(e['attrs'].get('id') == aid for e in parser.elements):
        raise ValueError('Generated anchor ID already exists; choose an explicit anchor_id.')
    wrapped = '<span id="%s" data-pr-comment="%s">%s</span>' % (aid, number, value)
    return source[:at] + wrapped + badge + source[at + len(value):], aid


def transform(source, request, session):
    digest = hashlib.sha256(source.encode('utf-8')).hexdigest()
    if request.get('expected_sha256') != digest:
        raise ValueError('The HTML changed or expected_sha256 is missing. Inspect again before applying the follow-up.')
    body, state = unpack(source)
    state['session'] = session
    if request.get('host') in ('codex', 'claude'):
        state['host'] = request['host']
    action = request.get('action')
    if action == 'rewrite':
        old, new = request.get('old_html'), request.get('new_html')
        if not isinstance(old, str) or not old or not isinstance(new, str) or not new.strip() or body.count(old) != 1:
            raise ValueError('Rewrite requires a nonempty exact, unique old_html and nonempty new_html.')
        if START in new or END in new:
            raise ValueError('Do not replace the follow-up runtime.')
        body = body.replace(old, new, 1)
        elements = Locations(body).elements
        for thread in state['threads']:
            if thread.get('anchor_id'):
                matches = [e for e in elements if e['attrs'].get('id') == thread['anchor_id'] and
                           e['attrs'].get('data-pr-comment') == thread['id']]
                if len(matches) != 1 or body.count('data-pr-open="' + thread['id'] + '"') != 1:
                    raise ValueError('Rewrite would remove or duplicate a comment anchor/badge. Preserve or relocate it in new_html.')
        selected = str(request.get('select_thread', state['selected']))
        if selected != 'global' and not any(t['id'] == selected for t in state['threads']):
            raise ValueError('Unknown select_thread.')
        state['selected'] = selected
    elif action == 'comment':
        question, answer = request.get('question'), request.get('answer')
        if not all(isinstance(v, str) and v.strip() for v in (question, answer)):
            raise ValueError('Comment requires a question and a source-grounded answer (plain text, optional TeX).')
        target = str(request.get('thread', 'new'))
        if target == 'new':
            target = str(state['next_id'])
            body, aid = anchor(body, target, request)
            thread = {'id': target, 'anchor_id': aid, 'label': request.get('label', question[:48]), 'messages': []}
            state['next_id'] += 1
            state['threads'].append(thread)
        else:
            threads = [t for t in state['threads'] if t['id'] == target]
            if not threads and target == 'global':
                thread = {'id': 'global', 'label': '全局', 'messages': []}
                state['threads'].append(thread)
            elif len(threads) == 1:
                thread = threads[0]
            else:
                raise ValueError('Unknown thread; inspect existing thread IDs first.')
        thread['messages'].append({'question': question, 'answer': answer,
                                   'created': datetime.now().astimezone().isoformat(timespec='seconds')})
        state['selected'] = target
    else:
        raise ValueError('action must be rewrite or comment.')
    return pack(body, state), state


def apply(store, session, request):
    store = Path(store).resolve()
    with library_lock(store):
        index = read_index(store)
        entry = next((e for e in index['entries'] if e['id'] == session), None)
        if not entry:
            raise ValueError('Unknown session ID; no note was modified.')
        path = note_path(store, entry['path'])
        if path.suffix.lower() not in {'.html', '.htm'}:
            raise ValueError('Follow-ups require the original HTML note.')
        source = path.read_bytes().decode('utf-8')
        updated, state = transform(source, request, session)
        backup = store / '.reading-history' / hashlib.sha256(session.encode()).hexdigest()[:24] / (hashlib.sha256(source.encode()).hexdigest() + '.html')
        atomic_write(backup, source)
        original_index = json.loads(json.dumps(index))
        atomic_write(path, updated)
        entry['date'] = datetime.now().astimezone().isoformat(timespec='microseconds')
        try:
            save_and_render(store, index)
        except Exception:
            atomic_write(path, source)
            save_and_render(store, original_index)
            raise
        return entry, state, backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('store', type=Path)
    parser.add_argument('--session', required=True)
    parser.add_argument('--request', type=Path, help='UTF-8 JSON request; omit to inspect the existing note')
    parser.add_argument('--base-url', help='Verified loopback library URL used by read-main')
    parser.add_argument('--host', choices=('codex', 'claude'), help='Host used for copied follow-up commands')
    args = parser.parse_args()
    if args.base_url:
        base = urlparse(args.base_url)
        if base.scheme != 'http' or base.hostname not in ('localhost', '127.0.0.1', '::1') or base.username or base.password or base.query or base.fragment:
            parser.error('--base-url must be a loopback HTTP URL without credentials, query or fragment')
    if not args.request:
        index = read_index(args.store)
        entry = next((e for e in index['entries'] if e['id'] == args.session), None)
        if not entry:
            raise ValueError('Unknown session ID.')
        path = note_path(args.store, entry['path'])
        source = path.read_bytes().decode('utf-8')
        body, state = unpack(source)
        print(json.dumps({'entry': entry, 'file': str(path.resolve()), 'sha256': hashlib.sha256(source.encode()).hexdigest(),
                          'threads': state['threads'], 'anchors': [e['attrs']['id'] for e in Locations(body).elements if e['attrs'].get('id')]}, ensure_ascii=False, indent=2))
        return
    from host_config import host_name
    request = json.loads(args.request.read_text(encoding='utf-8-sig'))
    request['host'] = host_name(args.host)
    entry, state, backup = apply(args.store, args.session, request)
    base = args.base_url.rstrip('/') + '/' if args.base_url else args.store.resolve().as_uri() + '/'
    print('[打开阅读工作台](' + base + 'index.html#session=' + quote(args.session, safe='') + ')')
    print('[打开完整笔记](' + base + quote(entry['path'].replace('\\', '/'), safe='/') + '#pr-comment=' + state['selected'] + ')')
    print('Backup: ' + str(backup))


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
