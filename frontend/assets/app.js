const root = document.querySelector('#app');
const state = { file: null, token: '', user: null, auth: { mode: 'local', firebase: {} }, firebaseAuth: null, firebaseSdk: null };
let processingPoll = null;

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (state.token) headers.set('Authorization', `Bearer ${state.token}`);
  const response = await fetch(path, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || 'The request could not be completed.');
  return body;
}

function shell(content, active = 'projects') {
  root.innerHTML = `<div class="shell"><aside class="rail"><div class="brand">V&Eacute;RIT&Eacute;</div><div><div class="rail-label">Workspace</div><a class="nav-item ${active === 'projects' ? 'active' : ''}" href="#/dashboard">Projects</a><a class="nav-item ${active === 'settings' ? 'active' : ''}" href="#/settings">Settings</a></div><button class="new-button" id="new-project">+ New project</button>${state.user ? '<button class="link-button" id="sign-out">Sign out</button>' : ''}</aside><main class="main">${content}</main></div>`;
  document.querySelector('#new-project')?.addEventListener('click', () => navigate('#/projects/new'));
  document.querySelector('#sign-out')?.addEventListener('click', () => state.firebaseSdk.signOut(state.firebaseAuth));
}
function navigate(path) { window.location.hash = path; }

async function renderDashboard() {
  const projects = await api('/api/projects');
  const cards = projects.map(project => `<article class="panel project-card"><h2>${escapeHtml(project.title)}</h2><div class="meta">${project.script?.scenes_count || 0} scenes &middot; updated ${formatDate(project.updated_at)}</div><span class="status ${project.status === 'ready' ? 'ready' : ''}">${project.status === 'empty' ? 'Awaiting screenplay' : project.status === 'ready' ? 'Parsed script ready' : project.status}</span><button class="link-button" data-project="${project.id}" style="float:right;margin-top:14px">Open</button></article>`).join('');
  shell(`<div class="topline"><div><h1 class="page-title">Projects</h1><p class="sub">Your uploaded screenplays and their processing state.</p></div></div>${cards ? `<div class="grid">${cards}</div>` : `<div class="empty">No scripts yet. Upload one to build its scene breakdown.<br><button class="primary" id="empty-new" style="margin-top:18px">Upload a screenplay</button></div>`}`);
  document.querySelectorAll('[data-project]').forEach(button => button.addEventListener('click', () => navigate(`#/projects/${button.dataset.project}/processing`)));
  document.querySelector('#empty-new')?.addEventListener('click', () => navigate('#/projects/new'));
}

function renderNewProject() {
  shell(`<div class="form-wrap"><div class="eyebrow">New project</div><h1 class="page-title">Slot in a screenplay.</h1><p class="sub">V&eacute;rit&eacute; will parse the uploaded file into ordered scenes, dialogue, characters, props, and locations.</p><form id="upload-form"><label class="field"><span>Project title</span><input id="title" required maxlength="160" placeholder="The Night Shift"></label><label class="drop" id="drop"><input id="file" type="file" accept=".pdf,.fountain,.txt" hidden><strong>Drop a screenplay, or browse.</strong><small>PDF, Fountain, or plain text</small></label><div id="file-note"></div><div id="form-error" class="error"></div><button class="primary" type="submit">Start processing</button></form></div>`);
  const drop = document.querySelector('#drop'); const input = document.querySelector('#file');
  drop.addEventListener('click', () => input.click());
  drop.addEventListener('dragover', event => { event.preventDefault(); drop.classList.add('focus'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('focus'));
  drop.addEventListener('drop', event => { event.preventDefault(); drop.classList.remove('focus'); chooseFile(event.dataTransfer.files[0]); });
  input.addEventListener('change', () => chooseFile(input.files[0]));
  function chooseFile(file) { state.file = file; if (file) document.querySelector('#file-note').innerHTML = `<div class="file-note"><strong>${escapeHtml(file.name)}</strong><small>${formatBytes(file.size)} &middot; ready to upload</small></div>`; }
  document.querySelector('#upload-form').addEventListener('submit', upload);
}

async function upload(event) {
  event.preventDefault();
  const error = document.querySelector('#form-error');
  if (!state.file) { error.textContent = 'Choose a screenplay file before starting.'; return; }
  const title = document.querySelector('#title').value.trim();
  if (!title) { error.textContent = 'Add a project title before starting.'; return; }
  const button = event.target.querySelector('button'); button.disabled = true; button.textContent = 'Creating project...';
  try {
    const project = await api('/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title }) });
    const form = new FormData(); form.append('file', state.file);
    await uploadWithProgress(`/api/projects/${project.id}/scripts`, form, percent => { button.textContent = `Uploading ${percent}%`; });
    navigate(`#/projects/${project.id}/processing`);
  } catch (err) { button.disabled = false; button.textContent = 'Start processing'; error.textContent = err.message; }
}

function uploadWithProgress(path, form, onProgress) {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open('POST', path);
    if (state.token) request.setRequestHeader('Authorization', `Bearer ${state.token}`);
    request.upload.addEventListener('progress', event => { if (event.lengthComputable) onProgress(Math.round((event.loaded / event.total) * 100)); });
    request.addEventListener('load', () => { let body = {}; try { body = JSON.parse(request.responseText); } catch {} if (request.status >= 200 && request.status < 300) resolve(body); else reject(new Error(body.detail || 'The upload could not be completed.')); });
    request.addEventListener('error', () => reject(new Error('The upload connection failed.')));
    request.send(form);
  });
}

async function renderProcessing(id) {
  if (processingPoll) { clearTimeout(processingPoll); processingPoll = null; }
  const project = await api(`/api/projects/${id}`); const ready = project.status === 'ready'; const failed = project.status === 'error';
  shell(`<div class="topline"><div><div class="eyebrow">Script processing</div><h1 class="page-title">${escapeHtml(project.title)}</h1><p class="sub">${ready ? `${project.scenes.length} scenes parsed and ready to review.` : failed ? 'Processing stopped. Review the error and upload a corrected file.' : 'Reading the screenplay structure.'}</p></div>${ready ? '<button class="primary" id="open-scenes">Open parsed scenes</button>' : failed ? '<button class="primary" id="retry-upload">Retry upload</button>' : ''}</div><div class="processing"><section><div class="stages"><div class="stage done">Upload</div><div class="stage ${ready || failed ? 'done' : 'active'}">Parse</div><div class="stage">Review</div></div><div class="panel log">${project.processing_log.map(line => `<span class="log-line">${formatLog(line)}</span>`).join('')}</div>${failed ? `<div class="error" style="margin-top:14px">${escapeHtml(project.script?.error || 'The screenplay could not be parsed.')}</div>` : ''}</section><aside class="feed"><div class="feed-label">Processing record</div><div class="feed-item"><div class="stamp ${ready ? 'ready' : 'neutral'}">${ready ? 'PARSED' : failed ? 'ERROR' : 'READING'}</div><p class="sub" style="margin:10px 0 0">${ready ? 'Scene structure is available below. No research or citations run in this milestone.' : 'The parser records each completed step here.'}</p></div></aside></div>`);
  document.querySelector('#open-scenes')?.addEventListener('click', () => navigate(`#/projects/${id}/scenes`));
  document.querySelector('#retry-upload')?.addEventListener('click', () => navigate('#/projects/new'));
  if (!ready && !failed) processingPoll = setTimeout(() => renderProcessing(id), 500);
}

async function renderScenes(id) {
  const project = await api(`/api/projects/${id}`); const scenes = project.scenes || [];
  shell(`<div class="topline"><div><div class="eyebrow">Parsed script</div><h1 class="page-title">${escapeHtml(project.title)}</h1><p class="sub">${scenes.length} scenes extracted from ${escapeHtml(project.script?.filename || 'the uploaded screenplay')}.</p></div><button class="link-button" id="back-processing">Processing record</button></div>${scenes.length ? `<div class="scene-grid">${scenes.map(scene => `<article class="panel scene-card"><h3>Scene ${String(scene.scene_number).padStart(2, '0')} &middot; ${escapeHtml(scene.slugline)}</h3><p>${escapeHtml(scene.synopsis)}</p><div class="chips">${[...(scene.characters || []), ...(scene.props || []), ...(scene.locations || [])].map(item => `<span class="chip">${escapeHtml(item)}</span>`).join('')}</div><div class="mono" style="margin-top:14px">${scene.dialogue?.length || 0} dialogue beats &middot; ${scene.action?.length || 0} action lines</div></article>`).join('')}</div>` : '<div class="empty">No scenes were parsed from this screenplay.</div>'}`);
  document.querySelector('#back-processing')?.addEventListener('click', () => navigate(`#/projects/${id}/processing`));
}

function renderSettings() { shell(`<div class="form-wrap"><div class="eyebrow">Workspace</div><h1 class="page-title">Settings</h1><p class="sub">Authentication and persistence configuration are supplied by the deployment environment.</p><div class="panel" style="padding:20px"><div class="mono">AUTH MODE</div><p>${escapeHtml(state.auth.mode)}</p><div class="mono">STORAGE</div><p>Local development fallback or configured Cloud Storage / Firestore</p><div class="mono">PROCESSING</div><p>Deterministic screenplay structure parser in M2</p></div></div>`, 'settings'); }

function renderAuth() {
  root.innerHTML = `<div class="auth-layout"><section class="auth-brand"><div class="stamp neutral">V&Eacute;RIT&Eacute;</div><h1>Ground every scene in truth.</h1><p>Sign in to upload and structure a screenplay for production review.</p></section><section class="auth-form"><form id="auth-form"><h2 id="auth-title">Log in</h2><button type="button" class="link-button" id="google-signin">Continue with Google</button><div class="auth-divider">or</div><label class="field"><span>Email</span><input id="auth-email" type="email" required autocomplete="email"></label><label class="field"><span>Password</span><input id="auth-password" type="password" required minlength="6" autocomplete="current-password"></label><div class="error" id="auth-error"></div><button class="primary" id="auth-submit">Log in</button><button type="button" class="text-button" id="auth-toggle">Create an account instead</button></form></section></div>`;
  let signup = false;
  document.querySelector('#auth-toggle').addEventListener('click', () => {
    signup = !signup;
    document.querySelector('#auth-title').textContent = signup ? 'Create account' : 'Log in';
    document.querySelector('#auth-submit').textContent = signup ? 'Create account' : 'Log in';
    document.querySelector('#auth-toggle').textContent = signup ? 'Log in instead' : 'Create an account instead';
  });
  document.querySelector('#google-signin').addEventListener('click', async () => {
    try { await state.firebaseSdk.signInWithPopup(state.firebaseAuth, new state.firebaseSdk.GoogleAuthProvider()); }
    catch (error) { document.querySelector('#auth-error').textContent = authMessage(error); }
  });
  document.querySelector('#auth-form').addEventListener('submit', async event => {
    event.preventDefault();
    const email = document.querySelector('#auth-email').value;
    const password = document.querySelector('#auth-password').value;
    try {
      if (signup) await state.firebaseSdk.createUserWithEmailAndPassword(state.firebaseAuth, email, password);
      else await state.firebaseSdk.signInWithEmailAndPassword(state.firebaseAuth, email, password);
    } catch (error) { document.querySelector('#auth-error').textContent = authMessage(error); }
  });
}

async function configureAuth(config) {
  state.auth = config;
  if (config.mode !== 'firebase') { route(); return; }
  const [{ initializeApp }, sdk] = await Promise.all([
    import('https://www.gstatic.com/firebasejs/11.3.1/firebase-app.js'),
    import('https://www.gstatic.com/firebasejs/11.3.1/firebase-auth.js')
  ]);
  state.firebaseSdk = sdk;
  state.firebaseAuth = sdk.getAuth(initializeApp(config.firebase));
  sdk.onAuthStateChanged(state.firebaseAuth, async user => {
    state.user = user;
    state.token = user ? await user.getIdToken() : '';
    if (user) route(); else renderAuth();
  });
}

function formatLog(line) { const match = line.match(/^(\S+)\s{2}([^\-]+?)\s+->\s+(.*)$/); return match ? `<span class="log-time">${escapeHtml(match[1])}</span><span class="log-agent">${escapeHtml(match[2].trim())}</span><span style="color:#d8d3c5"> &rarr; ${escapeHtml(match[3])}</span>` : escapeHtml(line); }
function formatDate(value) { return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }); }
function formatBytes(value) { if (value < 1024) return `${value} B`; if (value < 1048576) return `${(value / 1024).toFixed(1)} KB`; return `${(value / 1048576).toFixed(1)} MB`; }
function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[char])); }
function authMessage(error) { const code = String(error?.code || ''); if (code.includes('invalid-credential')) return 'The email or password is incorrect.'; if (code.includes('email-already-in-use')) return 'That email is already in use. Log in instead.'; if (code.includes('popup-closed')) return 'Google sign-in was closed before it completed.'; return 'Sign-in could not be completed. Check your details and try again.'; }
async function route() { if (processingPoll) { clearTimeout(processingPoll); processingPoll = null; } try { const hash = window.location.hash || '#/dashboard'; if (hash === '#/dashboard' || hash === '#/') return renderDashboard(); if (hash === '#/projects/new') return renderNewProject(); if (hash === '#/settings') return renderSettings(); const processing = hash.match(/^#\/projects\/([^/]+)\/processing$/); if (processing) return renderProcessing(processing[1]); const scenes = hash.match(/^#\/projects\/([^/]+)\/scenes$/); if (scenes) return renderScenes(scenes[1]); return renderDashboard(); } catch (err) { root.innerHTML = `<main class="main"><div class="error">${escapeHtml(err.message)}</div><a class="nav-item" href="#/dashboard">Return to projects</a></main>`; } }
window.addEventListener('hashchange', route); api('/api/auth/config').then(configureAuth).catch(route);
