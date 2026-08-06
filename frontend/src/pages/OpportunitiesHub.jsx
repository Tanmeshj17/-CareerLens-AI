import React, { useState, useEffect, useContext, memo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getOpportunities, getRecommendedOpportunities, createApplication } from '../api'
import { AuthContext } from '../App'
import { Alert } from '../components/ui/Alert'
import { Badge } from '../components/ui/Badge'
import { EmptyState } from '../components/ui/EmptyState'
import { Button } from '../components/ui/Button'

// --- Phase 8.55: Link Integrity Badge ---
const LINK_BADGE_CONFIG = {
  VERIFIED_DIRECT:               { label: 'Verified Apply', icon: 'verified', cls: 'bg-success/10 text-success border-success/20' },
  VERIFIED_POSTING:              { label: 'Posting Page',   icon: 'link',      cls: 'bg-primary/10 text-primary border-primary/20' },
  BROWSER_VERIFICATION_REQUIRED: { label: 'ATS Protected',  icon: 'shield',    cls: 'bg-secondary-container/30 text-on-secondary-container border-secondary-container/50' },
  CAREER_BOARD:                  { label: 'Careers Page',   icon: 'open_in_new',cls: 'bg-warning/10 text-warning border-warning/20' },
  UNKNOWN:                       { label: 'Unverified',     icon: 'help',      cls: 'bg-surface-container text-on-surface-variant border-outline-variant' },
  HOMEPAGE_ONLY:                 { label: 'Homepage Only',  icon: 'warning',   cls: 'bg-error/10 text-error border-error/20' },
  BROKEN:                        { label: 'Broken Link',    icon: 'link_off',  cls: 'bg-error/10 text-error border-error/20' },
}

function LinkBadge({ status }) {
  if (!status) return null
  const cfg = LINK_BADGE_CONFIG[status] || LINK_BADGE_CONFIG.UNKNOWN
  const variantMap = {
    'bg-success/10 text-success border-success/20': 'success',
    'bg-primary/10 text-primary border-primary/20': 'primary',
    'bg-secondary-container/30 text-on-secondary-container border-secondary-container/50': 'default',
    'bg-warning/10 text-warning border-warning/20': 'warning',
    'bg-surface-container text-on-surface-variant border-outline-variant': 'default',
    'bg-error/10 text-error border-error/20': 'error'
  };
  return <Badge variant={variantMap[cfg.cls] || 'default'} icon={cfg.icon}>{cfg.label}</Badge>
}

// --- Phase 8.6: Lifecycle & Confidence Badges ---
const LIFECYCLE_BADGE_CONFIG = {
  NEW:      { label: 'Fresh',    icon: 'new_releases',  cls: 'bg-primary text-on-primary border-primary/20' },
  ACTIVE:   { label: 'Active',   icon: 'check_circle',  cls: 'bg-success/10 text-success border-success/20' },
  STALE:    { label: 'Stale',    icon: 'update',        cls: 'bg-warning/10 text-warning border-warning/20' },
  EXPIRED:  { label: 'Expired',  icon: 'history',       cls: 'bg-error/10 text-error border-error/20' },
  BROKEN:   { label: 'Broken',   icon: 'broken_image',  cls: 'bg-error/10 text-error border-error/20' },
  CLOSED:   { label: 'Closed',   icon: 'lock',          cls: 'bg-error/10 text-error border-error/20' },
  INVALID:  { label: 'Invalid',  icon: 'cancel',        cls: 'bg-error/10 text-error border-error/20' },
  ARCHIVED: { label: 'Archived', icon: 'archive',       cls: 'bg-surface-container text-on-surface-variant border-outline-variant' },
}

function LifecycleBadge({ status }) {
  if (!status) return null
  const cfg = LIFECYCLE_BADGE_CONFIG[status] || LIFECYCLE_BADGE_CONFIG.ACTIVE
  const variantMap = {
    'bg-primary text-on-primary border-primary/20': 'primary',
    'bg-success/10 text-success border-success/20': 'success',
    'bg-warning/10 text-warning border-warning/20': 'warning',
    'bg-error/10 text-error border-error/20': 'error',
    'bg-surface-container text-on-surface-variant border-outline-variant': 'default'
  };
  return <Badge variant={variantMap[cfg.cls] || 'default'} icon={cfg.icon} className={cfg.cls.includes('text-on-primary') ? 'bg-primary text-on-primary border-primary' : ''}>{cfg.label}</Badge>
}

// Phase 11.3.8: Status Badge from new `status` field
const STATUS_BADGE_CONFIG = {
  ACTIVE:   null, // Don't show a badge for normal active jobs
  STALE:    { label: 'Stale',    icon: 'schedule',     cls: 'bg-warning/10 text-warning border-warning/20' },
  CLOSED:   { label: 'Closed',   icon: 'lock',         cls: 'bg-error/10 text-error border-error/20' },
  INVALID:  { label: 'Invalid',  icon: 'cancel',       cls: 'bg-error/10 text-error border-error/20' },
  ARCHIVED: { label: 'Archived', icon: 'archive',      cls: 'bg-surface-container text-on-surface-variant border-outline-variant' },
}

function StatusBadge({ status }) {
  if (!status) return null
  const cfg = STATUS_BADGE_CONFIG[status]
  if (!cfg) return null
  const variantMap = {
    'bg-warning/10 text-warning border-warning/20': 'warning',
    'bg-error/10 text-error border-error/20': 'error',
    'bg-surface-container text-on-surface-variant border-outline-variant': 'default'
  };
  return <Badge variant={variantMap[cfg.cls] || 'default'} icon={cfg.icon}>{cfg.label}</Badge>
}

const JobCard = memo(({ job, navigate, savedIds, savingId, handleSave, handleApply, getTrustColor, formatDate }) => {
  const md = job.match_data
  const rolePct = md?.scores?.role_pct ?? null
  const isRelated = job.search_level === 2
  const isFallback = job.search_level === 3
  
  return (
    <div className={`bg-white p-lg rounded-xl border transition-all flex flex-col justify-between group ${
      isFallback ? 'border-outline-variant/50 opacity-80 hover:opacity-100' : 'border-outline-variant hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5'
    }`}>
      {isFallback && (
        <div className="flex items-center gap-xs mb-sm text-xs text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
          <span className="material-symbols-outlined text-[13px]">shuffle</span>
          Related Opportunity
        </div>
      )}
      <div className="flex justify-between items-start gap-md">
        <div className="flex gap-md">
          <div className="w-14 h-14 rounded-lg bg-surface-container-high flex items-center justify-center border border-outline-variant overflow-hidden shrink-0">
            <span className="text-xl font-bold text-primary">{(job.company || '?')[0]}</span>
          </div>
          <div>
            <h3 className="text-xl font-bold text-on-background group-hover:text-primary transition-colors cursor-pointer"
                onClick={() => navigate(`/app/opportunities/${job.id}`)}>
              {job.title}
            </h3>
            <p className="text-base text-on-surface-variant font-medium">{job.company}</p>
            <div className="flex flex-wrap gap-sm mt-sm items-center">
              {job.location && (
                <span className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
                  <span className="material-symbols-outlined text-[14px]">location_on</span> {job.location}
                </span>
              )}
              {job.job_type && (
                <span className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
                  <span className="material-symbols-outlined text-[14px]">work</span> {job.job_type}
                </span>
              )}
              {job.salary_range && (
                <span className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
                  <span className="material-symbols-outlined text-[14px]">payments</span> {job.salary_range}
                </span>
              )}
              {/* Phase 8.65: Role Match % badge */}
              {rolePct !== null && (
                <span className={`flex items-center gap-[3px] text-xs font-bold px-sm py-xs rounded border ${
                  rolePct >= 80 ? 'bg-success/10 text-success border-success/20' :
                  rolePct >= 40 ? 'bg-warning/10 text-warning border-warning/20' :
                  'bg-surface-container text-on-surface-variant border-outline-variant'
                }`}>
                  <span className="material-symbols-outlined text-[12px]">target</span>
                  {rolePct}% Role Match
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-sm shrink-0">
          {md && (
            <div className={`px-md py-xs rounded text-xs font-bold uppercase tracking-wider border ${
              md.probability === 'High Probability' ? 'bg-success/10 text-success border-success/20' :
              md.probability === 'Medium Probability' ? 'bg-warning/10 text-warning border-warning/20' :
              'bg-error/10 text-error border-error/20'
            }`}>
              {md.scores.total_score}% Match
            </div>
          )}
          {/* Phase 8.6: Lifecycle badge */}
          {job.lifecycle_status && <LifecycleBadge status={job.lifecycle_status} />}
          {/* Phase 11.3.8: Status badge (CLOSED, INVALID, STALE, ARCHIVED) */}
          <StatusBadge status={job.status} />
          {/* Phase 8.55: Link integrity badge */}
          <LinkBadge status={job.apply_url_status} />
        </div>
      </div>

      {/* Skills */}
      {job.required_skills && (
        <div className="flex flex-wrap gap-1 mt-md">
          {job.required_skills.split(',').slice(0, 5).map((skill, i) => (
            <span key={i} className="text-[11px] px-2 py-0.5 rounded-full bg-secondary-container/40 text-on-secondary-container font-medium">{skill.trim()}</span>
          ))}
          {job.required_skills.split(',').length > 5 && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-medium">+{job.required_skills.split(',').length - 5} more</span>
          )}
        </div>
      )}

      <div className="mt-lg pt-lg border-t border-outline-variant/30 flex flex-col md:flex-row justify-between items-start md:items-center gap-sm">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-xs">
            <span className="material-symbols-outlined text-[16px] text-primary">verified</span>
            <span className="text-xs font-semibold font-[Geist] text-on-surface">Source: {job.primary_source || job.ats_type || 'Official'}</span>
          </div>
          <div className="flex items-center gap-xs text-on-surface-variant">
            <span className="material-symbols-outlined text-[16px]">shield</span>
            <span className="text-[11px] font-medium font-[Geist]">
              Confidence: <span className={getTrustColor(job.confidence_score || job.trust_score || 0)}>{job.confidence_score || job.trust_score || 0}/100</span> • 
              Completeness: <span className="font-bold">{job.completeness_score || 0}/100</span> • {formatDate(job.posted_date)}
            </span>
          </div>
          {/* Phase 9.0: Explainable Recommendation Diagnostics */}
          {md?.diagnostics?.why_recommended?.length > 0 && (
            <div className="flex items-center gap-xs mt-1">
              <span className="material-symbols-outlined text-[13px] text-success">lightbulb</span>
              <span className="text-[10px] font-medium font-[Geist] text-success">
                {md.diagnostics.why_recommended.join(' • ')}
              </span>
            </div>
          )}
          {md?.missing_skills?.length > 0 && (
            <div className="flex items-center gap-xs mt-0.5">
              <span className="material-symbols-outlined text-[13px] text-warning">school</span>
              <span className="text-[10px] font-medium font-[Geist] text-on-surface-variant">
                Missing: {md.missing_skills.slice(0, 4).join(', ')}{md.missing_skills.length > 4 ? ` +${md.missing_skills.length - 4}` : ''}
              </span>
            </div>
          )}
        </div>
        <div className="flex gap-sm w-full md:w-auto">
          <Button
            variant="secondary"
            onClick={() => handleSave(job.id)}
            disabled={savingId === job.id || savedIds.has(job.id)}
            className={`!px-3 !py-2 shrink-0 ${savedIds.has(job.id) ? 'bg-primary/10 text-primary border-primary/30' : ''}`}
          >
            <span className="material-symbols-outlined text-sm" style={savedIds.has(job.id) ? {fontVariationSettings: "'FILL' 1"} : {}}>
              {savingId === job.id ? 'progress_activity' : 'bookmark'}
            </span>
          </Button>
          {/* Don't show active Apply button for CLOSED, EXPIRED, or INVALID jobs */}
          {job.status === 'CLOSED' || job.status === 'INVALID' || job.lifecycle_status === 'CLOSED' || job.lifecycle_status === 'EXPIRED' || job.lifecycle_status === 'INVALID_LINK' || job.apply_url_status === 'INVALID_LINK' ? (
            <Button
              variant="secondary"
              disabled
              className="w-full md:w-auto flex items-center justify-center gap-2 opacity-60"
            >
              <span className="material-symbols-outlined text-[16px]">block</span>
              {job.lifecycle_status === 'EXPIRED' ? 'Expired' : (job.status === 'CLOSED' || job.lifecycle_status === 'CLOSED' ? 'Position Closed' : 'Link Invalid')}
            </Button>
          ) : job.apply_url ? (
            <Button
              variant="primary"
              onClick={() => handleApply(job.id, job.apply_url, job.apply_url_status)}
              className="w-full md:w-auto flex items-center justify-center gap-2"
            >
              Apply Now <span className="material-symbols-outlined text-[16px]">open_in_new</span>
            </Button>
          ) : (
            <Button
              variant="secondary"
              onClick={() => navigate(`/app/opportunities/${job.id}`)}
              className="w-full md:w-auto bg-secondary-container text-on-secondary-container border-secondary-container hover:bg-secondary-container/80"
            >
              View Details
            </Button>
          )}
        </div>
      </div>
    </div>
  )
})

export default function OpportunitiesHub() {
  const { user } = useContext(AuthContext)
  const navigate = useNavigate()

  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [searchMeta, setSearchMeta] = useState(null) // Phase 8.65: search confidence

  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [suggestions, setSuggestions] = useState({roles:[], skills:[], companies:[]})
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [locationFilter, setLocationFilter] = useState('')
  const [jobType, setJobType] = useState('All')

  // Saved jobs tracker
  const [savedIds, setSavedIds] = useState(new Set())
  const [savingId, setSavingId] = useState(null)

  const fetchJobs = async (append = false, page = 1) => {
    try {
      if (append) setLoadingMore(true)
      else setLoading(true)
      setError(null)

      const params = {
        search: searchQuery || undefined,
        type: jobType !== 'All' ? jobType : undefined,
        location: locationFilter || undefined,
        limit: 20,
        skip: (page - 1) * 20,
        page: page, // legacy compatibility
      }

      let data;
      if (user) {
        data = await getRecommendedOpportunities(params)
        // Map recommended opportunities format
        if (data.items) {
          const mappedJobs = data.items.map(item => ({
            ...item.opportunity,
            match_data: item.match_data,
            search_level: item.search_level
          }));
          data.opportunities = mappedJobs;
          data.has_more = (page * 20) < data.total;
          if (!append && data.search_metadata) setSearchMeta(data.search_metadata)
        }
      } else {
        data = await getOpportunities(params)
      }

      if (append) {
        setJobs(prev => [...prev, ...data.opportunities])
      } else {
        setJobs(data.opportunities)
      }
      setTotal(data.total)
      setHasMore(data.has_more)
      setCurrentPage(page)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  // Autocomplete debouncer
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSuggestions({roles:[], skills:[], companies:[]})
      return
    }
    const timer = setTimeout(async () => {
      try {
        const { getAutocomplete } = await import('../api')
        const data = await getAutocomplete(searchQuery)
        setSuggestions(data.suggestions || {roles:[], skills:[], companies:[]})
      } catch (e) {
        console.error(e)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const handleSearch = () => {
    setCurrentPage(1)
    fetchJobs(false, 1)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch()
  }

  const resetFilters = () => {
    setSearchQuery('')
    setLocationFilter('')
    setJobType('All')
    setCurrentPage(1)
    setTimeout(() => fetchJobs(false, 1), 0)
  }

  const loadMore = () => {
    if (hasMore) {
      fetchJobs(true, currentPage + 1)
    }
  }

  const handleApply = async (jobId, applyUrl, linkStatus) => {
    if (!applyUrl) return

    // Phase 8.55: Track the apply attempt
    try {
      const API_BASE = (await import('../api')).API_BASE
      fetch(`${API_BASE}/api/opportunities/${jobId}/track-apply?event_type=attempt`, { method: 'POST' })
    } catch (_) {}

    // Warn user if link quality is low (CAREER_BOARD = one extra click)
    if (linkStatus === 'CAREER_BOARD') {
      // Non-blocking toast via console (no modal redesign)
      console.info('[CareerLens] This link leads to a company careers board. You may need one extra click to find this specific role.')
    }

    window.open(applyUrl, '_blank', 'noopener,noreferrer')
  }

  const handleSave = async (opportunityId) => {
    if (savedIds.has(opportunityId)) return
    setSavingId(opportunityId)
    try {
      await createApplication({ opportunity_id: opportunityId, status: 'Saved' })
      setSavedIds(prev => new Set([...prev, opportunityId]))
    } catch (e) {
      console.error('Failed to save:', e)
    } finally {
      setSavingId(null)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now - date
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours} hours ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays === 1) return '1 day ago'
    if (diffDays < 30) return `${diffDays} days ago`
    return date.toLocaleDateString()
  }

  const getTrustColor = (score) => {
    if (score >= 90) return 'text-success font-bold'
    if (score >= 70) return 'text-warning font-bold'
    return 'text-error font-bold'
  }

  return (
    <div className="space-y-lg flex flex-col min-h-full">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-md animate-fade-in-up">
        <div>
          <h2 className="text-3xl font-semibold text-on-background">Opportunities Hub</h2>
          <p className="text-base text-on-surface-variant">Discover roles from official company career pages.</p>
        </div>
        <div className="flex items-center gap-sm bg-primary-container/10 px-md py-sm rounded-lg border border-primary/20">
          <span className="material-symbols-outlined text-primary" style={{fontVariationSettings: "'FILL' 1"}}>work</span>
          <span className="text-sm font-medium font-[Geist] text-primary">{total.toLocaleString()} Jobs Available</span>
        </div>
      </div>

      {/* Search & Filter Header */}
      <section className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm space-y-md animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-md">
          <div className="space-y-xs md:col-span-2 xl:col-span-1">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Search</label>
            <div className="relative z-20">
              <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline text-sm">search</span>
              <input type="text" value={searchQuery} 
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setShowSuggestions(true)
                }} 
                onKeyDown={handleKeyDown}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                className="w-full pl-xl pr-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none" 
                placeholder="Job title, company, skill..." />
                
              {showSuggestions && (suggestions.roles?.length > 0 || suggestions.skills?.length > 0) && (
                <div className="absolute top-full mt-1 w-full bg-white border border-outline-variant rounded-lg shadow-xl overflow-hidden z-50">
                  {suggestions.roles?.length > 0 && (
                    <>
                      <div className="px-md pt-sm pb-xs text-xs font-semibold text-on-surface-variant uppercase tracking-wider bg-surface-container-low">Roles</div>
                      {suggestions.roles.map((sug, i) => (
                        <div key={`r${i}`} className="px-md py-sm text-sm hover:bg-surface-container cursor-pointer text-on-background flex items-center gap-sm"
                          onClick={() => { setSearchQuery(sug); setShowSuggestions(false); setCurrentPage(1); setTimeout(() => fetchJobs(false, 1), 50) }}>
                          <span className="material-symbols-outlined text-primary text-sm">work</span>{sug}
                        </div>
                      ))}
                    </>
                  )}
                  {suggestions.skills?.length > 0 && (
                    <>
                      <div className="px-md pt-sm pb-xs text-xs font-semibold text-on-surface-variant uppercase tracking-wider bg-surface-container-low">Skills</div>
                      {suggestions.skills.map((sug, i) => (
                        <div key={`s${i}`} className="px-md py-sm text-sm hover:bg-surface-container cursor-pointer text-on-background flex items-center gap-sm"
                          onClick={() => { setSearchQuery(sug); setShowSuggestions(false); setCurrentPage(1); setTimeout(() => fetchJobs(false, 1), 50) }}>
                          <span className="material-symbols-outlined text-tertiary text-sm">code</span>{sug}
                        </div>
                      ))}
                    </>
                  )}
                  {suggestions.companies?.length > 0 && (
                    <>
                      <div className="px-md pt-sm pb-xs text-xs font-semibold text-on-surface-variant uppercase tracking-wider bg-surface-container-low">Companies</div>
                      {suggestions.companies.map((sug, i) => (
                        <div key={`c${i}`} className="px-md py-sm text-sm hover:bg-surface-container cursor-pointer text-on-background flex items-center gap-sm"
                          onClick={() => { setSearchQuery(sug); setShowSuggestions(false); setCurrentPage(1); setTimeout(() => fetchJobs(false, 1), 50) }}>
                          <span className="material-symbols-outlined text-secondary text-sm">business</span>{sug}
                        </div>
                      ))}
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Location</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline text-sm">location_on</span>
              <input type="text" value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)} onKeyDown={handleKeyDown}
                className="w-full pl-xl pr-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none" placeholder="City or Remote..." />
            </div>
          </div>
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Type</label>
            <select value={jobType} onChange={(e) => setJobType(e.target.value)}
              className="w-full px-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none appearance-none cursor-pointer">
              <option value="All">All Types</option>
              <option value="Full-time">Full-time</option>
              <option value="Part-time">Part-time</option>
              <option value="Internship">Internship</option>
              <option value="Contract">Contract</option>
            </select>
          </div>
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Sorted By</label>
            <div className="w-full px-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg text-sm text-on-surface-variant flex items-center gap-xs">
              <span className="material-symbols-outlined text-primary text-sm">auto_awesome</span>
              India Relevance
            </div>
          </div>
        </div>
        <div className="flex flex-col-reverse md:flex-row justify-between items-stretch md:items-center pt-md border-t border-outline-variant/30 gap-sm">
          <Button variant="ghost" className="w-full md:w-auto text-on-surface-variant hover:text-primary" onClick={resetFilters}>Clear All</Button>
          <Button
            variant="primary"
            onClick={handleSearch}
            isLoading={loading}
            className="w-full md:w-auto min-w-[140px]"
          >
            Search Results
          </Button>
        </div>
      </section>

      {/* Phase 8.65: Search Confidence Banner */}
      {!loading && searchMeta && searchQuery && (
        <div className="flex items-center gap-md bg-primary-container/10 border border-primary/20 px-lg py-sm rounded-xl animate-fade-in-up">
          <span className="material-symbols-outlined text-primary text-lg">manage_search</span>
          <div className="flex-1">
            <span className="text-sm font-medium text-primary">Searching for &ldquo;{searchMeta.query}&rdquo;</span>
            <span className="ml-md text-xs text-on-surface-variant">
              {searchMeta.exact_matches > 0 && <span className="text-success font-semibold">{searchMeta.exact_matches} exact matches</span>}
              {searchMeta.related_matches > 0 && <span className="ml-sm text-on-surface-variant">· {searchMeta.related_matches} related</span>}
            </span>
          </div>
          {searchMeta.intent_type === 'skill' && (
            <span className="text-xs bg-tertiary/10 text-tertiary border border-tertiary/20 px-sm py-xs rounded-full font-medium">Skill Search</span>
          )}
        </div>
      )}

      {/* Error State */}
      {error && (
        <Alert 
          type="error" 
          message={error} 
          action={
            <Button variant="ghost" size="sm" onClick={() => fetchJobs()} className="font-bold underline">
              Retry
            </Button>
          } 
        />
      )}

      {/* Loading State */}
      {loading && !error && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-lg flex-1">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-white p-lg rounded-xl border border-outline-variant animate-pulse">
              <div className="flex gap-md">
                <div className="w-14 h-14 rounded-lg bg-surface-container-high"></div>
                <div className="flex-1 space-y-sm">
                  <div className="h-5 bg-surface-container-high rounded w-3/4"></div>
                  <div className="h-4 bg-surface-container rounded w-1/2"></div>
                  <div className="flex gap-sm mt-sm">
                    <div className="h-6 bg-surface-container rounded w-24"></div>
                    <div className="h-6 bg-surface-container rounded w-20"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && jobs.length === 0 && (
        <EmptyState 
          icon="search_off"
          title="No results found"
          description="We couldn't find any opportunities matching your current filters. Try adjusting your search criteria."
          actionLabel="Clear All Filters"
          onAction={resetFilters}
          className="flex-1 animate-fade-in-up mt-lg border-none"
        />
      )}

      {/* Job Cards */}
      {!loading && !error && jobs.length > 0 && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-lg stagger-children flex-1 pb-xl">
          {jobs.map((job) => (
            <JobCard 
              key={job.id} 
              job={job} 
              navigate={navigate} 
              savedIds={savedIds} 
              savingId={savingId} 
              handleSave={handleSave} 
              handleApply={handleApply} 
              getTrustColor={getTrustColor} 
              formatDate={formatDate} 
            />
          ))}

          {/* Load More */}
          {hasMore && (
            <div className="col-span-full flex justify-center pt-xl">
              <Button
                variant="secondary"
                onClick={loadMore}
                isLoading={loadingMore}
                className="rounded-full group"
              >
                {!loadingMore && (
                  <>
                    <span className="mr-2">Load More Opportunities</span>
                    <span className="material-symbols-outlined group-hover:translate-y-1 transition-transform">keyboard_arrow_down</span>
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
