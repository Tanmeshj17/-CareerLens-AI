import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import React, { useState, createContext, useEffect, Suspense } from 'react'
import { getCurrentUser, clearToken } from './api'
import DashboardLayout from './layouts/DashboardLayout'
import RouteTracker from './components/RouteTracker'

// Lazy loaded pages for performance optimization
const LandingPage = React.lazy(() => import('./pages/LandingPage'))
const Login = React.lazy(() => import('./pages/Login'))
const Register = React.lazy(() => import('./pages/Register'))
const VerifyEmail = React.lazy(() => import('./pages/VerifyEmail'))
const ForgotPassword = React.lazy(() => import('./pages/ForgotPassword'))
const ResetPassword = React.lazy(() => import('./pages/ResetPassword'))
const Dashboard = React.lazy(() => import('./pages/Dashboard'))
const OpportunitiesHub = React.lazy(() => import('./pages/OpportunitiesHub'))
const ResumeAnalysis = React.lazy(() => import('./pages/ResumeAnalysis'))
const LearnSkills = React.lazy(() => import('./pages/LearnSkills'))
const CareerExplorer = React.lazy(() => import('./pages/CareerExplorer'))
const FreeResources = React.lazy(() => import('./pages/FreeResources'))
const Certifications = React.lazy(() => import('./pages/Certifications'))
const InterviewPrep = React.lazy(() => import('./pages/InterviewPrep'))
const ApplicationTracker = React.lazy(() => import('./pages/ApplicationTracker'))
const Notifications = React.lazy(() => import('./pages/Notifications'))
const Profile = React.lazy(() => import('./pages/Profile'))
const Feedback = React.lazy(() => import('./pages/Feedback'))
const AdminPanel = React.lazy(() => import('./pages/AdminPanel'))
const InsightsDashboard = React.lazy(() => import('./pages/InsightsDashboard'))
const DataIntelligenceDashboard = React.lazy(() => import('./pages/DataIntelligenceDashboard'))

export const AuthContext = createContext()

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    let isMounted = true
    const initAuth = async () => {
      const existingToken = localStorage.getItem('careerlens_token')
      if (!existingToken) {
        setIsAuthenticated(false)
        setUser(null)
        setAuthLoading(false)
        return
      }
      try {
        const userData = await getCurrentUser()
        if (isMounted) {
          if (userData) {
            setIsAuthenticated(true)
            setUser(userData)
          } else {
            setIsAuthenticated(false)
            setUser(null)
          }
        }
      } catch (err) {
        if (isMounted) {
          setIsAuthenticated(false)
          setUser(null)
        }
      } finally {
        if (isMounted) setAuthLoading(false)
      }
    }
    initAuth()

    // ── Backend keep-alive: prevents Render cold-start (biggest speed win) ──
    const API_BASE = (import.meta.env.VITE_API_URL || 'https://careerlens-api-f74a.onrender.com').replace(/\/$/, '')
    const pingBackend = () => fetch(`${API_BASE}/health`, { method: 'GET' }).catch(() => {})
    pingBackend() // immediate ping on page load
    const pingInterval = setInterval(pingBackend, 5 * 60 * 1000) // ping every 5 min to prevent cold starts

    // ── Idle prefetch for core lazy routes to make page transitions instantaneous ──
    const prefetchIdle = () => {
      const routesToPrefetch = [
        () => import('./pages/Dashboard'),
        () => import('./pages/OpportunitiesHub'),
        () => import('./pages/ResumeAnalysis'),
        () => import('./pages/LearnSkills'),
        () => import('./pages/ApplicationTracker'),
        () => import('./pages/Profile'),
      ]
      routesToPrefetch.forEach(importer => {
        if ('requestIdleCallback' in window) {
          window.requestIdleCallback(() => importer().catch(() => {}))
        } else {
          setTimeout(() => importer().catch(() => {}), 1500)
        }
      })
    }
    prefetchIdle()

    const handleUnauthorized = () => {
      if (isMounted) {
        setIsAuthenticated(false)
        setUser(null)
        clearToken()
        navigate('/login')
      }
    }
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => {
      isMounted = false
      clearInterval(pingInterval)
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [navigate])

  const login = (userData) => {
    setIsAuthenticated(true)
    setUser(userData)
  }

  const logout = () => {
    // Set user to null FIRST before anything else so no component can ever
    // read stale user data between the logout call and the navigation.
    setUser(null)
    setIsAuthenticated(false)
    setAuthLoading(false)
    clearToken()       // clears localStorage token AND the full in-memory cache
    navigate('/login', { replace: true })
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  const LoadingFallback = () => (
    <div className="min-h-[50vh] flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
  )

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, setIsAuthenticated }}>
      <RouteTracker />
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={isAuthenticated ? (user?.role === 'admin' ? <Navigate to="/app/admin" replace /> : <Navigate to="/app" replace />) : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/app" replace /> : <Register />} />
          <Route path="/verify" element={isAuthenticated ? <Navigate to="/app" replace /> : <VerifyEmail />} />
          <Route path="/forgot-password" element={isAuthenticated ? <Navigate to="/app" replace /> : <ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* Protected Routes - Dashboard Layout */}
          <Route path="/app" element={isAuthenticated ? <DashboardLayout /> : <Navigate to="/login" replace />}>
            <Route index element={<Dashboard />} />
            <Route path="opportunities" element={<OpportunitiesHub />} />
            <Route path="resume" element={<ResumeAnalysis />} />
            <Route path="learn" element={<LearnSkills />} />
            <Route path="careers" element={<CareerExplorer />} />
            <Route path="resources" element={<FreeResources />} />
            <Route path="certifications" element={<Certifications />} />
            <Route path="interview-prep" element={<InterviewPrep />} />
            <Route path="tracker" element={<ApplicationTracker />} />
            <Route path="notifications" element={<Notifications />} />
            <Route path="profile" element={<Profile />} />
            <Route path="feedback" element={<Feedback />} />
            <Route path="admin" element={user?.role === 'admin' ? <AdminPanel /> : <Navigate to="/app" replace />} />
            <Route path="insights" element={<InsightsDashboard />} />
            <Route path="data-intelligence" element={<DataIntelligenceDashboard />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </AuthContext.Provider>
  )
}
