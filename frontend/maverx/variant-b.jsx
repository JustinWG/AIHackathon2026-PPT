/* variant-b.jsx — Direction B: "Split Workspace"
   Left: compact guided chat. Right: a live deck preview that assembles the
   didactic arc as you answer, then builds into draft slides. Tool-like. */

function VariantB() {
  const Bld = useBuilder();
  const { phase, messages, botTyping, currentField, meta, answeredCount, totalFields, outline } = Bld;
  const scrollRef = React.useRef(null);
  const [draft, setDraft] = React.useState('');

  React.useEffect(() => { const el = scrollRef.current; if (el) el.scrollTop = el.scrollHeight; }, [messages, botTyping]);
  const send = () => { if (draft.trim()) { Bld.submit(draft); setDraft(''); } };

  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
      background: MVX.surface, fontFamily: MVX.body, color: MVX.ink }}>

      {/* top bar spanning both panes */}
      <header style={{ flex: '0 0 auto', height: 56, display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', padding: '0 22px', borderBottom: `1px solid ${MVX.line}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <MvxLockup size={24} />
          <span style={{ width: 1, height: 18, background: MVX.line }} />
          <span style={{ fontFamily: MVX.display, fontSize: 12.5, fontWeight: 500, color: MVX.slate }}>Training Builder</span>
        </div>
        <span style={{ display: 'flex', alignItems: 'center', gap: 7, fontFamily: MVX.display, fontSize: 11,
          fontWeight: 600, color: MVX.slate, background: MVX.page, padding: '5px 11px', borderRadius: 20 }}>
          <span style={{ width: 6, height: 6, borderRadius: 6, background: MVX.orange }} /> Maverx master template
        </span>
      </header>

      <div style={{ flex: 1, minHeight: 0, display: 'flex' }}>
        {/* LEFT — chat */}
        <div style={{ flex: '0 0 43%', display: 'flex', flexDirection: 'column', borderRight: `1px solid ${MVX.line}` }}>
          {/* field stepper */}
          <div style={{ flex: '0 0 auto', padding: '14px 20px 12px', borderBottom: `1px solid ${MVX.line}` }}>
            <div style={{ display: 'flex', gap: 7 }}>
              {FIELDS.map((f) => {
                const done = meta[f.key] != null;
                const active = phase === 'intake' && currentField && currentField.key === f.key;
                return (
                  <div key={f.key} style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <span style={{ height: 3, borderRadius: 2, background: done ? MVX.ink : active ? MVX.orange : MVX.line, transition: 'background .3s' }} />
                    <span style={{ fontFamily: MVX.display, fontSize: 9.5, fontWeight: 600, letterSpacing: '.03em',
                      color: done ? MVX.ink : active ? MVX.orange : MVX.faint, textTransform: 'uppercase' }}>{f.short}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div ref={scrollRef} className="mvx-scroll" style={{ flex: 1, minHeight: 0, overflowY: 'auto',
            padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map((m, i) => <MsgB key={i} m={m} />)}
            {botTyping && (
              <div className="mvx-msg" style={{ alignSelf: 'flex-start', background: MVX.page,
                borderRadius: '3px 12px 12px 12px', padding: '10px 13px' }}><TypingDots /></div>
            )}
          </div>

          {/* input */}
          <div style={{ flex: '0 0 auto', padding: '13px 16px', borderTop: `1px solid ${MVX.line}` }}>
            {phase === 'intake' && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', background: '#fff',
                border: `1.5px solid ${MVX.line}`, borderRadius: 11, padding: '4px 4px 4px 14px' }}>
                <input value={draft} onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
                  placeholder={currentField ? currentField.hint : ''} disabled={botTyping}
                  style={{ flex: 1, border: 'none', outline: 'none', fontFamily: MVX.body, fontSize: 13.5,
                    color: MVX.ink, background: 'transparent', minWidth: 0 }} />
                <button onClick={send} disabled={!draft.trim() || botTyping}
                  style={{ flex: '0 0 auto', width: 34, height: 34, borderRadius: 8, border: 'none',
                    background: draft.trim() && !botTyping ? MVX.ink : MVX.line, color: '#fff', cursor: draft.trim() ? 'pointer' : 'default', display: 'grid', placeItems: 'center' }}>
                  <svg width="15" height="15" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 9h13M10 4l5 5-5 5"/></svg>
                </button>
              </div>
            )}
            {phase === 'ready' && (
              <button onClick={Bld.generate} style={{ width: '100%', height: 44, borderRadius: 11, border: 'none',
                cursor: 'pointer', background: MVX.grad, color: '#fff', fontFamily: MVX.display, fontWeight: 600,
                fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <SparkIcon /> Generate deck
              </button>
            )}
            {phase === 'generating' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 4px', color: MVX.slate, fontFamily: MVX.display, fontSize: 13, fontWeight: 500 }}>
                <span style={{ width: 14, height: 14, borderRadius: 8, border: `2px solid ${MVX.purple}`, borderTopColor: 'transparent', animation: 'mvxSpin .7s linear infinite' }} />
                {Bld.genSteps[Math.min(Bld.genStep, Bld.genSteps.length - 1)]}…
              </div>
            )}
            {phase === 'done' && (
              <button onClick={Bld.reset} style={{ width: '100%', height: 40, borderRadius: 10, cursor: 'pointer',
                background: 'transparent', border: `1px solid ${MVX.line}`, color: MVX.slate, fontFamily: MVX.display, fontWeight: 600, fontSize: 13 }}>
                ↺  Start a new training
              </button>
            )}
          </div>
        </div>

        {/* RIGHT — live deck preview */}
        <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: MVX.page }}>
          <DeckPreview Bld={Bld} />
        </div>
      </div>
    </div>
  );

  function MsgB({ m }) {
    if (m.role === 'user') {
      return <div className="mvx-msg" style={{ alignSelf: 'flex-end', maxWidth: '82%', background: MVX.ink, color: '#fff',
        borderRadius: '12px 12px 3px 12px', padding: '9px 13px', fontSize: 13.5, lineHeight: 1.4 }}>{m.text}</div>;
    }
    return (
      <div className="mvx-msg" style={{ alignSelf: 'flex-start', maxWidth: '88%' }}>
        <div style={{ background: m.followup ? '#FFF6EC' : MVX.page, border: m.followup ? `1px solid ${MVX.orange}55` : `1px solid ${MVX.line}`,
          color: MVX.inkSoft, borderRadius: '3px 12px 12px 12px', padding: '10px 13px', fontSize: 13.5, lineHeight: 1.48 }}>
          {m.followup && <span style={{ display: 'block', fontFamily: MVX.display, fontSize: 9.5, fontWeight: 700, letterSpacing: '.06em', color: MVX.orange, marginBottom: 3 }}>NEED A BIT MORE</span>}
          {m.text}
        </div>
      </div>
    );
  }
}

// ── Right pane: the deck that builds itself ────────────────────
function DeckPreview({ Bld }) {
  const { phase, meta, outline, answeredCount } = Bld;
  const building = phase === 'intake';

  return (
    <>
      <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '13px 22px', borderBottom: `1px solid ${MVX.line}` }}>
        <span style={{ fontFamily: MVX.display, fontSize: 12.5, fontWeight: 600, color: MVX.inkSoft, letterSpacing: '.02em' }}>
          {building ? 'DECK PREVIEW' : `DRAFT DECK \u00B7 ${outline.slides.length} SLIDES`}
        </span>
        <span style={{ fontFamily: MVX.display, fontSize: 11, fontWeight: 600, color: MVX.faint }}>
          {building ? 'assembling\u2026' : `${outline.mins} min`}
        </span>
      </div>

      <div className="mvx-scroll" style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '20px 22px' }}>
        {/* mini title slide */}
        <div style={{ borderRadius: 12, overflow: 'hidden', boxShadow: '0 8px 26px rgba(13,0,106,0.10)',
          border: `1px solid ${MVX.line}`, marginBottom: 18 }}>
          <div style={{ position: 'relative', aspectRatio: '16 / 7', background: MVX.gradSoft, padding: '20px 22px',
            display: 'flex', flexDirection: 'column', justifyContent: 'space-between', color: '#fff' }}>
            <MvxMark size={26} style={{ filter: 'brightness(0) invert(1)' }} />
            <div>
              <div style={{ fontFamily: MVX.display, fontSize: 20, fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.1,
                color: '#fff', opacity: meta.topic ? 1 : 0.35, transition: 'opacity .4s' }}>
                {meta.topic ? titleCase(meta.topic) : 'Your training title'}
              </div>
              <div style={{ fontFamily: MVX.body, fontSize: 12.5, marginTop: 6, color: 'rgba(255,255,255,.82)',
                opacity: meta.audience ? 1 : 0.3, transition: 'opacity .4s' }}>
                {meta.audience ? `for ${meta.audience}` : 'for your audience'} · maverx.nl
              </div>
            </div>
          </div>
        </div>

        {building ? <ArcSkeleton meta={meta} answeredCount={answeredCount} /> : <SlideList Bld={Bld} />}
      </div>

      {phase === 'done' && (
        <div style={{ flex: '0 0 auto', borderTop: `1px solid ${MVX.line}`, background: '#fff', padding: '12px 16px',
          display: 'flex', gap: 9 }}>
          <div style={{ flex: 2 }}><FileCard compact icon="PPTX" accent={MVX.ink}
            name={`${slug(meta.topic)}.pptx`} meta={`${outline.slides.length} editable slides`} /></div>
          <div style={{ flex: 1 }}><FileCard compact icon="DOC" accent={MVX.purple} name="prebite.docx" meta="Prep" /></div>
          <div style={{ flex: 1 }}><FileCard compact icon="DOC" accent={MVX.red} name="postbite.docx" meta="Follow-up" /></div>
        </div>
      )}
    </>
  );
}

// Skeleton of the didactic arc shown during intake
function ArcSkeleton({ meta, answeredCount }) {
  const arc = Object.keys(BLOCKS);
  return (
    <div>
      <div style={{ fontSize: 12, color: MVX.slate, marginBottom: 14, lineHeight: 1.5 }}>
        Every Maverx training follows the same arc. It fills in as you answer.
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
        {arc.map((k, i) => {
          const b = BLOCKS[k];
          const lit = answeredCount > i || (answeredCount >= 1 && i < 2);
          return (
            <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '13px 15px',
              background: '#fff', borderRadius: 11, border: `1px solid ${MVX.line}`,
              opacity: lit ? 1 : 0.5, transition: 'opacity .4s' }}>
              <span style={{ width: 9, height: 9, borderRadius: 5, background: b.color }} />
              <span style={{ fontFamily: MVX.display, fontSize: 13.5, fontWeight: 600, color: MVX.ink, flex: 1 }}>{b.label}</span>
              <span style={{ flex: 2, height: 7, borderRadius: 4, background: lit ? b.tint : MVX.line, transition: 'background .4s' }} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

// The drafted slide list
function SlideList({ Bld }) {
  const { outline, phase, genStep, genSteps } = Bld;
  const total = outline.slides.length;
  // during generating, reveal slides progressively
  const revealed = phase === 'generating'
    ? Math.round(((genStep + 1) / (genSteps.length + 1)) * total)
    : total;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {outline.slides.map((s, i) => {
        const b = BLOCKS[s.block];
        const shown = i < revealed || phase !== 'generating';
        return (
          <div key={i} className="mvx-msg" style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
            background: '#fff', borderRadius: 10, border: `1px solid ${MVX.line}`, borderLeft: `3px solid ${b.color}`,
            opacity: shown ? 1 : 0.32, transition: 'opacity .4s' }}>
            <span style={{ fontFamily: MVX.display, fontSize: 11, fontWeight: 700, color: MVX.faint, width: 18, fontVariantNumeric: 'tabular-nums' }}>{String(i + 1).padStart(2, '0')}</span>
            <span style={{ flex: 1, minWidth: 0 }}>
              <span style={{ display: 'block', fontFamily: MVX.display, fontSize: 13.5, fontWeight: 600, color: MVX.ink,
                whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.title}</span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginTop: 3 }}>
                <span style={{ fontFamily: MVX.display, fontSize: 9.5, fontWeight: 700, letterSpacing: '.04em',
                  color: b.color, background: b.tint, padding: '2px 7px', borderRadius: 5, textTransform: 'uppercase' }}>{b.label}</span>
                <span style={{ fontSize: 11, color: MVX.faint }}>{s.t} min</span>
              </span>
            </span>
            {(phase === 'done') && <NotesGlyph />}
          </div>
        );
      })}
    </div>
  );
}

function NotesGlyph() {
  return (
    <span title="Speaker notes attached" style={{ flex: '0 0 auto', display: 'inline-flex', alignItems: 'center', gap: 4,
      fontFamily: MVX.display, fontSize: 10, fontWeight: 600, color: '#1F9B5B' }}>
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M2 3h8M2 6h8M2 9h5"/></svg>
      notes
    </span>
  );
}

function titleCase(s) { return s.replace(/\.$/, '').replace(/\b\w/g, (c) => c.toUpperCase()); }
function slug(s) { return (s || 'training').toLowerCase().replace(/[^a-z0-9]+/g, '_').slice(0, 24); }

Object.assign(window, { VariantB });
