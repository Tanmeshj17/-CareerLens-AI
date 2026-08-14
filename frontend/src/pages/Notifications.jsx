export default function Notifications() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in-up text-center px-4">

      {/* Animated icon */}
      <div className="relative mb-8">
        <div className="w-28 h-28 rounded-full bg-primary-container/10 flex items-center justify-center">
          <span
            className="material-symbols-outlined text-primary"
            style={{ fontSize: 52, fontVariationSettings: "'FILL' 1" }}
          >
            notifications
          </span>
        </div>
        {/* Ping rings */}
        <span className="absolute inset-0 rounded-full bg-primary/10 animate-ping opacity-60" />
        <span className="absolute inset-2 rounded-full bg-primary/5 animate-ping opacity-40 animation-delay-300" />
      </div>

      {/* Badge */}
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-container/15 text-primary text-xs font-bold uppercase tracking-widest mb-4">
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
        Coming Soon
      </span>

      <h2 className="text-3xl sm:text-4xl font-bold text-on-surface mb-3">
        Notifications
      </h2>
      <p className="text-base text-on-surface-variant max-w-sm leading-relaxed mb-8">
        We're building a smart notification system — real-time job alerts, application updates, and AI-powered career tips, all in one place.
      </p>

      {/* Feature preview chips */}
      <div className="flex flex-wrap justify-center gap-2.5 mb-10">
        {[
          { icon: 'work', label: 'Job Match Alerts' },
          { icon: 'fact_check', label: 'Application Updates' },
          { icon: 'lightbulb', label: 'AI Career Tips' },
          { icon: 'phone_android', label: 'Push Notifications' },
        ].map(({ icon, label }) => (
          <div
            key={label}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-outline-variant bg-surface text-sm text-on-surface-variant"
          >
            <span className="material-symbols-outlined text-primary" style={{ fontSize: 16 }}>
              {icon}
            </span>
            {label}
          </div>
        ))}
      </div>

      {/* Decorative notification preview cards */}
      <div className="w-full max-w-sm space-y-2 opacity-40 pointer-events-none select-none">
        {[
          { icon: 'work', color: 'text-primary', bg: 'bg-primary-container/15', text: 'New Match: Senior Frontend Engineer at Stripe' },
          { icon: 'fact_check', color: 'text-success', bg: 'bg-success/10', text: 'Your application was viewed by a recruiter' },
          { icon: 'lightbulb', color: 'text-warning', bg: 'bg-warning/10', text: 'Adding 3 skills could boost your profile 40%' },
        ].map(({ icon, color, bg, text }) => (
          <div key={text} className="flex items-center gap-3 p-3 rounded-xl border border-outline-variant bg-surface">
            <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center shrink-0`}>
              <span className={`material-symbols-outlined text-[16px] ${color}`} style={{ fontVariationSettings: "'FILL' 1" }}>
                {icon}
              </span>
            </div>
            <span className="text-xs text-on-surface-variant text-left leading-relaxed">{text}</span>
            <span className="w-2 h-2 rounded-full bg-primary shrink-0 ml-auto" />
          </div>
        ))}
      </div>
    </div>
  )
}
