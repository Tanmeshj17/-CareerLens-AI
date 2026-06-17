import { Link } from 'react-router-dom'
import { useContext } from 'react'
import { AuthContext } from '../App'

export default function Dashboard() {
  const { user } = useContext(AuthContext)

  const stats = [
    { title: 'Jobs Found Today', val: '142', icon: 'travel_explore', trend: '+24%', colorBg: 'bg-primary-container/10', colorIcon: 'text-primary', colorTrend: 'text-success' },
    { title: 'Internships Found', val: '28', icon: 'school', trend: 'Steady', colorBg: 'bg-secondary-container/10', colorIcon: 'text-secondary', colorTrend: 'text-on-surface-variant' },
    { title: 'Saved Jobs', val: '12', icon: 'bookmark', trend: '+5', colorBg: 'bg-surface-container-highest/20', colorIcon: 'text-on-surface-variant', colorTrend: 'text-success' },
    { title: 'Applied Jobs', val: '45', icon: 'send', trend: 'Action req.', colorBg: 'bg-error-container/10', colorIcon: 'text-error', colorTrend: 'text-error' },
  ]

  const recentSearches = [
    { role: 'Senior Product Designer', company: 'Google • California (Remote) • $140k-$180k', match: '98%', matchColor: 'bg-success/10 text-success' },
    { role: 'UX Researcher', company: 'Airbnb • Seattle, WA • $120k-$160k', match: '85%', matchColor: 'bg-success/10 text-success' },
    { role: 'Frontend Engineer (React)', company: 'Stripe • Remote • $135k-$175k', match: '76%', matchColor: 'bg-secondary-container text-on-secondary-container' },
  ]

  const notifications = [
    { title: 'Interview Invitation', desc: 'Google wants to chat about your Product Designer application.', time: '2 hours ago', icon: 'mark_email_unread', color: 'bg-primary-container/20 text-primary' },
    { title: 'Skill Gap Detected', desc: 'You\'re missing "Framer" for 4 recent job matches. Try our 5-min guide.', time: '5 hours ago', icon: 'tips_and_updates', color: 'bg-secondary-container/20 text-secondary' },
    { title: 'Profile Viewed', desc: 'Recruiters from Netflix and Meta viewed your profile today.', time: 'Yesterday', icon: 'person_check', color: 'bg-surface-container-highest/20 text-on-surface-variant' },
  ]

  return (
    <div className="space-y-xl animate-fade-in-up">
      {/* Welcome Message */}
      <section className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-md">
        <div>
          <h2 className="text-3xl font-semibold text-on-surface">Welcome back, {user?.name?.split(' ')[0]}</h2>
          <p className="text-base text-on-surface-variant">Your career growth is 12% faster than last month. Here's what's happening today.</p>
        </div>
        <Link to="/app/tracker" className="hidden md:flex bg-primary text-on-primary px-lg py-sm rounded-lg text-sm font-medium font-[Geist] shadow-sm hover:brightness-110 transition-all items-center gap-sm">
          <span className="material-symbols-outlined text-[20px]">add</span>
          New Application
        </Link>
      </section>

      {/* Stats Row */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md stagger-children">
        {stats.map((stat, i) => (
          <div key={i} className="bg-surface border border-outline-variant p-lg rounded-xl hover:shadow-lg transition-shadow duration-300">
            <div className="flex justify-between items-start mb-md">
              <div className={`p-sm ${stat.colorBg} rounded-lg`}>
                <span className={`material-symbols-outlined ${stat.colorIcon}`}>{stat.icon}</span>
              </div>
              <span className={`text-xs font-medium font-[Geist] ${stat.colorTrend}`}>{stat.trend}</span>
            </div>
            <p className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider">{stat.title}</p>
            <h3 className="text-2xl font-bold mt-xs">{stat.val}</h3>
          </div>
        ))}
      </section>

      {/* AI Tools */}
      <section>
        <h4 className="text-sm font-bold font-[Geist] text-on-surface mb-md">AI POWERED TOOLS</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-md stagger-children">
          <Link to="/app/resume" className="glass-insight p-lg rounded-xl border border-primary/20 flex flex-col justify-between hover:border-primary transition-all group">
            <div>
              <div className="flex items-center gap-sm text-primary mb-sm">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>auto_awesome</span>
                <span className="text-xs font-bold font-[Geist] uppercase">Analyze Resume</span>
              </div>
              <p className="text-sm text-on-surface-variant mb-md">Get instant score and optimization tips for your next application.</p>
            </div>
            <div className="flex items-center text-primary text-sm font-bold font-[Geist]">
              Upload PDF <span className="material-symbols-outlined ml-xs transition-transform group-hover:translate-x-1">arrow_forward</span>
            </div>
          </Link>
          <Link to="/app/learn" className="glass-insight p-lg rounded-xl border border-primary/20 flex flex-col justify-between hover:border-primary transition-all group">
            <div>
              <div className="flex items-center gap-sm text-primary mb-sm">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>bolt</span>
                <span className="text-xs font-bold font-[Geist] uppercase">Learn New Skill</span>
              </div>
              <p className="text-sm text-on-surface-variant mb-md">AI-curated learning paths based on current job market demands.</p>
            </div>
            <div className="flex items-center text-primary text-sm font-bold font-[Geist]">
              View Path <span className="material-symbols-outlined ml-xs transition-transform group-hover:translate-x-1">arrow_forward</span>
            </div>
          </Link>
          <Link to="/app/careers" className="glass-insight p-lg rounded-xl border border-primary/20 flex flex-col justify-between hover:border-primary transition-all group">
            <div>
              <div className="flex items-center gap-sm text-primary mb-sm">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>map</span>
                <span className="text-xs font-bold font-[Geist] uppercase">Explore Careers</span>
              </div>
              <p className="text-sm text-on-surface-variant mb-md">Simulate career moves and see potential salary growth.</p>
            </div>
            <div className="flex items-center text-primary text-sm font-bold font-[Geist]">
              Start Exploration <span className="material-symbols-outlined ml-xs transition-transform group-hover:translate-x-1">arrow_forward</span>
            </div>
          </Link>
        </div>
      </section>

      {/* Main Grid: Recent Searches & Notifications */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-xl">
        <div className="lg:col-span-2 bg-surface border border-outline-variant rounded-xl p-lg">
          <div className="flex justify-between items-center mb-lg">
            <h3 className="text-2xl font-bold">Recent Searches</h3>
            <Link to="/app/opportunities" className="text-primary text-sm font-medium font-[Geist]">View All</Link>
          </div>
          <div className="space-y-sm">
            {recentSearches.map((item, i) => (
              <div key={i} className="flex items-center justify-between p-md border border-outline-variant rounded-lg hover:bg-surface-container-low transition-colors cursor-pointer group">
                <div className="flex items-center gap-md">
                  <div className="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 bg-surface-container-highest flex items-center justify-center">
                    <span className="material-symbols-outlined text-outline">business</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold font-[Geist]">{item.role}</p>
                    <p className="text-xs font-medium font-[Geist] text-on-surface-variant">{item.company}</p>
                  </div>
                </div>
                <div className="flex items-center gap-md">
                  <div className={`px-sm py-xs rounded text-xs font-medium font-[Geist] ${item.matchColor}`}>{item.match}</div>
                  <span className="material-symbols-outlined text-outline group-hover:text-primary">chevron_right</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col">
          <div className="flex justify-between items-center mb-lg">
            <h3 className="text-2xl font-bold">Notifications</h3>
            <button className="material-symbols-outlined text-outline hover:text-on-surface transition-colors">more_horiz</button>
          </div>
          <div className="space-y-lg flex-1">
            {notifications.map((n, i) => (
              <div key={i} className={`flex gap-md relative ${i !== notifications.length - 1 ? 'pb-md after:absolute after:left-[19px] after:top-[40px] after:bottom-0 after:w-[1px] after:bg-outline-variant' : ''}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${n.color}`}>
                  <span className="material-symbols-outlined text-[20px]">{n.icon}</span>
                </div>
                <div>
                  <p className="text-sm font-bold font-[Geist]">{n.title}</p>
                  <p className="text-sm text-on-surface-variant">{n.desc}</p>
                  <span className="text-xs font-medium font-[Geist] text-outline mt-xs block">{n.time}</span>
                </div>
              </div>
            ))}
          </div>
          <button className="w-full mt-lg py-sm text-primary text-sm font-medium font-[Geist] border border-primary/20 rounded-lg hover:bg-primary-container/5 transition-colors">
            Clear All Notifications
          </button>
        </div>
      </section>

      {/* FAB search */}
      <Link to="/app/opportunities" className="fixed bottom-lg right-lg w-14 h-14 bg-primary text-on-primary rounded-full shadow-2xl flex items-center justify-center hover:scale-105 transition-transform z-50">
        <span className="material-symbols-outlined text-[32px]">search</span>
      </Link>
    </div>
  )
}
