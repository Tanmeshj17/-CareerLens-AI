import { useState, useContext, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { AuthContext } from '../App'
import {
  getCareerProfile, createCareerProfile, updateCareerProfile,
  getSkillProfile, addSkill as apiAddSkill, updateSkill as apiUpdateSkill, deleteSkill as apiDeleteSkill,
  getProfileCompleteness, updateUserProfile, changeUserPassword, deleteUserAccount,
  getResumes
} from '../api'

const POPULAR_ROLES = [
  'Full Stack Developer',
  'Frontend Engineer',
  'Backend Developer',
  'Data Scientist',
  'AI / ML Engineer',
  'DevOps Engineer',
  'Cloud Engineer',
  'Cybersecurity Analyst',
  'Product Manager',
  'UI/UX Designer',
]

const EXPERIENCE_LEVELS = [
  { value: 'Fresher / Entry-Level', label: 'Fresher / Entry-Level (0-1 yrs)' },
  { value: 'Junior (1-3 years)', label: 'Junior (1-3 yrs)' },
  { value: 'Mid-Level (3-5 years)', label: 'Mid-Level (3-5 yrs)' },
  { value: 'Senior (5+ years)', label: 'Senior (5+ yrs)' },
]

const EDUCATION_OPTIONS = [
  'B.Tech / B.E. (Computer Science / IT)',
  'B.Tech / B.E. (Other Branches)',
  'BCA / MCA',
  'B.Sc / M.Sc (Computer Science / Data)',
  'Master’s Degree (M.Tech / MS / MBA)',
  'Diploma / Certificate Program',
  'Self-Taught / Other',
]

const POPULAR_LOCATIONS = [
  'Remote',
  'Bengaluru, India',
  'Hyderabad, India',
  'Pune, India',
  'Delhi NCR, India',
  'Mumbai, India',
  'San Francisco, USA',
  'London, UK',
]

const SUGGESTED_SKILLS = [
  'React', 'Python', 'JavaScript', 'TypeScript', 'Node.js',
  'SQL', 'FastAPI', 'Docker', 'AWS', 'TailwindCSS',
  'Git', 'MongoDB', 'GraphQL', 'Next.js', 'Java'
]

const SKILL_LEVELS = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']

const LEVEL_CONFIG = {
  BEGINNER: { label: 'Beginner', bg: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20' },
  INTERMEDIATE: { label: 'Intermediate', bg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20' },
  ADVANCED: { label: 'Advanced', bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' },
  EXPERT: { label: 'Expert', bg: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20' },
}

export default function Profile() {
  const { user, login, logout } = useContext(AuthContext)
  const navigate = useNavigate()

  const displayName = user?.full_name || 'User'
  const initials = displayName
    ? displayName.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
    : 'U'

  // --- Profile Completeness & Resumes ---
  const [completeness, setCompleteness] = useState({ percentage: 0, missing: [] })
  const [resumeCount, setResumeCount] = useState(0)
  const [latestAtsScore, setLatestAtsScore] = useState(null)

  // --- Account Info State ---
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [isEditingName, setIsEditingName] = useState(false)
  const [savingName, setSavingName] = useState(false)
  const [nameSuccess, setNameSuccess] = useState('')
  const [nameError, setNameError] = useState('')

  // --- Password Change State ---
  const [showPasswordSection, setShowPasswordSection] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [passwordError, setPasswordError] = useState('')

  // --- Career Preferences State ---
  const [hasCareerProfile, setHasCareerProfile] = useState(false)
  const [careerData, setCareerData] = useState({
    target_role: '',
    current_role: '',
    experience_level: 'Fresher / Entry-Level',
    education: 'B.Tech / B.E. (Computer Science / IT)',
    location: 'Remote',
  })
  const [careerLoading, setCareerLoading] = useState(false)
  const [careerSuccess, setCareerSuccess] = useState('')
  const [careerError, setCareerError] = useState('')

  // --- Skills State ---
  const [skills, setSkills] = useState([])
  const [newSkillName, setNewSkillName] = useState('')
  const [newSkillLevel, setNewSkillLevel] = useState('INTERMEDIATE')
  const [skillLoading, setSkillLoading] = useState(false)
  const [skillError, setSkillError] = useState('')

  // --- Delete Account State ---
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  // ── Load User & Career Data ──
  const refreshCompleteness = async () => {
    try {
      const comp = await getProfileCompleteness()
      if (comp) {
        setCompleteness({
          percentage: comp.completeness_percentage || 0,
          missing: comp.missing_items || []
        })
      }
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '')

      // 1. Fetch Career Profile
      getCareerProfile()
        .then(res => {
          setHasCareerProfile(true)
          setCareerData({
            target_role: res.target_role || '',
            current_role: res.current_role || '',
            experience_level: res.experience_level || 'Fresher / Entry-Level',
            education: res.education || 'B.Tech / B.E. (Computer Science / IT)',
            location: res.location || 'Remote',
          })
        })
        .catch(err => {
          if (err.message && err.message.includes('404')) {
            setHasCareerProfile(false)
          }
        })

      // 2. Fetch Skills
      getSkillProfile()
        .then(res => {
          setSkills(res || [])
        })
        .catch(() => {})

      // 3. Fetch Completeness
      refreshCompleteness()

      // 4. Fetch Resumes for Quick Status
      getResumes()
        .then(res => {
          if (Array.isArray(res)) {
            setResumeCount(res.length)
            if (res.length > 0 && res[0].ats_score != null) {
              setLatestAtsScore(res[0].ats_score)
            }
          }
        })
        .catch(() => {})
    }
  }, [user])

  // ── Handle Update Name ──
  const handleSaveName = async (e) => {
    e?.preventDefault()
    if (!fullName.trim()) {
      setNameError('Full name cannot be empty')
      return
    }
    setSavingName(true)
    setNameError('')
    setNameSuccess('')
    try {
      const updated = await updateUserProfile({ full_name: fullName.trim() })
      login({ ...user, full_name: updated.full_name })
      setNameSuccess('Name updated successfully!')
      setIsEditingName(false)
      refreshCompleteness()
      setTimeout(() => setNameSuccess(''), 3000)
    } catch (err) {
      setNameError(err.message || 'Failed to update name')
    } finally {
      setSavingName(false)
    }
  }

  // ── Handle Change Password ──
  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match')
      return
    }
    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters')
      return
    }
    setPasswordLoading(true)
    setPasswordError('')
    setPasswordSuccess('')
    try {
      await changeUserPassword(currentPassword, newPassword)
      setPasswordSuccess('Password changed successfully!')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setTimeout(() => {
        setPasswordSuccess('')
        setShowPasswordSection(false)
      }, 2500)
    } catch (err) {
      setPasswordError(err.message || 'Failed to change password')
    } finally {
      setPasswordLoading(false)
    }
  }

  // ── Handle Save Career Preferences ──
  const handleSaveCareer = async (e) => {
    e.preventDefault()
    setCareerLoading(true)
    setCareerError('')
    setCareerSuccess('')
    try {
      if (hasCareerProfile) {
        await updateCareerProfile(careerData)
      } else {
        await createCareerProfile(careerData)
        setHasCareerProfile(true)
      }
      setCareerSuccess('Career preferences saved successfully!')
      refreshCompleteness()
      setTimeout(() => setCareerSuccess(''), 3500)
    } catch (err) {
      setCareerError(err.message || 'Failed to save preferences')
    } finally {
      setCareerLoading(false)
    }
  }

  // ── Handle Add Skill ──
  const handleAddSkill = async (skillNameToAdd, levelToAdd = newSkillLevel) => {
    const name = (skillNameToAdd || newSkillName).trim()
    if (!name) return

    // Check if already exists
    const exists = skills.some(s => s.skill_name?.toLowerCase() === name.toLowerCase())
    if (exists) {
      setSkillError(`"${name}" is already in your skills list`)
      setTimeout(() => setSkillError(''), 3000)
      return
    }

    setSkillLoading(true)
    setSkillError('')
    try {
      const added = await apiAddSkill({
        skill_name: name,
        proficiency_level: levelToAdd.toUpperCase()
      })
      setSkills(prev => [...prev, added])
      setNewSkillName('')
      refreshCompleteness()
    } catch (err) {
      setSkillError(err.message || 'Failed to add skill')
    } finally {
      setSkillLoading(false)
    }
  }

  // ── Handle Cycle / Update Skill Level ──
  const handleCycleSkillLevel = async (skill) => {
    const currentIdx = SKILL_LEVELS.indexOf((skill.proficiency_level || 'BEGINNER').toUpperCase())
    const nextLevel = SKILL_LEVELS[(currentIdx + 1) % SKILL_LEVELS.length]
    try {
      await apiUpdateSkill(skill.id, { proficiency_level: nextLevel })
      setSkills(prev => prev.map(s => s.id === skill.id ? { ...s, proficiency_level: nextLevel } : s))
    } catch (err) {
      setSkillError('Failed to update skill level')
    }
  }

  // ── Handle Delete Skill ──
  const handleDeleteSkill = async (skillId) => {
    try {
      await apiDeleteSkill(skillId)
      setSkills(prev => prev.filter(s => s.id !== skillId))
      refreshCompleteness()
    } catch (err) {
      setSkillError('Failed to delete skill')
    }
  }

  // ── Handle Delete Account ──
  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') return
    setDeleteLoading(true)
    setDeleteError('')
    try {
      await deleteUserAccount()
      logout()
      navigate('/')
    } catch (err) {
      setDeleteError(err.message || 'Failed to delete account')
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in-up max-w-4xl mx-auto pb-24 font-['Plus_Jakarta_Sans',sans-serif]">

      {/* ═══════════════ PROFILE HEADER ═══════════════ */}
      <section className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800 relative overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-blue-500/10 via-indigo-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row items-center sm:items-start justify-between gap-6">
          {/* Avatar & User Info */}
          <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-br from-[#0050cb] via-[#2563eb] to-[#7c3aed] flex items-center justify-center text-3xl font-bold text-white shadow-md shadow-blue-500/20">
              {initials}
            </div>

            <div>
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 mb-1">
                <h1 className="text-2xl sm:text-3xl font-bold text-slate-800 dark:text-white">
                  {user?.full_name || 'User'}
                </h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-blue-50 dark:bg-blue-900/30 text-[#0050cb] dark:text-blue-400 border border-blue-200/60 dark:border-blue-800">
                  {user?.role === 'admin' ? 'Admin' : 'Member'}
                </span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>

              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 mt-3">
                {careerData.target_role && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium rounded-full">
                    <span className="material-symbols-outlined text-[15px] text-[#0050cb]">target</span>
                    {careerData.target_role}
                  </span>
                )}
                {careerData.location && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium rounded-full">
                    <span className="material-symbols-outlined text-[15px] text-slate-400">location_on</span>
                    {careerData.location}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Profile Completeness Ring */}
          <div className="flex flex-col items-center bg-slate-50 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 min-w-[150px]">
            <div className="relative w-16 h-16 mb-2">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
                <circle
                  cx="32" cy="32" r="26" fill="none"
                  stroke="currentColor" className="text-slate-200 dark:text-slate-700" strokeWidth="5"
                />
                <circle
                  cx="32" cy="32" r="26" fill="none"
                  stroke="currentColor" className="text-[#0050cb]" strokeWidth="5"
                  strokeDasharray={`${(completeness.percentage / 100) * 2 * Math.PI * 26} ${2 * Math.PI * 26}`}
                  strokeLinecap="round"
                />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-slate-800 dark:text-white">
                {completeness.percentage}%
              </span>
            </div>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Profile Complete</span>
            {completeness.missing.length > 0 && (
              <span className="text-[11px] text-slate-400 mt-0.5 text-center">
                {completeness.missing.length} action{completeness.missing.length > 1 ? 's' : ''} left
              </span>
            )}
          </div>
        </div>

        {/* Missing Action items prompt */}
        {completeness.missing.length > 0 && (
          <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800/80">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2.5">
              Complete your profile for 3x better AI job matching:
            </p>
            <div className="flex flex-wrap gap-2">
              {completeness.missing.map((item, i) => (
                <span key={i} className="inline-flex items-center gap-1 text-xs text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 px-3 py-1 rounded-full border border-amber-200/60 dark:border-amber-900/60">
                  <span className="material-symbols-outlined text-[14px]">add_circle</span>
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ═══════════════ 1. ACCOUNT INFORMATION ═══════════════ */}
      <section className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-[#0050cb] dark:text-blue-400">
              <span className="material-symbols-outlined text-2xl">account_circle</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Account Information</h2>
              <p className="text-xs text-slate-500">Manage your name, login email, and password</p>
            </div>
          </div>
        </div>

        {nameSuccess && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-50 text-emerald-700 text-xs font-medium flex items-center gap-2 border border-emerald-200">
            <span className="material-symbols-outlined text-sm">check_circle</span>
            {nameSuccess}
          </div>
        )}
        {nameError && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 text-red-700 text-xs font-medium flex items-center gap-2 border border-red-200">
            <span className="material-symbols-outlined text-sm">error</span>
            {nameError}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {/* Full Name */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Full Name
            </label>
            {isEditingName ? (
              <form onSubmit={handleSaveName} className="flex gap-2">
                <input
                  type="text"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
                  placeholder="Your Full Name"
                  required
                />
                <button
                  type="submit"
                  disabled={savingName}
                  className="px-4 py-2 bg-[#0050cb] hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50"
                >
                  {savingName ? 'Saving...' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => { setFullName(user?.full_name || ''); setIsEditingName(false) }}
                  className="px-3 py-2 border border-slate-200 text-slate-600 rounded-xl text-xs font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
              </form>
            ) : (
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
                <span className="text-sm font-medium text-slate-800 dark:text-white">{user?.full_name || 'Not specified'}</span>
                <button
                  onClick={() => setIsEditingName(true)}
                  className="text-xs font-bold text-[#0050cb] hover:underline flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[15px]">edit</span>
                  Edit
                </button>
              </div>
            )}
          </div>

          {/* Email Address */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Email Address
            </label>
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
              <span className="text-sm font-medium text-slate-800 dark:text-white">{user?.email}</span>
              <span className="text-xs text-slate-400 font-normal">Primary Login</span>
            </div>
          </div>
        </div>

        {/* Change Password Section */}
        <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800">
          {!showPasswordSection ? (
            <button
              onClick={() => setShowPasswordSection(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
            >
              <span className="material-symbols-outlined text-[18px] text-slate-500">lock_reset</span>
              Change Account Password
            </button>
          ) : (
            <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/80 animate-fade-in-up">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px] text-[#0050cb]">key</span>
                  Change Password
                </h3>
                <button
                  type="button"
                  onClick={() => setShowPasswordSection(false)}
                  className="text-xs text-slate-400 hover:text-slate-600"
                >
                  Close
                </button>
              </div>

              {passwordSuccess && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-50 text-emerald-700 text-xs font-medium flex items-center gap-2 border border-emerald-200">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  {passwordSuccess}
                </div>
              )}
              {passwordError && (
                <div className="mb-4 p-3 rounded-xl bg-red-50 text-red-700 text-xs font-medium flex items-center gap-2 border border-red-200">
                  <span className="material-symbols-outlined text-sm">error</span>
                  {passwordError}
                </div>
              )}

              <form onSubmit={handleChangePassword} className="space-y-3 max-w-md">
                <div>
                  <label className="text-xs font-medium text-slate-500 mb-1 block">Current Password</label>
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={currentPassword}
                    onChange={e => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb]"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500 mb-1 block">New Password (min 8 characters)</label>
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb]"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500 mb-1 block">Confirm New Password</label>
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb]"
                  />
                </div>

                <div className="flex items-center justify-between pt-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showPw}
                      onChange={e => setShowPw(e.target.checked)}
                      className="w-3.5 h-3.5 rounded text-[#0050cb]"
                    />
                    <span className="text-xs text-slate-500">Show passwords</span>
                  </label>

                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setShowPasswordSection(false)}
                      className="px-3 py-2 border border-slate-200 text-slate-600 rounded-xl text-xs font-medium hover:bg-slate-100"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={passwordLoading}
                      className="px-4 py-2 bg-[#0050cb] hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50"
                    >
                      {passwordLoading ? 'Updating...' : 'Update Password'}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          )}
        </div>
      </section>

      {/* ═══════════════ 2. CAREER PREFERENCES ═══════════════ */}
      <section className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400">
              <span className="material-symbols-outlined text-2xl">work</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Career Goals & Preferences</h2>
              <p className="text-xs text-slate-500">Powers your personalized AI job recommendations & skill roadmaps</p>
            </div>
          </div>
        </div>

        {careerSuccess && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-50 text-emerald-700 text-xs font-medium flex items-center gap-2 border border-emerald-200">
            <span className="material-symbols-outlined text-sm">check_circle</span>
            {careerSuccess}
          </div>
        )}
        {careerError && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 text-red-700 text-xs font-medium flex items-center gap-2 border border-red-200">
            <span className="material-symbols-outlined text-sm">error</span>
            {careerError}
          </div>
        )}

        <form onSubmit={handleSaveCareer} className="space-y-5">
          {/* Target Role */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider block">
              Target Dream Role <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={careerData.target_role}
              onChange={e => setCareerData(prev => ({ ...prev, target_role: e.target.value }))}
              placeholder="e.g. Full Stack Developer, Data Scientist"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
            />
            {/* Quick Role Suggestions */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-[11px] text-slate-400 self-center mr-1">Popular:</span>
              {POPULAR_ROLES.slice(0, 6).map(role => (
                <button
                  type="button"
                  key={role}
                  onClick={() => setCareerData(prev => ({ ...prev, target_role: role }))}
                  className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                    careerData.target_role === role
                      ? 'bg-[#0050cb] text-white border-[#0050cb]'
                      : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* Current Role */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider block">
                Current Role / Status
              </label>
              <input
                type="text"
                value={careerData.current_role}
                onChange={e => setCareerData(prev => ({ ...prev, current_role: e.target.value }))}
                placeholder="e.g. Student / Intern / Junior SDE"
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
              />
            </div>

            {/* Experience Level */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider block">
                Experience Level
              </label>
              <select
                value={careerData.experience_level}
                onChange={e => setCareerData(prev => ({ ...prev, experience_level: e.target.value }))}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
              >
                {EXPERIENCE_LEVELS.map(exp => (
                  <option key={exp.value} value={exp.value}>{exp.label}</option>
                ))}
              </select>
            </div>

            {/* Education */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider block">
                Highest Education
              </label>
              <select
                value={careerData.education}
                onChange={e => setCareerData(prev => ({ ...prev, education: e.target.value }))}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
              >
                {EDUCATION_OPTIONS.map(edu => (
                  <option key={edu} value={edu}>{edu}</option>
                ))}
              </select>
            </div>

            {/* Preferred Location */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider block">
                Preferred Job Location
              </label>
              <input
                type="text"
                value={careerData.location}
                onChange={e => setCareerData(prev => ({ ...prev, location: e.target.value }))}
                placeholder="e.g. Remote, Bengaluru, San Francisco"
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
              />
            </div>
          </div>

          {/* Quick Location Pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            <span className="text-[11px] text-slate-400 self-center mr-1">Locations:</span>
            {POPULAR_LOCATIONS.map(loc => (
              <button
                type="button"
                key={loc}
                onClick={() => setCareerData(prev => ({ ...prev, location: loc }))}
                className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                  careerData.location === loc
                    ? 'bg-[#0050cb] text-white border-[#0050cb]'
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                }`}
              >
                {loc}
              </button>
            ))}
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={careerLoading}
              className="px-6 py-3 bg-[#0050cb] hover:bg-blue-700 text-white rounded-xl text-sm font-bold shadow-md shadow-blue-500/20 transition-all disabled:opacity-50 flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">save</span>
              {careerLoading ? 'Saving...' : 'Save Career Preferences'}
            </button>
          </div>
        </form>
      </section>

      {/* ═══════════════ 3. SKILLS & EXPERTISE ═══════════════ */}
      <section className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400">
              <span className="material-symbols-outlined text-2xl">psychology</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-800 dark:text-white">Skills & Technologies</h2>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300">
                  {skills.length}
                </span>
              </div>
              <p className="text-xs text-slate-500">Click a badge to adjust proficiency level (Beginner → Expert)</p>
            </div>
          </div>
        </div>

        {skillError && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 text-red-700 text-xs font-medium flex items-center gap-2 border border-red-200">
            <span className="material-symbols-outlined text-sm">error</span>
            {skillError}
          </div>
        )}

        {/* Add Skill Form */}
        <div className="flex flex-col sm:flex-row gap-2.5 mb-6">
          <input
            type="text"
            placeholder="Add a new skill (e.g. Next.js, Kubernetes)"
            value={newSkillName}
            onChange={e => setNewSkillName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAddSkill()}
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-[#0050cb] focus:bg-white"
          />
          <select
            value={newSkillLevel}
            onChange={e => setNewSkillLevel(e.target.value)}
            className="px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none font-medium"
          >
            {SKILL_LEVELS.map(lvl => (
              <option key={lvl} value={lvl}>{LEVEL_CONFIG[lvl]?.label || lvl}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => handleAddSkill()}
            disabled={!newSkillName.trim() || skillLoading}
            className="px-5 py-2.5 bg-[#0050cb] hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-1.5"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            Add Skill
          </button>
        </div>

        {/* Suggested Skills to Add */}
        <div className="mb-6">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Quick Add Suggested Skills:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_SKILLS.filter(s => !skills.some(userSkill => userSkill.skill_name?.toLowerCase() === s.toLowerCase())).map(suggested => (
              <button
                key={suggested}
                type="button"
                onClick={() => handleAddSkill(suggested, 'INTERMEDIATE')}
                className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-blue-400 hover:text-[#0050cb] transition-all"
              >
                <span className="material-symbols-outlined text-[13px] text-slate-400">+</span>
                {suggested}
              </button>
            ))}
          </div>
        </div>

        {/* Current Skills List */}
        <div className="pt-2">
          {skills.length === 0 ? (
            <div className="text-center py-8 bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
              <span className="material-symbols-outlined text-4xl text-slate-300 mb-2 block">psychology</span>
              <p className="text-sm text-slate-600 font-medium">No skills added yet</p>
              <p className="text-xs text-slate-400 mt-1">Add at least 5 skills to boost your AI match rate.</p>
            </div>
          ) : (
            <div className="flex flex-wrap gap-2.5">
              {skills.map(skill => {
                const lvlKey = (skill.proficiency_level || 'BEGINNER').toUpperCase()
                const config = LEVEL_CONFIG[lvlKey] || LEVEL_CONFIG.BEGINNER

                return (
                  <div
                    key={skill.id || skill.skill_name}
                    className="group inline-flex items-center gap-2 pl-3.5 pr-2 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-slate-300 transition-all"
                  >
                    <span className="text-sm font-semibold text-slate-800 dark:text-white">
                      {skill.skill_name}
                    </span>

                    {/* Clickable Level Pill */}
                    <button
                      type="button"
                      onClick={() => handleCycleSkillLevel(skill)}
                      title="Click to cycle level: Beginner → Intermediate → Advanced → Expert"
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border transition-all cursor-pointer hover:scale-105 ${config.bg}`}
                    >
                      {config.label}
                    </button>

                    {/* Delete Button */}
                    <button
                      type="button"
                      onClick={() => handleDeleteSkill(skill.id)}
                      title="Remove skill"
                      className="text-slate-400 hover:text-red-500 transition-colors p-0.5 rounded-full"
                    >
                      <span className="material-symbols-outlined text-[15px]">close</span>
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </section>

      {/* ═══════════════ 4. RESUMES & QUICK ACTIONS ═══════════════ */}
      <section className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400">
              <span className="material-symbols-outlined text-2xl">description</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800 dark:text-white">Resume & Application Hub</h2>
              <p className="text-xs text-slate-500">Track your uploaded resumes and job applications</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">ATS Resume Scanner</span>
                {latestAtsScore != null && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                    ATS {latestAtsScore}/100
                  </span>
                )}
              </div>
              <p className="text-sm font-bold text-slate-800 dark:text-white">
                {resumeCount > 0 ? `${resumeCount} Analyzed Resume(s)` : 'No Resumes Uploaded'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Upload your resume to extract skills and unlock ATS score optimization.
              </p>
            </div>
            <Link
              to="/app/resume"
              className="mt-4 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-xl text-xs font-bold hover:border-[#0050cb] hover:text-[#0050cb] transition-all"
            >
              <span className="material-symbols-outlined text-[16px]">upload_file</span>
              Go to Resume Analysis
            </Link>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Application Tracker</span>
                <span className="material-symbols-outlined text-[18px] text-blue-500">inventory_2</span>
              </div>
              <p className="text-sm font-bold text-slate-800 dark:text-white">Applied Opportunities</p>
              <p className="text-xs text-slate-500 mt-1">
                Manage interviews, application statuses, and follow-ups in your pipeline.
              </p>
            </div>
            <Link
              to="/app/tracker"
              className="mt-4 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-xl text-xs font-bold hover:border-[#0050cb] hover:text-[#0050cb] transition-all"
            >
              <span className="material-symbols-outlined text-[16px]">view_kanban</span>
              View Tracker
            </Link>
          </div>
        </div>
      </section>

      {/* ═══════════════ 5. DANGER ZONE ═══════════════ */}
      <section className="bg-red-50/50 dark:bg-red-950/20 rounded-3xl p-6 sm:p-8 border border-red-200/80 dark:border-red-900/40">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-red-900 dark:text-red-300 flex items-center gap-2">
              <span className="material-symbols-outlined text-red-600">warning</span>
              Delete Account
            </h3>
            <p className="text-xs text-red-700/80 dark:text-red-400 mt-1 max-w-lg">
              Permanently delete your CareerLens AI account and all saved applications, career profiles, and resume scans. This action cannot be undone.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowDeleteModal(true)}
            className="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all shadow-sm shrink-0"
          >
            Delete Account
          </button>
        </div>
      </section>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-red-200 dark:border-red-900/60 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-2xl">delete_forever</span>
            </div>

            <div className="text-center">
              <h3 className="text-lg font-bold text-slate-800 dark:text-white">Are you absolutely sure?</h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                This will immediately delete your account and all associated data. Type <strong className="text-red-600 font-bold">DELETE</strong> to confirm.
              </p>
            </div>

            {deleteError && (
              <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs font-medium border border-red-200">
                {deleteError}
              </div>
            )}

            <input
              type="text"
              value={deleteConfirmText}
              onChange={e => setDeleteConfirmText(e.target.value)}
              placeholder="Type DELETE to confirm"
              className="w-full px-4 py-3 rounded-xl border border-red-200 dark:border-red-900 bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white outline-none focus:border-red-500 text-center font-bold"
            />

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => { setShowDeleteModal(false); setDeleteConfirmText(''); setDeleteError('') }}
                className="flex-1 py-3 rounded-xl border border-slate-200 text-slate-700 text-xs font-bold hover:bg-slate-50 transition-all"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={deleteConfirmText !== 'DELETE' || deleteLoading}
                onClick={handleDeleteAccount}
                className="flex-1 py-3 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {deleteLoading ? 'Deleting...' : 'Permanently Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
