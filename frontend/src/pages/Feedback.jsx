import { useState, useContext } from 'react'
import { AuthContext } from '../App'

const CATEGORIES = ['Bug Report', 'Feature Request', 'UI/UX Improvement', 'Performance', 'General Feedback']
const PRIORITIES = [
  { label: 'Low', color: 'bg-blue-400', ring: 'ring-blue-400/30', text: 'text-blue-400' },
  { label: 'Medium', color: 'bg-amber-400', ring: 'ring-amber-400/30', text: 'text-amber-400' },
  { label: 'High', color: 'bg-orange-500', ring: 'ring-orange-500/30', text: 'text-orange-500' },
  { label: 'Critical', color: 'bg-red-500', ring: 'ring-red-500/30', text: 'text-red-500' },
]

const RATINGS = [
  { emoji: '😡', label: 'Terrible', color: 'from-red-500/20 to-red-600/5' },
  { emoji: '😕', label: 'Poor', color: 'from-orange-400/20 to-orange-500/5' },
  { emoji: '😐', label: 'Okay', color: 'from-yellow-400/20 to-yellow-500/5' },
  { emoji: '🙂', label: 'Good', color: 'from-emerald-400/20 to-emerald-500/5' },
  { emoji: '😍', label: 'Amazing', color: 'from-green-400/20 to-green-500/5' },
]

const MOCK_SUBMISSIONS = [
  {
    id: 'FB-1042',
    date: '2026-06-15',
    category: 'Feature Request',
    subject: 'Add dark-mode toggle to settings page',
    status: 'In Review',
    priority: 'Medium',
  },
  {
    id: 'FB-1038',
    date: '2026-06-13',
    category: 'Bug Report',
    subject: 'Resume parser fails on multi-page PDF uploads',
    status: 'Open',
    priority: 'High',
  },
  {
    id: 'FB-1031',
    date: '2026-06-10',
    category: 'UI/UX Improvement',
    subject: 'Career explorer cards feel too cramped on mobile',
    status: 'Resolved',
    priority: 'Medium',
  },
  {
    id: 'FB-1024',
    date: '2026-06-06',
    category: 'Performance',
    subject: 'Dashboard takes 4+ seconds to load on slow connections',
    status: 'Resolved',
    priority: 'Critical',
  },
  {
    id: 'FB-1019',
    date: '2026-06-02',
    category: 'General Feedback',
    subject: 'Love the new interview prep module — super helpful!',
    status: 'Closed',
    priority: 'Low',
  },
  {
    id: 'FB-1012',
    date: '2026-05-28',
    category: 'Feature Request',
    subject: 'Allow exporting tracked applications to CSV',
    status: 'Resolved',
    priority: 'Low',
  },
]

const FAQ_ITEMS = [
  {
    q: 'How long does it take to get a response?',
    a: 'Our team typically reviews feedback within 24-48 hours. Bug reports marked as Critical are triaged within 4 hours during business days.',
  },
  {
    q: 'Can I track the status of my feedback?',
    a: 'Absolutely! Every submission gets a unique ID and appears in your "Recent Submissions" list. You\'ll also receive email notifications when the status changes.',
  },
  {
    q: 'What happens after my feature request is approved?',
    a: 'Approved feature requests enter our product backlog and are prioritized during sprint planning. You can follow progress on our public roadmap page.',
  },
  {
    q: 'How do I report a security vulnerability?',
    a: 'Please do not use this form for security issues. Instead, email security@careerlens.ai directly. We follow responsible disclosure practices and will acknowledge receipt within 12 hours.',
  },
  {
    q: 'Can I edit or delete a submitted feedback?',
    a: 'You can edit submissions that are still in "Open" status by clicking the item in your Recent Submissions list. Once a submission moves to "In Review," it can no longer be edited.',
  },
]

const COMMUNITY_STATS = [
  { label: 'Total Feedback', value: '2,847', icon: 'forum', trend: '+128 this month', bg: 'bg-primary-container/10', iconColor: 'text-primary' },
  { label: 'Features Shipped', value: '64', icon: 'rocket_launch', trend: '12 from user ideas', bg: 'bg-success/10', iconColor: 'text-success' },
  { label: 'Avg Response Time', value: '18h', icon: 'schedule', trend: '38% faster', bg: 'bg-secondary-container/10', iconColor: 'text-secondary' },
  { label: 'Satisfaction Score', value: '4.7', icon: 'star', trend: 'Out of 5.0', bg: 'bg-amber-400/10', iconColor: 'text-amber-500' },
]

const categoryBadge = (cat) => {
  const map = {
    'Bug Report': 'bg-red-500/10 text-red-400 border-red-500/20',
    'Feature Request': 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    'UI/UX Improvement': 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    'Performance': 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    'General Feedback': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  }
  return map[cat] || 'bg-surface-container text-on-surface-variant border-outline-variant'
}

const statusBadge = (status) => {
  const map = {
    'Open': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    'In Review': 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    'Resolved': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    'Closed': 'bg-neutral-500/10 text-neutral-400 border-neutral-500/20',
  }
  return map[status] || ''
}

const statusIcon = (status) => {
  const map = { 'Open': 'radio_button_unchecked', 'In Review': 'pending', 'Resolved': 'check_circle', 'Closed': 'cancel' }
  return map[status] || 'help'
}

const priorityDot = (priority) => {
  const map = { Low: 'bg-blue-400', Medium: 'bg-amber-400', High: 'bg-orange-500', Critical: 'bg-red-500' }
  return map[priority] || 'bg-neutral-400'
}

export default function Feedback() {
  const { user } = useContext(AuthContext)

  // Form state
  const [rating, setRating] = useState(null)
  const [category, setCategory] = useState('')
  const [subject, setSubject] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('Medium')
  const [fileName, setFileName] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  // FAQ state
  const [expandedFaq, setExpandedFaq] = useState(null)

  const MAX_DESC = 1000

  const handleSubmit = (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setTimeout(() => {
      setIsSubmitting(false)
      setSubmitted(true)
      setTimeout(() => setSubmitted(false), 4000)
      setRating(null)
      setCategory('')
      setSubject('')
      setDescription('')
      setPriority('Medium')
      setFileName('')
    }, 2000)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer?.files?.[0]
    if (file) setFileName(file.name)
  }

  return (
    <div className="space-y-xl animate-fade-in-up">
      {/* ── Header ── */}
      <section className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-md">
        <div>
          <h2 className="text-3xl font-semibold text-on-surface flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary text-[32px]">rate_review</span>
            Feedback & Reviews
          </h2>
          <p className="text-base text-on-surface-variant mt-xs">
            Your voice shapes CareerLens AI. Share suggestions, report bugs, or just tell us how we're doing.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-sm bg-success/10 text-success px-md py-sm rounded-lg text-sm font-medium font-[Geist] border border-success/20">
          <span className="material-symbols-outlined text-[18px]">verified</span>
          {MOCK_SUBMISSIONS.filter(s => s.status === 'Resolved').length} issues resolved this month
        </div>
      </section>

      {/* ── Quick Satisfaction Rating ── */}
      <section className="bg-surface border border-outline-variant rounded-xl p-lg">
        <h3 className="text-lg font-semibold text-on-surface mb-xs">How are you feeling about CareerLens today?</h3>
        <p className="text-sm text-on-surface-variant mb-lg">Quick pulse — tap a face below</p>
        <div className="flex flex-wrap justify-center gap-lg">
          {RATINGS.map((r, i) => (
            <button
              key={i}
              onClick={() => setRating(i)}
              className={`group flex flex-col items-center gap-sm transition-all duration-300 cursor-pointer
                ${rating === i
                  ? `scale-110 bg-gradient-to-b ${r.color} ring-2 ring-white/10 shadow-lg rounded-2xl p-md`
                  : 'opacity-60 hover:opacity-100 hover:scale-105 p-md rounded-2xl hover:bg-surface-container'}`}
            >
              <span className={`text-5xl transition-transform duration-300 ${rating === i ? 'animate-gentle-pulse' : 'group-hover:scale-110'}`}>
                {r.emoji}
              </span>
              <span className={`text-xs font-[Geist] font-medium tracking-wide uppercase transition-colors
                ${rating === i ? 'text-on-surface' : 'text-on-surface-variant'}`}>
                {r.label}
              </span>
            </button>
          ))}
        </div>
        {rating !== null && (
          <p className="text-center mt-md text-sm text-on-surface-variant animate-fade-in-up">
            Thanks for the quick pulse! You selected <strong className="text-on-surface">{RATINGS[rating].label}</strong>. Feel free to share more details below.
          </p>
        )}
      </section>

      {/* ── Main Content Grid ── */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-xl">
        {/* ── Feedback Form (3 cols) ── */}
        <form onSubmit={handleSubmit} className="xl:col-span-3 space-y-lg">
          <div className="glass-effect border border-outline-variant rounded-xl p-xl space-y-lg">
            <div className="flex items-center gap-sm mb-sm">
              <span className="material-symbols-outlined text-primary">edit_note</span>
              <h3 className="text-xl font-semibold text-on-surface">Submit Feedback</h3>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium font-[Geist] text-on-surface-variant mb-xs">Category</label>
              <div className="relative">
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-surface-container border border-outline-variant rounded-lg px-md py-sm text-on-surface text-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all"
                >
                  <option value="">Select a category…</option>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <span className="material-symbols-outlined absolute right-sm top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-[20px]">
                  expand_more
                </span>
              </div>
            </div>

            {/* Subject */}
            <div>
              <label className="block text-sm font-medium font-[Geist] text-on-surface-variant mb-xs">Subject</label>
              <input
                type="text"
                placeholder="Brief title for your feedback…"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full bg-surface-container border border-outline-variant rounded-lg px-md py-sm text-on-surface text-sm placeholder:text-on-surface-variant/50 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium font-[Geist] text-on-surface-variant mb-xs">Description</label>
              <textarea
                rows={5}
                maxLength={MAX_DESC}
                placeholder="Tell us more — steps to reproduce, expected vs actual behavior, screenshots context…"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-surface-container border border-outline-variant rounded-lg px-md py-sm text-on-surface text-sm placeholder:text-on-surface-variant/50 resize-none focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all custom-scrollbar"
              />
              <div className="flex justify-end mt-xs">
                <span className={`text-xs font-[Geist] ${description.length > MAX_DESC * 0.9 ? 'text-error' : 'text-on-surface-variant'}`}>
                  {description.length}/{MAX_DESC}
                </span>
              </div>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium font-[Geist] text-on-surface-variant mb-sm">Priority</label>
              <div className="flex flex-wrap gap-sm">
                {PRIORITIES.map((p) => (
                  <label
                    key={p.label}
                    className={`flex items-center gap-xs px-md py-xs rounded-lg cursor-pointer border text-sm font-medium transition-all duration-200
                      ${priority === p.label
                        ? `${p.ring} ring-2 border-transparent bg-surface-container ${p.text}`
                        : 'border-outline-variant bg-surface-container/50 text-on-surface-variant hover:bg-surface-container'}`}
                  >
                    <input
                      type="radio"
                      name="priority"
                      value={p.label}
                      checked={priority === p.label}
                      onChange={() => setPriority(p.label)}
                      className="sr-only"
                    />
                    <span className={`w-2.5 h-2.5 rounded-full ${p.color} ${priority === p.label ? 'animate-gentle-pulse' : ''}`} />
                    {p.label}
                  </label>
                ))}
              </div>
            </div>

            {/* Screenshot Upload */}
            <div>
              <label className="block text-sm font-medium font-[Geist] text-on-surface-variant mb-sm">Attachment (optional)</label>
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => setFileName('screenshot_2026-06-16.png')}
                className={`border-2 border-dashed rounded-xl p-xl text-center cursor-pointer transition-all duration-300
                  ${isDragging
                    ? 'border-primary bg-primary/5 scale-[1.01]'
                    : fileName
                      ? 'border-success/40 bg-success/5'
                      : 'border-outline-variant hover:border-primary/40 hover:bg-surface-container/50'}`}
              >
                {fileName ? (
                  <div className="flex flex-col items-center gap-sm animate-fade-in-up">
                    <span className="material-symbols-outlined text-success text-[36px]">check_circle</span>
                    <p className="text-sm text-on-surface font-medium">{fileName}</p>
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); setFileName('') }}
                      className="text-xs text-error hover:underline cursor-pointer"
                    >
                      Remove
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-sm">
                    <span className={`material-symbols-outlined text-[36px] transition-colors ${isDragging ? 'text-primary' : 'text-on-surface-variant'}`}>
                      cloud_upload
                    </span>
                    <p className="text-sm text-on-surface-variant">
                      <span className="text-primary font-medium">Click to upload</span> or drag & drop
                    </p>
                    <p className="text-xs text-on-surface-variant/60">PNG, JPG, GIF up to 10MB</p>
                  </div>
                )}
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting || !subject.trim()}
              className={`w-full flex items-center justify-center gap-sm py-sm rounded-lg text-sm font-semibold font-[Geist] transition-all duration-300 cursor-pointer
                ${isSubmitting
                  ? 'bg-primary/60 text-on-primary cursor-wait'
                  : submitted
                    ? 'bg-success text-white'
                    : !subject.trim()
                      ? 'bg-surface-container text-on-surface-variant/40 cursor-not-allowed'
                      : 'bg-primary text-on-primary hover:brightness-110 hover:shadow-lg hover:shadow-primary/20 active:scale-[.98]'}`}
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Submitting…
                </>
              ) : submitted ? (
                <>
                  <span className="material-symbols-outlined text-[18px]">check</span>
                  Submitted Successfully!
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">send</span>
                  Submit Feedback
                </>
              )}
            </button>
          </div>
        </form>

        {/* ── Sidebar (2 cols) ── */}
        <div className="xl:col-span-2 space-y-lg">
          {/* Community Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
            {COMMUNITY_STATS.map((s, i) => (
              <div key={i} className="bg-surface border border-outline-variant rounded-xl p-md hover:shadow-lg transition-shadow duration-300">
                <div className={`${s.bg} w-10 h-10 rounded-lg flex items-center justify-center mb-sm`}>
                  <span className={`material-symbols-outlined ${s.iconColor} text-[20px]`}>{s.icon}</span>
                </div>
                <p className="text-2xl font-bold text-on-surface">{s.value}</p>
                <p className="text-xs font-[Geist] text-on-surface-variant mt-xs">{s.label}</p>
                <p className="text-[11px] text-on-surface-variant/60 mt-xs">{s.trend}</p>
              </div>
            ))}
          </div>

          {/* FAQ / Help */}
          <div className="bg-surface border border-outline-variant rounded-xl p-lg">
            <div className="flex items-center gap-sm mb-md">
              <span className="material-symbols-outlined text-primary">help</span>
              <h3 className="text-lg font-semibold text-on-surface">Common Questions</h3>
            </div>
            <div className="space-y-xs">
              {FAQ_ITEMS.map((faq, i) => (
                <div key={i} className="border border-outline-variant rounded-lg overflow-hidden transition-all duration-300">
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                    className="w-full flex items-center justify-between px-md py-sm text-left cursor-pointer hover:bg-surface-container/60 transition-colors"
                  >
                    <span className="text-sm font-medium text-on-surface pr-sm">{faq.q}</span>
                    <span className={`material-symbols-outlined text-on-surface-variant text-[20px] shrink-0 transition-transform duration-300 ${expandedFaq === i ? 'rotate-180' : ''}`}>
                      expand_more
                    </span>
                  </button>
                  <div
                    className={`overflow-hidden transition-all duration-300 ease-in-out ${expandedFaq === i ? 'max-h-48 opacity-100' : 'max-h-0 opacity-0'}`}
                  >
                    <p className="px-md pb-sm text-sm text-on-surface-variant leading-relaxed">{faq.a}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Recent Submissions ── */}
      <section className="bg-surface border border-outline-variant rounded-xl overflow-hidden">
        <div className="flex items-center justify-between p-lg pb-md">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary">history</span>
            <h3 className="text-lg font-semibold text-on-surface">Recent Submissions</h3>
            <span className="bg-primary-container/10 text-primary text-xs font-[Geist] font-medium px-sm py-[2px] rounded-full">
              {MOCK_SUBMISSIONS.length}
            </span>
          </div>
        </div>

        {/* Desktop Table */}
        <div className="hidden md:block overflow-x-auto custom-scrollbar">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-t border-outline-variant text-on-surface-variant font-[Geist] text-xs uppercase tracking-wider">
                <th className="text-left px-lg py-sm font-medium">ID</th>
                <th className="text-left px-lg py-sm font-medium">Date</th>
                <th className="text-left px-lg py-sm font-medium">Category</th>
                <th className="text-left px-lg py-sm font-medium">Subject</th>
                <th className="text-left px-lg py-sm font-medium">Priority</th>
                <th className="text-left px-lg py-sm font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_SUBMISSIONS.map((item) => (
                <tr key={item.id} className="border-t border-outline-variant/60 hover:bg-surface-container/40 transition-colors">
                  <td className="px-lg py-md font-mono text-xs text-on-surface-variant">{item.id}</td>
                  <td className="px-lg py-md text-on-surface-variant">
                    {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </td>
                  <td className="px-lg py-md">
                    <span className={`inline-block text-xs font-[Geist] font-medium px-sm py-[3px] rounded-md border ${categoryBadge(item.category)}`}>
                      {item.category}
                    </span>
                  </td>
                  <td className="px-lg py-md text-on-surface font-medium max-w-xs truncate">{item.subject}</td>
                  <td className="px-lg py-md">
                    <span className="flex items-center gap-xs text-on-surface-variant">
                      <span className={`w-2.5 h-2.5 rounded-full ${priorityDot(item.priority)}`} />
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-lg py-md">
                    <span className={`inline-flex items-center gap-xs text-xs font-[Geist] font-medium px-sm py-[3px] rounded-md border ${statusBadge(item.status)}`}>
                      <span className="material-symbols-outlined text-[14px]">{statusIcon(item.status)}</span>
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Cards */}
        <div className="md:hidden space-y-sm px-md pb-md">
          {MOCK_SUBMISSIONS.map((item) => (
            <div key={item.id} className="border border-outline-variant rounded-lg p-md space-y-sm">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-on-surface-variant">{item.id}</span>
                <span className={`inline-flex items-center gap-xs text-xs font-[Geist] font-medium px-sm py-[2px] rounded-md border ${statusBadge(item.status)}`}>
                  <span className="material-symbols-outlined text-[13px]">{statusIcon(item.status)}</span>
                  {item.status}
                </span>
              </div>
              <p className="text-sm font-medium text-on-surface">{item.subject}</p>
              <div className="flex items-center gap-sm flex-wrap">
                <span className={`text-[11px] font-[Geist] font-medium px-sm py-[2px] rounded-md border ${categoryBadge(item.category)}`}>
                  {item.category}
                </span>
                <span className="flex items-center gap-xs text-xs text-on-surface-variant">
                  <span className={`w-1.5 h-1.5 rounded-full ${priorityDot(item.priority)}`} />
                  {item.priority}
                </span>
                <span className="text-xs text-on-surface-variant/60">
                  {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
