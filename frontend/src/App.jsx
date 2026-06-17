import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, createContext } from 'react'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Register from './pages/Register'
import DashboardLayout from './layouts/DashboardLayout'
import Dashboard from './pages/Dashboard'
import OpportunitiesHub from './pages/OpportunitiesHub'
import ResumeAnalysis from './pages/ResumeAnalysis'
import LearnSkills from './pages/LearnSkills'
import CareerExplorer from './pages/CareerExplorer'
import FreeResources from './pages/FreeResources'
import Certifications from './pages/Certifications'
import InterviewPrep from './pages/InterviewPrep'
import ApplicationTracker from './pages/ApplicationTracker'
import Notifications from './pages/Notifications'
import Profile from './pages/Profile'
import Feedback from './pages/Feedback'
import AdminPanel from './pages/AdminPanel'
import InsightsDashboard from './pages/InsightsDashboard'

export const AuthContext = createContext()

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState({
    name: 'Alex Johnson',
    email: 'alex@careerlens.ai',
    role: 'Pro Member',
    avatar: null
  })

  const login = (email, password) => {
    setIsAuthenticated(true)
    setUser({ ...user, email })
  }

  const logout = () => {
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, setIsAuthenticated }}>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes - Dashboard Layout */}
        <Route path="/app" element={<DashboardLayout />}>
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
          <Route path="admin" element={<AdminPanel />} />
          <Route path="insights" element={<InsightsDashboard />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthContext.Provider>
  )
}
