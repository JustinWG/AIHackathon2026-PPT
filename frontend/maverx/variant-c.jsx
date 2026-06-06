/* variant-c.jsx — Direction C: "Gradient-forward"
   A vivid brand rail on the left doubling as a live brief; an airy,
   one-question-at-a-time focus wizard on the right. Editorial & premium. */

function VariantC() {
  const Bld = useBuilder();
  const { phase, messages, botTyping, currentField, meta, answeredCount, totalFields, outline } = Bld;
  const [draft, setDraft] = React.useState('');
  const inputRef = React.useRef(null);

  React.useEffect(() => {
    if (phase === 'intake' && !botTyping && inputRef.current) inputRef.current.focus();
  }, [botTyping, phase, messages.length]);

  const send = () => { if (draft.trim()) { Bld.submit(draft); setDraft(''); } };
  const lastBot = [...messages].reverse().find((m) => m.role === 'bot');
  const isFollowup = lastBot && lastBot.followup;

  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', fontFamily: MVX.body, color: MVX.ink, background: '#fff' }}>

      {/* ── LEFT: gradient rail / live brief ── */}
      <div style={{ flex: '0 0 37%', maxWidth: 480, minWidth: 340, position: 'relative', background: MVX.grad, color: '#fff',
        padding: '34px 32px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* soft glow */}
        <div style={{ position: 'absolute', top: -120, right: -120, width: 320, height: 320, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.22), transparent 70%)', pointerEvents: 'none' }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: 9, position: 'relative' }}>
          <MvxMark size={28} style={{ filter: 'brightness(0) invert(1)' }} />
          <span style={{ fontFamily: MVX.display, fontWeight: 700, fontSize: 21, letterSpacing: '-0.02em' }}>maverx</span>
        </div>

        <div style={{ marginTop: 30, marginBottom: 26, position: 'relative' }}>
          <span style={{ fontFamily: MVX.display, fontSize: 11.5, fontWeight: 600, letterSpacing: '.12em',
            color: 'rgba(255,255,255,.7)' }}>AI TRAINING BUILDER</span>
          <h1 style={{ margin: '10px 0 0', fontFamily: MVX.display, fontSize: 28, fontWeight: 700,
            lineHeight: 1.12, letterSpacing: '-0.02em' }}>
            {phase === 'done' ? 'Your training is ready.' : 'Let\u2019s build your training.'}
          </h1>
        </div>

        {/* live brief / steps */}
        <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
          {FIELDS.map((f, i) => {
            const done = meta[f.key] != null;
            const active = phase === 'intake' && currentField && currentField.key === f.key;
            return (
              <div key={f.key} style={{ display: 'flex', gap: 13, padding: '11px 0',
                borderBottom: '1px solid rgba(255,255,255,0.14)' }}>
                <span style={{ flex: '0 0 auto', width: 24, height: 24, borderRadius: 12, display: 'grid', placeItems: 'center',
                  background: done ? '#fff' : active ? 'rgba(255,255,255,0.22)' : 'rgba(255,255,255,0.10)',
                  border: active ? '1.5px solid #fff' : 'none', transition: 'all .3s' }}>
                  {done
                    ? <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="#7B1FA2" strokeWidth="2.2" strokeLinecap="round"><path d="M2.5 6L5 8.5 9.5 3.5"/></svg>
                    : <span style={{ fontFamily: MVX.display, fontSize: 11, fontWeight: 700, color: active ? '#fff' : 'rgba(255,255,255,.6)' }}>{i + 1}</span>}
                </span>
                <span style={{ flex: 1, minWidth: 0 }}>
                  <span style={{ display: 'block', fontFamily: MVX.display, fontSize: 12.5, fontWeight: 600,
                    color: active || done ? '#fff' : 'rgba(255,255,255,.62)', letterSpacing: '.01em' }}>{f.short}</span>
                  {done && <span style={{ display: 'block', fontSize: 12, color: 'rgba(255,255,255,.78)', marginTop: 2,
                    lineHeight: 1.35, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box',
                    WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{meta[f.key]}</span>}
                </span>
              </div>
            );
          })}
        </div>

        <div style={{ position: 'relative', display: 'flex', gap: 16, marginTop: 18, fontFamily: MVX.display,
          fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', color: 'rgba(255,255,255,.78)' }}>
          <span>ON-BRAND</span><span>EDITABLE .PPTX</span><span>SPEAKER NOTES</span>
        </div>
      </div>

      {/* ── RIGHT: focus area ── */}
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', padding: '34px 44px',
        justifyContent: 'center' }}>

        {phase === 'intake' && (
          <div style={{ maxWidth: 460, width: '100%', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
              <span style={{ fontFamily: MVX.display, fontSize: 12, fontWeight: 700, letterSpacing: '.04em', color: MVX.orange }}>
                {isFollowup ? 'LET\u2019S REFINE' : `QUESTION ${Math.min(answeredCount + 1, totalFields)} OF ${totalFields}`}
              </span>
              <span style={{ flex: 1, height: 1, background: MVX.line }} />
            </div>

            <h2 style={{ margin: 0, fontFamily: MVX.display, fontSize: 26, fontWeight: 600, lineHeight: 1.2,
              letterSpacing: '-0.015em', color: MVX.ink, minHeight: 64 }}>
              {botTyping ? <TypingDots color={MVX.faint} /> : (lastBot ? lastBot.text : '')}
            </h2>

            <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
              <textarea ref={inputRef} value={draft} onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                placeholder={currentField ? currentField.hint : ''} rows={2} disabled={botTyping}
                style={{ width: '100%', resize: 'none', border: `1.5px solid ${MVX.line}`, borderRadius: 14,
                  padding: '15px 16px', fontFamily: MVX.body, fontSize: 16, color: MVX.ink, outline: 'none',
                  lineHeight: 1.45, boxSizing: 'border-box', transition: 'border-color .15s', background: botTyping ? MVX.page : '#fff' }}
                onFocus={(e) => (e.target.style.borderColor = MVX.purple)}
                onBlur={(e) => (e.target.style.borderColor = MVX.line)} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 12, color: MVX.faint }}>Press <b style={{ color: MVX.slate }}>Enter</b> to continue</span>
                <button onClick={send} disabled={!draft.trim() || botTyping}
                  style={{ height: 46, padding: '0 22px', borderRadius: 12, border: 'none',
                    background: draft.trim() && !botTyping ? MVX.ink : MVX.line, color: '#fff', cursor: draft.trim() ? 'pointer' : 'default',
                    fontFamily: MVX.display, fontWeight: 600, fontSize: 14.5, display: 'flex', alignItems: 'center', gap: 8, transition: 'background .15s' }}>
                  Continue
                  <svg width="16" height="16" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 9h13M10 4l5 5-5 5"/></svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {phase === 'ready' && (
          <div style={{ maxWidth: 470, width: '100%', margin: '0 auto' }}>
            <span style={{ fontFamily: MVX.display, fontSize: 12, fontWeight: 700, letterSpacing: '.04em', color: '#1F9B5B' }}>BRIEF COMPLETE</span>
            <h2 style={{ margin: '10px 0 6px', fontFamily: MVX.display, fontSize: 27, fontWeight: 600, letterSpacing: '-0.015em' }}>
              {titleCaseC(meta.topic)}
            </h2>
            <p style={{ margin: '0 0 22px', fontSize: 14.5, color: MVX.slate, lineHeight: 1.5 }}>
              A {outline.mins}-minute {meta.level ? meta.level.toLowerCase().replace(/[^a-z].*$/, '') : ''} session for {meta.audience}, built on the full Maverx didactic arc.
            </p>
            <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
              {Object.keys(BLOCKS).map((k) => (
                <span key={k} style={{ fontFamily: MVX.display, fontSize: 11, fontWeight: 600, color: BLOCKS[k].color,
                  background: BLOCKS[k].tint, padding: '5px 11px', borderRadius: 20 }}>{BLOCKS[k].label}</span>
              ))}
            </div>
            <button onClick={Bld.generate} style={{ width: '100%', height: 54, borderRadius: 14, border: 'none', cursor: 'pointer',
              background: MVX.grad, color: '#fff', fontFamily: MVX.display, fontWeight: 600, fontSize: 16,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, boxShadow: '0 12px 30px rgba(123,31,162,0.32)' }}>
              <SparkIcon size={19} /> Generate training deck
            </button>
          </div>
        )}

        {phase === 'generating' && (
          <div style={{ maxWidth: 420, width: '100%', margin: '0 auto' }}>
            <h2 style={{ margin: '0 0 22px', fontFamily: MVX.display, fontSize: 24, fontWeight: 600, letterSpacing: '-0.015em' }}>Building your deck…</h2>
            {Bld.genSteps.map((s, i) => {
              const st = i < Bld.genStep ? 'done' : i === Bld.genStep ? 'active' : 'todo';
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 13, padding: '9px 0', opacity: st === 'todo' ? 0.4 : 1, transition: 'opacity .3s' }}>
                  <span style={{ flex: '0 0 auto', width: 22, height: 22, borderRadius: 11, display: 'grid', placeItems: 'center',
                    background: st === 'done' ? '#1F9B5B' : 'transparent', border: st === 'active' ? `2px solid ${MVX.purple}` : st === 'todo' ? `2px solid ${MVX.line}` : 'none' }}>
                    {st === 'done' && <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"><path d="M2.5 6L5 8.5 9.5 3.5"/></svg>}
                    {st === 'active' && <span style={{ width: 10, height: 10, borderRadius: 6, border: `2px solid ${MVX.purple}`, borderTopColor: 'transparent', animation: 'mvxSpin .7s linear infinite' }} />}
                  </span>
                  <span style={{ fontFamily: MVX.display, fontSize: 15, fontWeight: st === 'active' ? 600 : 500, color: st === 'active' ? MVX.ink : MVX.slate }}>{s}</span>
                </div>
              );
            })}
          </div>
        )}

        {phase === 'done' && (
          <div style={{ maxWidth: 460, width: '100%', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span style={{ width: 30, height: 30, borderRadius: 16, background: '#1F9B5B', display: 'grid', placeItems: 'center' }}>
                <svg width="15" height="15" viewBox="0 0 14 14" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round"><path d="M3 7l3 3 5-6"/></svg>
              </span>
              <h2 style={{ margin: 0, fontFamily: MVX.display, fontSize: 24, fontWeight: 600, letterSpacing: '-0.015em' }}>Done in seconds.</h2>
            </div>
            <p style={{ margin: '0 0 20px', fontSize: 14, color: MVX.slate, lineHeight: 1.5 }}>
              {outline.slides.length} editable slides in the Maverx house style, with trainer notes on every slide — plus prep and follow-up docs.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
              <FileCard icon="PPTX" accent={MVX.ink} name={`${slugC(meta.topic)}.pptx`} meta={`${outline.slides.length} slides \u00b7 speaker notes`} />
              <div style={{ display: 'flex', gap: 9 }}>
                <div style={{ flex: 1 }}><FileCard compact icon="DOC" accent={MVX.purple} name="prebite.docx" meta="Pre-session prep" /></div>
                <div style={{ flex: 1 }}><FileCard compact icon="DOC" accent={MVX.red} name="postbite.docx" meta="Follow-up" /></div>
              </div>
            </div>
            <button onClick={Bld.reset} style={{ marginTop: 16, background: 'transparent', border: 'none', cursor: 'pointer',
              fontFamily: MVX.display, fontSize: 13, fontWeight: 600, color: MVX.slate }}>↺  Build another training</button>
          </div>
        )}
      </div>
    </div>
  );
}

function titleCaseC(s) { return (s || '').replace(/\.$/, '').replace(/\b\w/g, (c) => c.toUpperCase()); }
function slugC(s) { return (s || 'training').toLowerCase().replace(/[^a-z0-9]+/g, '_').slice(0, 24); }

Object.assign(window, { VariantC });
