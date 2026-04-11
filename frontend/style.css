/* ResponseArena v4 — RL-Powered Evaluation Lab */
'use strict';

const API = window.location.origin;
let currentMode  = 'ai';
let currentQuery = null;
let scenarioLoaded = false;
let evalCount    = 0;

const $ = id => document.getElementById(id);
const el = {
  envStatus:      $('env-status'),
  taskSelect:     $('task-select'),
  modeAiBtn:      $('mode-ai-btn'),
  modeHumanBtn:   $('mode-human-btn'),
  modeHint:       $('mode-hint'),
  loadBlock:      $('load-block'),
  loadBtn:        $('load-btn'),

  // AI workspace
  aiWorkspace:    $('ai-workspace'),
  sTask:          $('s-task'),
  sDiff:          $('s-diff'),
  sTone:          $('s-tone'),
  sName:          $('s-name'),
  sQuery:         $('s-query'),
  humanTextarea:  $('human-textarea'),
  charCount:      $('char-count'),
  aiBox:          $('ai-box'),
  aiPlaceholder:  $('ai-placeholder'),
  aiThinking:     $('ai-thinking'),
  aiText:         $('ai-text'),
  evaluateBtn:    $('evaluate-btn'),
  actionHint:     $('action-hint'),

  // Human workspace
  humanWorkspace:       $('human-workspace'),
  humanQueryInput:      $('human-query-input'),
  hqCharCount:          $('hq-char-count'),
  hqTaskChip:           $('hq-task-chip'),
  aiBoxHuman:           $('ai-box-human'),
  aiPlaceholderHuman:   $('ai-placeholder-human'),
  aiThinkingHuman:      $('ai-thinking-human'),
  aiTextHuman:          $('ai-text-human'),
  humanEvaluateBtn:     $('human-evaluate-btn'),
  humanQuery: $('human-query'),

  // Stats
  statsBtn:     $('stats-btn'),
  statsPanel:   $('stats-panel'),
  statsClose:   $('stats-close'),
  statTotal:    $('stat-total'),
  statAvg:      $('stat-avg'),
  statUpdates:  $('stat-updates'),
  pwBars:       $('pw-bars'),
  trendCanvas:  $('trend-canvas'),

  resetBtn: $('reset-btn'),

  resultsArea:  $('results-area'),
};

const CIRC_R28 = 2 * Math.PI * 28;

// ── Canvas background (particle field) ────────────────────────────────────────
(function initCanvas() {
  const cv = $('bg-canvas');
  if (!cv) return;
  const ctx = cv.getContext('2d');
  let W, H, pts, mX = 600, mY = 300;

  const COLORS = ['#3ecf8e', '#6ab0f5', '#f5a623', '#c084fc'];
  const resize = () => { W = cv.width = window.innerWidth; H = cv.height = window.innerHeight; };
  const mkP = () => ({
    x: Math.random()*W, y: Math.random()*H,
    r: Math.random()*1.4+.4,
    vx: (Math.random()-.5)*.22, vy: (Math.random()-.5)*.22,
    c: COLORS[Math.floor(Math.random()*COLORS.length)],
    a: Math.random()*.35+.06,
  });
  const hex2rgb = h => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)];

  window.addEventListener('mousemove', e => { mX=e.clientX; mY=e.clientY; });
  window.addEventListener('resize', resize);
  resize();
  pts = Array.from({length:70}, mkP);

  (function draw() {
    ctx.clearRect(0,0,W,H);
    for (let i=0;i<pts.length;i++) for (let j=i+1;j<pts.length;j++) {
      const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y, d=Math.sqrt(dx*dx+dy*dy);
      if (d<100) {
        ctx.beginPath(); ctx.moveTo(pts[i].x,pts[i].y); ctx.lineTo(pts[j].x,pts[j].y);
        ctx.strokeStyle=`rgba(62,207,142,${(1-d/100)*.05})`; ctx.lineWidth=.5; ctx.stroke();
      }
    }
    for (const p of pts) {
      const dx=mX-p.x, dy=mY-p.y, dm=Math.sqrt(dx*dx+dy*dy);
      if (dm<160) { p.vx+=(dx/dm)*.005; p.vy+=(dy/dm)*.005; }
      p.vx*=.978; p.vy*=.978;
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<0)p.x=W; if(p.x>W)p.x=0; if(p.y<0)p.y=H; if(p.y>H)p.y=0;
      const [r,g,b] = hex2rgb(p.c);
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(${r},${g},${b},${p.a})`; ctx.fill();
    }
    requestAnimationFrame(draw);
  })();
})();

// ── Utilities ──────────────────────────────────────────────────────────────────
function toast(msg, type='info', ms=3500) {
  const t = $('toast'); t.textContent=msg; t.className=`toast show ${type}`;
  clearTimeout(t._t); t._t=setTimeout(()=>t.className='toast', ms);
}
async function apiFetch(path, opts={}) {
  const r = await fetch(API+path, { headers:{'Content-Type':'application/json'}, ...opts });
  if (!r.ok) {
    let d = r.statusText;
    try { const e=await r.json(); d=e.detail||JSON.stringify(e)||d; } catch(_){}
    throw new Error(d);
  }
  return r.json();
}
const fmt  = v => typeof v==='number' ? v.toFixed(4) : '—';
const pct  = v => typeof v==='number' ? `${Math.round(v*100)}%` : '—';
const clr  = v => v>=.72 ? 'green' : v>=.45 ? 'amber' : 'red';
const grade = v => v>=.82 ? 'Excellent' : v>=.65 ? 'Good' : v>=.45 ? 'Fair' : 'Needs Work';

function typeText(el, text, speed=12) {
  el.textContent = ''; let i = 0;
  return new Promise(res => {
    const tick = () => {
      if (i < text.length) { el.textContent += text[i++]; setTimeout(tick, speed + Math.random()*8); }
      else res();
    };
    tick();
  });
}

function animateScore(el, final) {
  let val = 0;
  const step = final / 30;

  const interval = setInterval(() => {
    val += step;
    if (val >= final) {
      val = final;
      clearInterval(interval);
    }
    el.textContent = val.toFixed(4);
  }, 20);
}

// ── Health check ────────────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    await apiFetch('/health');
    el.envStatus.innerHTML = '<span class="status-dot"></span><span class="status-label">Connected</span>';
    el.envStatus.className = 'nav-pill connected';
  } catch {
    el.envStatus.innerHTML = '<span class="status-dot"></span><span class="status-label">Offline</span>';
    el.envStatus.className = 'nav-pill';
    setTimeout(checkHealth, 5000);
  }
}

// ── Mode switching ──────────────────────────────────────────────────────────────
function setMode(mode) {
  currentMode = mode;
  el.modeAiBtn.classList.toggle('active', mode==='ai');
  el.modeHumanBtn.classList.toggle('active', mode==='human');

  if (mode === 'ai') {
    el.modeHint.textContent = 'AI scenario → you & AI both respond';
    el.aiWorkspace.style.display   = '';
    el.humanWorkspace.style.display= 'none';
    el.loadBlock.style.display     = '';
    currentQuery = null;
    scenarioLoaded = false;

    // 🔥 Enable random again in AI mode
  if (el.taskSelect.options[0].value === "") {
    el.taskSelect.options[0].disabled = false;
  }
    resetAiWorkspace();
  }
  else {
  el.modeHint.textContent = 'You ask → AI responds & is evaluated';
  el.aiWorkspace.style.display   = 'none';
  el.humanWorkspace.style.display= '';
  el.loadBlock.style.display     = 'none';

  // 🔥 ADD THIS
  // Disable random option in human mode
  if (el.taskSelect.options[0].value === "") {
    el.taskSelect.options[0].disabled = true;
  }

  // 🔥 Always enforce valid task
  if (!el.taskSelect.value || el.taskSelect.value === "") {
    el.taskSelect.value = "emotional_support";
  }

  updateHqTaskChip();
  resetHumanAiBox();
}
}

el.modeAiBtn.addEventListener('click', () => setMode('ai'));
el.modeHumanBtn.addEventListener('click', () => setMode('human'));
el.taskSelect.addEventListener('change', () => {
  if (currentMode === 'human') {

    // 🔥 Force prevent selecting random
    if (!el.taskSelect.value) {
      el.taskSelect.value = "emotional_support";
      toast('Random is not allowed in Human mode', 'error');
    }

    updateHqTaskChip();
  }
});
function updateHqTaskChip() {
  const v = el.taskSelect.value;

  if (!v) {
    el.hqTaskChip.textContent = 'Select Task';
  } else {
    const label = el.taskSelect.options[el.taskSelect.selectedIndex].text;
    el.hqTaskChip.textContent = label;
  }
}

document.addEventListener('keydown', async (e) => {
  if (e.key !== 'Enter' || e.shiftKey) return;

  const active = document.activeElement;
  const isTyping = active && (
    active.tagName === 'TEXTAREA' ||
    active.tagName === 'INPUT'
  );

// 🔥 FIX: allow Enter only when NOT typing OR when in AI textarea
  if (isTyping && active !== el.humanTextarea) return;

  e.preventDefault();

  if (currentMode === 'ai') {
    await evaluateAiMode();
  } else {
    await evaluateHumanMode();
  }
});

// ── Reset workspace displays ────────────────────────────────────────────────────
function resetAiWorkspace() {
  el.sTask.textContent  = '—'; el.sDiff.textContent='—'; el.sTone.textContent='—';
  el.sName.textContent  = 'Load a scenario to begin';
  el.sQuery.textContent = 'Click "Load Scenario" to get started.';
  el.humanTextarea.value=''; el.charCount.textContent='0 chars';
  el.evaluateBtn.disabled = false;
  el.actionHint.textContent = 'Load a scenario first';
  resetAiBox(el.aiBox, el.aiPlaceholder, el.aiThinking, el.aiText);
}
function resetAiBox(box, ph, thinking, text) {
  ph.style.display      = 'flex';
  thinking.style.display= 'none';
  text.style.display    = 'none';
  text.textContent      = '';
  box.style.alignItems  = 'center';
}
function resetHumanAiBox() {
  resetAiBox(el.aiBoxHuman, el.aiPlaceholderHuman, el.aiThinkingHuman, el.aiTextHuman);
}

// ── Load scenario (AI mode) ─────────────────────────────────────────────────────
async function loadScenario() {
  el.loadBtn.disabled = true;
  el.loadBtn.innerHTML = '<svg viewBox="0 0 16 16" fill="none" style="width:14px;height:14px;animation:spin .7s linear infinite"><path d="M2 8a6 6 0 1 0 1.4-3.7M2 4.5V8h3.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg> Loading…';
  try {
    const params = new URLSearchParams({ mode: 'ai' });
    const tid = el.taskSelect.value;
    if (tid) params.append('task_id', tid);
    currentQuery = await apiFetch(`/query?${params}`);
    scenarioLoaded = true;
    el.sTask.textContent = currentQuery.task_id;
    el.sDiff.textContent = currentQuery.difficulty;
    el.sDiff.className   = 'meta-chip difficulty';
    el.sTone.textContent = currentQuery.tone;
    el.sTone.className   = 'meta-chip tone';
    el.sName.textContent = currentQuery.task_name;
    el.sQuery.textContent= currentQuery.query;

    el.humanTextarea.value=''; el.charCount.textContent='0 chars';
    resetAiBox(el.aiBox, el.aiPlaceholder, el.aiThinking, el.aiText);
    el.evaluateBtn.disabled   = false;
    el.actionHint.textContent = 'Write your response (optional), then evaluate';
    toast(`Loaded: ${currentQuery.task_name}`, 'info');
  } catch(e) {
    toast(`Failed to load: ${e.message}`, 'error');
  } finally {
    el.loadBtn.disabled = false;
    el.loadBtn.innerHTML = '<svg viewBox="0 0 16 16" fill="none"><path d="M2 8a6 6 0 1 0 1.4-3.7M2 4.5V8h3.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg> Load Scenario';
  }
}
el.loadBtn.addEventListener('click', loadScenario);

// ── Evaluate (AI mode) ─────────────────────────────────────────────────────────

async function evaluateAiMode() {

if (!scenarioLoaded) {
  try {
    const params = new URLSearchParams({ mode: 'ai' });
    const tid = el.taskSelect.value;
    if (tid) params.append('task_id', tid);

    currentQuery = await apiFetch(`/query?${params}`);

    el.sTask.textContent = currentQuery.task_id;
    el.sDiff.textContent = currentQuery.difficulty;
    el.sTone.textContent = currentQuery.tone;
    el.sName.textContent = currentQuery.task_name;
    el.sQuery.textContent = currentQuery.query;

    scenarioLoaded = true; 

    return;

  } catch (e) {
    toast('Failed to auto-load scenario', 'error');
    return;
  }
}

  const human = el.humanTextarea.value.trim();

  setEvalBtnLoading(el.evaluateBtn, true);

  // Show thinking animation
  el.aiPlaceholder.style.display = 'none';
  el.aiThinking.style.display    = 'flex';
  el.aiText.style.display        = 'none';

  evalCount++;
  const epNum = evalCount;
  const item = {
    task_id:   currentQuery.task_id,
    task_name: currentQuery.task_name,
    difficulty:currentQuery.difficulty,
    tone:      currentQuery.tone,
    query:     currentQuery.query,
    mode:      'ai',
  };
  const card = insertPlaceholderCard(epNum, item);

  try {
    const result = await apiFetch('/evaluate', {
      method:'POST',
      body: JSON.stringify({ task_id:item.task_id, query:item.query, human_response:human||undefined }),
    });

    // Reveal AI response in panel with typewriter
    el.aiThinking.style.display = 'none';
    el.aiText.style.display     = 'block';
    el.aiBox.style.alignItems   = 'flex-start';
    await typeText(el.aiText, result.ai.response, 10);

    await fillResultCard(card, epNum, item, result);
    toast('Evaluation complete', 'success');
  } catch(err) {
    el.aiThinking.style.display = 'none';
    el.aiPlaceholder.style.display = 'flex';
    showCardError(card, err.message);
    toast(`Error: ${err.message}`, 'error');
  } finally {
    setEvalBtnLoading(el.evaluateBtn, false, 'Evaluate');
    currentQuery = null;
    scenarioLoaded = false;
  }
}
el.evaluateBtn.addEventListener('click', evaluateAiMode);
el.humanTextarea.addEventListener('input', () => {
  el.charCount.textContent = `${el.humanTextarea.value.length} chars`;
});

// ── Evaluate (Human mode) ──────────────────────────────────────────────────────
async function evaluateHumanMode() {
  const query = el.humanQueryInput.value.trim();

  // 🔥 NEW FIX
  if (!query) {
    toast('Please enter a query', 'error');
    el.humanQueryInput.focus();
    return;
  }

  const taskId = el.taskSelect.value;

// 🔥 HARD BLOCK random in human mode
  if (!taskId || taskId === "") {
    toast('Please select a valid task (Random not allowed in Human mode)', 'error');
    return;
  }
  setEvalBtnLoading(el.humanEvaluateBtn, true);

  el.aiPlaceholderHuman.style.display = 'none';
  el.aiThinkingHuman.style.display    = 'flex';
  el.aiTextHuman.style.display        = 'none';

  evalCount++;
  const epNum = evalCount;
  const taskLabel = el.taskSelect.options[el.taskSelect.selectedIndex].text;
  const item = { task_id:taskId, task_name:taskLabel, difficulty:'—', tone:'—', query, mode:'human' };
  const card = insertPlaceholderCard(epNum, item);

  try {
    const result = await apiFetch('/evaluate', {
      method:'POST',
      body: JSON.stringify({ task_id:taskId, query }),
    });
    item.task_name = result.task_name || item.task_name;

    el.aiThinkingHuman.style.display = 'none';
    el.aiTextHuman.style.display     = 'block';
    el.aiBoxHuman.style.alignItems   = 'flex-start';
    await typeText(el.aiTextHuman, result.ai.response, 10);

    await fillResultCard(card, epNum, item, result);
    toast('Response generated & evaluated', 'success');
  } catch(err) {
    el.aiThinkingHuman.style.display = 'none';
    el.aiPlaceholderHuman.style.display = 'flex';
    showCardError(card, err.message);
    toast(`Error: ${err.message}`, 'error');
  } finally {
    setEvalBtnLoading(el.humanEvaluateBtn, false, 'Generate &amp; Evaluate');
  }
}
el.humanEvaluateBtn.addEventListener('click', evaluateHumanMode);
el.humanQueryInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();

    const value = el.humanQueryInput.value.trim();

    if (!value) {
      toast('Please enter a query before submitting', 'error');
      return;
    }

    evaluateHumanMode();
  }
});
el.humanQueryInput.addEventListener('input', () => {
  el.hqCharCount.textContent = `${el.humanQueryInput.value.length} chars`;
});

// ── Eval button helpers ────────────────────────────────────────────────────────
function setEvalBtnLoading(btn, loading, label='') {
  btn.disabled = loading;
  if (loading) {
    btn.innerHTML = '<svg viewBox="0 0 16 16" fill="none" style="width:15px;height:15px;animation:spin .7s linear infinite"><path d="M2 8a6 6 0 1 0 1.4-3.7M2 4.5V8h3.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg> Evaluating…';
  } else {
    btn.innerHTML = `<svg viewBox="0 0 16 16" fill="none"><path d="M2 8a6 6 0 1 0 12 0A6 6 0 0 0 2 8zM8 5v3l2.5 2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg> ${label}`;
  }
}

// ── Result cards ───────────────────────────────────────────────────────────────
function insertPlaceholderCard(epNum, item) {
  const card = document.createElement('div');
  card.className = 'result-card';
  card.innerHTML = `
    <div class="result-header">
      <div class="rh-left">
        <span class="rh-ep">EP ${epNum}</span>
        <span class="rh-task">${item.task_name}</span>
        <span class="rh-mode ${item.mode}-mode">${item.mode==='ai'?'AI Query':'Human Query'}</span>
      </div>
      <div class="verdict"><span>Evaluating…</span></div>
    </div>
    <div class="result-loading">
      <div class="thinking-dots" style="gap:5px">
        <span style="width:7px;height:7px;border-radius:50%;background:var(--accent);display:inline-block;animation:bounce-dot 1.1s ease infinite"></span>
        <span style="width:7px;height:7px;border-radius:50%;background:var(--accent);display:inline-block;animation:bounce-dot 1.1s ease infinite;animation-delay:.18s"></span>
        <span style="width:7px;height:7px;border-radius:50%;background:var(--accent);display:inline-block;animation:bounce-dot 1.1s ease infinite;animation-delay:.36s"></span>
      </div>
      Generating AI response and scoring…
    </div>`;
  el.resultsArea.insertBefore(card, el.resultsArea.firstChild);
  return card;
}

function showCardError(card, msg) {
  card.querySelector('.result-loading').innerHTML =
    `<span style="color:var(--red)">Error: ${msg}</span>`;
}

async function fillResultCard(card, epNum, item, result) {
  const ai    = result.ai || {};
  const human = result.human || null;
  const better= result.better || 'ai';
  const aiR   = ai.reward ?? 0;
  const humanR= human ? (human.reward ?? null) : null;

  // Verdict
  let vClass = 'ai-wins', vLabel = 'AI';
  if (human) {
    if (better==='human') { vClass='human-wins'; vLabel='Human'; }
    else if (better==='tie') { vClass='tie'; vLabel='Tie'; }
  } else {
    vLabel = 'AI only';
  }
  const delta = human && humanR!==null && better!=='tie'
    ? `<span class="delta">Δ${fmt(Math.abs(aiR-humanR))}</span>` : '';

  // FIX 1: Always render side-by-side — never fall back to single column
  const showSideBySide = true;

  // Human column: always shown; use "No response submitted" text if empty
  const humanResponse = (human && human.response) ? human.response : null;
  const humanEval     = (human && human.evaluation) ? human.evaluation : null;
  const humanReward   = (human && human.reward != null) ? human.reward : null;
  const humanColHTML  = scoreColHTML('human', humanReward, humanEval, humanResponse);

  const aiColHTML   = scoreColHTML('ai', aiR, ai.evaluation, ai.response);
  const gridClass   = 'score-grid';
  const dividerHTML = '<div class="score-divider"></div>';

  card.innerHTML = `
    <div class="result-header">
      <div class="rh-left">
        <span class="rh-ep">EP ${epNum}</span>
        <span class="rh-task">${item.task_name}</span>
        <span class="rh-mode ${item.mode}-mode">${item.mode==='ai'?'AI Query':'Human Query'}</span>
      </div>
      <div class="verdict ${vClass}">
        <svg viewBox="0 0 16 16" fill="none" width="13" height="13"><path d="M8 1l1.9 3.9 4.3.6-3.1 3 .7 4.3L8 10.8l-3.8 2 .7-4.3-3.1-3 4.3-.6z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>
        <span>Better: ${vLabel}</span>
        ${delta}
      </div>
    </div>
    <div class="result-body">
      <div class="result-query">
        <div class="rq-label">${item.mode==='human'?'Your Question':'Scenario'}</div>
        <div class="rq-text">${escHtml(item.query)}</div>
      </div>
      <div class="${gridClass}">
        ${humanColHTML + dividerHTML + aiColHTML}
      </div>
      ${(result && result.policy && result.policy.weights) ? `
  <div class="policy-badge">
    <svg viewBox="0 0 14 14" fill="none" width="11" height="11">
      <path d="M7 1l1.5 3 3.5.5-2.5 2.5.6 3.5L7 8.5l-3.1 2 .6-3.5L2 4.5 5.5 4z"
      stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
    </svg>
    Policy weights:
    S=${result.policy?.weights?.semantic ?? '—'}
    T=${result.policy?.weights?.tone ?? '—'}
    St=${result.policy?.weights?.structure ?? '—'}
    · Updates: ${result.policy?.update_count ?? 0}
  </div>
` : ''}
    </div>`;

  animateBarsAndArcs(card);

  updateLogoByScore(aiR);

  // Typewriter for AI response in card
  const tw = card.querySelector('.typewriter');
  if (tw && ai.response) await typeText(tw, ai.response, 11);
}

function scoreColHTML(side, reward, evaluation, response) {
  // FIX 1: Handle null/undefined reward — show N/A panel but still render column
  if (reward === null || reward === undefined) {
    return `<div class="score-col">
      <div class="sc-head ${side==='human'?'human-head':'ai-head'}">
        ${side==='human'
          ? '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M2.5 14c0-3 2.5-5 5.5-5s5.5 2 5.5 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg> Human Response'
          : '<svg viewBox="0 0 16 16" fill="none"><rect x="1" y="3" width="14" height="10" rx="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M5 7h6M5 10h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="8" cy="1.5" r="1" fill="currentColor"/></svg> AI Response'}
      </div>
      <div class="na-panel">
        <svg viewBox="0 0 32 32" fill="none" width="24" height="24"><circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="1.3" opacity=".3"/><path d="M10 16h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity=".3"/></svg>
        <span>No response submitted</span>
      </div>
    </div>`;
  }
  const bd  = evaluation?.breakdown ?? {};
  const fbk = evaluation?.feedback  ?? {};
  const sem = bd.semantic   ?? 0;
  const ton = bd.tone       ?? 0;
  const str = bd.structure  ?? 0;
  const missing = Array.isArray(fbk.missing_keywords) ? fbk.missing_keywords : [];

  const rewardColor = clr(reward);
  const arcStroke   = reward>=.72 ? 'var(--green)' : reward>=.45 ? 'var(--amber)' : 'var(--red)';
  const realCirc    = CIRC_R28;
  const offset      = realCirc - reward * realCirc;

  // Feedback items
  const toneOk   = fbk.tone_feedback === 'good';
  const structOk = fbk.structure_feedback === 'good';

  // FIX 5: Contextual feedback labels
  const actor = side === 'ai' ? 'AI' : 'Your';
  let fbHTML = '';
  fbHTML += `<div class="fb-item ${toneOk?'good':'warn'}">
    <span class="fb-icon">${toneOk?'✓':'!'}</span>
    <span><strong>Tone</strong> — ${toneOk
      ? actor+' response matches the expected tone for this task.'
      : 'Based on your response, the tone doesn\'t align with the expected style. Try adjusting the emotional register.'
    }</span>
  </div>`;
  fbHTML += `<div class="fb-item ${structOk?'good':'warn'}">
    <span class="fb-icon">${structOk?'✓':'!'}</span>
    <span><strong>Structure</strong> — ${structOk
      ? actor+' response is well-structured and clear.'
      : 'Compared to expected structure, this could use more sentences or step-by-step clarity.'
    }</span>
  </div>`;
  if (missing.length > 0) {
    fbHTML += `<div class="fb-item bad">
      <span class="fb-icon">✗</span>
      <span><strong>Missing concepts:</strong> ${actor} response didn't cover: ${missing.map(k=>`"${escHtml(k)}"`).join(', ')}</span>
    </div>`;
  } else {
    fbHTML += `<div class="fb-item good">
      <span class="fb-icon">✓</span>
      <span><strong>Semantic coverage</strong> — ${actor} response covered all key concepts.</span>
    </div>`;
  }

  const isAi = side === 'ai';
  const respHTML = response
    ? `<div class="resp-block">
        <div class="resp-block-label">${isAi?'AI response':'Your response'}</div>
        <div class="resp-block-text ${isAi?'typewriter':''}">${isAi?'':escHtml(response)}</div>
      </div>` : '';

  return `<div class="score-col">
    <div class="sc-head ${side==='human'?'human-head':'ai-head'}">
      ${side==='human'
        ? '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M2.5 14c0-3 2.5-5 5.5-5s5.5 2 5.5 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg> Human Response'
        : '<svg viewBox="0 0 16 16" fill="none"><rect x="1" y="3" width="14" height="10" rx="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M5 7h6M5 10h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="8" cy="1.5" r="1" fill="currentColor"/></svg> AI Response'}
    </div>
    <div class="score-panel">
      <div class="ov-row">
        <div class="ov-left">
          <div class="ov-label">OVERALL SCORE</div>
          <div class="ov-score ${rewardColor}" data-score="${reward}">0.0000</div>
          <div class="ov-grade">${grade(reward)} · ${pct(reward)}</div>
        </div>
        <div class="arc-wrap">
          <svg class="arc-svg" viewBox="0 0 68 68">
            <circle class="arc-track" cx="34" cy="34" r="28"/>
            <circle class="arc-fill" cx="34" cy="34" r="28"
              style="stroke-dasharray:${realCirc};stroke-dashoffset:${realCirc};stroke:${arcStroke}"
              data-final-offset="${offset}" data-circ="${realCirc}"/>
          </svg>
          <div class="arc-pct">${pct(reward)}</div>
        </div>
      </div>
      <div class="dim-bars">
        <div class="dim-row">
          <span class="dim-name">Semantic</span>
          <div class="dim-track"><div class="dim-fill semantic" data-w="${sem*100}" style="width:0%"></div></div>
          <span class="dim-val">${pct(sem)}</span>
        </div>
        <div class="dim-row">
          <span class="dim-name">Tone</span>
          <div class="dim-track"><div class="dim-fill tone" data-w="${ton*100}" style="width:0%"></div></div>
          <span class="dim-val">${pct(ton)}</span>
        </div>
        <div class="dim-row">
          <span class="dim-name">Structure</span>
          <div class="dim-track"><div class="dim-fill structure" data-w="${str*100}" style="width:0%"></div></div>
          <span class="dim-val">${pct(str)}</span>
        </div>
      </div>
      ${respHTML}
      <div class="fb-stack">${fbHTML}</div>
    </div>
  </div>`;
}

function naColHTML() {
  return `<div class="score-col">
    <div class="sc-head human-head">
      <svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M2.5 14c0-3 2.5-5 5.5-5s5.5 2 5.5 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
      Human Response
    </div>
    <div class="na-panel">
      <svg viewBox="0 0 32 32" fill="none" width="24" height="24"><circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="1.3" opacity=".3"/><path d="M12 16h8M16 12v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity=".3"/></svg>
      <span>No response submitted</span>
    </div>
  </div>`;
}

function animateBarsAndArcs(card) {
  requestAnimationFrame(() => {

    // Existing bars animation
    card.querySelectorAll('.dim-fill[data-w]').forEach(el => {
      setTimeout(() => { el.style.width = el.dataset.w + '%'; }, 100);
    });

    // Existing arc animation
    card.querySelectorAll('.arc-fill[data-final-offset]').forEach(el => {
      const finalOffset = parseFloat(el.dataset.finalOffset);
      const circ        = parseFloat(el.dataset.circ);
      el.style.strokeDasharray  = circ;
      el.style.strokeDashoffset = circ;
      setTimeout(() => { el.style.strokeDashoffset = finalOffset; }, 150);
    });

    // 🔥 ADD THIS PART (your question)
    card.querySelectorAll('.ov-score[data-score]').forEach(el => {
      const final = parseFloat(el.dataset.score);
      animateScore(el, final);
    });

  });
}

function escHtml(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── RL Stats panel ─────────────────────────────────────────────────────────────
el.statsBtn.addEventListener('click', async () => {
  const showing = el.statsPanel.style.display !== 'none';
  if (showing) {
    el.statsPanel.style.display = 'none';
    return;
  }
  el.statsPanel.style.display = '';
  try {
    const stats = await apiFetch('/stats');
    el.statTotal.textContent  = stats.total_evaluations ?? 0;
    el.statAvg.textContent    = stats.average_reward ? pct(stats.average_reward) : '—';
    el.statUpdates.textContent= stats.policy?.update_count ?? 0;

    // Policy weights bars
    const weights = stats.policy?.weights ?? {};
    el.pwBars.innerHTML = '';
    for (const [dim, val] of Object.entries(weights)) {
      el.pwBars.innerHTML += `
        <div class="pw-row">
          <span class="pw-dim">${dim}</span>
          <div class="pw-track"><div class="pw-fill" style="width:0%" data-w="${val*100}"></div></div>
          <span class="pw-val">${(val*100).toFixed(1)}%</span>
        </div>`;
    }
    requestAnimationFrame(() => {
      el.pwBars.querySelectorAll('.pw-fill[data-w]').forEach(f => {
        setTimeout(() => { f.style.width = f.dataset.w + '%'; }, 80);
      });
    });

    // Trend sparkline
    const trend = stats.reward_trend || [];
    drawTrendCanvas(trend);
  } catch(e) {
    toast(`Failed to load stats: ${e.message}`, 'error');
  }
});
el.statsClose.addEventListener('click', () => { el.statsPanel.style.display = 'none'; });

function drawTrendCanvas(trend) {
  const cv  = el.trendCanvas;
  const ctx = cv.getContext('2d');
  cv.width  = cv.offsetWidth || 600;
  const W = cv.width, H = cv.height || 60;
  ctx.clearRect(0,0,W,H);
  if (trend.length < 2) {
    ctx.fillStyle = 'rgba(125,133,144,.4)';
    ctx.font = '11px DM Mono, monospace';
    ctx.fillText('Not enough data yet', 10, H/2+4);
    return;
  }
  const min  = Math.min(...trend) * .9;
  const max  = Math.max(...trend) * 1.05 || 1;
  const xStep= W / (trend.length - 1);
  const yMap = v => H - ((v - min) / (max - min)) * (H * .8) - H * .1;

  const grad = ctx.createLinearGradient(0,0,0,H);
  grad.addColorStop(0, 'rgba(62,207,142,.25)');
  grad.addColorStop(1, 'rgba(62,207,142,0)');

  ctx.beginPath();
  trend.forEach((v,i) => i===0 ? ctx.moveTo(0,yMap(v)) : ctx.lineTo(i*xStep, yMap(v)));
  ctx.lineTo((trend.length-1)*xStep, H);
  ctx.lineTo(0, H);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  ctx.beginPath();
  trend.forEach((v,i) => i===0 ? ctx.moveTo(0,yMap(v)) : ctx.lineTo(i*xStep, yMap(v)));
  ctx.strokeStyle = 'var(--green)';
  ctx.lineWidth   = 1.5;
  ctx.stroke();
}

// ── CSS spin keyframe inject ────────────────────────────────────────────────────
const spinStyle = document.createElement('style');
spinStyle.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
document.head.appendChild(spinStyle);

// ── Init ────────────────────────────────────────────────────────────────────────
checkHealth();
setMode('ai');
toast('Select a task and load a scenario to begin', 'info', 5000);
scenarioLoaded = false;
currentQuery = null;

el.resetBtn.addEventListener('click', async () => {

  scenarioLoaded = false;
  currentQuery = null;
  // 🔥 ALWAYS RESET UI FIRST (independent of backend)
  evalCount = 0;
  el.resultsArea.innerHTML = '';
  resetAiWorkspace();
  resetHumanAiBox();

  // 🔥 FIX: correct input field
  el.humanQueryInput.value = '';
  el.hqCharCount.textContent = '0 chars';

  try {
    await apiFetch('/reset-policy', { method: 'POST' });
    toast('RL system reset successfully', 'success');
  } catch (e) {
    toast('Backend reset failed (UI still cleared)', 'error');
  }

});

// FIX 6: Ensure logo rotation animation runs (no JS override)
(function initLogoAnimation() {
  const logo = document.querySelector('.logo-mark');
  if (!logo) return;

  // FULL RESET FIX
  logo.style.animation = 'none';
  void logo.offsetWidth; // force reflow
  logo.style.animation = 'spin-slow 6s linear infinite';
})();

function updateLogoByScore(score) {
  const logo = document.querySelector('.logo-mark');
  if (!logo) return;

  if (score >= 0.7) {
    logo.style.filter = 'drop-shadow(0 0 12px #3ecf8e)';
  } else if (score >= 0.4) {
    logo.style.filter = 'drop-shadow(0 0 12px #f5a623)';
  } else {
    logo.style.filter = 'drop-shadow(0 0 12px #f06570)';
  }
}
