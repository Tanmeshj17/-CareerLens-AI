import { useState, useEffect, useContext } from 'react'
import { AuthContext } from '../App'
import { submitFeedback, getMyFeedback, getFeedbackStats } from '../api'

const CATEGORIES = ['Bug Report', 'Feature Request', 'UI/UX Improvement', 'Performance', 'General Feedback']
const PRIORITIES = [
  { label: 'Low',      text: '#60a5fa' },
  { label: 'Medium',   text: '#fbbf24' },
  { label: 'High',     text: '#f97316' },
  { label: 'Critical', text: '#ef4444' },
]
const RATINGS = [
  { emoji: '\u{1F621}', label: 'Terrible', value: 1 },
  { emoji: '\u{1F615}', label: 'Poor',     value: 2 },
  { emoji: '\u{1F610}', label: 'Okay',     value: 3 },
  { emoji: '\u{1F642}', label: 'Good',     value: 4 },
  { emoji: '\u{1F60D}', label: 'Amazing',  value: 5 },
]
const STATUS_STYLE = {
  'Open':      { bg: 'rgba(59,130,246,.12)', color: '#60a5fa', border: 'rgba(59,130,246,.25)' },
  'In Review': { bg: 'rgba(251,191,36,.12)', color: '#fbbf24', border: 'rgba(251,191,36,.25)' },
  'Resolved':  { bg: 'rgba(16,185,129,.12)', color: '#34d399', border: 'rgba(16,185,129,.25)' },
  'Closed':    { bg: 'rgba(107,114,128,.12)',color: '#9ca3af', border: 'rgba(107,114,128,.25)' },
}
const FAQ_ITEMS = [
  { q: 'How long does it take to get a response?', a: 'Our team reviews feedback within 24-48 hours. Critical bugs are triaged within 4 hours during business days.' },
  { q: 'Can I track my feedback status?', a: 'Yes - every submission appears in your My Submissions tab with a live status pulled directly from PostgreSQL.' },
  { q: 'What happens to Feature Requests?', a: 'Feature requests are reviewed in our product sprint cycle. The most-requested ones get shipped first.' },
  { q: 'How do I report a security vulnerability?', a: 'Please contact security@careerlens.ai directly. Do not submit security issues through the feedback form.' },
]

export default function Feedback() {
  const { user } = useContext(AuthContext)
  const [form, setForm] = useState({ rating: null, category: '', priority: 'Medium', subject: '', description: '' })
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [submissions, setSubmissions] = useState([])
  const [stats, setStats] = useState(null)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [openFaq, setOpenFaq] = useState(null)
  const [activeTab, setActiveTab] = useState('form')

  useEffect(() => {
    loadStats()
    if (user) loadHistory()
  }, [user])

  async function loadStats() {
    try { const d = await getFeedbackStats(); setStats(d) } catch (_) {}
  }
  async function loadHistory() {
    setLoadingHistory(true)
    try { const d = await getMyFeedback(); setSubmissions(d || []) }
    catch (_) { setSubmissions([]) }
    finally { setLoadingHistory(false) }
  }

  function updateField(k, v) { setForm(f => ({ ...f, [k]: v })); setError('') }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.category) { setError('Please select a category.'); return }
    if (!form.subject.trim()) { setError('Subject is required.'); return }
    if (form.description.trim().length < 20) { setError('Please provide at least 20 characters in the description.'); return }
    setSubmitting(true); setError('')
    try {
      await submitFeedback({ rating: form.rating, category: form.category, priority: form.priority, subject: form.subject.trim(), description: form.description.trim() })
      setSubmitted(true)
      await loadHistory(); await loadStats()
    } catch (err) { setError(err?.message || 'Submission failed. Please try again.') }
    finally { setSubmitting(false) }
  }

  function resetForm() { setForm({ rating: null, category: '', priority: 'Medium', subject: '', description: '' }); setSubmitted(false); setError('') }

  const charLeft = 1000 - form.description.length
  const surf = 'var(--color-surface-container, #1a1f2e)'
  const outline = 'var(--color-outline-variant, #2a3040)'
  const txt = 'var(--color-on-surface, #e2e8f0)'
  const muted = 'var(--color-on-surface-variant, #94a3b8)'
  const primary = 'var(--color-primary, #6366f1)'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-surface, #0f1117)', color: txt, fontFamily: "Inter, sans-serif" }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.25rem' }}>

        {/* Header */}
        <div style={{ marginBottom: '2.5rem' }}>
          <h1 style={{ fontSize: 'clamp(1.5rem,4vw,2rem)', fontWeight: 700, margin: '0 0 0.4rem', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span>ðŸ’¬</span> Feedback &amp; Support
          </h1>
          <p style={{ color: muted, margin: 0, fontSize: '0.95rem' }}>
            Help us improve CareerLens AI. Your feedback is saved directly to PostgreSQL and shapes the next sprint.
          </p>
        </div>

        {/* Stats Bar */}
        {stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px,1fr))', gap: '1rem', marginBottom: '2rem' }}>
            {[
              { label: 'Total Submissions', value: stats.total_feedback, icon: 'ðŸ“Š' },
              { label: 'Resolved',          value: stats.resolved_count,  icon: 'âœ…' },
              { label: 'In Review',         value: stats.in_review_count, icon: 'ðŸ”' },
              { label: 'Avg Rating',        value: stats.average_rating > 0 ? `${stats.average_rating}/5` : 'N/A', icon: 'â­' },
              { label: 'Avg Response',      value: stats.avg_response_hours, icon: 'âš¡' },
            ].map(s => (
              <div key={s.label} style={{ background: surf, borderRadius: 12, padding: '1rem 1.25rem', border: `1px solid ${outline}` }}>
                <div style={{ fontSize: '1.2rem', marginBottom: '0.3rem' }}>{s.icon}</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{s.value}</div>
                <div style={{ fontSize: '0.75rem', color: muted, marginTop: '0.2rem' }}>{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '1.5rem', borderBottom: `1px solid ${outline}`, paddingBottom: '0.25rem' }}>
          {[['form','âœï¸ Submit Feedback'], ['history',`ðŸ“‹ My Submissions (${submissions.length})`], ['faq','â“ FAQ']].map(([t,lbl]) => (
            <button key={t} onClick={() => setActiveTab(t)} style={{ background: activeTab===t ? primary : 'transparent', color: activeTab===t ? '#fff' : muted, border: 'none', borderRadius: '8px 8px 0 0', padding: '0.5rem 1rem', cursor: 'pointer', fontWeight: activeTab===t ? 600 : 400, fontSize: '0.875rem', transition: 'all .15s' }}>{lbl}</button>
          ))}
        </div>

        {/* FORM */}
        {activeTab === 'form' && (
          <div style={{ maxWidth: 700 }}>
            {submitted ? (
              <div style={{ background: 'rgba(16,185,129,.1)', border: '1px solid rgba(16,185,129,.3)', borderRadius: 16, padding: '2.5rem 2rem', textAlign: 'center' }}>
                <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>ðŸŽ‰</div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 0.5rem', color: '#10b981' }}>Feedback Submitted!</h2>
                <p style={{ color: muted, marginBottom: '1.5rem' }}>Saved to PostgreSQL. We typically respond within 48 hours.</p>
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                  <button onClick={resetForm} style={{ background: primary, color: '#fff', border: 'none', borderRadius: 8, padding: '0.6rem 1.4rem', fontWeight: 600, cursor: 'pointer' }}>Submit Another</button>
                  <button onClick={() => setActiveTab('history')} style={{ background: 'transparent', color: primary, border: `1px solid ${primary}`, borderRadius: 8, padding: '0.6rem 1.4rem', fontWeight: 600, cursor: 'pointer' }}>View My Submissions</button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                {/* Rating */}
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>Overall Rating <span style={{ color: muted, fontWeight: 400 }}>(optional)</span></label>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    {RATINGS.map(r => (
                      <button key={r.value} type="button" onClick={() => updateField('rating', form.rating===r.value ? null : r.value)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.3rem', padding: '0.65rem 1rem', borderRadius: 10, cursor: 'pointer', transition: 'all .15s', background: form.rating===r.value ? 'rgba(99,102,241,.18)' : surf, border: form.rating===r.value ? `1.5px solid ${primary}` : `1px solid ${outline}`, transform: form.rating===r.value ? 'scale(1.1)' : 'scale(1)' }}>
                        <span style={{ fontSize: '1.5rem' }}>{r.emoji}</span>
                        <span style={{ fontSize: '0.7rem', color: muted }}>{r.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Category + Priority */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.875rem' }}>Category <span style={{ color: '#ef4444' }}>*</span></label>
                    <select value={form.category} onChange={e => updateField('category', e.target.value)} style={{ width: '100%', boxSizing: 'border-box', background: surf, border: `1px solid ${outline}`, borderRadius: 8, padding: '0.6rem 0.85rem', color: txt, fontSize: '0.9rem', outline: 'none' }}>
                      <option value="">Select categoryâ€¦</option>
                      {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.875rem' }}>Priority</label>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', paddingTop: '0.2rem' }}>
                      {PRIORITIES.map(p => (
                        <button key={p.label} type="button" onClick={() => updateField('priority', p.label)} style={{ padding: '0.3rem 0.75rem', borderRadius: 20, cursor: 'pointer', fontSize: '0.8rem', fontWeight: form.priority===p.label ? 600 : 400, background: form.priority===p.label ? `${p.text}22` : 'transparent', border: form.priority===p.label ? `1.5px solid ${p.text}` : `1px solid ${outline}`, color: form.priority===p.label ? p.text : muted, transition: 'all .15s' }}>{p.label}</button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Subject */}
                <div>
                  <label style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.875rem' }}>Subject <span style={{ color: '#ef4444' }}>*</span></label>
                  <input type="text" value={form.subject} onChange={e => updateField('subject', e.target.value)} placeholder="Brief summary of your feedbackâ€¦" maxLength={255} style={{ width: '100%', boxSizing: 'border-box', background: surf, border: `1px solid ${outline}`, borderRadius: 8, padding: '0.6rem 0.85rem', color: txt, fontSize: '0.9rem', outline: 'none' }} />
                </div>

                {/* Description */}
                <div>
                  <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontWeight: 600, fontSize: '0.875rem' }}>
                    <span>Description <span style={{ color: '#ef4444' }}>*</span></span>
                    <span style={{ color: charLeft < 100 ? '#ef4444' : muted, fontWeight: 400, fontSize: '0.8rem' }}>{charLeft} chars left</span>
                  </label>
                  <textarea value={form.description} onChange={e => updateField('description', e.target.value)} placeholder="Steps to reproduce, expected vs actual behaviour, any relevant contextâ€¦" maxLength={1000} rows={5} style={{ width: '100%', boxSizing: 'border-box', background: surf, border: `1px solid ${outline}`, borderRadius: 8, padding: '0.6rem 0.85rem', color: txt, fontSize: '0.9rem', outline: 'none', resize: 'vertical', minHeight: 120, fontFamily: 'inherit' }} />
                </div>

                {error && <div style={{ background: 'rgba(239,68,68,.1)', border: '1px solid rgba(239,68,68,.3)', borderRadius: 8, padding: '0.75rem 1rem', color: '#f87171', fontSize: '0.875rem' }}>âš ï¸ {error}</div>}

                <button type="submit" disabled={submitting} style={{ background: primary, color: '#fff', border: 'none', borderRadius: 8, padding: '0.65rem 1.5rem', fontWeight: 600, fontSize: '0.9rem', cursor: submitting ? 'wait' : 'pointer', opacity: submitting ? 0.7 : 1, transition: 'opacity .15s', alignSelf: 'flex-start' }}>
                  {submitting ? 'â³ Submittingâ€¦' : 'ðŸš€ Submit Feedback'}
                </button>
              </form>
            )}
          </div>
        )}

        {/* HISTORY */}
        {activeTab === 'history' && (
          <div>
            {!user ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: muted }}>ðŸ”’ Sign in to view your submission history.</div>
            ) : loadingHistory ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: muted }}>Loadingâ€¦</div>
            ) : submissions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: muted }}>
                <div style={{ fontSize: '3rem' }}>ðŸ“­</div>
                <p>No submissions yet.</p>
                <button onClick={() => setActiveTab('form')} style={{ background: primary, color: '#fff', border: 'none', borderRadius: 8, padding: '0.6rem 1.4rem', fontWeight: 600, cursor: 'pointer', marginTop: '1rem' }}>Submit Feedback</button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {submissions.map(s => {
                  const st = STATUS_STYLE[s.status] || STATUS_STYLE['Closed']
                  return (
                    <div key={s.id} style={{ background: surf, border: `1px solid ${outline}`, borderRadius: 12, padding: '1rem 1.25rem', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ flex: 1, minWidth: 200 }}>
                        <div style={{ fontWeight: 600, marginBottom: '0.2rem' }}>{s.subject}</div>
                        <div style={{ fontSize: '0.8rem', color: muted }}>#{s.id} Â· {s.category} Â· {new Date(s.created_at).toLocaleDateString('en-IN')}</div>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <span style={{ background: st.bg, color: st.color, border: `1px solid ${st.border}`, padding: '0.2rem 0.6rem', borderRadius: 6, fontSize: '0.75rem', fontWeight: 500 }}>{s.status}</span>
                        <span style={{ background: `${PRIORITIES.find(p=>p.label===s.priority)?.text || '#94a3b8'}22`, color: PRIORITIES.find(p=>p.label===s.priority)?.text || '#94a3b8', padding: '0.2rem 0.6rem', borderRadius: 6, fontSize: '0.75rem', fontWeight: 500 }}>{s.priority}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* FAQ */}
        {activeTab === 'faq' && (
          <div style={{ maxWidth: 700, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {FAQ_ITEMS.map((item, i) => (
              <div key={i} style={{ background: surf, border: `1px solid ${outline}`, borderRadius: 12, overflow: 'hidden' }}>
                <button onClick={() => setOpenFaq(openFaq===i ? null : i)} style={{ width: '100%', textAlign: 'left', padding: '1rem 1.25rem', background: 'transparent', border: 'none', cursor: 'pointer', color: txt, display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontWeight: 600, fontSize: '0.95rem' }}>
                  {item.q}
                  <span style={{ transition: 'transform .2s', transform: openFaq===i ? 'rotate(180deg)' : 'none', flexShrink: 0, marginLeft: '1rem' }}>â–¾</span>
                </button>
                {openFaq === i && <div style={{ padding: '0 1.25rem 1rem', color: muted, fontSize: '0.9rem', lineHeight: 1.7 }}>{item.a}</div>}
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
