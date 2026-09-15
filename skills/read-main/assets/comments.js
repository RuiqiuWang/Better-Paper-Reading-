(() => {
  'use strict';
  if (document.getElementById('pr-panel')) return;
  const data = JSON.parse(document.getElementById('pr-comment-data').textContent);
  const el = (tag, text, attrs = {}) => {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    return n;
  };
  let selected = data.selected || 'global';
  let pendingCommand = '';
  const hash = new URLSearchParams(location.hash.slice(1)).get('pr-comment');
  if (hash === 'global' || data.threads.some(t => t.id === hash)) selected = hash;
  const toggle = el('button', '收起批注', { id: 'pr-toggle', type: 'button', 'aria-controls': 'pr-panel', 'aria-expanded': 'true' });
  const panel = el('aside', undefined, { id: 'pr-panel', 'aria-label': '论文追问与批注' });
  const header = el('header'); header.append(el('h2', '追问与批注'));
  const tabs = el('nav', undefined, { id: 'pr-tabs', role: 'tablist', 'aria-label': '批注线程' });
  const messages = el('div', undefined, { id: 'pr-messages', role: 'tabpanel' });
  const compose = el('div', undefined, { id: 'pr-compose' });
  const label = el('label', '继续追问当前批注', { for: 'pr-followup' });
  const question = el('textarea', undefined, { id: 'pr-followup', placeholder: '输入疑惑，复制指令到阅读任务中发送' });
  const copy = el('button', '复制追问指令', { type: 'button' });
  const host = el('select', undefined, {'aria-label':'追问指令格式'});
  host.append(el('option', 'Codex', {value:'codex'}), el('option', 'Claude Code', {value:'claude'}));
  host.value = data.host === 'codex' ? 'codex' : 'claude';
  const help = el('p', '复制后回到阅读任务发送；回答将保存到当前批注。');
  compose.append(label, question, host, copy, help); panel.append(header, tabs, messages, compose);
  document.body.append(panel, toggle);
  function visible(open) {
    panel.hidden = !open;
    document.documentElement.classList.toggle('pr-comments-open', open);
    toggle.textContent = open ? '收起批注' : '批注';
    toggle.setAttribute('aria-expanded', String(open));
  }
  function answerText(node, text) {
    const re = /https?:\/\/[^\s<>]+/g; let at = 0;
    for (const match of text.matchAll(re)) {
      node.append(document.createTextNode(text.slice(at, match.index)));
      node.append(el('a', match[0], { href: match[0], target: '_blank', rel: 'noopener noreferrer' }));
      at = match.index + match[0].length;
    }
    node.append(document.createTextNode(text.slice(at)));
  }
  function render(id, scroll = false) {
    selected = id; tabs.replaceChildren(); messages.replaceChildren();
    const numbered = data.threads.filter(t => t.id !== 'global');
    [{id:'global', label:'全局'}, ...numbered].forEach(t => {
      const button = el('button', t.id === 'global' ? '全局' : t.id, {
        type:'button', role:'tab', 'aria-selected':String(t.id === selected),
        title:t.label, id:'pr-tab-' + t.id, 'aria-controls':'pr-messages'
      });
      button.addEventListener('click', () => render(t.id, true)); tabs.append(button);
    });
    messages.setAttribute('aria-labelledby', 'pr-tab-' + selected);
    const thread = data.threads.find(t => t.id === selected);
    messages.append(el('h3', selected === 'global' ? '整篇论文 · 全局问题' : '批注 ' + selected + ' · ' + thread.label));
    if (!thread || !thread.messages.length) messages.append(el('p', '这里保存有关整篇论文的额外问题。'));
    for (const item of thread?.messages || []) {
      const card = el('article');
      const answer = el('div', undefined, {class:'pr-answer'}); answerText(answer, item.answer);
      card.append(el('p', item.question, {class:'pr-question'}), answer, el('time', item.created));
      messages.append(card);
    }
    if (window.MathJax?.typesetPromise) window.MathJax.typesetPromise([messages]).catch(() => {});
    visible(true);
    if (scroll && thread?.anchor_id) document.getElementById(thread.anchor_id)?.scrollIntoView({behavior:'smooth', block:'center'});
    question.value = ''; pendingCommand = ''; help.textContent = '复制后回到阅读任务发送；回答将保存到当前批注。';
  }
  toggle.addEventListener('click', () => visible(panel.hidden));
  document.addEventListener('click', event => {
    const badge = event.target.closest('[data-pr-open]');
    if (badge && data.threads.some(t => t.id === badge.dataset.prOpen)) render(badge.dataset.prOpen, true);
  });
  panel.addEventListener('keydown', event => { if (event.key === 'Escape') {visible(false); toggle.focus();} });
  host.addEventListener('change', () => {
    if (pendingCommand && question.value === pendingCommand) {
      question.value = question.value.replace(/^(?:\/read-comment|\$read-comment)/, host.value === 'codex' ? '$read-comment' : '/read-comment');
      pendingCommand = question.value;
    }
  });
  copy.addEventListener('click', async () => {
    if (!question.value.trim()) { question.focus(); return; }
    const prefix = host.value === 'codex' ? '$read-comment' : '/read-comment';
    const command = question.value === pendingCommand ? pendingCommand : prefix + ' --session ' + data.session + ' --comment ' + selected + ' ' + question.value.trim();
    try { await navigator.clipboard.writeText(command); help.textContent = '已复制，请回到阅读任务粘贴发送。'; }
    catch { pendingCommand = command; question.value = command; question.focus(); question.select(); help.textContent = '请复制已选中的指令，回到阅读任务发送。'; }
  });
  render(selected);
})();
