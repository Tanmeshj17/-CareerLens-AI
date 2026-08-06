import { useState, useEffect, useContext } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getOpportunity, createApplication, getOpportunities } from '../api'
import { AuthContext } from '../App'

export default function JobDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useContext(AuthContext)

  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [relatedJobs, setRelatedJobs] = useState([])
  const [matchData, setMatchData] = useState(null)

  useEffect(() => {
    const fetchJob = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getOpportunity(id)
        setJob(data)
        
        // Fetch personalized match data
        if (user) {
          try {
            const { getJobMatch } = await import('../api')
            const mData = await getJobMatch(id)
            setMatchData(mData)
          } catch (e) { console.error("Match engine error:", e) }
        }

        // Fetch related jobs from the same company
        try {
          const related = await getOpportunities({ search: data.company, limit: 4 })
          setRelatedJobs((related.opportunities || []).filter(j => j.id !== data.id).slice(0, 3))
        } catch { /* non-critical */ }
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    fetchJob()
  }, [id, user])

  const handleApply = async () => {
    if (!job?.apply_url) return
    // Phase 8.55: Track apply attempt
    try {
      const { API_BASE } = await import('../api')
      fetch(`${API_BASE}/api/opportunities/${job.id}/track-apply?event_type=attempt`, { method: 'POST' })
    } catch (_) {}
    window.open(job.apply_url, '_blank', 'noopener,noreferrer')
  }

  const handleSave = async () => {
    if (saved) return
    setSaving(true)
    try {
      await createApplication({ opportunity_id: job.id, status: 'Saved' })
      setSaved(true)
    } catch (e) {
      console.error('Failed to save:', e)
    } finally {
      setSaving(false)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  if (loading) {
    return (
      <div className="space-y-lg animate-fade-in-up">
        <div className="animate-pulse space-y-lg">
          <div className="h-8 bg-surface-container-high rounded w-1/3"></div>
          <div className="bg-white p-xl rounded-xl border border-outline-variant space-y-md">
            <div className="h-8 bg-surface-container-high rounded w-2/3"></div>
            <div className="h-5 bg-surface-container rounded w-1/3"></div>
            <div className="h-40 bg-surface-container rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-3xl text-center space-y-md animate-fade-in-up">
        <span className="material-symbols-outlined text-5xl text-error">error</span>
        <h3 className="text-2xl font-bold text-on-background">Failed to load job</h3>
        <p className="text-on-surface-variant">{error}</p>
        <button onClick={() => navigate(-1)} className="bg-primary text-on-primary px-xl py-sm rounded-lg text-sm font-medium cursor-pointer">Go Back</button>
      </div>
    )
  }

  if (!job) return null

  return (
    <div className="space-y-lg animate-fade-in-up max-w-4xl">
      {/* Back Button */}
      <button onClick={() => navigate('/app/opportunities')} className="flex items-center gap-xs text-on-surface-variant hover:text-primary transition-colors cursor-pointer text-sm">
        <span className="material-symbols-outlined text-[18px]">arrow_back</span> Back to Opportunities
      </button>

      {/* Main Card */}
      <div className="bg-white p-xl rounded-xl border border-outline-variant shadow-sm space-y-lg">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between gap-lg">
          <div className="flex gap-lg">
            <div className="w-16 h-16 rounded-xl bg-surface-container-high flex items-center justify-center border border-outline-variant shrink-0">
              <span className="text-2xl font-bold text-primary">{(job.company || '?')[0]}</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-on-background">{job.title}</h1>
              <p className="text-lg text-on-surface-variant font-medium mt-1">{job.company}</p>
              <div className="flex flex-wrap gap-sm mt-md">
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
                {job.ats_type && (
                  <span className="flex items-center gap-xs text-xs font-medium font-[Geist] bg-primary/10 text-primary px-sm py-xs rounded">
                    <span className="material-symbols-outlined text-[14px]">verified</span> {job.ats_type}
                  </span>
                )}
              </div>
            </div>
          </div>
          {/* Action Buttons */}
          <div className="flex gap-sm shrink-0 md:flex-col">
            {/* Phase 11.3.8: Disable apply button for CLOSED, EXPIRED, or INVALID jobs */}
            {job.status === 'CLOSED' || job.status === 'INVALID' || job.lifecycle_status === 'CLOSED' || job.lifecycle_status === 'EXPIRED' || job.lifecycle_status === 'INVALID_LINK' || job.apply_url_status === 'INVALID_LINK' ? (
              <button disabled
                className="px-xl py-sm bg-surface-container text-on-surface-variant rounded-lg text-sm font-bold font-[Geist] cursor-not-allowed flex items-center gap-2 opacity-60">
                <span className="material-symbols-outlined text-[16px]">block</span>
                {job.lifecycle_status === 'EXPIRED' ? 'Expired' : (job.status === 'CLOSED' || job.lifecycle_status === 'CLOSED' ? 'Position Closed' : 'Link Invalid')}
              </button>
            ) : job.apply_url ? (
              <button onClick={handleApply}
                className="px-xl py-sm bg-primary text-on-primary rounded-lg text-sm font-bold font-[Geist] hover:bg-primary-container transition-all flex items-center gap-2 cursor-pointer shadow-lg shadow-primary/20">
                Apply Now <span className="material-symbols-outlined text-[16px]">open_in_new</span>
              </button>
            ) : null}
            <button onClick={handleSave} disabled={saved || saving}
              className={`px-xl py-sm rounded-lg text-sm font-medium font-[Geist] transition-all flex items-center gap-2 cursor-pointer border ${saved ? 'bg-primary/5 border-primary/30 text-primary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container'}`}>
              <span className="material-symbols-outlined text-[16px]" style={saved ? {fontVariationSettings: "'FILL' 1"} : {}}>
                {saving ? 'progress_activity' : 'bookmark'}
              </span>
              {saved ? 'Saved' : 'Save Job'}
            </button>
          </div>
        </div>

        {/* Match Data (Phase 8.5) */}
        {matchData && (
          <div className="bg-primary/5 p-lg rounded-xl border border-primary/20 space-y-md">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-on-surface">
                <span className="text-primary">{matchData.match_score}% Match</span> • {matchData.probability}
              </h3>
            </div>
            
            {matchData.explanation && matchData.explanation.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-on-surface mb-xs">Recommended because:</p>
                <ul className="space-y-1">
                  {matchData.explanation.map((reason, i) => (
                    <li key={i} className="text-sm text-on-surface-variant flex items-center gap-xs">
                      <span className="material-symbols-outlined text-success text-[16px]">check_circle</span>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {matchData.missing_skills && matchData.missing_skills.length > 0 && (
              <div className="mt-md pt-md border-t border-primary/10">
                <p className="text-sm font-semibold text-on-surface mb-xs text-error">Missing Skills (Consider Learning):</p>
                <div className="flex flex-wrap gap-2">
                  {matchData.missing_skills.map((skill, i) => (
                    <span key={i} className="text-xs px-2 py-1 rounded bg-error/10 text-error font-medium border border-error/20">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Meta Info — Phase 8.6 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-md p-md bg-surface-container-lowest rounded-lg border border-outline-variant/50">
          <div>
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider">Posted</p>
            <p className="text-sm font-medium text-on-surface">{formatDate(job.posted_date)}</p>
          </div>
          <div>
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider">Confidence</p>
            <p className={`text-sm font-bold ${(job.confidence_score||0) >= 70 ? 'text-success' : (job.confidence_score||0) >= 40 ? 'text-warning' : 'text-error'}`}>{job.confidence_score ?? 0}/100</p>
          </div>
          <div>
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider">Completeness</p>
            <p className={`text-sm font-bold ${(job.completeness_score||0) >= 70 ? 'text-success' : (job.completeness_score||0) >= 40 ? 'text-warning' : 'text-error'}`}>{job.completeness_score ?? 0}/100</p>
          </div>
          <div>
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider">Status</p>
            <p className={`text-sm font-bold ${
              job.status === 'CLOSED' || job.status === 'INVALID' ? 'text-error' :
              job.status === 'STALE' ? 'text-warning' :
              job.status === 'ARCHIVED' ? 'text-on-surface-variant' :
              job.lifecycle_status === 'ACTIVE' || job.lifecycle_status === 'NEW' ? 'text-success' :
              job.lifecycle_status === 'STALE' ? 'text-warning' : 'text-error'
            }`}>{job.status || job.lifecycle_status || 'ACTIVE'}</p>
          </div>
        </div>

        {/* Phase 8.6: Salary Intelligence */}
        {(job.salary_min || job.salary_max || job.salary_range) && (
          <div className="bg-surface-container-lowest rounded-lg border border-outline-variant/50 p-md">
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider mb-sm">Salary Intelligence</p>
            <div className="flex flex-wrap gap-md items-center">
              {job.salary_min && job.salary_max ? (
                <span className="text-xl font-black text-on-surface">
                  {job.salary_currency === 'INR' ? '₹' : job.salary_currency === 'USD' ? '$' : job.salary_currency}
                  {(job.salary_min / 100000).toFixed(1)}L
                  &nbsp;–&nbsp;
                  {(job.salary_max / 100000).toFixed(1)}L
                  <span className="text-xs font-medium text-on-surface-variant ml-1">{job.salary_period || ''}</span>
                </span>
              ) : (
                <span className="text-base font-semibold text-on-surface-variant">{job.salary_range}</span>
              )}
              <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary font-medium">
                {job.salary_currency || 'INR'}
              </span>
            </div>
          </div>
        )}

        {/* Link Quality */}
        <div className="grid grid-cols-2 gap-md p-md bg-surface-container-lowest rounded-lg border border-outline-variant/50">
          <div>
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider">Source</p>
            <p className="text-sm font-medium text-on-surface">{job.link_classification || job.primary_source || 'Official'}</p>
          </div>
          <div>
            <p className="text-[11px] uppercase font-bold text-on-surface-variant tracking-wider">Link Quality</p>
            <p className={`text-sm font-bold ${
              (job.link_quality_score || 0) >= 95 ? 'text-success' :
              (job.link_quality_score || 0) >= 80 ? 'text-primary' :
              (job.link_quality_score || 0) >= 45 ? 'text-warning' : 'text-error'
            }`}>{job.link_quality_score ?? 25}/100 · {job.apply_url_status || 'UNKNOWN'}</p>
          </div>
        </div>

        {/* Skills */}
        {job.required_skills && (
          <div>
            <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider mb-sm">Required Skills</h3>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.split(',').map((skill, i) => (
                <span key={i} className="text-xs px-3 py-1.5 rounded-full bg-secondary-container/50 text-on-secondary-container font-medium border border-secondary-container">
                  {skill.trim()}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        {job.description && (
          <div>
            <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider mb-sm">Job Description</h3>
            <div className="text-sm text-on-surface-variant leading-relaxed whitespace-pre-line">
              {job.description}
            </div>
          </div>
        )}

        {/* Apply CTA - Phase 11.3.8: skip entirely for CLOSED/INVALID */}
        {job.apply_url && job.status !== 'CLOSED' && job.status !== 'INVALID' && (
          <div className="pt-lg border-t border-outline-variant/30 flex flex-col md:flex-row items-center justify-between gap-md">
            <p className="text-sm text-on-surface-variant">
              <span className="material-symbols-outlined text-[14px] align-middle mr-1">info</span>
              You will be redirected to the official company career page to submit your application.
            </p>
            <button onClick={handleApply}
              className="px-xl py-md bg-primary text-on-primary rounded-lg font-bold font-[Geist] hover:bg-primary-container transition-all flex items-center gap-2 cursor-pointer shadow-lg shadow-primary/20">
              Apply on {job.company} <span className="material-symbols-outlined text-[18px]">open_in_new</span>
            </button>
          </div>
        )}
      </div>

      {/* Related Jobs */}
      {relatedJobs.length > 0 && (
        <div className="space-y-md">
          <h3 className="text-lg font-bold text-on-background">More from {job.company}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
            {relatedJobs.map(rj => (
              <div key={rj.id} onClick={() => navigate(`/app/opportunities/${rj.id}`)}
                className="bg-white p-md rounded-xl border border-outline-variant hover:border-primary/50 hover:shadow-lg transition-all cursor-pointer">
                <h4 className="font-bold text-on-surface text-sm">{rj.title}</h4>
                <p className="text-xs text-on-surface-variant mt-1">{rj.location}</p>
                {rj.salary_range && <p className="text-xs text-primary font-medium mt-1">{rj.salary_range}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
