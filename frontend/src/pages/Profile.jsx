import { useState, useContext, useEffect } from 'react'
import { AuthContext } from '../App'
import {
  getCareerProfile, createCareerProfile, updateCareerProfile,
  getSkillProfile, addSkill as apiAddSkill, updateSkill as apiUpdateSkill, deleteSkill as apiDeleteSkill
} from '../api'

const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced']
const LEVEL_COLORS = {
  Beginner: 'bg-info/15 text-info',
  Intermediate: 'bg-warning/15 text-warning',
  Advanced: 'bg-success/15 text-success',
}

const JOB_TYPES = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance']
const LOCATIONS = ['Remote', 'New York', 'San Francisco', 'London', 'Berlin', 'Bangalore', 'Toronto', 'Singapore', 'Tokyo', 'Sydney']
const INDUSTRIES = ['Technology', 'Finance', 'Healthcare', 'Education', 'E-commerce', 'AI / Machine Learning', 'Cybersecurity', 'Design', 'Marketing', 'Consulting']

export default function Profile() {
  const { user } = useContext(AuthContext)
  const displayName = user?.full_name || ''
  const initials = displayName ? displayName.split(' ').map(n => n[0]).join('').toUpperCase() : '?'

  // --- Personal Info ---
  const [isEditing, setIsEditing] = useState(false)
  const [personalInfo, setPersonalInfo] = useState({
    fullName: displayName,
    email: user?.email || '',
    phone: '',
    location: '',
    bio: '',
  })
  const [editDraft, setEditDraft] = useState({ ...personalInfo })

  const handleSavePersonal = () => {
    setPersonalInfo({ ...editDraft })
    setIsEditing(false)
  }
  const handleCancelEdit = () => {
    setEditDraft({ ...personalInfo })
    setIsEditing(false)
  }

  // --- Career Preferences ---
  const [selectedJobTypes, setSelectedJobTypes] = useState([])
  const [preferredLocations, setPreferredLocations] = useState([])
  const [salaryRange, setSalaryRange] = useState([80, 180])
  const [selectedIndustries, setSelectedIndustries] = useState([])
  const [hasCareerProfile, setHasCareerProfile] = useState(false)

  const toggleChip = (value, list, setList) => {
    setList(prev => prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value])
  }

  // --- Skills ---
  const [skills, setSkills] = useState([])
  const [newSkill, setNewSkill] = useState('')
  const [newSkillLevel, setNewSkillLevel] = useState('Intermediate')
  const [showAddSkill, setShowAddSkill] = useState(false)

  const addSkill = async () => {
    const trimmed = newSkill.trim()
    if (trimmed && !skills.find(s => s.name.toLowerCase() === trimmed.toLowerCase())) {
      try {
        const res = await apiAddSkill({ name: trimmed, level: newSkillLevel })
        setSkills(prev => [...prev, res])
        setNewSkill('')
        setNewSkillLevel('Intermediate')
        setShowAddSkill(false)
      } catch (err) {
        console.error('Failed to add skill', err)
      }
    }
  }
  const removeSkill = async (id, name) => {
    try {
      if (id) await apiDeleteSkill(id);
      setSkills(prev => prev.filter(s => s.name !== name))
    } catch (err) {
      console.error('Failed to remove skill', err)
    }
  }
  const cycleLevel = async (skill) => {
    const idx = SKILL_LEVELS.indexOf(skill.level)
    const nextLevel = SKILL_LEVELS[(idx + 1) % SKILL_LEVELS.length]
    try {
      await apiUpdateSkill(skill.id, { name: skill.name, level: nextLevel })
      setSkills(prev => prev.map(s => s.id === skill.id ? { ...s, level: nextLevel } : s))
    } catch (err) {
      console.error('Failed to update skill level', err)
    }
  }

  useEffect(() => {
    if (user) {
      getCareerProfile().then(res => {
        setHasCareerProfile(true)
        setSelectedJobTypes(res.job_types || [])
        setPreferredLocations(res.preferred_locations || [])
        setSalaryRange([res.salary_min || 80, res.salary_max || 180])
        setSelectedIndustries(res.industries || [])
      }).catch(err => {
        if (err.message && err.message.includes('404')) {
          setHasCareerProfile(false)
        } else {
          console.error("Failed to fetch career profile", err)
        }
      })
      
      getSkillProfile().then(res => {
        setSkills(res || [])
      }).catch(err => {
        console.error("Failed to fetch skills", err)
      })
    }
  }, [user])

  // --- Account Settings ---
  const [theme, setTheme] = useState('light')
  const [notifications, setNotifications] = useState({
    jobAlerts: true,
    weeklyDigest: true,
    applicationUpdates: true,
    promotionalEmails: false,
    skillRecommendations: true,
  })
  const [privacy, setPrivacy] = useState({
    profileVisible: true,
    showEmail: false,
    showPhone: false,
    allowRecruiterContact: true,
  })

  // --- Danger Zone ---
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteText, setDeleteText] = useState('')

  // --- Save feedback ---
  const [savedSection, setSavedSection] = useState(null)
  const flashSave = (section) => {
    setSavedSection(section)
    setTimeout(() => setSavedSection(null), 2000)
  }

  const handleSaveCareer = async () => {
    const data = {
      job_types: selectedJobTypes,
      preferred_locations: preferredLocations,
      salary_min: salaryRange[0],
      salary_max: salaryRange[1],
      industries: selectedIndustries
    }
    try {
      if (hasCareerProfile) {
        await updateCareerProfile(data)
      } else {
        await createCareerProfile(data)
        setHasCareerProfile(true)
      }
      flashSave('career')
    } catch (err) {
      console.error('Failed to save career preferences', err)
    }
  }

  // --- Helpers ---
  const SectionHeader = ({ icon, title, subtitle, children }) => (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-sm mb-lg">
      <div className="flex items-center gap-sm">
        <div className="p-sm bg-primary-container/10 rounded-lg">
          <span className="material-symbols-outlined text-primary">{icon}</span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-on-surface">{title}</h3>
          {subtitle && <p className="text-xs text-on-surface-variant font-[Geist]">{subtitle}</p>}
        </div>
      </div>
      {children}
    </div>
  )

  const Toggle = ({ checked, onChange, label }) => (
    <label className="flex items-center justify-between gap-md cursor-pointer group py-xs">
      <span className="text-sm text-on-surface group-hover:text-primary transition-colors">{label}</span>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-all duration-300 ${checked ? 'bg-primary' : 'bg-outline-variant'}`}
      >
        <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
      </button>
    </label>
  )

  const SavedBadge = ({ section }) => (
    savedSection === section ? (
      <span className="inline-flex items-center gap-xs text-xs font-medium text-success animate-fade-in-up">
        <span className="material-symbols-outlined text-[16px]">check_circle</span>
        Saved
      </span>
    ) : null
  )

  return (
    <div className="space-y-lg sm:space-y-xl animate-fade-in-up max-w-4xl mx-auto pb-3xl">

      {/* ═══════════════ PROFILE HEADER ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl relative overflow-hidden">
        {/* Decorative gradient band */}
        <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-br from-primary/10 via-primary-container/5 to-transparent rounded-t-2xl" />
        <div className="relative flex flex-col sm:flex-row items-center gap-lg pt-sm">
          {/* Avatar */}
          <div className="relative group">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-primary to-primary-container flex items-center justify-center text-2xl sm:text-3xl font-bold text-on-primary shadow-lg ring-4 ring-white/80 group-hover:scale-105 transition-transform duration-300">
              {initials}
            </div>
            <button className="absolute bottom-0 right-0 w-8 h-8 bg-surface border border-outline-variant rounded-full flex items-center justify-center shadow-sm hover:bg-primary hover:text-on-primary hover:border-primary transition-all duration-200" title="Change photo">
              <span className="material-symbols-outlined text-[16px]">photo_camera</span>
            </button>
          </div>

          {/* Info */}
          <div className="flex-1 text-center sm:text-left">
            <h2 className="text-xl sm:text-2xl font-bold text-on-surface">{personalInfo.fullName}</h2>
            <p className="text-xs sm:text-sm text-on-surface-variant mt-xs">{personalInfo.email}</p>
            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-sm mt-md">
              <span className="inline-flex items-center gap-xs px-sm py-xs bg-primary/10 text-primary text-xs font-bold font-[Geist] rounded-full">
                <span className="material-symbols-outlined text-[14px]">verified</span>
                Pro Member
              </span>
              <span className="inline-flex items-center gap-xs px-sm py-xs bg-success/10 text-success text-xs font-medium font-[Geist] rounded-full">
                <span className="material-symbols-outlined text-[14px]">trending_up</span>
                Top 12% Profile
              </span>
              <span className="text-xs text-on-surface-variant font-[Geist]">
                Member since Jan 2024
              </span>
            </div>
          </div>

          {/* Completion ring */}
          <div className="hidden md:flex flex-col items-center gap-xs">
            <div className="relative w-16 h-16">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
                <circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" className="text-outline-variant/30" strokeWidth="4" />
                <circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" className="text-primary" strokeWidth="4" strokeDasharray={`${0.82 * 2 * Math.PI * 28} ${2 * Math.PI * 28}`} strokeLinecap="round" />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-primary">82%</span>
            </div>
            <span className="text-[10px] font-[Geist] text-on-surface-variant uppercase tracking-wider">Profile</span>
          </div>
        </div>
      </section>

      {/* ═══════════════ PERSONAL INFORMATION ═══════════════ */}
      <section className="glass-effect rounded-2xl p-4 sm:p-xl">
        <SectionHeader icon="person" title="Personal Information" subtitle="Manage your personal details">
          <div className="flex items-center gap-sm">
            <SavedBadge section="personal" />
            {isEditing ? (
              <>
                <button onClick={handleCancelEdit} className="px-md py-xs text-sm font-[Geist] font-medium text-on-surface-variant border border-outline-variant rounded-lg hover:bg-surface-container transition-all">Cancel</button>
                <button onClick={() => { handleSavePersonal(); flashSave('personal') }} className="px-md py-xs text-sm font-[Geist] font-medium text-on-primary bg-primary rounded-lg hover:brightness-110 transition-all flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">save</span>
                  Save
                </button>
              </>
            ) : (
              <button onClick={() => { setEditDraft({ ...personalInfo }); setIsEditing(true) }} className="px-md py-xs text-sm font-[Geist] font-medium text-primary border border-primary/30 rounded-lg hover:bg-primary/5 transition-all flex items-center gap-xs">
                <span className="material-symbols-outlined text-[16px]">edit</span>
                Edit
              </button>
            )}
          </div>
        </SectionHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
          {[
            { key: 'fullName', label: 'Full Name', icon: 'badge', type: 'text' },
            { key: 'email', label: 'Email Address', icon: 'mail', type: 'email' },
            { key: 'phone', label: 'Phone Number', icon: 'call', type: 'tel' },
            { key: 'location', label: 'Location', icon: 'location_on', type: 'text' },
          ].map(field => (
            <div key={field.key} className="space-y-xs">
              <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider flex items-center gap-xs">
                <span className="material-symbols-outlined text-[14px]">{field.icon}</span>
                {field.label}
              </label>
              {isEditing ? (
                <input
                  type={field.type}
                  value={editDraft[field.key]}
                  onChange={e => setEditDraft(prev => ({ ...prev, [field.key]: e.target.value }))}
                  className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                />
              ) : (
                <p className="px-md py-sm bg-surface-container-low/50 rounded-lg text-sm text-on-surface border border-transparent">{personalInfo[field.key]}</p>
              )}
            </div>
          ))}

          {/* Bio — full width */}
          <div className="md:col-span-2 space-y-xs">
            <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider flex items-center gap-xs">
              <span className="material-symbols-outlined text-[14px]">description</span>
              Bio / About
            </label>
            {isEditing ? (
              <textarea
                rows={3}
                value={editDraft.bio}
                onChange={e => setEditDraft(prev => ({ ...prev, bio: e.target.value }))}
                className="w-full px-md py-sm bg-surface-container-low border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all resize-none"
              />
            ) : (
              <p className="px-md py-sm bg-surface-container-low/50 rounded-lg text-sm text-on-surface leading-relaxed border border-transparent">{personalInfo.bio}</p>
            )}
          </div>
        </div>
      </section>

      {/* ═══════════════ CAREER PREFERENCES ═══════════════ */}
      <section className="glass-effect rounded-2xl p-xl">
        <SectionHeader icon="work" title="Career Preferences" subtitle="Help us find the perfect opportunities for you">
          <SavedBadge section="career" />
        </SectionHeader>

        {/* Job Type */}
        <div className="mb-lg">
          <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider mb-sm block">Preferred Job Types</label>
          <div className="flex flex-wrap gap-sm">
            {JOB_TYPES.map(type => {
              const active = selectedJobTypes.includes(type)
              return (
                <button
                  key={type}
                  onClick={() => toggleChip(type, selectedJobTypes, setSelectedJobTypes)}
                  className={`px-md py-xs text-sm font-[Geist] font-medium rounded-full border transition-all duration-200 ${active ? 'bg-primary text-on-primary border-primary shadow-sm scale-[1.02]' : 'bg-surface-container-low text-on-surface-variant border-outline-variant hover:border-primary/40 hover:text-primary'}`}
                >
                  {active && <span className="material-symbols-outlined text-[14px] mr-xs align-middle">check</span>}
                  {type}
                </button>
              )
            })}
          </div>
        </div>

        {/* Preferred Locations */}
        <div className="mb-lg">
          <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider mb-sm block">Preferred Locations</label>
          <div className="flex flex-wrap gap-sm">
            {LOCATIONS.map(loc => {
              const active = preferredLocations.includes(loc)
              return (
                <button
                  key={loc}
                  onClick={() => toggleChip(loc, preferredLocations, setPreferredLocations)}
                  className={`px-md py-xs text-xs font-[Geist] font-medium rounded-full border transition-all duration-200 ${active ? 'bg-primary-container/15 text-primary border-primary/30' : 'bg-surface-container-low text-on-surface-variant border-outline-variant hover:border-primary/30'}`}
                >
                  {active && <span className="material-symbols-outlined text-[12px] mr-xs align-middle">location_on</span>}
                  {loc}
                </button>
              )
            })}
          </div>
        </div>

        {/* Salary */}
        <div className="mb-lg">
          <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider mb-sm block">Salary Expectations (USD/year)</label>
          <div className="bg-surface-container-low/60 rounded-xl p-lg">
            <div className="flex items-center justify-between mb-md">
              <span className="text-2xl font-bold text-on-surface">${salaryRange[0]}k <span className="text-on-surface-variant font-normal text-base">—</span> ${salaryRange[1]}k</span>
              <span className="text-xs font-[Geist] text-on-surface-variant bg-surface-container px-sm py-xs rounded-full">per year</span>
            </div>
            <div className="space-y-md">
              <div className="space-y-xs">
                <div className="flex justify-between text-xs font-[Geist] text-on-surface-variant">
                  <span>Minimum</span>
                  <span>${salaryRange[0]}k</span>
                </div>
                <input
                  type="range"
                  min={30}
                  max={300}
                  step={5}
                  value={salaryRange[0]}
                  onChange={e => {
                    const v = Number(e.target.value)
                    if (v <= salaryRange[1]) setSalaryRange([v, salaryRange[1]])
                  }}
                  className="w-full h-1.5 bg-outline-variant/30 rounded-full appearance-none cursor-pointer accent-primary [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:cursor-pointer"
                />
              </div>
              <div className="space-y-xs">
                <div className="flex justify-between text-xs font-[Geist] text-on-surface-variant">
                  <span>Maximum</span>
                  <span>${salaryRange[1]}k</span>
                </div>
                <input
                  type="range"
                  min={30}
                  max={300}
                  step={5}
                  value={salaryRange[1]}
                  onChange={e => {
                    const v = Number(e.target.value)
                    if (v >= salaryRange[0]) setSalaryRange([salaryRange[0], v])
                  }}
                  className="w-full h-1.5 bg-outline-variant/30 rounded-full appearance-none cursor-pointer accent-primary [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Industries */}
        <div className="mb-md">
          <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider mb-sm block">Industries of Interest</label>
          <div className="flex flex-wrap gap-sm">
            {INDUSTRIES.map(ind => {
              const active = selectedIndustries.includes(ind)
              return (
                <button
                  key={ind}
                  onClick={() => toggleChip(ind, selectedIndustries, setSelectedIndustries)}
                  className={`px-md py-xs text-xs font-[Geist] font-medium rounded-full border transition-all duration-200 ${active ? 'bg-success/10 text-success border-success/30' : 'bg-surface-container-low text-on-surface-variant border-outline-variant hover:border-success/30'}`}
                >
                  {active && <span className="material-symbols-outlined text-[12px] mr-xs align-middle">check</span>}
                  {ind}
                </button>
              )
            })}
          </div>
        </div>

        <div className="flex justify-end pt-sm">
          <button onClick={handleSaveCareer} className="px-lg py-sm text-sm font-[Geist] font-medium text-on-primary bg-primary rounded-lg hover:brightness-110 transition-all flex items-center gap-xs shadow-sm">
            <span className="material-symbols-outlined text-[16px]">save</span>
            Save Preferences
          </button>
        </div>
      </section>

      {/* ═══════════════ SKILLS & EXPERTISE ═══════════════ */}
      <section className="glass-effect rounded-2xl p-xl">
        <SectionHeader icon="psychology" title="Skills & Expertise" subtitle="Showcase your technical and soft skills">
          <button
            onClick={() => setShowAddSkill(!showAddSkill)}
            className="px-md py-xs text-sm font-[Geist] font-medium text-primary border border-primary/30 rounded-lg hover:bg-primary/5 transition-all flex items-center gap-xs"
          >
            <span className="material-symbols-outlined text-[16px]">{showAddSkill ? 'close' : 'add'}</span>
            {showAddSkill ? 'Cancel' : 'Add Skill'}
          </button>
        </SectionHeader>

        {/* Add skill form */}
        {showAddSkill && (
          <div className="mb-lg p-md bg-primary/5 border border-primary/15 rounded-xl animate-fade-in-up">
            <div className="flex flex-col sm:flex-row gap-sm">
              <input
                type="text"
                placeholder="Skill name (e.g. GraphQL)"
                value={newSkill}
                onChange={e => setNewSkill(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addSkill()}
                className="flex-1 px-md py-sm bg-white border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
              <select
                value={newSkillLevel}
                onChange={e => setNewSkillLevel(e.target.value)}
                className="px-md py-sm bg-white border border-outline-variant rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all font-[Geist]"
              >
                {SKILL_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
              <button
                onClick={addSkill}
                disabled={!newSkill.trim()}
                className="px-lg py-sm text-sm font-[Geist] font-medium text-on-primary bg-primary rounded-lg hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-xs"
              >
                <span className="material-symbols-outlined text-[16px]">add_circle</span>
                Add
              </button>
            </div>
          </div>
        )}

        {/* Skill chips */}
        <div className="flex flex-wrap gap-sm">
          {skills.map(skill => (
            <div
              key={skill.name}
              className="group flex items-center gap-xs px-md py-xs bg-surface-container-low border border-outline-variant rounded-full hover:border-primary/30 transition-all duration-200"
            >
              <span className="text-sm font-medium text-on-surface">{skill.name}</span>
              <button
                onClick={() => cycleLevel(skill)}
                title="Click to cycle level"
                className={`text-[10px] font-bold font-[Geist] uppercase px-xs py-[1px] rounded-full cursor-pointer transition-all ${LEVEL_COLORS[skill.level]}`}
              >
                {skill.level}
              </button>
              <button
                onClick={() => removeSkill(skill.id, skill.name)}
                className="opacity-0 group-hover:opacity-100 text-on-surface-variant hover:text-error transition-all duration-200 ml-xs"
              >
                <span className="material-symbols-outlined text-[14px]">close</span>
              </button>
            </div>
          ))}
        </div>

        {skills.length === 0 && (
          <div className="text-center py-xl text-on-surface-variant">
            <span className="material-symbols-outlined text-4xl mb-sm block opacity-40">lightbulb</span>
            <p className="text-sm">No skills added yet. Click "Add Skill" to get started.</p>
          </div>
        )}

        <p className="text-[11px] text-on-surface-variant font-[Geist] mt-md flex items-center gap-xs">
          <span className="material-symbols-outlined text-[14px]">info</span>
          Click a skill level badge to cycle through Beginner → Intermediate → Advanced. Hover to reveal the remove button.
        </p>
      </section>

      {/* ═══════════════ ACCOUNT SETTINGS ═══════════════ */}
      <section className="glass-effect rounded-2xl p-xl">
        <SectionHeader icon="settings" title="Account Settings" subtitle="Customize your experience">
          <SavedBadge section="settings" />
        </SectionHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
          {/* Theme */}
          <div className="space-y-md">
            <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider">Theme Preference</label>
            <div className="flex gap-sm">
              {[
                { id: 'light', icon: 'light_mode', label: 'Light' },
                { id: 'dark', icon: 'dark_mode', label: 'Dark' },
                { id: 'system', icon: 'desktop_windows', label: 'System' },
              ].map(opt => (
                <button
                  key={opt.id}
                  onClick={() => setTheme(opt.id)}
                  className={`flex-1 flex flex-col items-center gap-xs p-md rounded-xl border transition-all duration-200 ${theme === opt.id ? 'bg-primary/10 border-primary/30 text-primary shadow-sm' : 'bg-surface-container-low border-outline-variant text-on-surface-variant hover:border-primary/20'}`}
                >
                  <span className="material-symbols-outlined">{opt.icon}</span>
                  <span className="text-xs font-[Geist] font-medium">{opt.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Notifications */}
          <div className="space-y-md">
            <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider">Email Notifications</label>
            <div className="space-y-xs">
              {[
                { key: 'jobAlerts', label: 'New Job Alerts' },
                { key: 'weeklyDigest', label: 'Weekly Career Digest' },
                { key: 'applicationUpdates', label: 'Application Status Updates' },
                { key: 'promotionalEmails', label: 'Promotional Emails' },
                { key: 'skillRecommendations', label: 'Skill Recommendations' },
              ].map(item => (
                <Toggle
                  key={item.key}
                  checked={notifications[item.key]}
                  onChange={val => setNotifications(prev => ({ ...prev, [item.key]: val }))}
                  label={item.label}
                />
              ))}
            </div>
          </div>

          {/* Privacy */}
          <div className="md:col-span-2 space-y-md">
            <label className="text-xs font-[Geist] font-medium text-on-surface-variant uppercase tracking-wider">Privacy Settings</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-xl gap-y-xs">
              {[
                { key: 'profileVisible', label: 'Profile Visible to Recruiters' },
                { key: 'showEmail', label: 'Show Email on Profile' },
                { key: 'showPhone', label: 'Show Phone on Profile' },
                { key: 'allowRecruiterContact', label: 'Allow Recruiter Contact' },
              ].map(item => (
                <Toggle
                  key={item.key}
                  checked={privacy[item.key]}
                  onChange={val => setPrivacy(prev => ({ ...prev, [item.key]: val }))}
                  label={item.label}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-lg">
          <button onClick={() => flashSave('settings')} className="px-lg py-sm text-sm font-[Geist] font-medium text-on-primary bg-primary rounded-lg hover:brightness-110 transition-all flex items-center gap-xs shadow-sm">
            <span className="material-symbols-outlined text-[16px]">save</span>
            Save Settings
          </button>
        </div>
      </section>

      {/* ═══════════════ DANGER ZONE ═══════════════ */}
      <section className="border-2 border-error/20 rounded-2xl p-xl bg-error/[0.02]">
        <SectionHeader icon="warning" title="Danger Zone" subtitle="Irreversible and destructive actions" />

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md p-md bg-error/5 rounded-xl border border-error/10">
          <div>
            <h4 className="text-sm font-semibold text-on-surface">Delete Account</h4>
            <p className="text-xs text-on-surface-variant mt-xs">Once you delete your account, there is no going back. All your data, preferences, and history will be permanently removed.</p>
          </div>
          <button
            onClick={() => setShowDeleteConfirm(!showDeleteConfirm)}
            className="shrink-0 px-lg py-sm text-sm font-[Geist] font-medium text-error bg-error/10 border border-error/30 rounded-lg hover:bg-error hover:text-on-error transition-all duration-200"
          >
            Delete Account
          </button>
        </div>

        {showDeleteConfirm && (
          <div className="mt-md p-md bg-error/5 rounded-xl border border-error/20 animate-fade-in-up space-y-md">
            <p className="text-sm text-on-surface font-medium flex items-center gap-xs">
              <span className="material-symbols-outlined text-error text-[18px]">error</span>
              Please type <strong className="text-error mx-xs">DELETE</strong> to confirm
            </p>
            <input
              type="text"
              value={deleteText}
              onChange={e => setDeleteText(e.target.value)}
              placeholder="Type DELETE to confirm"
              className="w-full sm:w-72 px-md py-sm bg-white border border-error/30 rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-error/30 transition-all"
            />
            <div className="flex gap-sm">
              <button
                onClick={() => { setShowDeleteConfirm(false); setDeleteText('') }}
                className="px-md py-xs text-sm font-[Geist] font-medium text-on-surface-variant border border-outline-variant rounded-lg hover:bg-surface-container transition-all"
              >
                Cancel
              </button>
              <button
                disabled={deleteText !== 'DELETE'}
                className="px-md py-xs text-sm font-[Geist] font-medium text-on-error bg-error rounded-lg hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-xs"
              >
                <span className="material-symbols-outlined text-[16px]">delete_forever</span>
                Permanently Delete
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
