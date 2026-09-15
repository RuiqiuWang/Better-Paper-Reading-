(() => {
  'use strict';
  let data = window.PAPER_READING_DATA;
  const $ = id => document.getElementById(id);
  const key = 'paper-reading:v1:' + data.library_id;
  const fresh = () => ({version: 1, projects: [], sessions: {}, drafts: [], collapsed: [], selected: null, prefix: '/'});
  let state = fresh(), query = '', archivedView = false, mainSignature = '', toastTimer, composingProject = null;
  const own = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop);
  const validId = value => typeof value === 'string' && value.length > 0 && value.length <= 200 && !['__proto__', 'prototype', 'constructor'].includes(value);
  const text = value => typeof value === 'string' ? value.slice(0, 2000) : '';

  function validate(raw) {
    if (!raw || raw.version !== 1 || !Array.isArray(raw.projects) || !Array.isArray(raw.drafts) || !raw.sessions || typeof raw.sessions !== 'object') throw Error('备份格式不正确');
    const clean = fresh(), ids = new Set();
    for (const p of raw.projects) {
      if (!p || !validId(p.id) || !text(p.name).trim() || ids.has(p.id)) throw Error('项目数据不正确');
      ids.add(p.id); clean.projects.push({id: p.id, name: text(p.name).trim()});
    }
    for (const [id, m] of Object.entries(raw.sessions)) {
      if (!validId(id) || !m || typeof m !== 'object') continue;
      clean.sessions[id] = {pinned: m.pinned === true, archived: m.archived === true, project: ids.has(m.project) ? m.project : ''};
      if (typeof m.title === 'string' && m.title.trim()) clean.sessions[id].title = text(m.title).trim();
    }
    const drafts = new Set();
    for (const d of raw.drafts) {
      if (!d || !validId(d.id) || drafts.has(d.id) || !['read', 'search'].includes(d.type) || !text(d.request).trim()) throw Error('会话草稿数据不正确');
      drafts.add(d.id);
      clean.drafts.push({id: d.id, title: text(d.title), request: text(d.request), type: d.type, date: text(d.date), draft: true});
    }
    clean.collapsed = Array.isArray(raw.collapsed) ? raw.collapsed.filter(id => ids.has(id)) : [];
    clean.selected = validId(raw.selected) ? raw.selected : null;
    clean.prefix = raw.prefix === '$' ? '$' : '/';
    return clean;
  }
  function storageWarning(message) { $('storage-warning').textContent = message; $('storage-warning').hidden = false; }
  try { const saved = localStorage.getItem(key); if (saved) state = validate(JSON.parse(saved)); }
  catch (_) { storageWarning('无法读取浏览器中的分类设置。现有笔记仍可阅读；请使用“本地阅读库”导出本次整理。'); }

  function save() {
    try { localStorage.setItem(key, JSON.stringify(state)); }
    catch (_) { storageWarning('浏览器未能保存设置。请保持页面打开，并在“本地阅读库”中导出备份。'); }
  }
  function h(tag, attrs = {}, ...children) {
    const el = document.createElement(tag);
    for (const [name, value] of Object.entries(attrs)) {
      if (name.startsWith('on')) el.addEventListener(name.slice(2), value);
      else if (name === 'class') el.className = value;
      else el.setAttribute(name, value);
    }
    for (const child of children.flat()) if (child != null) el.append(child instanceof Node ? child : document.createTextNode(String(child)));
    return el;
  }
  function icon(name, cls = '') {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('aria-hidden', 'true');
    if (cls) svg.setAttribute('class', cls);
    const use = document.createElementNS(svg.namespaceURI, 'use'); use.setAttribute('href', '#i-' + name); svg.append(use); return svg;
  }
  const uid = () => crypto.randomUUID ? crypto.randomUUID() : Array.from(crypto.getRandomValues(new Uint8Array(16)), n => n.toString(16).padStart(2, '0')).join('');
  const meta = id => own(state.sessions, id) ? state.sessions[id] : {};
  function change(id, patch) { state.sessions[id] = {...meta(id), ...patch}; save(); render(); }
  const label = e => meta(e.id).title || e.title;
  const project = id => state.projects.find(p => p.id === id);
  const typeName = type => ({read: '论文笔记', search: '论文检索', search_topic: '主题图谱'})[type] || '阅读记录';
  function entries() {
    const real = new Set(data.entries.map(e => e.id));
    const time = e => Date.parse(String(e.date || '').replace(' ', 'T')) || 0;
    return [...data.entries, ...state.drafts.filter(e => !real.has(e.id))].sort((a, b) => time(b) - time(a) || b.id.localeCompare(a.id));
  }
  function toast(message) { clearTimeout(toastTimer); $('toast').textContent = message; $('toast').hidden = false; toastTimer = setTimeout(() => $('toast').hidden = true, 3500); }
  function closeMenu() { $('menu').hidden = true; }
  function menu(anchor, actions) {
    const el = $('menu'); el.replaceChildren();
    actions.forEach(([title, action, danger]) => el.append(h('button', {type: 'button', role: 'menuitem', class: danger ? 'danger' : '', onclick: () => {closeMenu(); action();}}, title)));
    el.hidden = false;
    const r = anchor.getBoundingClientRect();
    el.style.left = Math.max(8, Math.min(r.right - 15, innerWidth - el.offsetWidth - 8)) + 'px';
    el.style.top = Math.max(8, Math.min(r.bottom + 5, innerHeight - el.offsetHeight - 8)) + 'px';
    el.querySelector('button')?.focus();
  }
  document.addEventListener('click', e => { if (!$('menu').contains(e.target) && !e.target.closest('[data-menu]')) closeMenu(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeMenu();
    if (!$('menu').hidden && ['ArrowDown', 'ArrowUp'].includes(e.key)) {
      e.preventDefault(); const items = [...$('menu').querySelectorAll('button')], i = items.indexOf(document.activeElement);
      items[(i + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length].focus();
    }
  });
  function modal(title, nodes, onSave, submit = '保存') {
    $('dialog-title').textContent = title; $('dialog-body').replaceChildren(...nodes); $('dialog-submit').textContent = submit;
    $('dialog-form').onsubmit = event => {
      event.preventDefault();
      try { onSave(); $('dialog').close(); }
      catch (error) {
        $('dialog-body').querySelector('.error')?.remove();
        $('dialog-body').append(h('div', {class: 'error', role: 'alert'}, error.message));
      }
    };
    $('dialog').showModal();
    const field = $('dialog-body').querySelector('input,select'); if (field) {field.focus(); if (field.select) field.select();}
  }
  $('dialog-cancel').onclick = () => $('dialog').close();
  function nameModal(title, initial, action) {
    const input = h('input', {value: initial, required: '', maxlength: '120', 'aria-label': title});
    modal(title, [input], () => {const name = input.value.trim(); if (!name) throw Error('请输入名称'); action(name);});
  }
  function createProject() {
    nameModal('新建项目', '', name => {
      if (state.projects.some(p => p.name.toLocaleLowerCase() === name.toLocaleLowerCase())) throw Error('已经有同名项目');
      const p = {id: uid(), name}; state.projects.push(p); save(); render(); toast('项目已创建');
    });
  }
  function moveSession(e) {
    const select = h('select', {'aria-label': '选择项目'}, h('option', {value: ''}, '未分类'), state.projects.map(p => h('option', {value: p.id}, p.name)));
    select.value = meta(e.id).project || '';
    modal('移动到项目', [select], () => {change(e.id, {project: select.value}); toast('已移动会话');});
  }
  function sessionMenu(e, anchor) {
    const m = meta(e.id);
    menu(anchor, [
      [m.pinned ? '取消置顶' : '置顶会话', () => change(e.id, {pinned: !m.pinned})],
      ['重命名', () => nameModal('重命名会话', label(e), title => change(e.id, {title}))],
      ['移动到项目', () => moveSession(e)],
      [m.archived ? '恢复会话' : '归档会话', () => { change(e.id, {archived: !m.archived}); toast(m.archived ? '会话已恢复' : '已归档，可在左下角恢复'); }]
    ]);
  }
  function projectMenu(p, anchor) {
    menu(anchor, [
      ['在此项目新建会话', () => newProjectSession(p.id)],
      ['重命名项目', () => nameModal('重命名项目', p.name, name => {
        if (state.projects.some(other => other.id !== p.id && other.name.toLocaleLowerCase() === name.toLocaleLowerCase())) throw Error('已经有同名项目');
        p.name = name; save(); render();
      })],
      ['删除项目', () => modal('删除项目“' + p.name + '”？', [h('p', {}, '项目中的会话将回到未分类，笔记文件会保留。')], () => {
        state.projects = state.projects.filter(other => other.id !== p.id);
        state.collapsed = state.collapsed.filter(id => id !== p.id);
        Object.values(state.sessions).forEach(m => { if (m.project === p.id) m.project = ''; }); save(); render();
      }, '删除项目'), true]
    ]);
  }
  function row(e) {
    const more = h('button', {class: 'icon-button', type: 'button', 'aria-label': '管理会话：' + label(e), 'data-menu': '', onclick: () => sessionMenu(e, more)}, icon('more'));
    const button = h('button', {class: 'entry-button', type: 'button', title: label(e) + ' · ' + typeName(e.type), onclick: () => selectSession(e.id)},
      icon(e.type === 'read' ? 'chat' : e.type === 'search' ? 'search' : 'book'), h('span', {class: 'entry-label'}, label(e)), e.draft ? h('span', {class: 'status-dot', title: '等待阅读结果'}) : null);
    if (state.selected === e.id) button.setAttribute('aria-current', 'page');
    const el = h('div', {class: 'row' + (state.selected === e.id ? ' active' : ''), draggable: 'true', 'data-session': e.id,
      ondragstart: event => {event.dataTransfer.setData('text/plain', e.id); event.dataTransfer.effectAllowed = 'move';}}, button, more);
    return el;
  }
  function heading(title, create = false) {
    return h('div', {class: 'nav-heading'}, title, create ? h('button', {class: 'icon-button', type: 'button', 'aria-label': '新建项目', title: '新建项目', onclick: createProject}, icon('plus')) : null);
  }
  function renderNav() {
    const all = entries(), nav = $('navigation');
    const visible = all.filter(e => Boolean(meta(e.id).archived) === archivedView && (!query || (label(e) + ' ' + (e.topics || []).join(' ') + ' ' + (project(meta(e.id).project)?.name || '')).toLocaleLowerCase().includes(query)));
    nav.replaceChildren();
    $('archive-count').textContent = all.filter(e => meta(e.id).archived).length || '';
    $('library-count').textContent = all.length + ' 个会话 · 阅读结果自动收录';
    if (archivedView || query) {
      nav.append(h('button', {class: 'nav-back', onclick: () => {archivedView = false; query = ''; $('search').value = ''; renderNav();}}, '← 返回全部会话'));
      nav.append(heading((archivedView ? '已归档' : '搜索结果') + ' · ' + visible.length));
      nav.append(...visible.map(row));
      if (!visible.length) nav.append(h('div', {class: 'empty-nav'}, '没有找到会话'));
      return;
    }
    const pinned = visible.filter(e => meta(e.id).pinned);
    if (pinned.length) nav.append(heading('置顶'), ...pinned.map(row));
    nav.append(heading('项目', true));
    for (const p of state.projects) {
      const items = visible.filter(e => meta(e.id).project === p.id);
      const opened = !state.collapsed.includes(p.id);
      const more = h('button', {class: 'icon-button', type: 'button', 'aria-label': '管理项目：' + p.name, 'data-menu': '', onclick: () => projectMenu(p, more)}, icon('more'));
      const group = h('div', {class: 'row project-row' + (opened ? ' open' : ''), 'data-project': p.id},
        h('button', {class: 'entry-button', type: 'button', 'aria-expanded': String(opened), onclick: () => {
          state.collapsed = opened ? [...state.collapsed, p.id] : state.collapsed.filter(id => id !== p.id); save(); renderNav();
        }}, icon('chevron', 'chevron'), icon('folder'), h('span', {class: 'entry-label'}, p.name), h('span', {class: 'count'}, items.length)), more);
      group.ondragover = event => {event.preventDefault(); group.classList.add('drag-over');};
      group.ondragleave = () => group.classList.remove('drag-over');
      group.ondrop = event => {event.preventDefault(); const id = event.dataTransfer.getData('text/plain'); if (all.some(e => e.id === id)) change(id, {project: p.id});};
      nav.append(group);
      if (opened) nav.append(h('div', {class: 'project-children'}, items.length ? items.map(row) : h('div', {class: 'empty-project'}, '将会话拖到这里，开始整理')));
    }
    if (!state.projects.length) nav.append(h('div', {class: 'empty-nav'}, '按研究方向建立项目，收好相关会话。'));
    nav.append(heading('会话'));
    const history = visible.filter(e => !meta(e.id).pinned && !project(meta(e.id).project));
    const now = new Date(); now.setHours(0, 0, 0, 0);
    let previous = '';
    for (const e of history) {
      const d = new Date((e.date || '').replace(' ', 'T'));
      const age = (now - d) / 86400000;
      const group = age < 0 ? '今天' : age < 7 ? '最近 7 天' : '更早';
      if (group !== previous) {nav.append(h('div', {class: 'date-heading'}, group)); previous = group;}
      nav.append(row(e));
    }
    if (!history.length) nav.append(h('div', {class: 'empty-nav'}, all.length ? '其余会话已收纳到项目或置顶。' : '在助手中运行 ' + state.prefix + 'read，笔记会自动加入这里。'));
  }
  function urlFor(path) { return path.split('/').map(encodeURIComponent).join('/'); }
  function command(e) {return state.prefix + (e.type === 'search' ? 'read-search' : 'read') + ' ' + e.request + ' --session ' + e.id;}
  async function copy(value) {
    try {await navigator.clipboard.writeText(value); toast('命令已复制，粘贴到助手中运行');}
    catch (_) {toast('请选中命令手动复制');}
  }
  function renderMain() {
    const e = entries().find(item => item.id === state.selected);
    const currentProject = e ? null : project(composingProject);
    const m = e ? meta(e.id) : {}, title = e ? label(e) : '阅读工作台';
    $('breadcrumb').textContent = e ? (project(m.project)?.name || typeName(e.type)) + ' / ' + title : currentProject ? currentProject.name + ' / 新建会话' : title;
    const signature = JSON.stringify(e ? [e.id, e.path, e.view_path, e.missing, e.date, e.draft, title, state.prefix] : [currentProject?.id, currentProject?.name, state.prefix]);
    if (signature === mainSignature) return;
    mainSignature = signature;
    $('welcome').hidden = Boolean(e || currentProject); $('project-session').hidden = !currentProject;
    $('reader').hidden = !e; $('open-note').hidden = true;
    $('composer-project').textContent = currentProject?.name || '';
    const reader = $('reader'); reader.replaceChildren();
    if (!e) return;
    if (e.draft) {
      const code = command(e);
      reader.append(h('div', {class: 'reader-message'}, h('div', {class: 'eyebrow'}, 'NEW READING SESSION'), h('h2', {}, title),
        h('p', {}, '会话已准备好。将下面的命令粘贴到助手中运行，生成的笔记会自动出现在这里。'),
        h('code', {tabindex: '0', 'aria-label': '阅读命令'}, code), h('button', {class: 'primary', onclick: () => copy(code)}, '复制命令'),
        h('p', {}, '左侧的项目、置顶和名称会保留。')));
    } else if (e.missing || !e.path) {
      reader.append(h('div', {class: 'reader-message'}, h('h2', {}, '暂时找不到这份笔记'), h('p', {}, '文件可能被移动或重命名。恢复文件后运行 ' + state.prefix + 'read-main 刷新目录。')));
    } else {
      const url = urlFor(e.view_path || e.path);
      reader.append(h('iframe', {src: url, title: title, sandbox: 'allow-scripts allow-popups allow-popups-to-escape-sandbox allow-downloads'}));
      $('open-note').href = url; $('open-note').hidden = false;
    }
  }
  function render() {
    renderNav(); renderMain();
    $('read-command').textContent = state.prefix + 'read 论文链接';
    const recent = entries().filter(e => !e.draft && !meta(e.id).archived).slice(0, 4);
    $('recent-sessions').replaceChildren(...(recent.length ? [h('div', {class: 'recent-heading'}, '最近阅读'), ...recent.map(e =>
      h('button', {type: 'button', class: 'recent-note', onclick: () => selectSession(e.id)}, icon('book'), h('span', {class: 'entry-label'}, label(e)), h('small', {}, typeName(e.type)), icon('arrow')))] : [h('p', {class: 'intro'}, '你的第一份阅读笔记，将出现在这里。')]));
  }
  function hashId() { try {return new URLSearchParams(location.hash.slice(1)).get('session');} catch (_) {return null;} }
  function selectSession(id) {
    composingProject = null; state.selected = id; save();
    const hash = '#session=' + encodeURIComponent(id);
    if (location.hash !== hash) location.hash = hash;
    render(); if (matchMedia('(max-width:760px)').matches) document.body.classList.add('sidebar-hidden');
  }
  function readRoute() {state.selected = hashId(); composingProject = new URLSearchParams(location.hash.slice(1)).get('project');}
  function newProjectSession(id) {
    if (!project(id)) return;
    composingProject = id; state.selected = null; save(); location.hash = 'project=' + encodeURIComponent(id);
    archivedView = false; query = ''; $('search').value = ''; render(); $('request').focus();
    if (matchMedia('(max-width:760px)').matches) document.body.classList.add('sidebar-hidden');
  }
  window.addEventListener('hashchange', () => {readRoute(); save(); render();});
  $('cancel-project-session').onclick = () => {composingProject = null; state.selected = null; save(); location.hash = 'library'; render();};
  $('search').oninput = event => {query = event.target.value.trim().toLocaleLowerCase(); renderNav();};
  $('archive-view').onclick = () => {archivedView = !archivedView; renderNav();};
  $('collapse').onclick = $('backdrop').onclick = () => document.body.classList.add('sidebar-hidden');
  $('expand').onclick = () => document.body.classList.remove('sidebar-hidden');
  $('composer').onsubmit = event => {
    event.preventDefault(); const request = $('request').value.trim().replace(/\s+/g, ' '); if (!request) return;
    if (!project(composingProject)) {toast('请从项目菜单中新建会话'); return;}
    if (/--session(?:\s|=)/.test(request)) {toast('请只填写论文链接或主题，会话编号将自动添加'); return;}
    const id = uid(), type = $('mode').value;
    state.drafts.push({id, title: request, request, type, date: new Date().toISOString(), draft: true});
    state.sessions[id] = {project: composingProject};
    $('request').value = ''; save(); selectSession(id);
  };
  function exportSettings() {
    const blob = new Blob([JSON.stringify({library_id: data.library_id, ...state}, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob), link = h('a', {href: url, download: 'paper-reading-sidebar.json'});
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  $('settings').onclick = () => {
    const prefix = h('select', {'aria-label': '助手命令格式'}, h('option', {value: '/'}, 'Claude Code · /read'), h('option', {value: '$'}, 'Codex · $read')); prefix.value = state.prefix;
    const exportButton = h('button', {type: 'button', class: 'primary', onclick: exportSettings}, '导出分类备份');
    const importButton = h('button', {type: 'button', onclick: () => {$('dialog').close(); $('import-file').click();}}, '导入备份');
    modal('本地阅读库', [h('p', {}, '笔记保存在你的文件夹中。项目、置顶、重命名和归档保存在当前浏览器；更换浏览器或清理数据前，请导出备份。'),
      h('label', {}, '新会话的命令格式'), prefix, h('p', {}, exportButton, '　', importButton)], () => {state.prefix = prefix.value; save(); renderMain();}, '完成');
  };
  $('import-file').onchange = async event => {
    const file = event.target.files[0]; if (!file) return;
    try {
      const raw = JSON.parse(await file.text()), clean = validate(raw);
      modal('导入分类备份', [h('p', {}, '将恢复 ' + clean.projects.length + ' 个项目和会话整理设置，替换当前浏览器的分类。笔记文件保持原样。')], () => {
        state = clean; save(); render(); toast('备份已恢复');
      }, '导入');
    } catch (error) {toast('导入失败：' + error.message);} finally {event.target.value = '';}
  };
  window.addEventListener('storage', event => {
    if (event.key !== key) return;
    try {state = event.newValue ? validate(JSON.parse(event.newValue)) : fresh(); render();} catch (_) {toast('另一个窗口的分类设置无法读取');}
  });
  window.paperReadingUpdate = next => {
    if (!next || next.library_id !== data.library_id || !Array.isArray(next.entries)) return;
    if (JSON.stringify(next.entries) === JSON.stringify(data.entries)) return;
    const before = new Set(data.entries.map(e => e.id)); data = next; render();
    if (next.entries.some(e => !before.has(e.id))) toast('新的阅读结果已加入侧边栏');
  };
  let refreshing = false;
  function refresh() {
    if (document.hidden || refreshing) return;
    refreshing = true;
    const script = h('script', {src: '_index.js?t=' + Date.now()});
    const finish = () => {clearTimeout(timeout); script.remove(); refreshing = false;};
    const timeout = setTimeout(finish, 4000);
    script.onload = script.onerror = finish; document.head.append(script);
  }
  if (location.hash) readRoute();
  if (matchMedia('(max-width:760px)').matches) document.body.classList.add('sidebar-hidden');
  render(); refresh(); setInterval(refresh, 5000); window.addEventListener('focus', refresh);
})();
