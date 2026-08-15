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

const LEVEL_BADGES = {
  BEGINNER: { label: 'Beginner', style: 'bg-info/10 text-info border-info/30' },
  INTERMEDIATE: { label: 'Intermediate', style: 'bg-warning/10 text-warning border-warning/30' },
  ADVANCED: { label: 'Advanced', style: 'bg-success/10 text-success border-success/30' },
  EXPERT: { label: 'Expert', style: 'bg-primary/10 text-primary border-primary/30' },
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

  // ── Handle Cycle Skill Level ──
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
    <div className="space-y-lg sm:space-y-xl animate-fade-in-up max-w-4xl mx-auto pb-3xl">

      {/* ═══════════════ PROFILE HEADER ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl relative overflow-hidden">
        {/* Subtle gradient banner */}
        <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-br from-primary/10 via-primary-container/5 to-transparent rounded-t-2xl pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row items-center sm:items-start justify-between gap-md sm:gap-lg pt-sm">
          {/* Avatar & User Info */}
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-md sm:gap-lg text-center sm:text-left">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-br from-primary to-primary-container flex items-center justify-center text-2xl sm:text-3xl font-bold text-on-primary shadow-lg ring-4 ring-white/80">
              {initials}
            </div>

            <div>
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-sm mb-xs">
                <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
                  {user?.full_name || 'User'}
                </h1>
                <span className="px-sm py-xs rounded-full text-xs font-bold font-[Geist] uppercase tracking-wider bg-primary-container/15 text-primary border border-primary/20">
                  {user?.role === 'admin' ? 'Administrator' : 'Career Seeker'}
                </span>
              </div>
              <p className="text-xs sm:text-sm text-on-surface-variant">{user?.email}</p>

              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-sm mt-sm">
                {careerData.target_role && (
                  <span className="inline-flex items-center gap-xs px-sm py-xs bg-surface-container text-on-surface-variant text-xs font-medium font-[Geist] rounded-full border border-outline-variant">
                    <span className="material-symbols-outlined text-[14px] text-primary">target</span>
                    {careerData.target_role}
                  </span>
                )}
                {careerData.location && (
                  <span className="inline-flex items-center gap-xs px-sm py-xs bg-surface-container text-on-surface-variant text-xs font-medium font-[Geist] rounded-full border border-outline-variant">
                    <span className="material-symbols-outlined text-[14px] text-on-surface-variant">location_on</span>
                    {careerData.location}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Profile Completeness Ring */}
          <div className="flex flex-col items-center bg-surface-container-low p-md rounded-xl border border-outline-variant min-w-[140px]">
            <div className="relative w-14 h-14 mb-xs">
              <svg className="w-14 h-14 -rotate-90" viewBox="0 0 64 64">
                <circle
                  cx="32" cy="32" r="26" fill="none"
                  stroke="currentColor" className="text-outline-variant/30" strokeWidth="4.5"
                />
                <circle
                  cx="32" cy="32" r="26" fill="none"
                  stroke="currentColor" className="text-primary" strokeWidth="4.5"
                  strokeDasharray={`${(completeness.percentage / 100) * 2 * Math.PI * 26} ${2 * Math.PI * 26}`}
                  strokeLinecap="round"
                />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-on-surface">
                {completeness.percentage}%
              </span>
            </div>
            <span className="text-xs font-semibold text-on-surface font-[Geist]">Profile Complete</span>
            {completeness.missing.length > 0 && (
              <span className="text-[10px] text-on-surface-variant mt-xs font-[Geist]">
                {completeness.missing.length} action{completeness.missing.length > 1 ? 's' : ''} left
              </span>
            )}
          </div>
        </div>

        {/* Missing Action items prompt */}
        {completeness.missing.length > 0 && (
          <div className="mt-md pt-md border-t border-outline-variant/50">
            <p className="text-xs font-semibold text-on-surface-variant font-[Geist] uppercase tracking-wider mb-sm">
              Complete your profile for optimized AI career matching:
            </p>
            <div className="flex flex-wrap gap-xs">
              {completeness.missing.map((item, i) => (
                <span key={i} className="inline-flex items-center gap-xs text-xs text-warning bg-warning/10 px-md py-xs rounded-full border border-warning/30 font-[Geist]">
                  <span className="material-symbols-outlined text-[13px]">add_circle</span>
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ═══════════════ 1. ACCOUNT INFORMATION ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl">
        <div className="flex items-center justify-between mb-lg pb-sm border-b border-outline-variant/60">
          <div className="flex items-center gap-sm">
            <div className="p-sm bg-primary-container/10 rounded-lg">
              <span className="material-symbols-outlined text-primary text-xl">account_circle</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-on-surface">Account Information</h2>
              <p className="text-xs text-on-surface-variant font-[Geist]">Manage your full name, login email, and password</p>
            </div>
          </div>
        </div>

        {nameSuccess && (
          <div className="mb-md p-sm rounded-lg bg-success/10 text-success text-xs font-medium font-[Geist] flex items-center gap-xs border border-success/30">
            <span className="material-symbols-outlined text-[16px]">check_circle</span>
            {nameSuccess}
          </div>
        )}
        {nameError && (
          <div className="mb-md p-sm rounded-lg bg-error/10 text-error text-xs font-medium font-[Geist] flex items-center gap-xs border border-error/30">
            <span className="material-symbols-outlined text-[16px]">error</span>
            {nameError}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
          {/* Full Name */}
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
              Full Name
            </label>
            {isEditingName ? (
              <form onSubmit={handleSaveName} className="flex gap-xs">
                <input
                  type="text"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  className="flex-1 px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                  placeholder="Your Full Name"
                  required
                />
                <button
                  type="submit"
                  disabled={savingName}
                  className="px-md py-sm bg-primary hover:brightness-110 text-on-primary rounded-lg text-xs font-medium font-[Geist] transition-all disabled:opacity-50"
                >
                  {savingName ? 'Saving...' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => { setFullName(user?.full_name || ''); setIsEditingName(false) }}
                  className="px-sm py-sm border border-outline-variant text-on-surface-variant rounded-lg text-xs font-medium font-[Geist] hover:bg-surface-container"
                >
                  Cancel
                </button>
              </form>
            ) : (
              <div className="flex items-center justify-between px-md py-sm rounded-lg bg-surface-container-low/60 border border-outline-variant/60">
                <span className="text-sm font-medium text-on-surface">{user?.full_name || 'Not specified'}</span>
                <button
                  onClick={() => setIsEditingName(true)}
                  className="text-xs font-medium font-[Geist] text-primary hover:underline flex items-center gap-xs"
                >
                  <span className="material-symbols-outlined text-[14px]">edit</span>
                  Edit
                </button>
              </div>
            )}
          </div>

          {/* Email Address */}
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
              Email Address
            </label>
            <div className="flex items-center justify-between px-md py-sm rounded-lg bg-surface-container-low/60 border border-outline-variant/60">
              <span className="text-sm font-medium text-on-surface">{user?.email}</span>
              <span className="text-xs text-on-surface-variant font-[Geist]">Primary Login</span>
            </div>
          </div>
        </div>

        {/* Change Password Section */}
        <div className="mt-lg pt-md border-t border-outline-variant/50">
          {!showPasswordSection ? (
            <button
              onClick={() => setShowPasswordSection(true)}
              className="inline-flex items-center gap-xs px-md py-sm rounded-lg border border-outline-variant text-sm font-medium font-[Geist] text-on-surface hover:bg-surface-container transition-all"
            >
              <span className="material-symbols-outlined text-[16px] text-primary">lock_reset</span>
              Change Account Password
            </button>
          ) : (
            <div className="p-md rounded-xl bg-surface-container-low border border-outline-variant animate-fade-in-up">
              <div className="flex items-center justify-between mb-md">
                <h3 className="text-sm font-semibold text-on-surface flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px] text-primary">key</span>
                  Change Password
                </h3>
                <button
                  type="button"
                  onClick={() => setShowPasswordSection(false)}
                  className="text-xs text-on-surface-variant hover:text-on-surface font-[Geist]"
                >
                  Close
                </button>
              </div>

              {passwordSuccess && (
                <div className="mb-sm p-sm rounded-lg bg-success/10 text-success text-xs font-medium font-[Geist] flex items-center gap-xs border border-success/30">
                  <span className="material-symbols-outlined text-[16px]">check_circle</span>
                  {passwordSuccess}
                </div>
              )}
              {passwordError && (
                <div className="mb-sm p-sm rounded-lg bg-error/10 text-error text-xs font-medium font-[Geist] flex items-center gap-xs border border-error/30">
                  <span className="material-symbols-outlined text-[16px]">error</span>
                  {passwordError}
                </div>
              )}

              <form onSubmit={handleChangePassword} className="space-y-sm max-w-md">
                <div>
                  <label className="text-xs font-medium font-[Geist] text-on-surface-variant mb-xs block">Current Password</label>
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={currentPassword}
                    onChange={e => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-md py-sm bg-surface-container-lowest border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium font-[Geist] text-on-surface-variant mb-xs block">New Password (min 8 characters)</label>
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-md py-sm bg-surface-container-lowest border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium font-[Geist] text-on-surface-variant mb-xs block">Confirm New Password</label>
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-md py-sm bg-surface-container-lowest border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                  />
                </div>

                <div className="flex items-center justify-between pt-xs">
                  <label className="flex items-center gap-xs cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showPw}
                      onChange={e => setShowPw(e.target.checked)}
                      className="w-3.5 h-3.5 rounded text-primary"
                    />
                    <span className="text-xs text-on-surface-variant font-[Geist]">Show passwords</span>
                  </label>

                  <div className="flex gap-xs">
                    <button
                      type="button"
                      onClick={() => setShowPasswordSection(false)}
                      className="px-md py-xs border border-outline-variant text-on-surface-variant rounded-lg text-xs font-medium font-[Geist] hover:bg-surface-container"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={passwordLoading}
                      className="px-md py-xs bg-primary hover:brightness-110 text-on-primary rounded-lg text-xs font-medium font-[Geist] transition-all disabled:opacity-50"
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
      <section className="glass-effect rounded-2xl p-4 sm:p-xl">
        <div className="flex items-center justify-between mb-lg pb-sm border-b border-outline-variant/60">
          <div className="flex items-center gap-sm">
            <div className="p-sm bg-primary-container/10 rounded-lg">
              <span className="material-symbols-outlined text-primary text-xl">work</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-on-surface">Career Goals & Preferences</h2>
              <p className="text-xs text-on-surface-variant font-[Geist]">Powers your personalized AI job recommendations & skill roadmaps</p>
            </div>
          </div>
        </div>

        {careerSuccess && (
          <div className="mb-md p-sm rounded-lg bg-success/10 text-success text-xs font-medium font-[Geist] flex items-center gap-xs border border-success/30">
            <span className="material-symbols-outlined text-[16px]">check_circle</span>
            {careerSuccess}
          </div>
        )}
        {careerError && (
          <div className="mb-md p-sm rounded-lg bg-error/10 text-error text-xs font-medium font-[Geist] flex items-center gap-xs border border-error/30">
            <span className="material-symbols-outlined text-[16px]">error</span>
            {careerError}
          </div>
        )}

        <form onSubmit={handleSaveCareer} className="space-y-md">
          {/* Target Role */}
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
              Target Dream Role <span className="text-error">*</span>
            </label>
            <input
              type="text"
              required
              value={careerData.target_role}
              onChange={e => setCareerData(prev => ({ ...prev, target_role: e.target.value }))}
              placeholder="e.g. Full Stack Developer, Data Scientist"
              className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
            {/* Quick Role Suggestions */}
            <div className="flex flex-wrap gap-xs pt-xs">
              <span className="text-[11px] text-on-surface-variant font-[Geist] self-center mr-xs">Popular:</span>
              {POPULAR_ROLES.slice(0, 6).map(role => (
                <button
                  type="button"
                  key={role}
                  onClick={() => setCareerData(prev => ({ ...prev, target_role: role }))}
                  className={`text-xs font-[Geist] font-medium px-sm py-xs rounded-full border transition-all ${
                    careerData.target_role === role
                      ? 'bg-primary text-on-primary border-primary shadow-xs'
                      : 'bg-surface-container-low text-on-surface-variant border-outline-variant hover:border-primary/40 hover:text-primary'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
            {/* Current Role */}
            <div className="space-y-xs">
              <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                Current Role / Status
              </label>
              <input
                type="text"
                value={careerData.current_role}
                onChange={e => setCareerData(prev => ({ ...prev, current_role: e.target.value }))}
                placeholder="e.g. Student / Intern / Junior SDE"
                className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>

            {/* Experience Level */}
            <div className="space-y-xs">
              <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                Experience Level
              </label>
              <select
                value={careerData.experience_level}
                onChange={e => setCareerData(prev => ({ ...prev, experience_level: e.target.value }))}
                className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all font-[Geist]"
              >
                {EXPERIENCE_LEVELS.map(exp => (
                  <option key={exp.value} value={exp.value}>{exp.label}</option>
                ))}
              </select>
            </div>

            {/* Education */}
            <div className="space-y-xs">
              <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                Highest Education
              </label>
              <select
                value={careerData.education}
                onChange={e => setCareerData(prev => ({ ...prev, education: e.target.value }))}
                className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all font-[Geist]"
              >
                {EDUCATION_OPTIONS.map(edu => (
                  <option key={edu} value={edu}>{edu}</option>
                ))}
              </select>
            </div>

            {/* Preferred Location */}
            <div className="space-y-xs">
              <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block">
                Preferred Job Location
              </label>
              <input
                type="text"
                value={careerData.location}
                onChange={e => setCareerData(prev => ({ ...prev, location: e.target.value }))}
                placeholder="e.g. Remote, Bengaluru, San Francisco"
                className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>
          </div>

          {/* Quick Location Pills */}
          <div className="flex flex-wrap gap-xs pt-xs">
            <span className="text-[11px] text-on-surface-variant font-[Geist] self-center mr-xs">Locations:</span>
            {POPULAR_LOCATIONS.map(loc => (
              <button
                type="button"
                key={loc}
                onClick={() => setCareerData(prev => ({ ...prev, location: loc }))}
                className={`text-xs font-[Geist] font-medium px-sm py-xs rounded-full border transition-all ${
                  careerData.location === loc
                    ? 'bg-primary text-on-primary border-primary shadow-xs'
                    : 'bg-surface-container-low text-on-surface-variant border-outline-variant hover:border-primary/40 hover:text-primary'
                }`}
              >
                {loc}
              </button>
            ))}
          </div>

          <div className="pt-sm flex justify-end">
            <button
              type="submit"
              disabled={careerLoading}
              className="px-lg py-sm bg-primary hover:brightness-110 text-on-primary rounded-lg text-sm font-medium font-[Geist] shadow-sm transition-all disabled:opacity-50 flex items-center gap-xs"
            >
              <span className="material-symbols-outlined text-[16px]">save</span>
              {careerLoading ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </form>
      </section>

      {/* ═══════════════ 3. SKILLS & EXPERTISE ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl">
        <div className="flex items-center justify-between mb-lg pb-sm border-b border-outline-variant/60">
          <div className="flex items-center gap-sm">
            <div className="p-sm bg-primary-container/10 rounded-lg">
              <span className="material-symbols-outlined text-primary text-xl">psychology</span>
            </div>
            <div>
              <div className="flex items-center gap-xs">
                <h2 className="text-lg font-semibold text-on-surface">Skills & Technologies</h2>
                <span className="px-sm py-xs rounded-full text-xs font-bold font-[Geist] bg-primary-container/15 text-primary">
                  {skills.length}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant font-[Geist]">Click level badge to cycle proficiency (Beginner → Expert)</p>
            </div>
          </div>
        </div>

        {skillError && (
          <div className="mb-md p-sm rounded-lg bg-error/10 text-error text-xs font-medium font-[Geist] flex items-center gap-xs border border-error/30">
            <span className="material-symbols-outlined text-[16px]">error</span>
            {skillError}
          </div>
        )}

        {/* Add Skill Form */}
        <div className="flex flex-col sm:flex-row gap-xs mb-md">
          <input
            type="text"
            placeholder="Add a new skill (e.g. Next.js, Docker)"
            value={newSkillName}
            onChange={e => setNewSkillName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAddSkill()}
            className="flex-1 px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
          />
          <select
            value={newSkillLevel}
            onChange={e => setNewSkillLevel(e.target.value)}
            className="px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none font-medium font-[Geist]"
          >
            {SKILL_LEVELS.map(lvl => (
              <option key={lvl} value={lvl}>{LEVEL_BADGES[lvl]?.label || lvl}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => handleAddSkill()}
            disabled={!newSkillName.trim() || skillLoading}
            className="px-lg py-sm bg-primary hover:brightness-110 text-on-primary rounded-lg text-xs font-medium font-[Geist] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-xs shadow-sm"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            Add Skill
          </button>
        </div>

        {/* Suggested Skills to Add */}
        <div className="mb-lg">
          <span className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider block mb-xs">
            Quick Add Suggested Skills:
          </span>
          <div className="flex flex-wrap gap-xs">
            {SUGGESTED_SKILLS.filter(s => !skills.some(userSkill => userSkill.skill_name?.toLowerCase() === s.toLowerCase())).map(suggested => (
              <button
                key={suggested}
                type="button"
                onClick={() => handleAddSkill(suggested, 'INTERMEDIATE')}
                className="inline-flex items-center gap-xs px-sm py-xs rounded-full text-xs font-medium font-[Geist] bg-surface-container-low text-on-surface-variant border border-outline-variant hover:border-primary/40 hover:text-primary transition-all"
              >
                <span className="material-symbols-outlined text-[12px] text-on-surface-variant">+</span>
                {suggested}
              </button>
            ))}
          </div>
        </div>

        {/* Current Skills List */}
        <div className="pt-xs">
          {skills.length === 0 ? (
            <div className="text-center py-xl bg-surface-container-low/40 rounded-xl border border-dashed border-outline-variant">
              <span className="material-symbols-outlined text-3xl text-on-surface-variant/40 mb-xs block">psychology</span>
              <p className="text-sm text-on-surface font-medium font-[Geist]">No skills added yet</p>
              <p className="text-xs text-on-surface-variant mt-xs">Add at least 5 skills to boost your AI match rate.</p>
            </div>
          ) : (
            <div className="flex flex-wrap gap-xs">
              {skills.map(skill => {
                const lvlKey = (skill.proficiency_level || 'BEGINNER').toUpperCase()
                const badgeConfig = LEVEL_BADGES[lvlKey] || LEVEL_BADGES.BEGINNER

                return (
                  <div
                    key={skill.id || skill.skill_name}
                    className="group inline-flex items-center gap-xs px-md py-xs rounded-full bg-surface-container-low border border-outline-variant shadow-xs hover:border-primary/30 transition-all"
                  >
                    <span className="text-sm font-medium text-on-surface">
                      {skill.skill_name}
                    </span>

                    {/* Clickable Level Pill */}
                    <button
                      type="button"
                      onClick={() => handleCycleSkillLevel(skill)}
                      title="Click to cycle level: Beginner → Intermediate → Advanced → Expert"
                      className={`text-[10px] font-bold font-[Geist] uppercase px-sm py-0.5 rounded-full border transition-all cursor-pointer hover:scale-105 ${badgeConfig.style}`}
                    >
                      {badgeConfig.label}
                    </button>

                    {/* Delete Button */}
                    <button
                      type="button"
                      onClick={() => handleDeleteSkill(skill.id)}
                      title="Remove skill"
                      className="opacity-0 group-hover:opacity-100 text-on-surface-variant hover:text-error transition-all p-0.5 rounded-full"
                    >
                      <span className="material-symbols-outlined text-[14px]">close</span>
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </section>

      {/* ═══════════════ 4. RESUMES & APPLICATION HUB ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl">
        <div className="flex items-center justify-between mb-lg pb-sm border-b border-outline-variant/60">
          <div className="flex items-center gap-sm">
            <div className="p-sm bg-primary-container/10 rounded-lg">
              <span className="material-symbols-outlined text-primary text-xl">description</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-on-surface">Resume & Application Hub</h2>
              <p className="text-xs text-on-surface-variant font-[Geist]">Track your analyzed resumes and job applications</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
          <div className="p-md rounded-xl bg-surface-container-low/70 border border-outline-variant flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-xs">
                <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">ATS Resume Scanner</span>
                {latestAtsScore != null && (
                  <span className="px-sm py-xs rounded-full text-xs font-bold font-[Geist] bg-success/15 text-success border border-success/30">
                    ATS {latestAtsScore}/100
                  </span>
                )}
              </div>
              <p className="text-sm font-bold text-on-surface">
                {resumeCount > 0 ? `${resumeCount} Analyzed Resume(s)` : 'No Resumes Uploaded'}
              </p>
              <p className="text-xs text-on-surface-variant mt-xs">
                Upload your resume to extract skills and unlock ATS score optimization.
              </p>
            </div>
            <Link
              to="/app/resume"
              className="mt-md inline-flex items-center justify-center gap-xs px-md py-sm bg-surface-container-lowest border border-outline-variant text-on-surface rounded-lg text-xs font-medium font-[Geist] hover:border-primary hover:text-primary transition-all shadow-xs"
            >
              <span className="material-symbols-outlined text-[16px]">upload_file</span>
              Go to Resume Analysis
            </Link>
          </div>

          <div className="p-md rounded-xl bg-surface-container-low/70 border border-outline-variant flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-xs">
                <span className="text-xs font-semibold font-[Geist] text-on-surface-variant uppercase tracking-wider">Application Tracker</span>
                <span className="material-symbols-outlined text-[18px] text-primary">inventory_2</span>
              </div>
              <p className="text-sm font-bold text-on-surface">Applied Opportunities</p>
              <p className="text-xs text-on-surface-variant mt-xs">
                Manage interviews, application statuses, and follow-ups in your pipeline.
              </p>
            </div>
            <Link
              to="/app/tracker"
              className="mt-md inline-flex items-center justify-center gap-xs px-md py-sm bg-surface-container-lowest border border-outline-variant text-on-surface rounded-lg text-xs font-medium font-[Geist] hover:border-primary hover:text-primary transition-all shadow-xs"
            >
              <span className="material-symbols-outlined text-[16px]">view_kanban</span>
              View Application Tracker
            </Link>
          </div>
        </div>
      </section>

      {/* ═══════════════ 5. DANGER ZONE ═══════════════ */}
      <section className="border border-error/30 rounded-2xl p-4 sm:p-xl bg-error/[0.03]">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md">
          <div>
            <h3 className="text-sm font-bold text-error flex items-center gap-xs">
              <span className="material-symbols-outlined text-error text-[18px]">warning</span>
              Delete Account
            </h3>
            <p className="text-xs text-on-surface-variant mt-xs max-w-lg">
              Permanently delete your CareerLens AI account and all saved applications, career preferences, and resume scans. This action is irreversible.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowDeleteModal(true)}
            className="px-md py-sm rounded-lg bg-error text-on-error text-xs font-medium font-[Geist] hover:brightness-110 transition-all shadow-xs shrink-0"
          >
            Delete Account
          </button>
        </div>
      </section>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-surface-container-lowest rounded-2xl p-md sm:p-xl max-w-md w-full shadow-2xl border border-error/30 space-y-md">
            <div className="w-12 h-12 rounded-xl bg-error/10 text-error flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-2xl">delete_forever</span>
            </div>

            <div className="text-center">
              <h3 className="text-lg font-bold text-on-surface">Are you absolutely sure?</h3>
              <p className="text-xs text-on-surface-variant mt-xs leading-relaxed">
                This will immediately delete your account and all associated data. Type <strong className="text-error font-bold">DELETE</strong> to confirm.
              </p>
            </div>

            {deleteError && (
              <div className="p-sm rounded-lg bg-error/10 text-error text-xs font-medium font-[Geist] border border-error/30">
                {deleteError}
              </div>
            )}

            <input
              type="text"
              value={deleteConfirmText}
              onChange={e => setDeleteConfirmText(e.target.value)}
              placeholder="Type DELETE to confirm"
              className="w-full px-md py-sm rounded-lg border border-error/30 bg-surface-container-low text-sm text-on-surface outline-none focus:ring-2 focus:ring-error/30 text-center font-bold font-[Geist]"
            />

            <div className="flex gap-sm pt-xs">
              <button
                type="button"
                onClick={() => { setShowDeleteModal(false); setDeleteConfirmText(''); setDeleteError('') }}
                className="flex-1 py-sm rounded-lg border border-outline-variant text-on-surface-variant text-xs font-medium font-[Geist] hover:bg-surface-container transition-all"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={deleteConfirmText !== 'DELETE' || deleteLoading}
                onClick={handleDeleteAccount}
                className="flex-1 py-sm rounded-lg bg-error hover:brightness-110 text-on-error text-xs font-medium font-[Geist] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
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
