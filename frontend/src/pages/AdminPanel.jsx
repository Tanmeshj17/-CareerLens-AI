import { useState, useEffect, useContext } from 'react'
import { AuthContext } from '../App'
import {
  adminGetSummary,
  adminGetUsers,
  adminGetUserStats,
  adminUpdateUserRole,
  adminDeleteUser,
  adminChangePassword,
  adminGetCollectorStats,
  adminTriggerCollector,
  adminGetPageAnalytics,
  adminGetFeedback,
  adminUpdateFeedback,
  adminGetOpportunitiesAudit,
  adminUpdateOpportunityStatus
} from '../api'

const RATING_EMOJIS = {
  1: { emoji: '😞', label: 'Poor' },
  2: { emoji: '😕', label: 'Fair' },
  3: { emoji: '😊', label: 'Good' },
  4: { emoji: '😄', label: 'Very Good' },
  5: { emoji: '🤩', label: 'Excellent' },
}

const STATUS_STYLE = {
  'Open': 'bg-info/10 text-info border-info/30',
  'In Review': 'bg-warning/10 text-warning border-warning/30',
  'Resolved': 'bg-success/10 text-success border-success/30',
  'Closed': 'bg-surface-container text-on-surface-variant border-outline-variant',
}

const PRIORITIES = {
  'Low': 'bg-info/10 text-info border-info/30',
  'Medium': 'bg-warning/10 text-warning border-warning/30',
  'High': 'bg-error/10 text-error border-error/30',
  'Critical': 'bg-error/20 text-error border-error/50 font-bold',
}

export default function AdminPanel() {
  const { user } = useContext(AuthContext)
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')

  // Password Change Modal State
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [pwError, setPwError] = useState('')
  const [pwSuccess, setPwSuccess] = useState('')
  const [changingPw, setChangingPw] = useState(false)

  // 1. Overview Summary Data
  const [summary, setSummary] = useState(null)

  // 2. Users Data
  const [usersList, setUsersList] = useState([])
  const [userStats, setUserStats] = useState(null)
  const [userSearch, setUserSearch] = useState('')
  const [userRoleFilter, setUserRoleFilter] = useState('')
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [userToDelete, setUserToDelete] = useState(null)
  const [deletingUser, setDeletingUser] = useState(false)

  // 3. Collector Analytics Data
  const [collectorStats, setCollectorStats] = useState(null)
  const [triggeringCollector, setTriggeringCollector] = useState(false)
  const [collectorResult, setCollectorResult] = useState(null)

  // 4. Page & Feature Analytics Data
  const [pageAnalytics, setPageAnalytics] = useState(null)
  const [pageDays, setPageDays] = useState(30)

  // 5. Feedback Data
  const [feedbackList, setFeedbackList] = useState([])
  const [feedbackFilter, setFeedbackFilter] = useState('')
  const [loadingFeedback, setLoadingFeedback] = useState(false)

  // 6. Job Inventory & Audit Data (Added/Deleted/Inactive jobs)
  const [inventoryData, setInventoryData] = useState(null)
  const [inventoryLoading, setInventoryLoading] = useState(false)
  const [inventoryStatusFilter, setInventoryStatusFilter] = useState('active')
  const [inventoryTimeRange, setInventoryTimeRange] = useState('all')
  const [inventorySearch, setInventorySearch] = useState('')
  const [inventorySourceFilter, setInventorySourceFilter] = useState('')
  const [inventoryOffset, setInventoryOffset] = useState(0)
  const [updatingOppId, setUpdatingOppId] = useState(null)

  useEffect(() => {
    if (user?.role === 'admin') {
      loadInitialData()
    }
  }, [user])

  async function loadInitialData() {
    setLoading(true)
    setError('')
    try {
      const [sum, col, pages] = await Promise.all([
        adminGetSummary().catch(() => null),
        adminGetCollectorStats().catch(() => null),
        adminGetPageAnalytics(30).catch(() => null),
      ])
      setSummary(sum)
      setCollectorStats(col)
      setPageAnalytics(pages)
    } catch (err) {
      setError(err?.message || 'Failed to load admin metrics')
    } finally {
      setLoading(false)
    }
  }

  // Load Users tab data
  useEffect(() => {
    if (activeTab === 'users' && user?.role === 'admin') {
      loadUsers()
      loadUserStats()
    }
  }, [activeTab, userSearch, userRoleFilter])

  async function loadUsers() {
    setLoadingUsers(true)
    try {
      const data = await adminGetUsers({
        q: userSearch,
        role: userRoleFilter,
        limit: 100,
      })
      setUsersList(data?.users || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingUsers(false)
    }
  }

  async function loadUserStats() {
    try {
      const stats = await adminGetUserStats()
      setUserStats(stats)
    } catch (_) {}
  }

  // Load Feedback tab data
  useEffect(() => {
    if (activeTab === 'feedback' && user?.role === 'admin') {
      loadFeedback()
    }
  }, [activeTab, feedbackFilter])

  async function loadFeedback() {
    setLoadingFeedback(true)
    try {
      const data = await adminGetFeedback({ status: feedbackFilter, limit: 100 })
      setFeedbackList(data?.items || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingFeedback(false)
    }
  }

  // Load Job Inventory & Audit tab data
  useEffect(() => {
    if (activeTab === 'inventory' && user?.role === 'admin') {
      loadInventory(0)
    }
  }, [activeTab, inventoryStatusFilter, inventoryTimeRange, inventorySearch, inventorySourceFilter])

  async function loadInventory(offset = inventoryOffset) {
    setInventoryLoading(true)
    try {
      const data = await adminGetOpportunitiesAudit({
        status_filter: inventoryStatusFilter,
        q: inventorySearch,
        source: inventorySourceFilter,
        time_range: inventoryTimeRange,
        limit: 50,
        offset: offset
      })
      setInventoryData(data)
      setInventoryOffset(offset)
    } catch (err) {
      console.error(err)
    } finally {
      setInventoryLoading(false)
    }
  }

  async function handleToggleOppStatus(oppId, currentIsActive) {
    const nextStatus = currentIsActive ? 'INACTIVE' : 'ACTIVE'
    const actionName = currentIsActive ? 'deactivate / soft-delete' : 'reactivate'
    if (!window.confirm(`Are you sure you want to ${actionName} this opportunity (#${oppId})?`)) return

    setUpdatingOppId(oppId)
    try {
      await adminUpdateOpportunityStatus(oppId, {
        status: nextStatus,
        is_active: !currentIsActive,
        reason: currentIsActive ? 'Admin Manual Deactivation' : null
      })
      setActionMessage(`Opportunity #${oppId} successfully updated to ${nextStatus}`)
      setTimeout(() => setActionMessage(''), 4000)
      await loadInventory(inventoryOffset)
      adminGetSummary().then(sum => setSummary(sum)).catch(() => {})
    } catch (err) {
      alert(err?.message || 'Failed to update opportunity status')
    } finally {
      setUpdatingOppId(null)
    }
  }

  // Handlers
  async function handleRoleToggle(targetUser) {
    const nextRole = targetUser.role === 'admin' ? 'user' : 'admin'
    try {
      await adminUpdateUserRole(targetUser.id, nextRole)
      setActionMessage(`Role for ${targetUser.email} changed to ${nextRole}`)
      await loadUsers()
      await loadInitialData()
      setTimeout(() => setActionMessage(''), 4000)
    } catch (err) {
      alert(err?.message || 'Failed to update role')
    }
  }

  async function handleDeleteUserConfirm() {
    if (!userToDelete) return
    setDeletingUser(true)
    try {
      await adminDeleteUser(userToDelete.id)
      setActionMessage(`User ${userToDelete.email} was permanently deleted`)
      setUserToDelete(null)
      await loadUsers()
      await loadInitialData()
      setTimeout(() => setActionMessage(''), 4000)
    } catch (err) {
      alert(err?.message || 'Failed to delete user')
    } finally {
      setDeletingUser(false)
    }
  }

  async function handleTriggerCollector() {
    setTriggeringCollector(true)
    setCollectorResult(null)
    try {
      const res = await adminTriggerCollector()
      setCollectorResult(res)
      setActionMessage(res?.message || 'Collector executed successfully!')
      // Refresh metrics
      const col = await adminGetCollectorStats()
      setCollectorStats(col)
      const sum = await adminGetSummary()
      setSummary(sum)
      setTimeout(() => setActionMessage(''), 6000)
    } catch (err) {
      alert(err?.message || 'Collector execution failed')
    } finally {
      setTriggeringCollector(false)
    }
  }

  async function handleFeedbackStatusChange(feedbackId, newStatus) {
    try {
      await adminUpdateFeedback(feedbackId, { status: newStatus })
      setFeedbackList(prev => prev.map(fb => fb.id === feedbackId ? { ...fb, status: newStatus } : fb))
    } catch (err) {
      alert(err?.message || 'Failed to update status')
    }
  }

  async function handleChangePasswordSubmit(e) {
    e.preventDefault()
    setPwError('')
    setPwSuccess('')
    if (newPw.length < 8) {
      setPwError('New password must be at least 8 characters long')
      return
    }
    if (newPw !== confirmPw) {
      setPwError('New password and confirmation do not match')
      return
    }
    setChangingPw(true)
    try {
      const res = await adminChangePassword({ current_password: currentPw, new_password: newPw })
      setPwSuccess(res?.message || 'Password updated successfully!')
      setCurrentPw('')
      setNewPw('')
      setConfirmPw('')
      setTimeout(() => {
        setShowPasswordModal(false)
        setPwSuccess('')
      }, 2000)
    } catch (err) {
      setPwError(err?.message || 'Failed to update password')
    } finally {
      setChangingPw(false)
    }
  }

  function exportUsersToCSV() {
    if (!usersList.length) return
    const headers = ['ID', 'Full Name', 'Email', 'Role', 'Verified', 'Created At', 'Applications', 'Resumes', 'Feedback']
    const rows = usersList.map(u => [
      u.id,
      `"${(u.full_name || '').replace(/"/g, '""')}"`,
      u.email,
      u.role,
      u.is_verified ? 'Yes' : 'No',
      u.created_at || '',
      u.applications_count || 0,
      u.resumes_count || 0,
      u.feedback_count || 0
    ])
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `careerlens_users_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Security Wall
  if (user?.role !== 'admin') {
    return (
      <div className="glass-effect rounded-2xl p-xl text-center max-w-lg mx-auto space-y-md my-xl animate-fade-in-up">
        <div className="w-16 h-16 rounded-2xl bg-error/15 text-error flex items-center justify-center mx-auto">
          <span className="material-symbols-outlined text-3xl">lock</span>
        </div>
        <h2 className="text-xl font-bold text-on-surface">Restricted Area</h2>
        <p className="text-sm text-on-surface-variant font-[Geist] leading-relaxed">
          This Command Center is restricted exclusively to authorized administrators (<code className="bg-surface-container px-1.5 py-0.5 rounded text-xs">careerlensadmin</code>).
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-lg sm:space-y-xl animate-fade-in-up max-w-7xl mx-auto pb-3xl">

      {/* ═══════════════ HEADER ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-br from-primary/15 via-primary-container/10 to-transparent rounded-t-2xl pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md pt-sm">
          <div className="flex items-center gap-md">
            <div className="p-md bg-primary text-on-primary rounded-2xl flex items-center justify-center shadow-md shadow-primary/20">
              <span className="material-symbols-outlined text-3xl">admin_panel_settings</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
                  Admin Command Center
                </h1>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-extrabold uppercase tracking-wide bg-primary/10 text-primary border border-primary/20">
                  ROOT ADMIN
                </span>
              </div>
              <p className="text-xs sm:text-sm text-on-surface-variant font-[Geist] mt-xs">
                Real-time user intelligence, live job collector ingestion velocity, and feature usage analytics.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-sm">
            <button
              onClick={() => { setShowPasswordModal(true); setPwError(''); setPwSuccess(''); }}
              className="px-md py-sm bg-surface-container hover:bg-surface-container-high text-on-surface rounded-xl text-xs font-semibold font-[Geist] transition-all flex items-center gap-1.5 border border-outline-variant"
            >
              <span className="material-symbols-outlined text-[16px]">lock_reset</span>
              Change Password
            </button>
            <button
              onClick={loadInitialData}
              disabled={loading}
              className="px-md py-sm bg-surface-container hover:bg-surface-container-high text-on-surface rounded-xl text-xs font-semibold font-[Geist] transition-all flex items-center gap-1.5 border border-outline-variant"
            >
              <span className={`material-symbols-outlined text-[16px] ${loading ? 'animate-spin' : ''}`}>refresh</span>
              Refresh Live Data
            </button>
          </div>
        </div>

        {actionMessage && (
          <div className="mt-md p-sm px-md rounded-xl bg-success/15 border border-success/30 text-success text-xs font-semibold font-[Geist] flex items-center gap-2 animate-fade-in">
            <span className="material-symbols-outlined text-base">check_circle</span>
            <span>{actionMessage}</span>
          </div>
        )}
      </section>

      {/* ═══════════════ TOP KPI COUNTERS (4 CARDS) ═══════════════ */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-sm sm:gap-md">
          {/* Total Registered Users */}
          <div className="p-md sm:p-lg rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
            <div className="flex justify-between items-start">
              <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Registered Accounts</span>
              <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                <span className="material-symbols-outlined text-lg">how_to_reg</span>
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
              {summary.users?.total?.toLocaleString() || 0}
            </div>
            <div className="flex items-center gap-1.5 text-[11px] font-[Geist] text-success mt-xs font-medium">
              <span className="material-symbols-outlined text-[14px]">verified</span>
              <span>{summary.users?.verified || 0} Verified Accounts ({summary.users?.verification_rate || 100}%)</span>
            </div>
          </div>

          {/* Total Active Jobs */}
          <div className="p-md sm:p-lg rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
            <div className="flex justify-between items-start">
              <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Active Jobs in DB</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                <span className="material-symbols-outlined text-lg">work</span>
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
              {summary.collector?.active?.toLocaleString() || 0}
            </div>
            <div className="text-[11px] font-[Geist] text-on-surface-variant mt-xs">
              <span className="font-semibold text-emerald-600">{summary.collector?.verified?.toLocaleString() || 0}</span> high-trust (&gt;80) listings
            </div>
          </div>

          {/* Ingestion Today (24 Hours) */}
          <div className="p-md sm:p-lg rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
            <div className="flex justify-between items-start">
              <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Ingested (24h)</span>
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-600 flex items-center justify-center">
                <span className="material-symbols-outlined text-lg">bolt</span>
              </div>
            </div>
            <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
              {summary.collector?.jobs_24h?.toLocaleString() || 0}
            </div>
            <div className="text-[11px] font-[Geist] text-amber-600 mt-xs font-medium">
              +{summary.collector?.jobs_1h || 0} in last 1 hour
            </div>
          </div>

          {/* Most Active Feature / Page */}
          <div className="p-md sm:p-lg rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
            <div className="flex justify-between items-start">
              <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Top Used Feature</span>
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
                <span className="material-symbols-outlined text-lg">trending_up</span>
              </div>
            </div>
            <div className="text-base sm:text-lg font-bold text-on-surface mt-sm truncate" title={pageAnalytics?.summary?.most_popular_page}>
              {pageAnalytics?.summary?.most_popular_page || 'Opportunities Hub'}
            </div>
            <div className="text-[11px] font-[Geist] text-indigo-600 mt-xs">
              {pageAnalytics?.summary?.today_views || 0} visits today
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ NAVIGATION TABS ═══════════════ */}
      <div className="flex gap-xs border-b border-outline-variant/60 pb-xs overflow-x-auto custom-scrollbar">
        {[
          { id: 'overview', icon: 'dashboard', label: 'Executive Pulse' },
          { id: 'inventory', icon: 'inventory_2', label: 'Job Inventory & Audits' },
          { id: 'users', icon: 'group', label: `Users (${summary?.users?.total || 0})` },
          { id: 'collector', icon: 'precision_manufacturing', label: 'Collector Ingestion' },
          { id: 'pages', icon: 'analytics', label: 'Feature Popularity' },
          { id: 'feedback', icon: 'reviews', label: `Feedback (${summary?.feedback?.total || 0})` },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-md py-sm rounded-lg text-xs font-semibold font-[Geist] transition-all flex items-center gap-xs whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-primary text-on-primary shadow-xs'
                : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* ═══════════════ TAB 1: EXECUTIVE OVERVIEW ═══════════════ */}
      {activeTab === 'overview' && (
        <div className="space-y-lg">
          {/* Quick Collector Trigger Bar */}
          <div className="glass-effect p-md sm:p-lg rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md border border-primary/20 bg-primary/5">
            <div className="flex items-center gap-md">
              <div className="w-12 h-12 rounded-xl bg-primary text-on-primary flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-2xl">sync</span>
              </div>
              <div>
                <h3 className="text-sm sm:text-base font-bold text-on-surface">India-First Live Job Collector Engine</h3>
                <p className="text-xs text-on-surface-variant font-[Geist]">
                  Pulls direct ATS openings from Lever, Greenhouse, Unstop, and Remotive with strict regional geofencing.
                </p>
              </div>
            </div>

            <button
              onClick={handleTriggerCollector}
              disabled={triggeringCollector}
              className="px-lg py-sm bg-primary hover:brightness-110 text-on-primary rounded-xl text-xs font-bold font-[Geist] transition-all disabled:opacity-50 flex items-center gap-2 shrink-0 shadow-md shadow-primary/20"
            >
              <span className={`material-symbols-outlined text-base ${triggeringCollector ? 'animate-spin' : ''}`}>
                {triggeringCollector ? 'autorenew' : 'play_arrow'}
              </span>
              {triggeringCollector ? 'Collecting Live Jobs...' : 'Trigger Collector Now'}
            </button>
          </div>

          {collectorResult && (
            <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant space-y-xs font-[Geist] text-xs">
              <div className="font-bold text-on-surface">Collector Output:</div>
              <div className="text-on-surface-variant">
                Inserted: <span className="font-bold text-primary">{collectorResult?.results?.inserted || 0}</span> |
                Active in DB: <span className="font-bold text-success">{collectorResult?.results?.active_jobs || 0}</span>
              </div>
            </div>
          )}

          {/* 4-Velocity Window Cards */}
          {collectorStats && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-sm sm:gap-md">
              <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant">
                <div className="text-[11px] font-semibold uppercase text-on-surface-variant font-[Geist]">⏱️ Last 1 Hour</div>
                <div className="text-2xl font-bold text-primary mt-xs">{collectorStats.metrics?.jobs_1h || 0}</div>
                <div className="text-[11px] text-on-surface-variant font-[Geist] mt-0.5">Jobs fetched/checked</div>
              </div>

              <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant">
                <div className="text-[11px] font-semibold uppercase text-on-surface-variant font-[Geist]">📅 Last 24 Hours</div>
                <div className="text-2xl font-bold text-emerald-600 mt-xs">{collectorStats.metrics?.jobs_24h || 0}</div>
                <div className="text-[11px] text-on-surface-variant font-[Geist] mt-0.5">Today's collection volume</div>
              </div>

              <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant">
                <div className="text-[11px] font-semibold uppercase text-on-surface-variant font-[Geist]">📆 Last 7 Days</div>
                <div className="text-2xl font-bold text-amber-600 mt-xs">{collectorStats.metrics?.jobs_7d || 0}</div>
                <div className="text-[11px] text-on-surface-variant font-[Geist] mt-0.5">Weekly pipeline total</div>
              </div>

              <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant">
                <div className="text-[11px] font-semibold uppercase text-on-surface-variant font-[Geist]">🗓️ Last 30 Days</div>
                <div className="text-2xl font-bold text-indigo-600 mt-xs">{collectorStats.metrics?.jobs_30d || 0}</div>
                <div className="text-[11px] text-on-surface-variant font-[Geist] mt-0.5">
                  Monthly velocity ({collectorStats.metrics?.mom_growth_pct > 0 ? '+' : ''}{collectorStats.metrics?.mom_growth_pct}%)
                </div>
              </div>
            </div>
          )}

          {/* Two-Column Breakdown: Ingestion by Source & Top Pages */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-md">
            {/* Jobs by ATS / Source */}
            <div className="p-md sm:p-lg rounded-2xl bg-surface-container-low border border-outline-variant space-y-md">
              <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-lg">source</span>
                Ingestion by ATS &amp; Source
              </h3>
              <div className="space-y-sm">
                {(collectorStats?.by_source || []).slice(0, 6).map((item, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-[Geist]">
                      <span className="font-semibold text-on-surface">{item.source}</span>
                      <span className="text-on-surface-variant">{item.count.toLocaleString()} ({item.percentage}%)</span>
                    </div>
                    <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(item.percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Visited Pages */}
            <div className="p-md sm:p-lg rounded-2xl bg-surface-container-low border border-outline-variant space-y-md">
              <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-indigo-600 text-lg">insights</span>
                Most Popular Features
              </h3>
              <div className="space-y-sm">
                {(pageAnalytics?.ranked_pages || []).slice(0, 6).map((p, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-[Geist]">
                      <span className="font-semibold text-on-surface truncate max-w-[200px]" title={p.page_name}>
                        {p.page_name}
                      </span>
                      <span className="text-on-surface-variant">{p.views.toLocaleString()} views ({p.percentage}%)</span>
                    </div>
                    <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(p.percentage * 2, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ TAB: JOB INVENTORY & AUDITS (ADDED/DELETED JOBS) ═══════════════ */}
      {activeTab === 'inventory' && (
        <div className="space-y-md">
          {/* 4-KPI Metric Cards for Inventory */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-sm sm:gap-md">
            {/* Active Jobs */}
            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Active Inventory</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                  <span className="material-symbols-outlined text-lg">check_circle</span>
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
                {inventoryData?.summary?.active_jobs?.toLocaleString() ?? summary?.collector?.active?.toLocaleString() ?? 0}
              </div>
              <div className="text-[11px] font-[Geist] text-emerald-600 mt-xs font-medium">
                Live opportunities in database
              </div>
            </div>

            {/* Deleted / Inactive Jobs */}
            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Deleted / Inactive</span>
                <div className="w-8 h-8 rounded-lg bg-error/10 text-error flex items-center justify-center">
                  <span className="material-symbols-outlined text-lg">delete_sweep</span>
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
                {inventoryData?.summary?.inactive_deleted_jobs?.toLocaleString() ?? 0}
              </div>
              <div className="text-[11px] font-[Geist] text-error mt-xs font-medium">
                Deactivated / expired opportunities
              </div>
            </div>

            {/* Added in Last 24 Hours */}
            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Added Today (24h)</span>
                <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-600 flex items-center justify-center">
                  <span className="material-symbols-outlined text-lg">bolt</span>
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
                {inventoryData?.summary?.added_24h?.toLocaleString() ?? summary?.collector?.jobs_24h?.toLocaleString() ?? 0}
              </div>
              <div className="text-[11px] font-[Geist] text-amber-600 mt-xs font-medium">
                Newly ingested in last 24h
              </div>
            </div>

            {/* Added in Last 7 Days */}
            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant/70 relative overflow-hidden">
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Added This Week (7d)</span>
                <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-lg">calendar_view_week</span>
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-on-surface mt-sm">
                {inventoryData?.summary?.added_7d?.toLocaleString() ?? summary?.collector?.jobs_7d?.toLocaleString() ?? 0}
              </div>
              <div className="text-[11px] font-[Geist] text-primary mt-xs font-medium">
                New jobs added over 7 days
              </div>
            </div>
          </div>

          {/* Mode Switcher Pills: Newly Added vs Deleted/Inactive vs Expired vs All */}
          <div className="flex items-center gap-xs p-1 bg-surface-container rounded-2xl border border-outline-variant overflow-x-auto custom-scrollbar">
            {[
              { id: 'active', label: '🟢 Active & Newly Ingested Jobs', icon: 'auto_awesome' },
              { id: 'inactive_deleted', label: '🔴 Inactive / Deleted Jobs', icon: 'remove_circle_outline' },
              { id: 'expired', label: '🟠 Expired / Closed Postings', icon: 'timer_off' },
              { id: 'all', label: '⚪ All Database Inventory', icon: 'dataset' },
            ].map(pill => (
              <button
                key={pill.id}
                onClick={() => {
                  setInventoryStatusFilter(pill.id)
                  setInventoryOffset(0)
                }}
                className={`px-md py-sm rounded-xl text-xs font-bold font-[Geist] transition-all flex items-center gap-1.5 whitespace-nowrap ${
                  inventoryStatusFilter === pill.id
                    ? 'bg-surface text-on-surface shadow-xs border border-outline-variant'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[16px]">{pill.icon}</span>
                {pill.label}
              </button>
            ))}
          </div>

          {/* Filter Bar: Search, Source, Time Range, Pagination */}
          <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-sm">
            <div className="flex flex-wrap items-center gap-sm flex-1">
              {/* Search Bar */}
              <div className="relative flex-1 min-w-[200px]">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
                  search
                </span>
                <input
                  type="text"
                  value={inventorySearch}
                  onChange={e => {
                    setInventorySearch(e.target.value)
                    setInventoryOffset(0)
                  }}
                  placeholder="Search by Job Title, Company, or Location..."
                  className="w-full pl-9 pr-md py-sm bg-surface rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 font-[Geist]"
                />
              </div>

              {/* Time Range Filter */}
              <select
                value={inventoryTimeRange}
                onChange={e => {
                  setInventoryTimeRange(e.target.value)
                  setInventoryOffset(0)
                }}
                className="px-md py-sm bg-surface rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none font-[Geist]"
              >
                <option value="all">All Ingestion Time</option>
                <option value="24h">Added Last 24 Hours</option>
                <option value="7d">Added Last 7 Days</option>
                <option value="30d">Added Last 30 Days</option>
              </select>

              {/* Primary Source Filter */}
              <select
                value={inventorySourceFilter}
                onChange={e => {
                  setInventorySourceFilter(e.target.value)
                  setInventoryOffset(0)
                }}
                className="px-md py-sm bg-surface rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none font-[Geist]"
              >
                <option value="">All ATS Sources</option>
                <option value="Greenhouse">Greenhouse</option>
                <option value="Lever">Lever</option>
                <option value="Unstop">Unstop</option>
                <option value="Remotive">Remotive</option>
                <option value="Workday">Workday</option>
                <option value="Direct ATS">Direct ATS</option>
              </select>
            </div>

            {/* Quick Actions & Counter */}
            <div className="flex items-center gap-sm shrink-0">
              <span className="text-xs font-[Geist] text-on-surface-variant">
                Matching: <strong className="text-on-surface">{inventoryData?.filtered_total?.toLocaleString() ?? 0}</strong>
              </span>
              <button
                onClick={() => loadInventory(inventoryOffset)}
                disabled={inventoryLoading}
                className="px-md py-sm bg-surface hover:bg-surface-container border border-outline-variant text-on-surface rounded-xl text-xs font-semibold font-[Geist] flex items-center gap-1.5 transition-all"
              >
                <span className={`material-symbols-outlined text-[16px] ${inventoryLoading ? 'animate-spin' : ''}`}>refresh</span>
                Refresh
              </button>
            </div>
          </div>

          {/* Opportunities Audit Data Table */}
          <div className="glass-effect rounded-2xl overflow-hidden border border-outline-variant">
            {inventoryLoading ? (
              <div className="text-center py-xl text-xs font-[Geist] text-on-surface-variant flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                Loading opportunity inventory & audit stream...
              </div>
            ) : !inventoryData?.opportunities?.length ? (
              <div className="text-center py-xl text-xs font-[Geist] text-on-surface-variant space-y-2">
                <span className="material-symbols-outlined text-3xl text-on-surface-variant/50">search_off</span>
                <p>No opportunities found matching your active filters.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-[Geist]">
                  <thead className="bg-surface-container-low text-on-surface-variant text-[11px] font-bold uppercase tracking-wider border-b border-outline-variant">
                    <tr>
                      <th className="py-md px-md">ID</th>
                      <th className="py-md px-md">Job Title & Employer</th>
                      <th className="py-md px-md">Location & Type</th>
                      <th className="py-md px-md">Status</th>
                      <th className="py-md px-md">Source & Trust</th>
                      <th className="py-md px-md">Ingestion / Seen Date</th>
                      <th className="py-md px-md">Apply Link</th>
                      <th className="py-md px-md text-right">Lifecycle Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/60">
                    {inventoryData.opportunities.map(opp => (
                      <tr key={opp.id} className="hover:bg-surface-container/40 transition-colors">
                        {/* ID */}
                        <td className="py-sm px-md font-mono text-on-surface-variant font-medium">
                          #{opp.id}
                        </td>

                        {/* Title & Company */}
                        <td className="py-sm px-md max-w-xs">
                          <div className="font-bold text-on-surface truncate" title={opp.title}>
                            {opp.title}
                          </div>
                          <div className="text-[11px] text-on-surface-variant flex items-center gap-1.5 mt-0.5">
                            <span className="font-semibold text-primary">{opp.company || 'Unknown Employer'}</span>
                            {opp.is_india_job && (
                              <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-500/10 text-amber-600 border border-amber-500/20">
                                🇮🇳 India
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Location & Job Type */}
                        <td className="py-sm px-md text-on-surface-variant">
                          <div className="flex items-center gap-1">
                            <span className="material-symbols-outlined text-[14px]">location_on</span>
                            <span className="truncate max-w-[150px]" title={opp.location}>{opp.location || 'Remote'}</span>
                          </div>
                          <div className="text-[11px] text-on-surface-variant/70 mt-0.5">
                            {opp.job_type} • {opp.opportunity_category}
                          </div>
                        </td>

                        {/* Status Badge */}
                        <td className="py-sm px-md">
                          {opp.is_active && opp.status === 'ACTIVE' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/15 text-emerald-700 border border-emerald-500/30">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                              Active
                            </span>
                          ) : opp.status === 'EXPIRED' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/15 text-amber-700 border border-amber-500/30">
                              Expired
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-error/15 text-error border border-error/30">
                              Inactive / Deleted
                            </span>
                          )}
                          {opp.expired_reason && (
                            <div className="text-[10px] text-error/80 mt-0.5 truncate max-w-[120px]" title={opp.expired_reason}>
                              {opp.expired_reason}
                            </div>
                          )}
                        </td>

                        {/* Source & Trust Score */}
                        <td className="py-sm px-md">
                          <div className="font-semibold text-on-surface">{opp.primary_source}</div>
                          <div className="mt-0.5 flex items-center gap-1">
                            <span className={`text-[11px] font-bold ${
                              opp.trust_score >= 80 ? 'text-emerald-600' : opp.trust_score >= 50 ? 'text-amber-600' : 'text-on-surface-variant'
                            }`}>
                              {opp.trust_score}% Trust
                            </span>
                          </div>
                        </td>

                        {/* Ingestion & Checked Dates */}
                        <td className="py-sm px-md text-on-surface-variant text-[11px]">
                          <div>
                            <span className="text-on-surface-variant/60">First Seen: </span>
                            <span className="font-medium text-on-surface">
                              {opp.first_seen ? new Date(opp.first_seen).toLocaleDateString() : 'N/A'}
                            </span>
                          </div>
                          <div className="text-[10px] text-on-surface-variant/60 mt-0.5">
                            Checked: {opp.last_checked ? new Date(opp.last_checked).toLocaleDateString() : 'N/A'}
                          </div>
                        </td>

                        {/* Apply Link Test */}
                        <td className="py-sm px-md">
                          {opp.apply_url ? (
                            <a
                              href={opp.apply_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 px-2 py-1 bg-surface-container hover:bg-primary/10 hover:text-primary rounded-lg text-[11px] font-semibold font-[Geist] transition-colors border border-outline-variant"
                              title="Test direct apply URL"
                            >
                              <span>Inspect</span>
                              <span className="material-symbols-outlined text-[13px]">open_in_new</span>
                            </a>
                          ) : (
                            <span className="text-on-surface-variant/50 text-[11px]">No URL</span>
                          )}
                        </td>

                        {/* Lifecycle Actions */}
                        <td className="py-sm px-md text-right">
                          <button
                            onClick={() => handleToggleOppStatus(opp.id, opp.is_active)}
                            disabled={updatingOppId === opp.id}
                            className={`px-2.5 py-1 rounded-lg text-[11px] font-bold font-[Geist] transition-all disabled:opacity-50 inline-flex items-center gap-1 ${
                              opp.is_active
                                ? 'bg-error/10 text-error hover:bg-error/20 border border-error/30'
                                : 'bg-emerald-500/10 text-emerald-700 hover:bg-emerald-500/20 border border-emerald-500/30'
                            }`}
                          >
                            {updatingOppId === opp.id ? (
                              <span className="material-symbols-outlined text-[12px] animate-spin">progress_activity</span>
                            ) : (
                              <span className="material-symbols-outlined text-[13px]">
                                {opp.is_active ? 'delete' : 'replay'}
                              </span>
                            )}
                            <span>{opp.is_active ? 'Deactivate' : 'Reactivate'}</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination Controls */}
            {inventoryData && inventoryData.filtered_total > 50 && (
              <div className="p-md bg-surface-container-low border-t border-outline-variant flex items-center justify-between font-[Geist] text-xs">
                <span className="text-on-surface-variant">
                  Showing {inventoryOffset + 1} to {Math.min(inventoryOffset + 50, inventoryData.filtered_total)} of {inventoryData.filtered_total.toLocaleString()} opportunities
                </span>
                <div className="flex items-center gap-xs">
                  <button
                    onClick={() => loadInventory(Math.max(0, inventoryOffset - 50))}
                    disabled={inventoryOffset === 0 || inventoryLoading}
                    className="px-md py-xs bg-surface border border-outline-variant text-on-surface rounded-lg disabled:opacity-40 font-semibold"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => loadInventory(inventoryOffset + 50)}
                    disabled={inventoryOffset + 50 >= inventoryData.filtered_total || inventoryLoading}
                    className="px-md py-xs bg-surface border border-outline-variant text-on-surface rounded-lg disabled:opacity-40 font-semibold"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ═══════════════ TAB 2: USER MANAGEMENT ═══════════════ */}
      {activeTab === 'users' && (
        <div className="space-y-md">
          {/* Controls Bar: Search, Filters & Export */}
          <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-sm">
            <div className="flex items-center gap-sm flex-1">
              <div className="relative flex-1 max-w-md">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
                  search
                </span>
                <input
                  type="text"
                  value={userSearch}
                  onChange={e => setUserSearch(e.target.value)}
                  placeholder="Search by Name or Gmail / Email..."
                  className="w-full pl-9 pr-md py-sm bg-surface rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 font-[Geist]"
                />
              </div>

              <select
                value={userRoleFilter}
                onChange={e => setUserRoleFilter(e.target.value)}
                className="px-md py-sm bg-surface rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none font-[Geist]"
              >
                <option value="">All Roles</option>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <button
              onClick={exportUsersToCSV}
              className="px-md py-sm bg-surface hover:bg-surface-container border border-outline-variant text-on-surface rounded-xl text-xs font-semibold font-[Geist] flex items-center gap-1.5 transition-all shrink-0"
            >
              <span className="material-symbols-outlined text-[16px]">download</span>
              Export CSV
            </button>
          </div>

          {/* User Table */}
          <div className="glass-effect rounded-2xl overflow-hidden border border-outline-variant">
            {loadingUsers ? (
              <div className="text-center py-xl text-xs font-[Geist] text-on-surface-variant flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                Loading registered users...
              </div>
            ) : usersList.length === 0 ? (
              <div className="text-center py-xl text-xs font-[Geist] text-on-surface-variant">
                No users found matching your criteria.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-[Geist]">
                  <thead className="bg-surface-container/60 border-b border-outline-variant/60 text-on-surface-variant uppercase tracking-wider font-semibold text-[10px]">
                    <tr>
                      <th className="py-sm px-md">User</th>
                      <th className="py-sm px-md">Email / Gmail</th>
                      <th className="py-sm px-md">Role</th>
                      <th className="py-sm px-md">Status</th>
                      <th className="py-sm px-md">Registered</th>
                      <th className="py-sm px-md text-center">Activity</th>
                      <th className="py-sm px-md text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/30">
                    {usersList.map(u => {
                      const isRootAdmin = u.email === 'careerlensadmin@careerlens.ai' || u.email === 'careerlensadmin'
                      return (
                        <tr key={u.id} className="hover:bg-surface-container/30 transition-colors">
                          {/* Name & Avatar */}
                          <td className="py-sm px-md font-medium text-on-surface">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs">
                                {(u.full_name || u.email).charAt(0).toUpperCase()}
                              </div>
                              <span className="font-semibold">{u.full_name}</span>
                            </div>
                          </td>

                          {/* Email */}
                          <td className="py-sm px-md text-on-surface font-mono text-[11px]">
                            {u.email}
                          </td>

                          {/* Role Badge */}
                          <td className="py-sm px-md">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide border ${
                              u.role === 'admin'
                                ? 'bg-primary/10 text-primary border-primary/30'
                                : 'bg-surface-container text-on-surface-variant border-outline-variant'
                            }`}>
                              {u.role}
                            </span>
                          </td>

                          {/* Verification Status */}
                          <td className="py-sm px-md">
                            <span className={`inline-flex items-center gap-1 text-[11px] font-semibold ${
                              u.is_verified ? 'text-success' : 'text-warning'
                            }`}>
                              <span className="material-symbols-outlined text-[14px]">
                                {u.is_verified ? 'verified' : 'pending'}
                              </span>
                              {u.is_verified ? 'Verified' : 'Unverified'}
                            </span>
                          </td>

                          {/* Joined Date */}
                          <td className="py-sm px-md text-on-surface-variant text-[11px]">
                            {u.created_at ? new Date(u.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—'}
                          </td>

                          {/* Activity Counters */}
                          <td className="py-sm px-md text-center text-on-surface-variant text-[11px]">
                            <span title="Applications" className="mr-2">📝 {u.applications_count || 0}</span>
                            <span title="Resumes">📄 {u.resumes_count || 0}</span>
                          </td>

                          {/* Actions */}
                          <td className="py-sm px-md text-right">
                            {!isRootAdmin && (
                              <div className="flex items-center justify-end gap-1">
                                <button
                                  onClick={() => handleRoleToggle(u)}
                                  className="p-1 hover:bg-surface-container rounded-lg text-on-surface-variant hover:text-primary transition-colors"
                                  title={u.role === 'admin' ? 'Demote to User' : 'Promote to Admin'}
                                >
                                  <span className="material-symbols-outlined text-base">
                                    {u.role === 'admin' ? 'person_remove' : 'verified_user'}
                                  </span>
                                </button>
                                <button
                                  onClick={() => setUserToDelete(u)}
                                  className="p-1 hover:bg-error/10 rounded-lg text-on-surface-variant hover:text-error transition-colors"
                                  title="Delete User"
                                >
                                  <span className="material-symbols-outlined text-base">delete</span>
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ═══════════════ TAB 3: COLLECTOR INGESTION ANALYTICS ═══════════════ */}
      {activeTab === 'collector' && collectorStats && (
        <div className="space-y-lg">
          {/* Time Window KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-sm sm:gap-md">
            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant space-y-xs">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">1 Hour Ingestion</div>
              <div className="text-3xl font-black text-primary">{collectorStats.metrics?.jobs_1h || 0}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">Real-time pipeline speed</div>
            </div>

            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant space-y-xs">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">1 Day (24h) Ingestion</div>
              <div className="text-3xl font-black text-emerald-600">{collectorStats.metrics?.jobs_24h || 0}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">New postings added today</div>
            </div>

            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant space-y-xs">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">1 Week (7d) Ingestion</div>
              <div className="text-3xl font-black text-amber-600">{collectorStats.metrics?.jobs_7d || 0}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">7-day throughput</div>
            </div>

            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant space-y-xs">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">1 Month (30d) Ingestion</div>
              <div className="text-3xl font-black text-indigo-600">{collectorStats.metrics?.jobs_30d || 0}</div>
              <div className="text-[11px] text-on-surface-variant font-[Geist]">
                Growth: <span className="font-bold text-success">{collectorStats.metrics?.mom_growth_pct}% MoM</span>
              </div>
            </div>
          </div>

          {/* Sources & ATS Breakdown */}
          <div className="glass-effect p-md sm:p-lg rounded-2xl border border-outline-variant space-y-md">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-bold text-on-surface">Verified ATS Feeds &amp; Aggregation Sources</h3>
              <span className="text-xs text-on-surface-variant font-[Geist]">Total Active: {collectorStats.metrics?.total_active?.toLocaleString()}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-sm">
              {(collectorStats.by_source || []).map((s, i) => (
                <div key={i} className="p-md rounded-xl bg-surface-container border border-outline-variant/60 space-y-xs">
                  <div className="flex justify-between items-center text-xs font-[Geist]">
                    <span className="font-bold text-on-surface">{s.source}</span>
                    <span className="text-primary font-extrabold">{s.percentage}%</span>
                  </div>
                  <div className="text-lg font-black text-on-surface">{s.count.toLocaleString()} jobs</div>
                </div>
              ))}
            </div>
          </div>

          {/* 30-Day Histogram Bar Visualizer */}
          <div className="glass-effect p-md sm:p-lg rounded-2xl border border-outline-variant space-y-md">
            <h3 className="text-base font-bold text-on-surface">30-Day Daily Ingestion Velocity</h3>
            <div className="flex items-end gap-1 h-36 pt-4 px-2 overflow-x-auto custom-scrollbar">
              {(collectorStats.daily_trend_30d || []).map((d, i) => {
                const maxVal = Math.max(...collectorStats.daily_trend_30d.map(x => x.jobs_collected), 1)
                const heightPct = Math.max((d.jobs_collected / maxVal) * 100, 8)
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1 group min-w-[18px]">
                    <div className="text-[9px] font-[Geist] text-on-surface-variant opacity-0 group-hover:opacity-100 transition-opacity">
                      {d.jobs_collected}
                    </div>
                    <div
                      className="w-full bg-primary/70 hover:bg-primary rounded-t transition-all duration-300"
                      style={{ height: `${heightPct}%` }}
                      title={`${d.date}: ${d.jobs_collected} jobs`}
                    />
                    <div className="text-[8px] font-[Geist] text-on-surface-variant truncate w-full text-center">
                      {i % 4 === 0 ? d.date.split(' ')[1] : ''}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ TAB 4: PAGE & FEATURE USAGE ═══════════════ */}
      {activeTab === 'pages' && pageAnalytics && (
        <div className="space-y-lg">
          {/* Top Feature Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-sm sm:gap-md">
            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">Total Views Logged</div>
              <div className="text-3xl font-black text-primary mt-xs">{pageAnalytics.summary?.total_views?.toLocaleString()}</div>
            </div>

            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">Views Today</div>
              <div className="text-3xl font-black text-emerald-600 mt-xs">{pageAnalytics.summary?.today_views?.toLocaleString()}</div>
            </div>

            <div className="p-md rounded-2xl bg-surface-container-low border border-outline-variant">
              <div className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">Top Destination</div>
              <div className="text-lg font-black text-indigo-600 mt-xs truncate" title={pageAnalytics.summary?.most_popular_page}>
                {pageAnalytics.summary?.most_popular_page}
              </div>
            </div>
          </div>

          {/* Full Page Ranking Table */}
          <div className="glass-effect rounded-2xl p-md sm:p-lg border border-outline-variant space-y-md">
            <h3 className="text-base font-bold text-on-surface">Page &amp; Feature Popularity Leaderboard</h3>
            <div className="space-y-sm">
              {(pageAnalytics.ranked_pages || []).map((p, idx) => (
                <div key={idx} className="p-md rounded-xl bg-surface-container-low border border-outline-variant/60 space-y-1.5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs font-[Geist]">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-[10px]">
                        #{idx + 1}
                      </span>
                      <span className="font-bold text-on-surface">{p.page_name}</span>
                      <code className="text-[10px] text-on-surface-variant bg-surface-container px-1 py-0.5 rounded">{p.path}</code>
                    </div>
                    <div className="text-on-surface-variant">
                      <span className="font-bold text-on-surface">{p.views.toLocaleString()}</span> views ({p.percentage}%) • <span className="font-semibold">{p.unique_users || 0}</span> unique users
                    </div>
                  </div>
                  <div className="w-full h-2.5 bg-surface-container rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary to-indigo-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(p.percentage * 2.5, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ TAB 5: FEEDBACK & RATINGS ═══════════════ */}
      {activeTab === 'feedback' && (
        <div className="space-y-md">
          {/* Status Filter */}
          <div className="flex gap-xs border-b border-outline-variant/40 pb-xs">
            {['', 'Open', 'In Review', 'Resolved', 'Closed'].map(st => (
              <button
                key={st}
                onClick={() => setFeedbackFilter(st)}
                className={`px-md py-xs rounded-lg text-xs font-semibold font-[Geist] transition-all ${
                  feedbackFilter === st
                    ? 'bg-primary text-on-primary'
                    : 'text-on-surface-variant hover:bg-surface-container'
                }`}
              >
                {st || 'All Feedback'}
              </button>
            ))}
          </div>

          {loadingFeedback ? (
            <div className="text-center py-xl text-xs font-[Geist] text-on-surface-variant">
              Loading user feedback...
            </div>
          ) : feedbackList.length === 0 ? (
            <div className="text-center py-xl bg-surface-container-low rounded-2xl border border-dashed border-outline-variant text-xs text-on-surface-variant font-[Geist]">
              No feedback entries found.
            </div>
          ) : (
            <div className="space-y-sm">
              {feedbackList.map(fb => {
                const priorityClass = PRIORITIES[fb.priority] || PRIORITIES['Medium']
                return (
                  <div key={fb.id} className="glass-effect p-md sm:p-lg rounded-2xl border border-outline-variant space-y-sm">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {fb.rating && (
                          <span className="text-2xl" title={RATING_EMOJIS[fb.rating]?.label}>
                            {RATING_EMOJIS[fb.rating]?.emoji || '⭐'}
                          </span>
                        )}
                        <h4 className="font-bold text-on-surface text-sm">{fb.subject}</h4>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold font-[Geist] border ${priorityClass}`}>
                          {fb.priority}
                        </span>
                      </div>

                      {/* Status Selector */}
                      <select
                        value={fb.status}
                        onChange={e => handleFeedbackStatusChange(fb.id, e.target.value)}
                        className={`px-sm py-1 rounded-lg text-xs font-bold font-[Geist] border focus:outline-none ${STATUS_STYLE[fb.status] || STATUS_STYLE['Open']}`}
                      >
                        <option value="Open">Open</option>
                        <option value="In Review">In Review</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Closed">Closed</option>
                      </select>
                    </div>

                    <p className="text-xs text-on-surface-variant font-[Geist] leading-relaxed">
                      {fb.description}
                    </p>

                    <div className="pt-xs border-t border-outline-variant/30 flex flex-wrap items-center justify-between gap-2 text-[11px] text-on-surface-variant font-[Geist]">
                      <div className="flex items-center gap-2">
                        <span>#{fb.id}</span>
                        <span>•</span>
                        <span>{fb.category}</span>
                        {fb.user?.email && (
                          <>
                            <span>•</span>
                            <span className="font-mono text-primary">{fb.user.email}</span>
                          </>
                        )}
                      </div>
                      <span>{fb.created_at ? new Date(fb.created_at).toLocaleString() : ''}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* ═══════════════ DELETE USER CONFIRMATION MODAL ═══════════════ */}
      {userToDelete && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-md">
          <div className="bg-surface rounded-2xl p-lg max-w-md w-full border border-outline-variant space-y-md animate-fade-in-up">
            <div className="w-12 h-12 rounded-xl bg-error/10 text-error flex items-center justify-center">
              <span className="material-symbols-outlined text-2xl">warning</span>
            </div>
            <h3 className="text-lg font-bold text-on-surface">Delete User Account</h3>
            <p className="text-xs text-on-surface-variant font-[Geist] leading-relaxed">
              Are you sure you want to permanently delete user <strong className="text-on-surface">{userToDelete.email}</strong>? All their applications and records will be deleted.
            </p>
            <div className="flex justify-end gap-sm pt-sm">
              <button
                onClick={() => setUserToDelete(null)}
                className="px-md py-sm bg-surface-container text-on-surface rounded-xl text-xs font-semibold font-[Geist]"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteUserConfirm}
                disabled={deletingUser}
                className="px-md py-sm bg-error text-on-error rounded-xl text-xs font-bold font-[Geist] disabled:opacity-50"
              >
                {deletingUser ? 'Deleting...' : 'Permanently Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ CHANGE ADMIN PASSWORD MODAL ═══════════════ */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-md">
          <div className="bg-surface rounded-2xl p-lg max-w-md w-full border border-outline-variant space-y-md animate-fade-in-up">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-xl">shield_lock</span>
                </div>
                <div>
                  <h3 className="text-base font-bold text-on-surface">Change Admin Password</h3>
                  <p className="text-xs text-on-surface-variant font-[Geist]">Update your root administrator credentials</p>
                </div>
              </div>
              <button
                onClick={() => setShowPasswordModal(false)}
                className="p-1 text-on-surface-variant hover:text-on-surface rounded-lg"
              >
                <span className="material-symbols-outlined text-base">close</span>
              </button>
            </div>

            {pwError && (
              <div className="p-sm px-md rounded-xl bg-error/15 border border-error/30 text-error text-xs font-semibold font-[Geist]">
                {pwError}
              </div>
            )}

            {pwSuccess && (
              <div className="p-sm px-md rounded-xl bg-success/15 border border-success/30 text-success text-xs font-semibold font-[Geist] flex items-center gap-2">
                <span className="material-symbols-outlined text-base">check_circle</span>
                {pwSuccess}
              </div>
            )}

            <form onSubmit={handleChangePasswordSubmit} className="space-y-sm">
              <div>
                <label className="text-[11px] font-bold text-on-surface font-[Geist]">Current Password</label>
                <input
                  type="password"
                  value={currentPw}
                  onChange={e => setCurrentPw(e.target.value)}
                  required
                  placeholder="Enter current admin password"
                  className="w-full mt-1 px-md py-sm bg-surface-container rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 font-[Geist]"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-on-surface font-[Geist]">New Password (min 8 chars)</label>
                <input
                  type="password"
                  value={newPw}
                  onChange={e => setNewPw(e.target.value)}
                  required
                  placeholder="Enter new strong password"
                  className="w-full mt-1 px-md py-sm bg-surface-container rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 font-[Geist]"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-on-surface font-[Geist]">Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPw}
                  onChange={e => setConfirmPw(e.target.value)}
                  required
                  placeholder="Re-enter new password"
                  className="w-full mt-1 px-md py-sm bg-surface-container rounded-xl border border-outline-variant text-xs text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 font-[Geist]"
                />
              </div>

              <div className="flex justify-end gap-sm pt-sm">
                <button
                  type="button"
                  onClick={() => setShowPasswordModal(false)}
                  className="px-md py-sm bg-surface-container text-on-surface rounded-xl text-xs font-semibold font-[Geist]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={changingPw}
                  className="px-md py-sm bg-primary text-on-primary rounded-xl text-xs font-bold font-[Geist] disabled:opacity-50 flex items-center gap-1.5"
                >
                  {changingPw && <span className="material-symbols-outlined text-xs animate-spin">progress_activity</span>}
                  {changingPw ? 'Saving...' : 'Update Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  )
}


