import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useState, useContext, useEffect } from 'react'
import { AuthContext } from '../App'
import Footer from '../components/Footer'

const navItems = [
  { icon: 'dashboard', label: 'Dashboard', path: '/app' },
  { icon: 'work', label: 'Opportunities', path: '/app/opportunities' },
  { icon: 'description', label: 'Resume Analysis', path: '/app/resume' },
  { icon: 'school', label: 'Learn Skills', path: '/app/learn' },
  { icon: 'explore', label: 'Career Explorer', path: '/app/careers' },
  { icon: 'menu_book', label: 'Free Resources', path: '/app/resources' },
  { icon: 'workspace_premium', label: 'Certifications', path: '/app/certifications' },
  { icon: 'quiz', label: 'Interview Prep', path: '/app/interview-prep' },
  { icon: 'fact_check', label: 'Application Tracker', path: '/app/tracker' },
  { icon: 'insights', label: 'Insights', path: '/app/insights' },
  { icon: 'monitor_heart', label: 'Data Intelligence', path: '/app/data-intelligence' },
]

const accountItems = [
  { icon: 'notifications', label: 'Notifications', path: '/app/notifications' },
  { icon: 'account_circle', label: 'Profile', path: '/app/profile' },
  { icon: 'rate_review', label: 'Feedback', path: '/app/feedback' },
  { icon: 'admin_panel_settings', label: 'Admin Panel', path: '/app/admin' },
]

export default function DashboardLayout() {

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()

  // Ensure sidebar overlay closes on navigation
  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  return (
    <div className="flex bg-background min-h-screen">
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        w-[260px] h-screen fixed left-0 top-0 flex flex-col bg-surface border-r border-outline-variant z-50
        transition-transform duration-300
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="p-lg">
          <h1 className="text-2xl font-bold text-primary">CareerLens AI</h1>
          <p className="text-xs font-medium text-on-surface-variant tracking-wider mt-1">AI-Powered Career Growth</p>
        </div>

        <nav className="flex-1 px-sm overflow-y-auto custom-scrollbar">
          <div className="space-y-xs">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/app'}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-md py-sm px-md transition-all text-sm font-medium ${
                    isActive
                      ? 'bg-secondary-container text-on-secondary-container border-l-4 border-primary'
                      : 'text-on-surface-variant hover:bg-surface-container'
                  }`
                }
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                <span className="font-[Geist]">{item.label}</span>
              </NavLink>
            ))}
          </div>

          <div className="pt-lg pb-sm px-md">
            <span className="text-xs font-medium text-on-surface-variant/40 uppercase tracking-widest font-[Geist]">Account</span>
          </div>

          <div className="space-y-xs">
            {accountItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-md py-sm px-md transition-all text-sm font-medium ${
                    isActive
                      ? 'bg-secondary-container text-on-secondary-container border-l-4 border-primary'
                      : 'text-on-surface-variant hover:bg-surface-container'
                  }`
                }
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                <span className="font-[Geist]">{item.label}</span>
              </NavLink>
            ))}
          </div>
        </nav>

        <div className="p-md border-t border-outline-variant">
          <div className="flex items-center gap-md p-sm rounded-lg hover:bg-surface-container cursor-pointer transition-colors">
            <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary font-bold text-sm">
              {user?.full_name?.split(' ').map(n => n[0]).join('')}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold font-[Geist] truncate">{user?.full_name}</p>
              <p className="text-xs font-medium text-on-surface-variant font-[Geist]">{user?.role}</p>
            </div>
            <button
              onClick={() => { logout(); navigate('/'); }}
              className="material-symbols-outlined text-on-surface-variant hover:text-error transition-colors text-xl"
              title="Logout"
            >
              logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 lg:ml-[260px] flex flex-col min-h-screen min-w-0">
        {/* Top Nav */}
        <header className="flex justify-between items-center h-16 px-sm sm:px-md md:px-lg sticky top-0 z-40 bg-surface/95 backdrop-blur-sm border-b border-outline-variant">
          <div className="flex items-center gap-xs sm:gap-md flex-1 min-w-0">
            <button
              className="lg:hidden material-symbols-outlined text-on-surface-variant p-2 hover:bg-surface-container rounded-lg shrink-0"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              menu
            </button>
            <div className="relative w-full max-w-[200px] sm:max-w-xs md:max-w-md">
              <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-outline text-sm">search</span>
              <input
                type="text"
                placeholder="Search..."
                className="w-full bg-surface-container-low border border-outline-variant rounded-full py-1.5 sm:py-2 pl-8 sm:pl-10 pr-3 sm:pr-4 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary truncate"
              />
            </div>
          </div>
          <div className="flex items-center gap-xs sm:gap-md md:gap-lg shrink-0 ml-2">
            <button className="relative p-1 text-on-surface-variant hover:text-primary transition-colors" onClick={() => navigate('/app/notifications')} title="Notifications">
              <span className="material-symbols-outlined text-xl sm:text-2xl">notifications</span>
              <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>
            </button>
            <button className="p-1 text-on-surface-variant hover:text-primary transition-colors hidden sm:block" onClick={() => navigate('/app/profile')} title="Settings">
              <span className="material-symbols-outlined text-xl sm:text-2xl">settings</span>
            </button>
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-primary-container flex items-center justify-center text-on-primary font-bold text-xs cursor-pointer shrink-0" onClick={() => navigate('/app/profile')}>
              {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-3 sm:p-5 md:p-8 max-w-[1440px] mx-auto w-full flex flex-col min-w-0 overflow-x-hidden">
          <div className="flex-1 mb-lg sm:mb-xl min-w-0">
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>
    </div>
  )
}
