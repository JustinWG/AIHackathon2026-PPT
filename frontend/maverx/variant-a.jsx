/* variant-a.jsx — Direction A: "Clean Studio"
   Centered single-column chat. White card on soft lilac page.
   Color used sparingly as accent. Friendly, product-y. */

function VariantA() {
  const B = useBuilder();
  const { phase, messages, botTyping, currentField, totalFields, answeredCount, meta } = B;
  const scrollRef = React.useRef(null);
  const [draft, setDraft] = React.useState('');

  React.useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, botTyping, phase]);

  const send = () => { if (draft.trim()) { B.submit(draft); setDraft(''); } };
  const stepNum = Math.min(answeredCount + 1, totalFields);

  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
      background: MVX.page, fontFamily: MVX.body, color: MVX.ink }}>

      {/* top bar */}
      <header style={{ flex: '0 0 auto', height: 62, display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', padding: '0 26px', background: MVX.surface,
        borderBottom: `1px solid ${MVX.line}` }}>
        <MvxLockup size={26} />
        <span style={{ display: 'flex', alignItems: 'center', gap: 8, fontFamily: MVX.display,
          fontSize: 11.5, fontWeight: 600, letterSpacing: '.02em', color: MVX.slate }}>
          <span style={{ width: 7, height: 7, borderRadius: 7, background: '#1F9B5B' }} />
          AI TRAINING BUILDER
        </span>
      </header>

      {/* centered stage */}
      <div style={{ flex: 1, minHeight: 0, display: 'flex', justifyContent: 'center', padding: '26px 24px' }}>
        <div style={{ width: '100%', maxWidth: 660, display: 'flex', flexDirection: 'column',
          background: MVX.surface, border: `1px solid ${MVX.line}`, borderRadius: 20,
          boxShadow: '0 18px 50px rgba(13,0,106,0.07)', overflow: 'hidden' }}>

          {/* card header + progress */}
          <div style={{ flex: '0 0 auto', padding: '18px 22px 16px', borderBottom: `1px solid ${MVX.line}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 11 }}>
              <h1 style={{ margin: 0, fontFamily: MVX.display, fontSize: 17, fontWeight: 600, letterSpacing: '-0.01em' }}>
                {phase === 'intake' ? 'Tell me about your training' :
                 phase === 'ready' ? 'Your brief is ready' :
                 phase === 'generating' ? 'Building your deck\u2026' : 'Your training is ready'}
              </h1>
              <span style={{ fontFamily: MVX.display, fontSize: 12, fontWeight: 600, color: MVX.faint }}>
                {phase === 'intake' ? `${stepNum} / ${totalFields}` : `${totalFields} / ${totalFields}`}
              </span>
            </div>
            <div style={{ display: 'flex', gap: 5 }}>
              {FIELDS.map((f, i) => {
                const filled = meta[f.key] != null;
                const active = phase === 'intake' && currentField && currentField.key === f.key;
                return (
                  <div key={f.key} style={{ flex: 1, height: 5, borderRadius: 3, position: 'relative',
                    background: filled ? MVX.ink : active ? MVX.orange : MVX.line,
                    transition: 'background .3s' }} />
                );
              })}
            </div>
          </div>

          {/* transcript */}
          <div ref={scrollRef} className="mvx-scroll" style={{ flex: 1, minHeight: 0, overflowY: 'auto',
            padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            {messages.map((m, i) => <Bubble key={i} m={m} />)}
            {botTyping && (
              <div className="mvx-msg" style={{ alignSelf: 'flex-start', display: 'flex', gap: 9, alignItems: 'flex-start' }}>
                <Avatar />
                <div style={{ background: MVX.pageWarm, borderRadius: '4px 14px 14px 14px', padding: '12px 14px' }}>
                  <TypingDots />
                </div>
              </div>
            )}
          </div>

          {/* dock — changes by phase */}
          <div style={{ flex: '0 0 auto', borderTop: `1px solid ${MVX.line}`, padding: '14px 18px',
            background: '#FCFBFE' }}>
            {(phase === 'intake') && (
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <textarea value={draft} onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                    placeholder={currentField ? currentField.hint : ''}
                    rows={1}
                    disabled={botTyping}
                    style={{ width: '100%', resize: 'none', border: `1.5px solid ${MVX.line}`, borderRadius: 12,
                      padding: '12px 14px', fontFamily: MVX.body, fontSize: 14, color: MVX.ink, outline: 'none',
                      background: botTyping ? MVX.page : '#fff', lineHeight: 1.4, boxSizing: 'border-box',
                      transition: 'border-color .15s' }}
                    onFocus={(e) => (e.target.style.borderColor = MVX.purple)}
                    onBlur={(e) => (e.target.style.borderColor = MVX.line)} />
                </div>
                <button onClick={send} disabled={!draft.trim() || botTyping}
                  style={{ flex: '0 0 auto', height: 44, width: 44, borderRadius: 12, border: 'none',
                    background: draft.trim() && !botTyping ? MVX.ink : MVX.line, color: '#fff', cursor: draft.trim() ? 'pointer' : 'default',
                    display: 'grid', placeItems: 'center', transition: 'background .15s' }}>
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M2 9h13M10 4l5 5-5 5"/></svg>
                </button>
              </div>
            )}

            {phase === 'ready' && (
              <button onClick={B.generate}
                style={{ width: '100%', height: 50, borderRadius: 13, border: 'none', cursor: 'pointer',
                  background: MVX.grad, color: '#fff', fontFamily: MVX.display, fontWeight: 600, fontSize: 15,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 9,
                  boxShadow: '0 10px 26px rgba(123,31,162,0.30)' }}>
                <SparkIcon /> Generate training
              </button>
            )}

            {phase === 'generating' && <GenProgress B={B} />}

            {phase === 'done' && <DonePanel B={B} />}
          </div>
        </div>
      </div>
    </div>
  );

  function Bubble({ m }) {
    if (m.role === 'user') {
      return (
        <div className="mvx-msg" style={{ alignSelf: 'flex-end', maxWidth: '80%', background: MVX.ink,
          color: '#fff', borderRadius: '14px 14px 4px 14px', padding: '11px 15px', fontSize: 14, lineHeight: 1.45 }}>
          {m.text}
        </div>
      );
    }
    return (
      <div className="mvx-msg" style={{ alignSelf: 'flex-start', maxWidth: '86%', display: 'flex', gap: 9, alignItems: 'flex-start' }}>
        <Avatar />
        <div>
          <div style={{ background: MVX.pageWarm, color: MVX.inkSoft, borderRadius: '4px 14px 14px 14px',
            padding: '11px 15px', fontSize: 14, lineHeight: 1.5,
            border: m.followup ? `1px solid ${MVX.orange}66` : 'none' }}>
            {m.followup && <span style={{ display: 'block', fontFamily: MVX.display, fontSize: 10.5, fontWeight: 700,
              letterSpacing: '.06em', color: MVX.orange, marginBottom: 4 }}>NEED A BIT MORE</span>}
            {m.text}
          </div>
          {m.summary && <BriefCard meta={m.summary} />}
        </div>
      </div>
    );
  }
}

function Avatar() {
  return (
    <span style={{ flex: '0 0 auto', width: 28, height: 28, borderRadius: 8, background: '#fff',
      border: `1px solid ${MVX.line}`, display: 'grid', placeItems: 'center' }}>
      <MvxMark size={16} />
    </span>
  );
}

function BriefCard({ meta }) {
  return (
    <div style={{ marginTop: 10, border: `1px solid ${MVX.line}`, borderRadius: 13, overflow: 'hidden', maxWidth: 380 }}>
      <div style={{ padding: '9px 14px', background: MVX.ink, color: '#fff', fontFamily: MVX.display,
        fontSize: 11, fontWeight: 600, letterSpacing: '.05em' }}>TRAINING BRIEF</div>
      <div style={{ padding: '6px 14px 10px' }}>
        {FIELDS.map((f) => meta[f.key] && (
          <div key={f.key} style={{ display: 'flex', gap: 10, padding: '6px 0', borderBottom: `1px solid ${MVX.page}` }}>
            <span style={{ flex: '0 0 78px', fontFamily: MVX.display, fontSize: 11.5, fontWeight: 600, color: MVX.faint }}>{f.short}</span>
            <span style={{ flex: 1, fontSize: 13, color: MVX.inkSoft, lineHeight: 1.4 }}>{meta[f.key]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function GenProgress({ B }) {
  const { genStep, genSteps } = B;
  return (
    <div style={{ padding: '2px 4px' }}>
      {genSteps.map((s, i) => {
        const state = i < genStep ? 'done' : i === genStep ? 'active' : 'todo';
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '5px 0',
            opacity: state === 'todo' ? 0.4 : 1, transition: 'opacity .3s' }}>
            <span style={{ flex: '0 0 auto', width: 18, height: 18, borderRadius: 9, display: 'grid', placeItems: 'center',
              background: state === 'done' ? '#1F9B5B' : state === 'active' ? 'transparent' : MVX.line,
              border: state === 'active' ? `2px solid ${MVX.purple}` : 'none' }}>
              {state === 'done' && <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round"><path d="M2 5.5L4.5 8 9 3"/></svg>}
              {state === 'active' && <span style={{ width: 9, height: 9, borderRadius: 5, border: `2px solid ${MVX.purple}`, borderTopColor: 'transparent', animation: 'mvxSpin .7s linear infinite' }} />}
            </span>
            <span style={{ fontSize: 13.5, fontFamily: MVX.display, fontWeight: state === 'active' ? 600 : 500,
              color: state === 'active' ? MVX.ink : MVX.slate }}>{s}{state === 'active' ? '\u2026' : ''}</span>
          </div>
        );
      })}
    </div>
  );
}

function DonePanel({ B }) {
  const { outline, meta } = B;
  const n = outline ? outline.slides.length : 9;
  const topicSlug = (meta.topic || 'training').toLowerCase().replace(/[^a-z0-9]+/g, '_').slice(0, 26);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
      <FileCard icon="PPTX" name={`${topicSlug}.pptx`} accent={MVX.ink}
        meta={`${n} editable slides · speaker notes on every slide`} />
      <div style={{ display: 'flex', gap: 9 }}>
        <div style={{ flex: 1 }}><FileCard compact icon="DOC" name="prebite.docx" accent={MVX.purple} meta="Pre-session prep" /></div>
        <div style={{ flex: 1 }}><FileCard compact icon="DOC" name="postbite.docx" accent={MVX.red} meta="Follow-up" /></div>
      </div>
      <button onClick={B.reset} style={{ marginTop: 2, background: 'transparent', border: 'none', cursor: 'pointer',
        fontFamily: MVX.display, fontSize: 12.5, fontWeight: 600, color: MVX.slate, padding: '4px' }}>
        \u21ba  Build another training
      </button>
    </div>
  );
}

Object.assign(window, { VariantA });
