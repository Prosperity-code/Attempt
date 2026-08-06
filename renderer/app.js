// ==================== 番茄钟 — Electron 版 ====================

const R = 105;
const CIRCUM = 2 * Math.PI * R;

const MODES = {
  work:       { min: 25, emoji: '🍅', label: '专注中...',   endEmoji: '🎉', endText: '专注完成！休息一下吧~' },
  shortBreak: { min: 5,  emoji: '☕', label: '休息中...',   endEmoji: '☕', endText: '休息结束，继续加油！' },
  longBreak:  { min: 15, emoji: '🌿', label: '放松中...',   endEmoji: '🌿', endText: '休息结束，开始新的番茄！' },
};

// ===== DOM =====
const $ = (id) => document.getElementById(id);
const elRing      = $('ring');
const elMm        = $('mm');
const elSs        = $('ss');
const elStatus    = $('status');
const elBtnPlay   = $('btnPlay');
const elBtnPause  = $('btnPause');
const elBtnReset  = $('btnReset');
const elOverlay   = $('overlay');
const elOvEmoji   = $('ovEmoji');
const elOvText    = $('ovText');
const elCntSess   = $('cntSessions');
const elCntMin    = $('cntMinutes');
const elCntStreak = $('cntStreak');
const elTabs      = document.querySelectorAll('.tab');
const elBody      = document.body;
const elTime      = $('timeDisplay');
const elBtnTop    = $('btnTop');
const elBtnMin    = $('btnMin');
const elBtnClose  = $('btnClose');

// ===== 状态 =====
let mode        = 'work';
let timeLeft    = MODES.work.min * 60;
let totalSec    = MODES.work.min * 60;
let timerId     = null;
let running     = false;
let alwaysOnTop = false;
let sessions    = 0;
let minutes     = 0;
let streak      = 0;

// ===== 音频 =====
let ctx = null;
function ac() {
  if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
  return ctx;
}
function beep(freq, dur, type = 'sine', vol = 0.3) {
  try {
    const c = ac();
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, c.currentTime);
    g.gain.setValueAtTime(vol, c.currentTime);
    g.gain.exponentialRampToValueAtTime(0.01, c.currentTime + dur);
    o.connect(g); g.connect(c.destination);
    o.start(); o.stop(c.currentTime + dur);
  } catch (_) {}
}
function playComplete() {
  [523, 659, 784, 1047].forEach((f, i) => setTimeout(() => beep(f, 0.35, 'sine', 0.25), i * 120));
}
function playTick() { beep(800, 0.06, 'sine', 0.12); }

// ===== 显示 =====
function render() {
  const m = Math.floor(timeLeft / 60);
  const s = timeLeft % 60;
  elMm.textContent = String(m).padStart(2, '0');
  elSs.textContent = String(s).padStart(2, '0');

  const pct = timeLeft / totalSec;
  elRing.style.strokeDasharray = CIRCUM;
  elRing.style.strokeDashoffset = CIRCUM * (1 - pct);

  elRing.classList.toggle('break', mode !== 'work');
  elRing.classList.toggle('urgent', running && timeLeft <= 10 && timeLeft > 0);
  elBody.classList.toggle('urgent', running && timeLeft <= 10 && timeLeft > 0);
  elBody.classList.toggle('running', running);
}

function setStatus(text) { elStatus.textContent = text; }
function defaultStatus() {
  const c = MODES[mode];
  return mode === 'work' ? '准备开始专注' : `${c.emoji} ${c.label} (${c.min}分钟)`;
}

// ===== 按钮状态 =====
function syncBtns() {
  elBtnPlay.style.display  = running ? 'none' : 'flex';
  elBtnPause.style.display = running ? 'flex' : 'none';
  elBtnPause.disabled = !running;

  elTabs.forEach(t => {
    t.classList.toggle('active', t.dataset.mode === mode);
    t.disabled = running;
  });
}

// ===== 操作 =====
function start() {
  if (timeLeft <= 0) reset(false);
  ac(); // 解锁 Web Audio
  running = true;
  syncBtns();
  setStatus(MODES[mode].label);

  timerId = setInterval(() => {
    timeLeft--;
    render();
    if (running && timeLeft <= 5 && timeLeft > 0) playTick();
    if (timeLeft <= 0) complete();
  }, 1000);
}

function pause() {
  running = false;
  clearInterval(timerId);
  timerId = null;
  syncBtns();
  setStatus('已暂停 ⏸');
}

function reset(silent = false) {
  running = false;
  clearInterval(timerId);
  timerId = null;
  timeLeft = MODES[mode].min * 60;
  totalSec = timeLeft;
  render();
  syncBtns();
  if (!silent) setStatus(defaultStatus());
}

function switchMode(m) {
  mode = m;
  timeLeft = MODES[m].min * 60;
  totalSec = timeLeft;
  render();
  syncBtns();
  if (!running) setStatus(defaultStatus());
}

// ===== 完成 =====
function complete() {
  running = false;
  clearInterval(timerId);
  timerId = null;

  playComplete();

  if (mode === 'work') {
    sessions++;
    minutes += MODES.work.min;
    save();
    showOverlay(MODES.work.endEmoji, MODES.work.endText);
    if (window.electronAPI) {
      window.electronAPI.notify({ title: '🍅 番茄钟', body: '专注时间结束！休息一下吧~' });
    }
    switchMode('shortBreak');
    reset(true);
  } else {
    showOverlay(MODES[mode].endEmoji, MODES[mode].endText);
    if (window.electronAPI) {
      window.electronAPI.notify({ title: '🍅 番茄钟', body: '休息结束，准备开始新的番茄！' });
    }
    switchMode('work');
    reset(true);
  }
  syncBtns();
}

// ===== 遮罩 =====
function showOverlay(emoji, text) {
  elOvEmoji.textContent = emoji;
  elOvText.textContent = text;
  elOverlay.classList.add('show');
  setTimeout(() => elOverlay.classList.remove('show'), 2500);
}

// ===== 持久化 =====
const SK = 'pomodoro_electron_v1';
function load() {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const raw = localStorage.getItem(SK);
    const d = raw ? JSON.parse(raw) : {};
    if (d.date === today) {
      sessions = d.sessions || 0;
      minutes  = d.focus || 0;
    }
    if (d.date) {
      const last = new Date(d.date);
      const yday = new Date();
      yday.setDate(yday.getDate() - 1);
      if (last.toISOString().slice(0, 10) === yday.toISOString().slice(0, 10)) {
        streak = (d.streak || 0) + 1;
      } else if (d.date !== today) {
        streak = 0;
      } else {
        streak = d.streak || 0;
      }
    }
    if (sessions > 0 && streak === 0) streak = 1;
    updateStats();
  } catch (_) {}
}
function save() {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const raw = localStorage.getItem(SK);
    const d = raw ? JSON.parse(raw) : {};
    let s = d.streak || 0;
    if (d.date && d.date !== today) {
      const last = new Date(d.date);
      const yday = new Date();
      yday.setDate(yday.getDate() - 1);
      if (last.toISOString().slice(0,10) === yday.toISOString().slice(0,10)) s += 1; else s = 1;
    } else { s = Math.max(s, 1); }
    localStorage.setItem(SK, JSON.stringify({ date: today, sessions, focus: minutes, streak: s }));
    streak = s;
    updateStats();
  } catch (_) {}
}
function updateStats() {
  elCntSess.textContent   = sessions;
  elCntMin.textContent    = minutes + ' min';
  elCntStreak.textContent = streak;
}

// ===== 标题栏按钮 =====
elBtnTop.addEventListener('click', () => {
  alwaysOnTop = !alwaysOnTop;
  elBtnTop.classList.toggle('on', alwaysOnTop);
  if (window.electronAPI) window.electronAPI.toggleTop(alwaysOnTop);
});
elBtnMin.addEventListener('click',  () => window.electronAPI?.minimize());
elBtnClose.addEventListener('click', () => window.electronAPI?.quit());

// ===== 计时按钮 =====
elBtnPlay.addEventListener('click', start);
elBtnPause.addEventListener('click', pause);
elBtnReset.addEventListener('click', () => reset(false));

// ===== 模式标签 =====
elTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    if (!running && tab.dataset.mode !== mode) switchMode(tab.dataset.mode);
  });
});

// ===== 遮罩点击关闭 =====
elOverlay.addEventListener('click', () => elOverlay.classList.remove('show'));

// ===== 键盘快捷键 =====
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  switch (e.code) {
    case 'Space':
      e.preventDefault();
      running ? pause() : start();
      break;
    case 'KeyR':
      if (!e.ctrlKey && !e.metaKey) { e.preventDefault(); reset(false); }
      break;
    case 'Digit1': if (!e.ctrlKey && !e.metaKey && !running) { e.preventDefault(); switchMode('work'); } break;
    case 'Digit2': if (!e.ctrlKey && !e.metaKey && !running) { e.preventDefault(); switchMode('shortBreak'); } break;
    case 'Digit3': if (!e.ctrlKey && !e.metaKey && !running) { e.preventDefault(); switchMode('longBreak'); } break;
  }
});

// ===== 初始化 =====
render();
syncBtns();
setStatus(defaultStatus());
load();
