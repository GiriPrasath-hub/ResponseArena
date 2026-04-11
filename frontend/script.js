/* ── ResponseArena v4 — Premium Lab Aesthetic ──────────────────────────────── */

/* ── Tokens ─────────────────────────────────────────────────────────────────── */
:root {
  --bg:          #0d0f11;
  --bg-2:        #131619;
  --bg-3:        #1a1d21;
  --bg-4:        #22262b;
  --border:      rgba(255,255,255,.09);
  --border-h:    rgba(255,255,255,.18);

  --tx:          #f0f2f4;
  --tx-2:        #c4c9d0;
  --tx-3:        #7d8590;

  --green:       #3ecf8e;
  --green-dim:   rgba(62,207,142,.12);
  --amber:       #f5a623;
  --amber-dim:   rgba(245,166,35,.12);
  --red:         #f06570;
  --red-dim:     rgba(240,101,112,.12);
  --blue:        #6ab0f5;
  --blue-dim:    rgba(106,176,245,.12);

  --accent:      #3ecf8e;
  --accent-glow: rgba(62,207,142,.2);

  --radius-sm:   6px;
  --radius:      10px;
  --radius-lg:   16px;

  --font-body:   'DM Sans', sans-serif;
  --font-mono:   'DM Mono', monospace;
  --font-serif:  'Playfair Display', serif;

  --shadow-card: 0 1px 3px rgba(0,0,0,.4), 0 4px 20px rgba(0,0,0,.3);
  --shadow-glow: 0 0 30px rgba(62,207,142,.08);

  --t: .18s ease;
}

/* ── Reset ───────────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 15px; scroll-behavior: smooth; }
body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--tx);
  min-height: 100vh;
  overflow-x: hidden;
  line-height: 1.6;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: var(--bg-4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--tx-3); }

/* ── Canvas background ───────────────────────────────────────────────────────── */
#bg-canvas {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: .7;
}

/* ── Header ──────────────────────────────────────────────────────────────────── */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(13,15,17,.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon {
  width: 34px; height: 34px;
  color: var(--accent);
}
.logo-icon svg { width: 100%; height: 100%; }
.logo-name {
  display: block;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 700;
  color: var(--tx);
  letter-spacing: -.02em;
}
.logo-tag {
  display: block;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--tx-3);
  letter-spacing: .04em;
  margin-top: -2px;
}

.header-nav { display: flex; align-items: center; gap: 10px; }
.nav-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 12px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: 100px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--tx-3);
}
.nav-pill.connected { color: var(--green); border-color: rgba(62,207,142,.2); }
.status-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--tx-3);
  flex-shrink: 0;
}
.nav-pill.connected .status-dot {
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity: 1; }
  50% { opacity: .4; }
}
.nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--tx-2);
  cursor: pointer;
  transition: all var(--t);
}
.nav-btn svg { width: 14px; height: 14px; }
.nav-btn:hover { border-color: var(--border-h); color: var(--tx); background: var(--bg-4); }

/* ── Main layout ─────────────────────────────────────────────────────────────── */
.main {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 24px 80px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* ── Card base ───────────────────────────────────────────────────────────────── */
.card-base {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

/* ── RL Stats panel ──────────────────────────────────────────────────────────── */
.stats-panel {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  animation: slideDown .2s ease;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: none; } }
.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.stats-title {
  font-family: var(--font-serif);
  font-size: 17px;
  color: var(--tx);
}
.close-btn {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-3); border: 1px solid var(--border); border-radius: 50%;
  color: var(--tx-3); font-size: 12px; cursor: pointer; transition: all var(--t);
}
.close-btn:hover { color: var(--tx); background: var(--bg-4); }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.stat-card {
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
}
.stat-label { font-size: 11px; color: var(--tx-3); font-family: var(--font-mono); letter-spacing: .04em; margin-bottom: 8px; }
.stat-value { font-family: var(--font-serif); font-size: 24px; color: var(--accent); }
.policy-weights, .reward-trend-wrap { margin-bottom: 16px; }
.pw-title { font-size: 11px; font-family: var(--font-mono); color: var(--tx-3); letter-spacing: .04em; margin-bottom: 10px; }
.pw-bars { display: flex; flex-direction: column; gap: 8px; }
.pw-row { display: flex; align-items: center; gap: 10px; }
.pw-dim { font-family: var(--font-mono); font-size: 11px; color: var(--tx-2); width: 72px; }
.pw-track { flex: 1; height: 5px; background: var(--bg-4); border-radius: 3px; overflow: hidden; }
.pw-fill { height: 100%; background: var(--accent); border-radius: 3px; transition: width .5s ease; }
.pw-val { font-family: var(--font-mono); font-size: 10px; color: var(--tx-3); width: 36px; text-align: right; }
#trend-canvas { width: 100%; display: block; }

/* ── Controls ────────────────────────────────────────────────────────────────── */
.control-row {
  display: grid;
  grid-template-columns: 1fr 1.5fr auto;
  gap: 14px;
  align-items: end;
}
.ctrl-block { display: flex; flex-direction: column; gap: 8px; }
.ctrl-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--tx-3);
}
.select-wrap { position: relative; }
.select-input {
  width: 100%;
  padding: 9px 34px 9px 14px;
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--tx);
  font-family: var(--font-body);
  font-size: 14px;
  appearance: none;
  cursor: pointer;
  transition: border-color var(--t);
}
.select-input:hover, .select-input:focus { border-color: var(--border-h); outline: none; }
.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  color: var(--tx-3);
  pointer-events: none;
}

.mode-switch { display: flex; gap: 4px; background: var(--bg-3); border: 1px solid var(--border); border-radius: var(--radius); padding: 3px; }
.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 7px 14px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--tx-3);
  cursor: pointer;
  transition: all var(--t);
  white-space: nowrap;
}
.mode-btn svg { width: 13px; height: 13px; }
.mode-btn.active { background: var(--bg-4); color: var(--tx); box-shadow: 0 1px 4px rgba(0,0,0,.3); }
.mode-hint { font-size: 11.5px; color: var(--tx-3); }

.btn-primary {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px;
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  color: var(--tx-2);
  cursor: pointer;
  transition: all var(--t);
  white-space: nowrap;
}
.btn-primary svg { width: 14px; height: 14px; }
.btn-primary:hover { border-color: var(--accent); color: var(--accent); }

/* ── Workspace ───────────────────────────────────────────────────────────────── */
.workspace {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  box-shadow: var(--shadow-card);
}

.scenario-bar { margin-bottom: 20px; }
.scenario-meta { display: flex; gap: 7px; flex-wrap: wrap; margin-bottom: 10px; }
.meta-chip {
  padding: 3px 10px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: 100px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--tx-3);
}
.meta-chip.difficulty { border-color: rgba(245,166,35,.25); color: var(--amber); background: var(--amber-dim); }
.meta-chip.tone { border-color: rgba(106,176,245,.25); color: var(--blue); background: var(--blue-dim); }
.meta-chip.human-mode-chip { border-color: rgba(62,207,142,.25); color: var(--green); background: var(--green-dim); }
.scenario-name {
  font-family: var(--font-serif);
  font-size: 17px;
  color: var(--tx);
  margin-bottom: 8px;
}
.scenario-text {
  font-size: 15px;
  color: var(--tx-2);
  line-height: 1.65;
  border-left: 2px solid var(--accent);
  padding-left: 14px;
  font-style: italic;
}

/* ── Dual panel ─────────────────────────────────────────────────────────────── */
.dual-panel {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0;
  align-items: start;
}
.panel { display: flex; flex-direction: column; gap: 8px; }
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.panel-label {
  display: flex; align-items: center; gap: 7px;
  font-size: 13px; font-weight: 600; color: var(--tx-2);
}
.panel-label svg { width: 14px; height: 14px; }
.human-label { color: var(--tx-2); }
.ai-label { color: var(--green); }
.panel-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 100px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  color: var(--tx-3);
}
.ai-badge { border-color: rgba(62,207,142,.2); color: var(--green); }

.panel-divider {
  display: flex; flex-direction: column; align-items: center;
  padding: 36px 20px 0;
  gap: 10px;
}
.divider-line { flex: 1; width: 1px; background: var(--border); min-height: 20px; }
.divider-vs {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--tx-3);
  padding: 6px 0;
}

/* ── Inputs ──────────────────────────────────────────────────────────────────── */
.response-input {
  width: 100%;
  min-height: 160px;
  padding: 12px 14px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--tx);
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.65;
  resize: vertical;
  transition: border-color var(--t);
}
.response-input::placeholder { color: var(--tx-3); }
.response-input:focus { outline: none; border-color: var(--border-h); }
.hq-input { min-height: 120px; }
.input-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}
.char-count { font-family: var(--font-mono); font-size: 10px; color: var(--tx-3); }

/* ── AI box ──────────────────────────────────────────────────────────────────── */
.ai-box {
  min-height: 160px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color var(--t);
}
.ai-placeholder {
  display: flex; flex-direction: column;
  align-items: center; gap: 10px; text-align: center;
  color: var(--tx-3);
}
.ai-placeholder svg { opacity: .4; }
.ai-placeholder p { font-size: 13px; line-height: 1.5; max-width: 200px; }
.ai-thinking {
  display: flex; flex-direction: column;
  align-items: center; gap: 12px;
}
.thinking-dots { display: flex; gap: 6px; }
.thinking-dots span {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent);
  animation: bounce-dot 1.1s ease infinite;
}
.thinking-dots span:nth-child(2) { animation-delay: .18s; }
.thinking-dots span:nth-child(3) { animation-delay: .36s; }
@keyframes bounce-dot {
  0%,80%,100% { transform: scale(0.6); opacity: .5; }
  40% { transform: scale(1); opacity: 1; }
}
.thinking-label { font-family: var(--font-mono); font-size: 11px; color: var(--tx-3); }
.ai-text {
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.7;
  color: var(--tx-2);
  width: 100%;
  align-self: flex-start;
}

/* ── Human query block ───────────────────────────────────────────────────────── */
.human-query-block { margin-bottom: 4px; }
.hq-label { display: block; font-size: 13px; font-weight: 500; color: var(--tx-2); margin-bottom: 8px; }

/* ── Action bar ──────────────────────────────────────────────────────────────── */
.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}
.action-hint { font-size: 13px; color: var(--tx-3); }
.btn-evaluate {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 24px;
  background: var(--accent);
  color: #051a12;
  border: none;
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--t);
}
.btn-evaluate svg { width: 15px; height: 15px; }
.btn-evaluate:hover:not(:disabled) {
  background: #52e09d;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px var(--accent-glow);
}
.btn-evaluate:active { transform: translateY(0); }
.btn-evaluate:disabled { opacity: .3; cursor: not-allowed; transform: none; box-shadow: none; }

/* ── Result cards ────────────────────────────────────────────────────────────── */
.result-card {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  animation: cardIn .35s cubic-bezier(.2,.8,.4,1) both;
  box-shadow: var(--shadow-card);
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px) scale(.98); }
  to   { opacity: 1; transform: none; }
}
.result-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 22px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-3);
}
.rh-left { display: flex; align-items: center; gap: 10px; }
.rh-ep {
  font-family: var(--font-mono);
  font-size: 10px; color: var(--tx-3);
  background: var(--bg-4); border: 1px solid var(--border);
  padding: 2px 8px; border-radius: 100px;
}
.rh-task { font-size: 14px; font-weight: 600; color: var(--tx); }
.rh-mode {
  font-family: var(--font-mono); font-size: 10px;
  padding: 2px 8px; border-radius: 100px;
  background: var(--bg-4); border: 1px solid var(--border); color: var(--tx-3);
}
.rh-mode.ai-mode { border-color: rgba(62,207,142,.2); color: var(--green); background: var(--green-dim); }
.rh-mode.human-mode { border-color: rgba(106,176,245,.2); color: var(--blue); background: var(--blue-dim); }

.verdict {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 14px;
  border-radius: 100px;
  background: var(--bg-4); border: 1px solid var(--border);
  font-size: 13px; font-weight: 600;
}
.verdict svg { width: 13px; height: 13px; }
.verdict.ai-wins { border-color: rgba(62,207,142,.25); color: var(--green); background: var(--green-dim); }
.verdict.human-wins { border-color: rgba(106,176,245,.25); color: var(--blue); background: var(--blue-dim); }
.verdict.tie { border-color: rgba(245,166,35,.25); color: var(--amber); background: var(--amber-dim); }
.verdict .delta { font-family: var(--font-mono); font-size: 10px; opacity: .7; }

.result-body { padding: 22px; }
.result-query {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--bg-3); border-radius: var(--radius);
  border-left: 2px solid var(--accent);
}
.rq-label {
  font-family: var(--font-mono); font-size: 10px; letter-spacing: .05em;
  text-transform: uppercase; color: var(--tx-3); margin-bottom: 6px;
}
.rq-text { font-size: 14px; color: var(--tx-2); line-height: 1.55; }

/* Score grid */
.score-grid {
  display: grid;
  grid-template-columns: 1fr 1px 1fr;
  gap: 16px;
  align-items: stretch;
}

.score-divider {
  width: 1px;
  background: var(--border);
}
.score-grid.single-col { grid-template-columns: 1fr; }
.score-col {}
.sc-head {
  display: flex; align-items: center; gap: 7px;
  font-size: 13px; font-weight: 600;
  margin-bottom: 14px; padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.sc-head svg { width: 14px; height: 14px; }
.sc-head.human-head { color: var(--tx-2); }
.sc-head.ai-head { color: var(--green); }

.score-panel {}
.ov-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.ov-left {}
.ov-label { font-family: var(--font-mono); font-size: 10px; color: var(--tx-3); letter-spacing: .04em; margin-bottom: 4px; }
.ov-score {
  font-family: var(--font-serif); font-size: 28px;
  color: var(--tx); margin-bottom: 2px;
}
.ov-score.green { color: var(--green); }
.ov-score.amber { color: var(--amber); }
.ov-score.red   { color: var(--red); }
.ov-score.na    { color: var(--tx-3); font-size: 22px; }
.ov-grade { font-size: 12px; color: var(--tx-3); }

/* Arc ring */
.arc-wrap { position: relative; width: 68px; height: 68px; flex-shrink: 0; }
.arc-svg { width: 68px; height: 68px; transform: rotate(-90deg); }
.arc-track { fill: none; stroke: var(--bg-4); stroke-width: 5; }
.arc-fill  { fill: none; stroke-width: 5; stroke-linecap: round; transition: stroke-dashoffset .8s cubic-bezier(.4,0,.2,1); }
.arc-pct {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 11px; color: var(--tx-2);
}

/* Dim bars */
.dim-bars { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.dim-row { display: flex; align-items: center; gap: 10px; }
.dim-name { font-size: 12px; color: var(--tx-3); width: 66px; }
.dim-track { flex: 1; height: 4px; background: var(--bg-4); border-radius: 2px; overflow: hidden; }
.dim-fill { height: 100%; border-radius: 2px; width: 0; transition: width .7s cubic-bezier(.4,0,.2,1); }
.dim-fill.semantic  { background: var(--green); }
.dim-fill.tone      { background: var(--blue); }
.dim-fill.structure { background: var(--amber); }
.dim-val { font-family: var(--font-mono); font-size: 10px; color: var(--tx-3); width: 34px; text-align: right; }

/* Feedback */
.fb-stack { display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }
.fb-item {
  display: flex; gap: 8px; padding: 8px 11px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  font-size: 12.5px; color: var(--tx-2); line-height: 1.5;
  animation: fadeIn .3s ease;
}
.fb-item.good { border-color: rgba(62,207,142,.2); background: var(--green-dim); }
.fb-item.warn { border-color: rgba(245,166,35,.2); background: var(--amber-dim); }
.fb-item.bad  { border-color: rgba(240,101,112,.2); background: var(--red-dim); }
.fb-icon { font-size: 11px; margin-top: 1px; flex-shrink: 0; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* Response text block */
.resp-block { margin-top: 12px; }
.resp-block-label {
  font-family: var(--font-mono); font-size: 10px; letter-spacing: .05em;
  text-transform: uppercase; color: var(--tx-3); margin-bottom: 6px;
}
.resp-block-text {
  font-size: 13.5px; line-height: 1.7; color: var(--tx-2);
  background: var(--bg-3); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 11px 13px;
  max-height: 140px; overflow-y: auto;
}
.resp-block-text.typewriter { font-style: italic; }

/* Policy badge */
.policy-badge {
  display: inline-flex; align-items: center; gap: 6px;
  margin-top: 12px; padding: 5px 12px;
  background: var(--bg-3); border: 1px solid var(--border);
  border-radius: 100px; font-family: var(--font-mono); font-size: 10px; color: var(--tx-3);
}

/* Result loading */
.result-loading {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  padding: 40px; color: var(--tx-3);
  font-family: var(--font-mono); font-size: 11px;
}

/* Score grid divider */
.score-divider {
  width: 1px; background: var(--border);
  margin: 0 8px; align-self: stretch;
}

/* NA panel */
.na-panel {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 120px; gap: 8px; text-align: center;
  color: var(--tx-3); font-size: 13px;
}

/* ── Toast ───────────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 24px; right: 24px;
  padding: 11px 18px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 13.5px; font-weight: 500; color: var(--tx);
  box-shadow: 0 8px 32px rgba(0,0,0,.5);
  transform: translateY(12px); opacity: 0;
  transition: all .2s cubic-bezier(.4,0,.2,1);
  z-index: 999; pointer-events: none; max-width: 340px;
}
.toast.show { transform: translateY(0); opacity: 1; }
.toast.success { border-color: rgba(62,207,142,.35); color: var(--green); }
.toast.error   { border-color: rgba(240,101,112,.35); color: var(--red); }
.toast.info    { border-color: rgba(106,176,245,.28); color: var(--blue); }

/* ── Responsive ──────────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .control-row { grid-template-columns: 1fr 1fr; }
  .load-block  { grid-column: 1 / -1; }
  .dual-panel  { grid-template-columns: 1fr 1px 1fr; }
  .panel-divider { flex-direction: row; padding: 12px 0; }
  .divider-line { height: 1px; width: auto; flex: 1; }
  .score-grid  { grid-template-columns: 1fr; }
  .score-divider { display: none; }
  .stats-grid  { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 580px) {
  .main { padding: 16px 14px 60px; }
  .header-inner { padding: 0 14px; }
  .control-row { grid-template-columns: 1fr; }
  .result-header { flex-direction: column; align-items: flex-start; gap: 10px; }
  .stats-grid { grid-template-columns: 1fr; }
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.logo-mark {
  display: inline-block;
  animation: spin-slow 6s linear infinite;
  transform-origin: 50% 50%;
  will-change: transform;
  filter: drop-shadow(0 0 6px rgba(62,207,142,0.4));
}

.logo-mark svg {
  width: 100%;
  height: 100%;
}

.logo-mark:hover {
  animation-duration: 2s;
}