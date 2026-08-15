import { useState, useEffect, useContext } from 'react'
import { AuthContext } from '../App'
import { submitFeedback, getMyFeedback, getFeedbackStats } from '../api'

const CATEGORIES = [
  'Bug Report',
  'Feature Request',
  'UI/UX Improvement',
  'Performance',
  'General Feedback'
]

const PRIORITIES = [
  { label: 'Low', badge: 'bg-info/10 text-info border-info/30' },
  { label: 'Medium', badge: 'bg-warning/10 text-warning border-warning/30' },
  { label: 'High', badge: 'bg-error/10 text-error border-error/30' },
  { label: 'Critical', badge: 'bg-error/20 text-error border-error/50 font-bold' },
]

const RATINGS = [
  { emoji: '😠', label: 'Terrible', value: 1 },
  { emoji: '🙁', label: 'Poor', value: 2 },
  { emoji: '😐', label: 'Okay', value: 3 },
  { emoji: '🙂', label: 'Good', value: 4 },
  { emoji: '😍', label: 'Amazing', value: 5 },
]

const STATUS_STYLE = {
  'Open': 'bg-info/10 text-info border-info/30',
  'In Review': 'bg-warning/10 text-warning border-warning/30',
  'Resolved': 'bg-success/10 text-success border-success/30',
  'Closed': 'bg-surface-container text-on-surface-variant border-outline-variant',
}

const FAQ_ITEMS = [
  {
    q: 'How long does it take to get a response?',
    a: 'Our team reviews feedback within 24 to 48 hours. Critical bugs are typically triaged within 4 hours during business days.'
  },
  {
    q: 'Can I track the status of my feedback?',
    a: 'Yes, every submission appears in your "My Submissions" tab with a live status update.'
  },
  {
    q: 'What happens to Feature Requests?',
    a: 'Feature requests are reviewed during our product development sprint planning. The most requested features are prioritized and built first.'
  },
  {
    q: 'How do I report a security vulnerability?',
    a: 'For security concerns, please contact security@careerlens.ai directly rather than submitting through the public feedback form.'
  },
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
    try {
      const d = await getFeedbackStats()
      setStats(d)
    } catch (_) {}
  }

  async function loadHistory() {
    setLoadingHistory(true)
    try {
      const d = await getMyFeedback()
      setSubmissions(d || [])
    } catch (_) {
      setSubmissions([])
    } finally {
      setLoadingHistory(false)
    }
  }

  function updateField(k, v) {
    setForm(f => ({ ...f, [k]: v }))
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.category) {
      setError('Please select a feedback category.')
      return
    }
    if (!form.subject.trim()) {
      setError('Subject is required.')
      return
    }
    if (form.description.trim().length < 20) {
      setError('Please provide at least 20 characters in the description.')
      return
    }

    setSubmitting(true)
    setError('')
    try {
      await submitFeedback({
        rating: form.rating,
        category: form.category,
        priority: form.priority,
        subject: form.subject.trim(),
        description: form.description.trim()
      })
      setSubmitted(true)
      await loadHistory()
      await loadStats()
    } catch (err) {
      setError(err?.message || 'Submission failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  function resetForm() {
    setForm({ rating: null, category: '', priority: 'Medium', subject: '', description: '' })
    setSubmitted(false)
    setError('')
  }

  const charLeft = 1000 - form.description.length

  return (
    <div className="space-y-lg sm:space-y-xl animate-fade-in-up max-w-4xl mx-auto pb-3xl">

      {/* ═══════════════ HEADER ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-br from-primary/10 via-primary-container/5 to-transparent rounded-t-2xl pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md pt-sm">
          <div className="flex items-center gap-md">
            <div className="p-md bg-primary-container/15 rounded-2xl text-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-3xl">chat_bubble</span>
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
                Feedback & Support
              </h1>
              <p className="text-xs sm:text-sm text-on-surface-variant font-[Geist] mt-xs">
                Help us improve CareerLens AI. Share your suggestions, report issues, or request new features.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════ STATS BAR ═══════════════ */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-sm sm:gap-md">
          <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant flex items-center gap-sm">
            <div className="w-10 h-10 rounded-lg bg-primary-container/15 text-primary flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl">forum</span>
            </div>
            <div>
              <div className="text-lg font-bold text-on-surface">{stats.total_feedback || 0}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">Total Feedback</div>
            </div>
          </div>

          <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant flex items-center gap-sm">
            <div className="w-10 h-10 rounded-lg bg-success/15 text-success flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl">check_circle</span>
            </div>
            <div>
              <div className="text-lg font-bold text-on-surface">{stats.resolved_count || 0}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">Resolved</div>
            </div>
          </div>

          <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant flex items-center gap-sm">
            <div className="w-10 h-10 rounded-lg bg-warning/15 text-warning flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl">star</span>
            </div>
            <div>
              <div className="text-lg font-bold text-on-surface">
                {stats.average_rating > 0 ? `${stats.average_rating}/5` : 'N/A'}
              </div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">Avg Rating</div>
            </div>
          </div>

          <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant flex items-center gap-sm">
            <div className="w-10 h-10 rounded-lg bg-info/15 text-info flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl">schedule</span>
            </div>
            <div>
              <div className="text-lg font-bold text-on-surface">{stats.avg_response_hours || '24h'}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">Avg Response</div>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ NAVIGATION TABS ═══════════════ */}
      <div className="flex gap-xs border-b border-outline-variant/60 pb-xs">
        <button
          onClick={() => setActiveTab('form')}
          className={`px-md py-sm rounded-lg text-xs font-semibold font-[Geist] transition-all flex items-center gap-xs ${
            activeTab === 'form'
              ? 'bg-primary text-on-primary shadow-xs'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">edit_note</span>
          Submit Feedback
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`px-md py-sm rounded-lg text-xs font-semibold font-[Geist] transition-all flex items-center gap-xs ${
            activeTab === 'history'
              ? 'bg-primary text-on-primary shadow-xs'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">history</span>
          My Submissions ({submissions.length})
        </button>

        <button
          onClick={() => setActiveTab('faq')}
          className={`px-md py-sm rounded-lg text-xs font-semibold font-[Geist] transition-all flex items-center gap-xs ${
            activeTab === 'faq'
              ? 'bg-primary text-on-primary shadow-xs'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">help_outline</span>
          FAQ
        </button>
      </div>

      {/* ═══════════════ 1. SUBMIT FORM TAB ═══════════════ */}
      {activeTab === 'form' && (
        <section className="glass-effect rounded-2xl p-4 sm:p-xl">
          {submitted ? (
            <div className="p-xl text-center space-y-md">
              <div className="w-16 h-16 rounded-2xl bg-success/15 text-success flex items-center justify-center mx-auto">
                <span className="material-symbols-outlined text-3xl">celebration</span>
              </div>
              <h2 className="text-xl font-bold text-on-surface">Thank You for Your Feedback!</h2>
              <p className="text-xs sm:text-sm text-on-surface-variant max-w-md mx-auto leading-relaxed">
                Your submission has been received. Our team will review it and follow up as soon as possible.
              </p>
              <div className="flex gap-sm justify-center pt-md">
                <button
                  onClick={resetForm}
                  className="px-lg py-sm bg-primary text-on-primary rounded-lg text-xs font-semibold font-[Geist] hover:brightness-110 transition-all shadow-xs"
                >
                  Submit Another Response
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className="px-lg py-sm border border-outline-variant text-on-surface-variant rounded-lg text-xs font-semibold font-[Geist] hover:bg-surface-container transition-all"
                >
                  View My Submissions
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-lg">
              {/* Overall Rating */}
              <div>
                <label className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider block mb-sm">
                  Overall Experience <span className="text-on-surface-variant/60 font-normal lowercase">(optional)</span>
                </label>
                <div className="flex flex-wrap gap-xs sm:gap-sm">
                  {RATINGS.map(r => (
                    <button
                      key={r.value}
                      type="button"
                      onClick={() => updateField('rating', form.rating === r.value ? null : r.value)}
                      className={`flex flex-col items-center gap-xs px-md py-sm rounded-xl border transition-all ${
                        form.rating === r.value
                          ? 'bg-primary/10 border-primary shadow-xs scale-105'
                          : 'bg-surface-container-low border-outline-variant hover:border-primary/40'
                      }`}
                    >
                      <span className="text-2xl">{r.emoji}</span>
                      <span className="text-[11px] font-medium font-[Geist] text-on-surface-variant">
                        {r.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Category & Priority */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
                <div className="space-y-xs">
                  <label className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                    Category <span className="text-error">*</span>
                  </label>
                  <select
                    value={form.category}
                    onChange={e => updateField('category', e.target.value)}
                    required
                    className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all font-[Geist]"
                  >
                    <option value="">Select a category...</option>
                    {CATEGORIES.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-xs">
                  <label className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                    Priority Level
                  </label>
                  <div className="flex flex-wrap gap-xs pt-1">
                    {PRIORITIES.map(p => (
                      <button
                        key={p.label}
                        type="button"
                        onClick={() => updateField('priority', p.label)}
                        className={`px-md py-xs rounded-full text-xs font-medium font-[Geist] border transition-all ${
                          form.priority === p.label
                            ? 'bg-primary text-on-primary border-primary shadow-xs'
                            : 'bg-surface-container-low text-on-surface-variant border-outline-variant hover:border-primary/40'
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Subject */}
              <div className="space-y-xs">
                <label className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                  Subject / Summary <span className="text-error">*</span>
                </label>
                <input
                  type="text"
                  value={form.subject}
                  onChange={e => updateField('subject', e.target.value)}
                  placeholder="e.g. ATS Resume Analyzer suggestions for PDF formatting"
                  maxLength={255}
                  required
                  className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                />
              </div>

              {/* Description */}
              <div className="space-y-xs">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                    Detailed Feedback <span className="text-error">*</span>
                  </label>
                  <span className={`text-[11px] font-[Geist] ${charLeft < 50 ? 'text-error font-bold' : 'text-on-surface-variant'}`}>
                    {charLeft} characters left
                  </span>
                </div>
                <textarea
                  value={form.description}
                  onChange={e => updateField('description', e.target.value)}
                  placeholder="Please describe what happened, what you expected, or your feature idea..."
                  maxLength={1000}
                  rows={5}
                  required
                  className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all resize-y"
                />
              </div>

              {error && (
                <div className="p-sm rounded-lg bg-error/10 text-error text-xs font-medium font-[Geist] flex items-center gap-xs border border-error/30">
                  <span className="material-symbols-outlined text-[16px]">error</span>
                  {error}
                </div>
              )}

              <div className="flex justify-end pt-xs">
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-lg py-sm bg-primary hover:brightness-110 text-on-primary rounded-lg text-sm font-semibold font-[Geist] transition-all disabled:opacity-50 flex items-center gap-xs shadow-sm"
                >
                  <span className="material-symbols-outlined text-[16px]">send</span>
                  {submitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </div>
            </form>
          )}
        </section>
      )}

      {/* ═══════════════ 2. MY SUBMISSIONS TAB ═══════════════ */}
      {activeTab === 'history' && (
        <section className="glass-effect rounded-2xl p-4 sm:p-xl space-y-md">
          {!user ? (
            <div className="text-center py-xl bg-surface-container-low rounded-xl border border-outline-variant">
              <span className="material-symbols-outlined text-3xl text-on-surface-variant/40 mb-xs block">lock</span>
              <p className="text-sm font-medium text-on-surface">Please sign in to view your past submissions.</p>
            </div>
          ) : loadingHistory ? (
            <div className="text-center py-xl text-on-surface-variant font-[Geist] text-sm flex items-center justify-center gap-xs">
              <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              Loading your submissions...
            </div>
          ) : submissions.length === 0 ? (
            <div className="text-center py-xl bg-surface-container-low rounded-xl border border-dashed border-outline-variant">
              <span className="material-symbols-outlined text-3xl text-on-surface-variant/40 mb-xs block">inbox</span>
              <p className="text-sm font-semibold text-on-surface font-[Geist]">No feedback submitted yet</p>
              <p className="text-xs text-on-surface-variant mt-xs mb-md">Any bug reports or suggestions you submit will appear here.</p>
              <button
                onClick={() => setActiveTab('form')}
                className="px-md py-sm bg-primary text-on-primary rounded-lg text-xs font-semibold font-[Geist] hover:brightness-110 transition-all"
              >
                Submit Feedback Now
              </button>
            </div>
          ) : (
            <div className="space-y-sm">
              {submissions.map(s => {
                const badgeClass = STATUS_STYLE[s.status] || STATUS_STYLE['Closed']
                const priorityBadge = PRIORITIES.find(p => p.label === s.priority)?.badge || 'bg-surface-container text-on-surface-variant'

                return (
                  <div
                    key={s.id}
                    className="p-md rounded-xl bg-surface-container-low border border-outline-variant flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md"
                  >
                    <div className="space-y-xs flex-1">
                      <div className="text-sm font-semibold text-on-surface">{s.subject}</div>
                      <div className="text-xs text-on-surface-variant font-[Geist] flex flex-wrap items-center gap-xs">
                        <span>#{s.id}</span>
                        <span>•</span>
                        <span>{s.category}</span>
                        <span>•</span>
                        <span>{new Date(s.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-xs shrink-0">
                      <span className={`px-sm py-0.5 rounded-full text-xs font-semibold font-[Geist] border ${badgeClass}`}>
                        {s.status}
                      </span>
                      <span className={`px-sm py-0.5 rounded-full text-xs font-medium font-[Geist] border ${priorityBadge}`}>
                        {s.priority}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      )}

      {/* ═══════════════ 3. FAQ TAB ═══════════════ */}
      {activeTab === 'faq' && (
        <section className="space-y-sm">
          {FAQ_ITEMS.map((item, i) => (
            <div
              key={i}
              className="rounded-xl bg-surface-container-low border border-outline-variant overflow-hidden transition-all"
            >
              <button
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                className="w-full text-left p-md sm:p-lg flex items-center justify-between gap-md hover:bg-surface-container/50 transition-all"
              >
                <span className="text-sm font-semibold text-on-surface">{item.q}</span>
                <span className={`material-symbols-outlined text-primary text-xl transition-transform duration-200 ${openFaq === i ? 'rotate-180' : ''}`}>
                  expand_more
                </span>
              </button>
              {openFaq === i && (
                <div className="px-md sm:px-lg pb-md sm:pb-lg text-xs sm:text-sm text-on-surface-variant font-[Geist] leading-relaxed border-t border-outline-variant/40 pt-sm">
                  {item.a}
                </div>
              )}
            </div>
          ))}
        </section>
      )}

    </div>
  )
}
