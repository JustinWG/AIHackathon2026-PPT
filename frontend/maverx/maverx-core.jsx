/* maverx-core.jsx — shared brand tokens, logo mark, and the training-builder
   state machine used by all three design directions. Exports to window. */

// ─────────────────────────────────────────────────────────────
// Fonts + brand tokens
// ─────────────────────────────────────────────────────────────
(function injectFonts() {
  if (document.getElementById('mvx-fonts')) return;
  const l = document.createElement('link');
  l.id = 'mvx-fonts';
  l.rel = 'stylesheet';
  l.href = 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Raleway:wght@400;500;600;700&display=swap';
  document.head.appendChild(l);
})();

const MVX = {
  ink: '#0D006A',        // primary dark blue
  inkSoft: '#3B3470',    // muted heading
  orange: '#F59235',
  red: '#F04E5B',
  purple: '#6A1F9C',
  slate: '#6B6685',      // secondary body text
  faint: '#9A95B0',
  line: '#E7E3F2',
  surface: '#FFFFFF',
  page: '#F5F3FB',
  pageWarm: '#F3F1F9',
  grad: 'linear-gradient(120deg, #45228A 0%, #7B1FA2 34%, #C81E8E 62%, #F58D25 100%)',
  gradSoft: 'linear-gradient(120deg, #2C1259 0%, #5A1C86 50%, #9A1E7E 100%)',
  display: '"Space Grotesk", system-ui, sans-serif',
  body: '"Raleway", system-ui, sans-serif',
};

// per-didactic-block accent (used by the live spec preview + chips)
const BLOCKS = {
  kickoff:  { label: 'Kickoff',  color: '#0D006A', tint: '#E9E7FA' },
  theory:   { label: 'Theory',   color: '#6A1F9C', tint: '#F0E6FA' },
  example:  { label: 'Example',  color: '#C81E8E', tint: '#FBE6F4' },
  exercise: { label: 'Exercise', color: '#F59235', tint: '#FDEEDD' },
  wrapup:   { label: 'Wrap-up',  color: '#F04E5B', tint: '#FCE6E8' },
};

// ─────────────────────────────────────────────────────────────
// Logo mark + lockup
// ─────────────────────────────────────────────────────────────
function MvxMark({ size = 30, style = {} }) {
  return (
    <img src="mark.png" alt="Maverx" width={size} height={size * 0.92}
      style={{ display: 'block', objectFit: 'contain', ...style }} />
  );
}

function MvxLockup({ size = 30, color = MVX.ink, gap = 9, style = {} }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap, ...style }}>
      <MvxMark size={size} />
      <span style={{ fontFamily: MVX.display, fontWeight: 700, fontSize: size * 0.72,
        letterSpacing: '-0.02em', color }}>maverx</span>
    </span>
  );
}

// ─────────────────────────────────────────────────────────────
// Intake field definitions — questions, vagueness detection, follow-ups
// ─────────────────────────────────────────────────────────────
const FIELDS = [
  {
    key: 'topic',
    short: 'Topic',
    q: 'What skill or topic should this training teach?',
    hint: 'e.g. Prompt engineering for marketing copy',
    vague: (a) => {
      const t = a.trim().toLowerCase();
      if (t.length < 4 || /^(ai|stuff|something|general|things?)\b/.test(t) || t === 'ai related')
        return 'That\u2019s a little broad. Which specific skill should people walk away able to do — e.g. \u201Cwriting effective prompts\u201D or \u201Cspotting AI errors\u201D?';
      return null;
    },
  },
  {
    key: 'audience',
    short: 'Audience',
    q: 'Who is it for? Tell me their role or department.',
    hint: 'e.g. The marketing team, no prior AI experience',
    vague: (a) => {
      const t = a.trim().toLowerCase();
      if (/^(everyone|our team|the team|all|staff|people|us)\.?$/.test(t))
        return 'Got it \u2014 which role or department exactly? Knowing whether they\u2019re marketers, analysts, or managers changes the examples I use.';
      return null;
    },
  },
  {
    key: 'level',
    short: 'Level',
    q: 'What level should I pitch it at \u2014 beginner, intermediate, or advanced?',
    hint: 'Beginner · Intermediate · Advanced',
    vague: (a) => {
      const t = a.trim().toLowerCase();
      if (!/(beginner|intermediate|advanced|basic|novice|expert|no experience|new)/.test(t))
        return 'Just so I calibrate the depth: would you call them beginner, intermediate, or advanced on this topic?';
      return null;
    },
  },
  {
    key: 'duration',
    short: 'Duration',
    q: 'How long is the session? Give me a number of minutes.',
    hint: 'e.g. 180 minutes',
    vague: (a) => {
      if (!/\d/.test(a))
        return 'I need a concrete length to pace the slides. Roughly how many minutes \u2014 e.g. 90, 120, 180?';
      return null;
    },
  },
  {
    key: 'objective',
    short: 'Objective',
    q: 'Last one: what should participants be able to DO afterwards?',
    hint: 'e.g. Write and refine prompts for campaign briefs',
    vague: (a) => {
      const t = a.trim().toLowerCase();
      if (t.length < 8 || /^(learn|understand|know)( stuff| things| ai)?\.?$/.test(t))
        return 'Let\u2019s make that measurable \u2014 finish this sentence: \u201CBy the end, participants can \u2026\u201D';
      return null;
    },
  },
];

function parseMinutes(s) {
  const m = String(s).match(/(\d+(?:\.\d+)?)\s*(h|hour|hr|min|m)?/i);
  if (!m) return 120;
  let n = parseFloat(m[1]);
  const unit = (m[2] || '').toLowerCase();
  if (/^h/.test(unit) || (n <= 8 && /hour|hr|h/.test(s))) n *= 60;
  return Math.round(n);
}

// Build a believable deck outline from the collected meta.
function buildOutline(meta) {
  const mins = parseMinutes(meta.duration || '120');
  const topic = (meta.topic || 'the topic').replace(/\.$/, '');
  const Topic = topic.charAt(0).toUpperCase() + topic.slice(1);
  const plan = [
    { block: 'kickoff',  title: 'About this session',      t: 5 },
    { block: 'kickoff',  title: 'Agenda & timetable',      t: 5 },
    { block: 'theory',   title: `${Topic}: the core idea`, t: 12 },
    { block: 'theory',   title: 'Why it matters now',      t: 8 },
    { block: 'example',  title: `${Topic} in practice`,    t: 12 },
    { block: 'exercise', title: `Try it yourself`,         t: Math.max(20, Math.round(mins * 0.3)) },
    { block: 'exercise', title: 'Work on your own case',   t: Math.max(10, Math.round(mins * 0.12)) },
    { block: 'wrapup',   title: 'Key takeaways',           t: 6 },
    { block: 'wrapup',   title: 'What\u2019s next?',       t: 5 },
  ];
  // pad/trim toward ~4 min per slide
  const target = Math.max(6, Math.min(14, Math.round(mins / 4)));
  let slides = plan.slice();
  if (target > plan.length) {
    slides.splice(5, 0, { block: 'example', title: 'A second example', t: 8 });
  }
  if (target < slides.length) slides = slides.slice(0, target);
  return { slides, mins };
}

// ─────────────────────────────────────────────────────────────
// useBuilder — the shared state machine
//   phase: 'intake' → 'ready' → 'generating' → 'done'
// ─────────────────────────────────────────────────────────────
const GEN_STEPS = [
  'Planning the didactic arc',
  'Writing slide content',
  'Injecting into the Maverx master template',
  'Adding trainer speaker notes',
  'Building pre-bite & post-bite docs',
];

// Same-origin backend (FastAPI serves this frontend); relative URLs avoid CORS.
const API_BASE = '';

// Trigger a browser download of text content (used for spec.json / bite docs
// while the real .pptx/.docx renderer—Person A's engine—is still pending).
function downloadText(filename, text, type = 'text/plain') {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function useBuilder() {
  const [phase, setPhase] = React.useState('intake');
  const [fieldIdx, setFieldIdx] = React.useState(0);
  const [followupActive, setFollowup] = React.useState(false);
  const [meta, setMeta] = React.useState({});
  const [spec, setSpec] = React.useState(null);
  const [genError, setGenError] = React.useState(null);
  const [messages, setMessages] = React.useState(() => ([
    { role: 'bot', text: 'Hi! I\u2019m the Maverx training builder. Answer five quick questions and I\u2019ll generate a complete, on-brand, editable deck \u2014 with speaker notes and prep docs.' },
    { role: 'bot', text: FIELDS[0].q, field: FIELDS[0].key },
  ]));
  const [botTyping, setBotTyping] = React.useState(false);
  const [genStep, setGenStep] = React.useState(-1);

  const totalFields = FIELDS.length;
  const currentField = phase === 'intake' ? FIELDS[fieldIdx] : null;
  const answeredCount = Object.keys(meta).length;

  const pushBot = React.useCallback((text, extra = {}) => {
    setBotTyping(true);
    const delay = 520 + Math.min(900, text.length * 9);
    setTimeout(() => {
      setBotTyping(false);
      setMessages((m) => [...m, { role: 'bot', text, ...extra }]);
    }, delay);
  }, []);

  const submit = React.useCallback((raw) => {
    const text = raw.trim();
    if (!text || phase !== 'intake' || botTyping) return;
    setMessages((m) => [...m, { role: 'user', text }]);
    const field = FIELDS[fieldIdx];

    // vagueness check (only once per field)
    if (!followupActive) {
      const fu = field.vague(text);
      if (fu) {
        setFollowup(true);
        pushBot(fu, { field: field.key, followup: true });
        return;
      }
    }

    // accept value
    const value = text;
    const nextMeta = { ...meta, [field.key]: value };
    setMeta(nextMeta);
    setFollowup(false);

    const nextIdx = fieldIdx + 1;
    if (nextIdx < FIELDS.length) {
      setFieldIdx(nextIdx);
      pushBot(FIELDS[nextIdx].q, { field: FIELDS[nextIdx].key });
    } else {
      // done with intake
      setBotTyping(true);
      setTimeout(() => {
        setBotTyping(false);
        setMessages((m) => [...m, {
          role: 'bot',
          text: 'That\u2019s everything I need. Here\u2019s your brief \u2014 generate when you\u2019re ready.',
          summary: nextMeta,
        }]);
        setPhase('ready');
      }, 700);
    }
  }, [phase, fieldIdx, followupActive, meta, botTyping, pushBot]);

  const generate = React.useCallback(async () => {
    if (phase !== 'ready' && phase !== 'done') return;
    setPhase('generating');
    setGenError(null);
    setSpec(null);
    setGenStep(0);
    // advance the step animation while the request is in flight
    let i = 0;
    const interval = setInterval(() => {
      i = Math.min(i + 1, GEN_STEPS.length - 1);
      setGenStep(i);
    }, 1500);
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(meta),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try { detail = (await res.json()).detail || detail; } catch (_) {}
        throw new Error(detail);
      }
      setSpec(await res.json());
    } catch (e) {
      setGenError(String((e && e.message) || e));
    } finally {
      clearInterval(interval);
      setGenStep(GEN_STEPS.length);
      setPhase('done');
    }
  }, [phase, meta]);

  const reset = React.useCallback(() => {
    setPhase('intake'); setFieldIdx(0); setFollowup(false); setMeta({}); setGenStep(-1);
    setSpec(null); setGenError(null);
    setMessages([
      { role: 'bot', text: 'Fresh start. Let\u2019s build another training.' },
      { role: 'bot', text: FIELDS[0].q, field: FIELDS[0].key },
    ]);
  }, []);

  // Prefer the REAL backend spec once it arrives; fall back to the client-side
  // estimate before generation so the live brief still renders during intake.
  const outline = React.useMemo(() => {
    if (spec && Array.isArray(spec.slides)) {
      return {
        slides: spec.slides.map((s) => ({ block: s.block, title: s.title, t: 0 })),
        mins: parseMinutes(meta.duration || '120'),
        real: true,
      };
    }
    return (phase === 'ready' || phase === 'generating' || phase === 'done')
      ? buildOutline(meta) : null;
  }, [spec, phase, meta]);

  return {
    phase, meta, messages, botTyping, currentField, totalFields, answeredCount,
    genStep, genSteps: GEN_STEPS, outline, spec, genError, downloadText,
    submit, generate, reset,
  };
}

// ─────────────────────────────────────────────────────────────
// Small shared UI atoms
// ─────────────────────────────────────────────────────────────
function TypingDots({ color = MVX.faint }) {
  return (
    <span style={{ display: 'inline-flex', gap: 4, alignItems: 'center', padding: '2px 0' }}>
      {[0, 1, 2].map((i) => (
        <span key={i} style={{ width: 6, height: 6, borderRadius: 6, background: color,
          animation: `mvxBlink 1s ${i * 0.16}s infinite ease-in-out` }} />
      ))}
    </span>
  );
}

function FileCard({ icon, kind, name, meta, onClick, accent = MVX.ink, compact = false }) {
  const [done, setDone] = React.useState(false);
  return (
    <button onClick={() => { setDone(true); onClick && onClick(); }}
      style={{ display: 'flex', alignItems: 'center', gap: 13, width: '100%', textAlign: 'left',
        background: MVX.surface, border: `1px solid ${MVX.line}`, borderRadius: 12,
        padding: compact ? '11px 13px' : '14px 16px', cursor: 'pointer', fontFamily: MVX.body,
        transition: 'border-color .15s, box-shadow .15s, transform .1s' }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = accent; e.currentTarget.style.boxShadow = '0 6px 22px rgba(13,0,106,0.10)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = MVX.line; e.currentTarget.style.boxShadow = 'none'; }}>
      <span style={{ flex: '0 0 auto', width: 40, height: 40, borderRadius: 9, display: 'grid',
        placeItems: 'center', background: accent + '14', color: accent, fontFamily: MVX.display,
        fontWeight: 700, fontSize: 12 }}>{icon}</span>
      <span style={{ flex: 1, minWidth: 0 }}>
        <span style={{ display: 'block', fontFamily: MVX.display, fontWeight: 600, fontSize: 14,
          color: MVX.ink, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{name}</span>
        <span style={{ display: 'block', fontSize: 11.5, color: MVX.slate, marginTop: 1 }}>{meta}</span>
      </span>
      <span style={{ flex: '0 0 auto', fontSize: 12, fontWeight: 600, fontFamily: MVX.display,
        color: done ? '#1F9B5B' : accent }}>{done ? '\u2713 Saved' : 'Download'}</span>
    </button>
  );
}

function SparkIcon({ size = 17 }) {
  return <svg width={size} height={size} viewBox="0 0 17 17" fill="currentColor"><path d="M8.5 0l1.6 5.3L15.5 7l-5.4 1.7L8.5 14l-1.6-5.3L1.5 7l5.4-1.7z"/></svg>;
}

// keyframes
(function injectKeyframes() {
  if (document.getElementById('mvx-keyframes')) return;
  const s = document.createElement('style');
  s.id = 'mvx-keyframes';
  s.textContent = `
    @keyframes mvxBlink{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-2px)}}
    @keyframes mvxIn{from{transform:translateY(7px)}to{transform:translateY(0)}}
    @keyframes mvxSpin{to{transform:rotate(360deg)}}
    @keyframes mvxBar{from{width:0}}
    .mvx-msg{animation:mvxIn .32s cubic-bezier(.2,.7,.3,1)}
    @media (prefers-reduced-motion: reduce){.mvx-msg{animation:none}}
    .mvx-scroll::-webkit-scrollbar{width:0;display:none}
    .mvx-scroll{scrollbar-width:none}
  `;
  document.head.appendChild(s);
})();

Object.assign(window, { MVX, BLOCKS, FIELDS, MvxMark, MvxLockup, useBuilder, TypingDots, FileCard, SparkIcon, buildOutline, parseMinutes });
