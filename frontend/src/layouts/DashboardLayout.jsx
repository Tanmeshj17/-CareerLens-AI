import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useState, useContext, useEffect } from 'react'
import { AuthContext } from '../App'
import Footer from '../components/Footer'
import CareerLensLogo from '../components/CareerLensLogo'

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
]

// Admin-only items — kept completely separate so they never leak into accountItems
const adminItems = [
  { icon: 'admin_panel_settings', label: 'Admin Panel', path: '/app/admin' },
]

// Mobile Bottom Navigation items (top 4 primary actions + Menu trigger)
const mobileBottomNav = [
  { icon: 'dashboard', label: 'Dashboard', path: '/app', end: true },
  { icon: 'work', label: 'Jobs', path: '/app/opportunities' },
  { icon: 'description', label: 'Resume', path: '/app/resume' },
  { icon: 'fact_check', label: 'Tracker', path: '/app/tracker' },
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
      {/* Mobile Overlay Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar (Preserves exact desktop Stitch design) */}
      <aside className={`
        w-[260px] h-screen fixed left-0 top-0 flex flex-col bg-surface border-r border-outline-variant z-50
        transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* Brand Header */}
        <div className="p-lg border-b border-outline-variant/40 flex items-center justify-between">
          <div>
            <CareerLensLogo size="md" />
            <p className="text-xs font-medium text-on-surface-variant tracking-wider mt-1 font-[Geist]">AI-Powered Career Growth</p>
          </div>
          {/* Close button inside mobile drawer */}
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-lg transition-colors"
            aria-label="Close sidebar"
          >
            <span className="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        <nav className="flex-1 px-sm py-xs overflow-y-auto custom-scrollbar">
          <div className="space-y-xs">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/app'}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-md py-sm px-md transition-all text-sm font-medium rounded-lg ${
                    isActive
                      ? 'bg-secondary-container text-on-secondary-container border-l-4 border-primary font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container'
                  }`
                }
              >
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span className="font-[Geist]">{item.label}</span>
              </NavLink>
            ))}
          </div>

          <div className="pt-lg pb-sm px-md">
            <span className="text-xs font-medium text-on-surface-variant/50 uppercase tracking-widest font-[Geist]">Account</span>
          </div>

          <div className="space-y-xs">
            {accountItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-md py-sm px-md transition-all text-sm font-medium rounded-lg ${
                    isActive
                      ? 'bg-secondary-container text-on-secondary-container border-l-4 border-primary font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container'
                  }`
                }
              >
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span className="font-[Geist]">{item.label}</span>
              </NavLink>
            ))}

            {/* Admin-only section — completely invisible to regular users */}
            {user?.role === 'admin' && (
              <>
                <div className="pt-sm pb-xs px-md">
                  <span className="text-[10px] font-bold text-primary/60 uppercase tracking-widest font-[Geist]">Admin</span>
                </div>
                {adminItems.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-md py-sm px-md transition-all text-sm font-medium rounded-lg ${
                        isActive
                          ? 'bg-primary/10 text-primary border-l-4 border-primary font-semibold'
                          : 'text-primary/70 hover:bg-primary/5'
                      }`
                    }
                  >
                    <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                    <span className="font-[Geist]">{item.label}</span>
                  </NavLink>
                ))}
              </>
            )}
          </div>
        </nav>

        {/* User Card */}
        <div className="p-md border-t border-outline-variant">
          <div className="flex items-center gap-md p-sm rounded-lg hover:bg-surface-container cursor-pointer transition-colors">
            <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary font-bold text-sm shrink-0">
              {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold font-[Geist] truncate">{user?.full_name}</p>
              <p className="text-xs font-medium text-on-surface-variant font-[Geist] truncate">{user?.role || 'Member'}</p>
            </div>
            <button
              onClick={() => { logout(); navigate('/'); }}
              className="material-symbols-outlined text-on-surface-variant hover:text-error transition-colors text-xl p-1.5 rounded-md hover:bg-surface-variant"
              title="Logout"
            >
              logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 lg:ml-[260px] flex flex-col min-h-screen min-w-0">
        {/* Top Nav (Responsive header) */}
        <header className="flex justify-between items-center h-16 px-3 sm:px-4 md:px-8 sticky top-0 z-40 bg-surface/95 backdrop-blur-md border-b border-outline-variant">
          <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
            <button
              className="lg:hidden text-on-surface-variant p-2 hover:bg-surface-container rounded-lg shrink-0 touch-target flex items-center justify-center"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <span className="material-symbols-outlined text-2xl">menu</span>
            </button>

            {/* Mobile Brand Logo Icon */}
            <div className="lg:hidden flex items-center shrink-0">
              <CareerLensLogo size="xs" variant="icon" />
            </div>

            {/* Search Input */}
            <div className="relative w-full max-w-[180px] sm:max-w-xs md:max-w-md">
              <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-outline text-sm">search</span>
              <input
                type="text"
                placeholder="Search..."
                className="w-full bg-surface-container-low border border-outline-variant rounded-full py-1.5 sm:py-2 pl-8 sm:pl-10 pr-3 sm:pr-4 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary truncate"
              />
            </div>
          </div>

          {/* Right Header Actions */}
          <div className="flex items-center gap-1 sm:gap-3 md:gap-4 shrink-0 ml-2">
            <button
              className="relative p-2 text-on-surface-variant hover:text-primary transition-colors touch-target-sm flex items-center justify-center rounded-lg hover:bg-surface-container"
              onClick={() => navigate('/app/notifications')}
              title="Notifications"
            >
              <span className="material-symbols-outlined text-xl sm:text-2xl">notifications</span>
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full ring-2 ring-surface"></span>
            </button>

            <button
              className="p-2 text-on-surface-variant hover:text-primary transition-colors hidden sm:flex items-center justify-center rounded-lg hover:bg-surface-container touch-target-sm"
              onClick={() => navigate('/app/profile')}
              title="Settings"
            >
              <span className="material-symbols-outlined text-xl sm:text-2xl">settings</span>
            </button>

            <div
              className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-primary-container flex items-center justify-center text-on-primary font-bold text-xs cursor-pointer shrink-0 ring-2 ring-outline-variant/30 hover:ring-primary transition-all"
              onClick={() => navigate('/app/profile')}
              title="My Profile"
            >
              {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
            </div>
          </div>
        </header>

        {/* Page Content (With bottom padding on mobile for Bottom Nav safety) */}
        <main className="flex-1 p-3 sm:p-5 md:p-8 pb-24 lg:pb-8 max-w-[1440px] mx-auto w-full flex flex-col min-w-0 overflow-x-hidden">
          <div className="flex-1 mb-lg sm:mb-xl min-w-0 min-h-[80vh]">
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>

      {/* ── Mobile Bottom Navigation Bar (Appears exclusively on < lg screens) ── */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-outline-variant py-1 px-2 flex justify-around items-center lg:hidden shadow-lg shadow-black/10">
        {mobileBottomNav.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all min-w-[56px] ${
                isActive
                  ? 'text-primary font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`p-1 rounded-full transition-all ${isActive ? 'bg-primary-container/15' : ''}`}>
                  <span
                    className="material-symbols-outlined text-[22px]"
                    style={isActive ? { fontVariationSettings: "'FILL' 1" } : {}}
                  >
                    {item.icon}
                  </span>
                </div>
                <span className="text-[10px] font-medium font-[Geist] leading-tight mt-0.5">
                  {item.label}
                </span>
              </>
            )}
          </NavLink>
        ))}

        {/* More / Menu Button for drawer */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="flex flex-col items-center justify-center py-1 px-2 rounded-xl text-on-surface-variant hover:text-on-surface min-w-[56px]"
          aria-label="Open full menu"
        >
          <div className="p-1 rounded-full">
            <span className="material-symbols-outlined text-[22px]">menu</span>
          </div>
          <span className="text-[10px] font-medium font-[Geist] leading-tight mt-0.5">
            More
          </span>
        </button>
      </nav>
    </div>
  )
}

