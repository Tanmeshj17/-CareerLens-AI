import { useState, useContext } from 'react'
import { AuthContext } from '../App'

const initialNotifications = [
  {
    id: 1,
    type: 'job',
    title: 'New Match: Senior Frontend Engineer',
    description: 'A new role at Stripe matches 96% of your profile. Remote position with $140k–$180k salary range.',
    timestamp: '12 minutes ago',
    read: false,
    action: { label: 'View Job', icon: 'arrow_forward' },
  },
  {
    id: 2,
    type: 'application',
    title: 'Application Viewed by Recruiter',
    description: 'Your application for Product Designer at Google was viewed by a hiring manager.',
    timestamp: '1 hour ago',
    read: false,
    action: { label: 'View Application', icon: 'arrow_forward' },
  },
  {
    id: 3,
    type: 'job',
    title: 'Saved Job Closing Soon',
    description: 'UX Researcher at Airbnb closes in 2 days. 47 applicants so far — apply now to stay competitive.',
    timestamp: '2 hours ago',
    read: false,
    action: { label: 'View Job', icon: 'arrow_forward' },
  },
  {
    id: 4,
    type: 'tip',
    title: 'Boost Your Profile Visibility',
    description: 'Adding 3 more skills to your profile could increase recruiter views by up to 40%. We identified Figma, Framer, and GraphQL as top picks.',
    timestamp: '3 hours ago',
    read: false,
    action: { label: 'Update Profile', icon: 'arrow_forward' },
  },
  {
    id: 5,
    type: 'application',
    title: 'Interview Scheduled',
    description: 'Congratulations! Netflix has scheduled a phone screen for your Full-Stack Developer application on June 20, 2026 at 2:00 PM PST.',
    timestamp: '5 hours ago',
    read: true,
    action: { label: 'View Details', icon: 'arrow_forward' },
  },
  {
    id: 6,
    type: 'system',
    title: 'Resume Analysis Complete',
    description: 'Your updated resume scored 88/100. We found 3 improvements that could help you stand out in tech roles.',
    timestamp: '6 hours ago',
    read: true,
    action: { label: 'View Report', icon: 'arrow_forward' },
  },
  {
    id: 7,
    type: 'job',
    title: 'Trending Role in Your Area',
    description: 'Design Engineer roles surged 32% this month. 18 new positions match your experience level in San Francisco.',
    timestamp: 'Yesterday',
    read: true,
  },
  {
    id: 8,
    type: 'tip',
    title: 'Weekly Career Insight',
    description: 'Companies hiring remotely increased by 15% this quarter. Consider expanding your search radius for better matches.',
    timestamp: 'Yesterday',
    read: true,
  },
  {
    id: 9,
    type: 'application',
    title: 'Application Status: Under Review',
    description: 'Your application for Senior UI Designer at Meta has moved to the review stage. Average review time: 5–7 business days.',
    timestamp: '2 days ago',
    read: true,
  },
  {
    id: 10,
    type: 'system',
    title: 'Account Security Update',
    description: 'We noticed a login from a new device (Chrome on Windows). If this wasn\'t you, please secure your account.',
    timestamp: '3 days ago',
    read: true,
    action: { label: 'Review Activity', icon: 'shield' },
  },
  {
    id: 11,
    type: 'job',
    title: 'Recruiter Reached Out',
    description: 'A recruiter from Spotify wants to connect about a Principal Designer role. Respond within 48 hours for best results.',
    timestamp: '4 days ago',
    read: true,
    action: { label: 'View Message', icon: 'arrow_forward' },
  },
  {
    id: 12,
    type: 'system',
    title: 'New Feature: AI Interview Prep',
    description: 'Practice with our new AI-powered mock interviews. Get real-time feedback on your answers, tone, and confidence level.',
    timestamp: '1 week ago',
    read: true,
    action: { label: 'Try Now', icon: 'arrow_forward' },
  },
  {
    id: 13,
    type: 'tip',
    title: 'Certification Recommendation',
    description: 'Based on your career goals, an AWS Solutions Architect certification could unlock 23% more job matches.',
    timestamp: '1 week ago',
    read: true,
    action: { label: 'Learn More', icon: 'arrow_forward' },
  },
  {
    id: 14,
    type: 'application',
    title: 'Application Rejected',
    description: 'Unfortunately, your application for Data Analyst at Amazon was not selected. Don\'t worry — we found 8 similar roles.',
    timestamp: '1 week ago',
    read: true,
    action: { label: 'See Similar Jobs', icon: 'arrow_forward' },
  },
]

const typeConfig = {
  job: {
    icon: 'work',
    borderColor: 'border-l-[var(--color-primary)]',
    bgIcon: 'bg-primary-container/15',
    textIcon: 'text-primary',
    label: 'Job Alert',
    labelBg: 'bg-primary-container/12 text-primary',
  },
  application: {
    icon: 'fact_check',
    borderColor: 'border-l-[var(--color-success)]',
    bgIcon: 'bg-success/10',
    textIcon: 'text-success',
    label: 'Application',
    labelBg: 'bg-success/10 text-success',
  },
  system: {
    icon: 'info',
    borderColor: 'border-l-[var(--color-on-surface-variant)]',
    bgIcon: 'bg-surface-container-highest/30',
    textIcon: 'text-on-surface-variant',
    label: 'System',
    labelBg: 'bg-surface-container-highest/30 text-on-surface-variant',
  },
  tip: {
    icon: 'lightbulb',
    borderColor: 'border-l-[var(--color-warning)]',
    bgIcon: 'bg-warning/10',
    textIcon: 'text-warning',
    label: 'Tip',
    labelBg: 'bg-warning/10 text-warning',
  },
}

const filterTabs = [
  { key: 'all', label: 'All', icon: 'notifications' },
  { key: 'unread', label: 'Unread', icon: 'mark_email_unread' },
  { key: 'job', label: 'Job Alerts', icon: 'work' },
  { key: 'application', label: 'Applications', icon: 'fact_check' },
  { key: 'system', label: 'System', icon: 'info' },
  { key: 'tip', label: 'Tips', icon: 'lightbulb' },
]

export default function Notifications() {
  const { user } = useContext(AuthContext)
  const [notifications, setNotifications] = useState(initialNotifications)
  const [activeFilter, setActiveFilter] = useState('all')
  const [showPreferences, setShowPreferences] = useState(false)
  const [preferences, setPreferences] = useState({
    job: true,
    application: true,
    system: true,
    tip: true,
    email: true,
    push: false,
    sound: true,
  })

  const unreadCount = notifications.filter((n) => !n.read).length

  const filtered = notifications.filter((n) => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'unread') return !n.read
    return n.type === activeFilter
  })

  const markRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    )
  }

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  const dismissNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  const togglePreference = (key) => {
    setPreferences((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="space-y-lg animate-fade-in-up max-w-4xl mx-auto">
      {/* ── Header ── */}
      <section className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-md">
        <div className="flex items-center gap-md">
          <div className="relative">
            <div className="p-sm bg-primary-container/12 rounded-xl">
              <span className="material-symbols-outlined text-primary text-[28px]">
                notifications
              </span>
            </div>
            {unreadCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 min-w-[20px] h-5 flex items-center justify-center bg-error text-white text-[11px] font-bold font-[Geist] rounded-full px-1 animate-gentle-pulse">
                {unreadCount}
              </span>
            )}
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-on-surface">
              Notifications
            </h2>
            <p className="text-sm text-on-surface-variant">
              {unreadCount > 0
                ? `You have ${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}`
                : 'You\'re all caught up!'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-sm">
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              className="flex items-center gap-xs px-md py-sm rounded-lg text-sm font-medium font-[Geist] text-primary bg-primary-container/10 hover:bg-primary-container/20 border border-primary/15 transition-all duration-200 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">
                done_all
              </span>
              Mark All Read
            </button>
          )}
          <button
            onClick={() => setShowPreferences(!showPreferences)}
            className={`flex items-center gap-xs px-md py-sm rounded-lg text-sm font-medium font-[Geist] transition-all duration-200 cursor-pointer border ${
              showPreferences
                ? 'bg-primary text-on-primary border-primary shadow-md'
                : 'text-on-surface-variant bg-surface border-outline-variant hover:bg-surface-container'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">
              settings
            </span>
            Preferences
          </button>
        </div>
      </section>

      {/* ── Preferences Panel (Collapsible) ── */}
      <div
        className={`overflow-hidden transition-all duration-400 ease-in-out ${
          showPreferences ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="bg-surface border border-outline-variant rounded-xl p-lg space-y-md">
          <div className="flex items-center gap-sm mb-sm">
            <span className="material-symbols-outlined text-on-surface-variant text-[20px]">
              tune
            </span>
            <h3 className="text-base font-semibold text-on-surface">
              Notification Preferences
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
            {/* Category toggles */}
            <div className="space-y-sm">
              <p className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider">
                Categories
              </p>
              {[
                { key: 'job', label: 'Job Alerts', icon: 'work' },
                {
                  key: 'application',
                  label: 'Application Updates',
                  icon: 'fact_check',
                },
                { key: 'system', label: 'System Notifications', icon: 'info' },
                {
                  key: 'tip',
                  label: 'Tips & Insights',
                  icon: 'lightbulb',
                },
              ].map((cat) => (
                <label
                  key={cat.key}
                  className="flex items-center justify-between p-sm rounded-lg hover:bg-surface-container transition-colors cursor-pointer group"
                >
                  <div className="flex items-center gap-sm">
                    <span className="material-symbols-outlined text-[18px] text-on-surface-variant group-hover:text-on-surface transition-colors">
                      {cat.icon}
                    </span>
                    <span className="text-sm text-on-surface">{cat.label}</span>
                  </div>
                  <button
                    onClick={() => togglePreference(cat.key)}
                    className={`relative w-10 h-[22px] rounded-full transition-colors duration-200 cursor-pointer ${
                      preferences[cat.key]
                        ? 'bg-primary'
                        : 'bg-surface-container-highest'
                    }`}
                  >
                    <span
                      className={`absolute top-[3px] w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                        preferences[cat.key]
                          ? 'translate-x-[22px]'
                          : 'translate-x-[3px]'
                      }`}
                    />
                  </button>
                </label>
              ))}
            </div>

            {/* Delivery toggles */}
            <div className="space-y-sm">
              <p className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider">
                Delivery
              </p>
              {[
                {
                  key: 'email',
                  label: 'Email Notifications',
                  icon: 'mail',
                  desc: 'Daily digest at 9 AM',
                },
                {
                  key: 'push',
                  label: 'Push Notifications',
                  icon: 'phone_android',
                  desc: 'Real-time alerts',
                },
                {
                  key: 'sound',
                  label: 'Sound Effects',
                  icon: 'volume_up',
                  desc: 'Play sound on new alerts',
                },
              ].map((del) => (
                <label
                  key={del.key}
                  className="flex items-center justify-between p-sm rounded-lg hover:bg-surface-container transition-colors cursor-pointer group"
                >
                  <div className="flex items-center gap-sm">
                    <span className="material-symbols-outlined text-[18px] text-on-surface-variant group-hover:text-on-surface transition-colors">
                      {del.icon}
                    </span>
                    <div>
                      <span className="text-sm text-on-surface block">
                        {del.label}
                      </span>
                      <span className="text-xs text-on-surface-variant">
                        {del.desc}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => togglePreference(del.key)}
                    className={`relative w-10 h-[22px] rounded-full transition-colors duration-200 cursor-pointer ${
                      preferences[del.key]
                        ? 'bg-primary'
                        : 'bg-surface-container-highest'
                    }`}
                  >
                    <span
                      className={`absolute top-[3px] w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                        preferences[del.key]
                          ? 'translate-x-[22px]'
                          : 'translate-x-[3px]'
                      }`}
                    />
                  </button>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Filter Tabs ── */}
      <section className="flex items-center gap-xs overflow-x-auto pb-xs custom-scrollbar -mb-sm">
        {filterTabs.map((tab) => {
          const count =
            tab.key === 'all'
              ? notifications.length
              : tab.key === 'unread'
                ? unreadCount
                : notifications.filter((n) => n.type === tab.key).length
          return (
            <button
              key={tab.key}
              onClick={() => setActiveFilter(tab.key)}
              className={`flex items-center gap-xs px-md py-sm rounded-lg text-sm font-medium font-[Geist] whitespace-nowrap transition-all duration-200 cursor-pointer border ${
                activeFilter === tab.key
                  ? 'bg-primary text-on-primary border-primary shadow-md shadow-primary/20'
                  : 'text-on-surface-variant bg-surface border-outline-variant hover:bg-surface-container hover:border-outline-variant'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">
                {tab.icon}
              </span>
              {tab.label}
              <span
                className={`min-w-[20px] h-5 flex items-center justify-center text-[11px] font-bold rounded-full px-1 ${
                  activeFilter === tab.key
                    ? 'bg-white/20 text-on-primary'
                    : 'bg-surface-container-highest/40 text-on-surface-variant'
                }`}
              >
                {count}
              </span>
            </button>
          )
        })}
      </section>

      {/* ── Notification List ── */}
      {filtered.length > 0 ? (
        <section className="space-y-sm stagger-children">
          {filtered.map((n) => {
            const config = typeConfig[n.type]
            return (
              <div
                key={n.id}
                onClick={() => markRead(n.id)}
                className={`group relative bg-surface border border-outline-variant rounded-xl overflow-hidden transition-all duration-300 hover:shadow-lg hover:border-primary/20 cursor-pointer border-l-[3px] ${config.borderColor} ${
                  !n.read ? 'bg-primary-container/[0.04]' : ''
                }`}
              >
                <div className="flex items-start gap-md p-md sm:p-lg">
                  {/* Icon */}
                  <div
                    className={`shrink-0 w-10 h-10 rounded-xl ${config.bgIcon} flex items-center justify-center transition-transform duration-300 group-hover:scale-110`}
                  >
                    <span
                      className={`material-symbols-outlined text-[20px] ${config.textIcon}`}
                    >
                      {config.icon}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-sm mb-xs">
                      <div className="flex items-center gap-sm flex-wrap">
                        <h4
                          className={`text-sm font-semibold ${
                            !n.read
                              ? 'text-on-surface'
                              : 'text-on-surface/80'
                          }`}
                        >
                          {n.title}
                        </h4>
                        <span
                          className={`text-[10px] font-bold font-[Geist] uppercase tracking-wider px-2 py-0.5 rounded-full ${config.labelBg}`}
                        >
                          {config.label}
                        </span>
                      </div>

                      <div className="flex items-center gap-sm shrink-0">
                        {!n.read && (
                          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-gentle-pulse shrink-0" />
                        )}
                        <span className="text-xs text-on-surface-variant font-[Geist] whitespace-nowrap">
                          {n.timestamp}
                        </span>
                      </div>
                    </div>

                    <p
                      className={`text-sm leading-relaxed mb-sm ${
                        !n.read
                          ? 'text-on-surface-variant'
                          : 'text-on-surface-variant/70'
                      }`}
                    >
                      {n.description}
                    </p>

                    {/* Actions */}
                    <div className="flex items-center gap-sm">
                      {n.action && (
                        <button
                          onClick={(e) => e.stopPropagation()}
                          className="flex items-center gap-xs text-xs font-medium font-[Geist] text-primary hover:text-primary/80 transition-colors cursor-pointer"
                        >
                          {n.action.label}
                          <span className="material-symbols-outlined text-[14px]">
                            {n.action.icon}
                          </span>
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          dismissNotification(n.id)
                        }}
                        className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant/60 hover:text-error transition-colors cursor-pointer opacity-0 group-hover:opacity-100"
                      >
                        <span className="material-symbols-outlined text-[14px]">
                          close
                        </span>
                        Dismiss
                      </button>
                      {!n.read && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            markRead(n.id)
                          }}
                          className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant/60 hover:text-success transition-colors cursor-pointer opacity-0 group-hover:opacity-100 ml-auto"
                        >
                          <span className="material-symbols-outlined text-[14px]">
                            check
                          </span>
                          Mark read
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Hover shimmer accent */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-500 bg-gradient-to-r from-primary/[0.02] via-transparent to-transparent" />
              </div>
            )
          })}
        </section>
      ) : (
        /* ── Empty State ── */
        <section className="flex flex-col items-center justify-center py-xl text-center">
          <div className="relative mb-lg">
            <div className="w-24 h-24 rounded-full bg-surface-container flex items-center justify-center">
              <span className="material-symbols-outlined text-[48px] text-on-surface-variant/40">
                notifications_off
              </span>
            </div>
            <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-success/15 flex items-center justify-center">
              <span className="material-symbols-outlined text-success text-[18px]">
                check_circle
              </span>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-on-surface mb-xs">
            {activeFilter === 'unread'
              ? 'All caught up!'
              : `No ${activeFilter === 'all' ? '' : filterTabs.find((t) => t.key === activeFilter)?.label + ' '}notifications`}
          </h3>
          <p className="text-sm text-on-surface-variant max-w-sm">
            {activeFilter === 'unread'
              ? 'You have read all your notifications. New ones will appear here when they arrive.'
              : `There are no ${activeFilter === 'all' ? '' : activeFilter + ' '}notifications to show right now. Check back later or try a different filter.`}
          </p>
          {activeFilter !== 'all' && (
            <button
              onClick={() => setActiveFilter('all')}
              className="mt-md flex items-center gap-xs px-md py-sm rounded-lg text-sm font-medium font-[Geist] text-primary bg-primary-container/10 hover:bg-primary-container/20 border border-primary/15 transition-all duration-200 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">
                filter_list_off
              </span>
              View all notifications
            </button>
          )}
        </section>
      )}

      {/* ── Summary Footer ── */}
      {filtered.length > 0 && (
        <div className="flex items-center justify-between text-xs text-on-surface-variant font-[Geist] pt-sm border-t border-outline-variant/50">
          <span>
            Showing {filtered.length} of {notifications.length} notifications
          </span>
          <button
            onClick={() =>
              setNotifications(
                notifications.filter((n) => !n.read ? true : false)
              )
            }
            className="flex items-center gap-xs text-on-surface-variant hover:text-error transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-[14px]">
              delete_sweep
            </span>
            Clear read notifications
          </button>
        </div>
      )}
    </div>
  )
}
