import { Link, useNavigate } from 'react-router-dom'
import { useContext, useState, useEffect } from 'react'
import { AuthContext } from '../App'
import { 
  getDashboardStats, 
  getInsightsCompanies, 
  getInsightsLocations, 
  getInsightsSkills, 
  getInsightsSalary, 
  getFastGrowingCareers,
  getReadiness,
  getProfileCompleteness
} from '../api'
import { Skeleton } from '../components/ui/Skeleton'
import { EmptyState } from '../components/ui/EmptyState'

export default function Dashboard() {
  const { user } = useContext(AuthContext)
  const navigate = useNavigate()
  
  // Initialize with cached snapshot for 0ms instant paint
  const [dbStats, setDbStats] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_stats')) || null } catch { return null }
  })
  const [topCompanies, setTopCompanies] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_companies')) || [] } catch { return [] }
  })
  const [topLocations, setTopLocations] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_locations')) || [] } catch { return [] }
  })
  const [topSkills, setTopSkills] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_skills')) || [] } catch { return [] }
  })
  const [salaryTrends, setSalaryTrends] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_salary')) || [] } catch { return [] }
  })
  const [fastGrowing, setFastGrowing] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_fast_growing')) || [] } catch { return [] }
  })
  const [readinessData, setReadinessData] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_readiness')) || [] } catch { return [] }
  })
  const [completenessData, setCompletenessData] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cl_completeness')) || null } catch { return null }
  })
  
  const [loadingStats, setLoadingStats] = useState(!dbStats)
  const [loadingInsights, setLoadingInsights] = useState(!topCompanies.length)

  useEffect(() => {
    let isMounted = true

    // Progressive independent data fetching (non-blocking)
    getDashboardStats()
      .then(data => {
        if (!isMounted) return
        setDbStats(data)
        setLoadingStats(false)
        try { sessionStorage.setItem('cl_stats', JSON.stringify(data)) } catch {}
      })
      .catch(() => { if (isMounted) setLoadingStats(false) })

    getInsightsCompanies()
      .then(data => {
        if (!isMounted) return
        setTopCompanies(data || [])
        try { sessionStorage.setItem('cl_companies', JSON.stringify(data)) } catch {}
      })
      .catch(() => {})

    getInsightsLocations()
      .then(data => {
        if (!isMounted) return
        setTopLocations(data || [])
        try { sessionStorage.setItem('cl_locations', JSON.stringify(data)) } catch {}
      })
      .catch(() => {})

    getInsightsSkills()
      .then(data => {
        if (!isMounted) return
        setTopSkills(data || [])
        setLoadingInsights(false)
        try { sessionStorage.setItem('cl_skills', JSON.stringify(data)) } catch {}
      })
      .catch(() => { if (isMounted) setLoadingInsights(false) })

    getInsightsSalary()
      .then(data => {
        if (!isMounted) return
        setSalaryTrends(data || [])
        try { sessionStorage.setItem('cl_salary', JSON.stringify(data)) } catch {}
      })
      .catch(() => {})

    getFastGrowingCareers()
      .then(data => {
        if (!isMounted) return
        setFastGrowing(data?.roles || [])
        try { sessionStorage.setItem('cl_fast_growing', JSON.stringify(data?.roles || [])) } catch {}
      })
      .catch(() => {})

    if (user) {
      getReadiness()
        .then(data => {
          if (!isMounted) return
          setReadinessData(data?.readiness_cards || [])
          try { sessionStorage.setItem('cl_readiness', JSON.stringify(data?.readiness_cards || [])) } catch {}
        })
        .catch(() => {})

      getProfileCompleteness()
        .then(data => {
          if (!isMounted) return
          setCompletenessData(data)
          try { sessionStorage.setItem('cl_completeness', JSON.stringify(data)) } catch {}
        })
        .catch(() => {})
    }

    return () => {
      isMounted = false
    }
  }, [user])

  // Mutually-exclusive opportunity categories — each record appears in exactly one bucket.
  // Priority: Internship > Apprenticeship > Graduate/Trainee > Fresher/Entry-Level
  //           > Hiring Challenge/Competition > Experienced/Professional
  const marketStats = [
    {
      title: 'Total Opportunities', val: dbStats?.total_opportunities,
      icon: 'travel_explore', trend: 'Live',
      colorBg: 'bg-primary-container/10', colorIcon: 'text-primary', colorTrend: 'text-success',
    },
    {
      title: 'Internships', val: dbStats?.internships,
      icon: 'local_library', trend: 'Exclusive',
      colorBg: 'bg-surface-container-highest/20', colorIcon: 'text-on-surface-variant', colorTrend: 'text-success',
    },
    {
      title: 'Fresher / Entry-Level', val: dbStats?.fresher_entry_level,
      icon: 'school', trend: 'Exclusive',
      colorBg: 'bg-secondary-container/10', colorIcon: 'text-secondary', colorTrend: 'text-success',
    },
    {
      title: 'Hiring Challenges', val: dbStats?.hiring_challenges,
      icon: 'emoji_events', trend: 'Compete & Get Hired',
      colorBg: 'bg-tertiary-container/10', colorIcon: 'text-tertiary', colorTrend: 'text-success',
    },
    {
      title: 'Experienced / Professional', val: dbStats?.experienced_professional,
      icon: 'work', trend: 'Mid & Senior',
      colorBg: 'bg-primary-container/10', colorIcon: 'text-primary', colorTrend: 'text-on-surface-variant',
    },
    {
      title: 'Applied Jobs', val: dbStats?.applied_opportunities ?? 0,
      icon: 'send', trend: 'Track',
      colorBg: 'bg-error-container/10', colorIcon: 'text-error', colorTrend: 'text-error',
    },
  ]

  const loading = loadingInsights && !topCompanies.length


  return (
    <div className="space-y-xl animate-fade-in-up">
      {/* Welcome Message */}
      <section className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-md">
        <div>
          <h2 className="text-3xl font-semibold text-on-surface">Welcome back, {user?.full_name?.split(' ')[0]}</h2>
          <p className="text-base text-on-surface-variant">Your career growth is 12% faster than last month. Here's what's happening today.</p>
        </div>
        <Link to="/app/tracker" className="hidden md:flex bg-primary text-on-primary px-lg py-sm rounded-lg text-sm font-medium font-[Geist] shadow-sm hover:brightness-110 transition-all items-center gap-sm">
          <span className="material-symbols-outlined text-[20px]">add</span>
          New Application
        </Link>
      </section>

      {/* Stats Row — 6 exclusive categories, sum = total_opportunities */}
      <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-md stagger-children">
        {marketStats.map((stat, i) => (
          <div key={i} className="bg-surface border border-outline-variant p-lg rounded-xl hover:shadow-lg transition-shadow duration-300">
            <div className="flex justify-between items-start mb-md">
              <div className={`p-sm ${stat.colorBg} rounded-lg`}>
                <span className={`material-symbols-outlined ${stat.colorIcon}`}>{stat.icon}</span>
              </div>
              <span className={`text-xs font-medium font-[Geist] ${stat.colorTrend}`}>{stat.trend}</span>
            </div>
            <p className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-wider">{stat.title}</p>
            <h3 className="text-2xl font-bold mt-xs">
              {stat.val !== undefined ? stat.val.toLocaleString() : <span className="inline-block w-16 h-7 bg-surface-variant animate-pulse rounded" />}
            </h3>
          </div>
        ))}
      </section>

      {/* AI Tools */}
      <section>
        <h4 className="text-sm font-bold font-[Geist] text-on-surface mb-md">AI POWERED TOOLS</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-md stagger-children">
          <Link to="/app/resume" className="glass-insight p-lg rounded-xl border border-primary/20 flex flex-col justify-between hover:border-primary transition-all group">
            <div>
              <div className="flex items-center gap-sm text-primary mb-sm">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>auto_awesome</span>
                <span className="text-xs font-bold font-[Geist] uppercase">Analyze Resume</span>
              </div>
              <p className="text-sm text-on-surface-variant mb-md">Get instant score and optimization tips for your next application.</p>
            </div>
            <div className="flex items-center text-primary text-sm font-bold font-[Geist]">
              Upload PDF <span className="material-symbols-outlined ml-xs transition-transform group-hover:translate-x-1">arrow_forward</span>
            </div>
          </Link>
          <Link to="/app/learn" className="glass-insight p-lg rounded-xl border border-primary/20 flex flex-col justify-between hover:border-primary transition-all group">
            <div>
              <div className="flex items-center gap-sm text-primary mb-sm">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>bolt</span>
                <span className="text-xs font-bold font-[Geist] uppercase">Learn New Skill</span>
              </div>
              <p className="text-sm text-on-surface-variant mb-md">AI-curated learning paths based on current job market demands.</p>
            </div>
            <div className="flex items-center text-primary text-sm font-bold font-[Geist]">
              View Path <span className="material-symbols-outlined ml-xs transition-transform group-hover:translate-x-1">arrow_forward</span>
            </div>
          </Link>
          <Link to="/app/careers" className="glass-insight p-lg rounded-xl border border-primary/20 flex flex-col justify-between hover:border-primary transition-all group">
            <div>
              <div className="flex items-center gap-sm text-primary mb-sm">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>map</span>
                <span className="text-xs font-bold font-[Geist] uppercase">Explore Careers</span>
              </div>
              <p className="text-sm text-on-surface-variant mb-md">Simulate career moves and see potential salary growth.</p>
            </div>
            <div className="flex items-center text-primary text-sm font-bold font-[Geist]">
              Start Exploration <span className="material-symbols-outlined ml-xs transition-transform group-hover:translate-x-1">arrow_forward</span>
            </div>
          </Link>
        </div>
      </section>

      {/* Career Intelligence Engine Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-xl">
        <div className="lg:col-span-2 space-y-xl">
          {/* Phase 8.5: Career Readiness */}
          {user && (
            <div className="bg-surface border border-outline-variant rounded-xl p-lg">
              <h3 className="text-2xl font-bold mb-lg">Career Readiness</h3>
              
              {(!readinessData || readinessData.length === 0) ? (
                <EmptyState
                  icon="person_search"
                  title="No Readiness Data Yet"
                  description="Complete your Career Profile and upload a Resume to get your readiness score."
                  actionLabel="Go to Profile"
                  onAction={() => navigate('/app/profile')}
                  className="py-xl"
                />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
                  {readinessData.map((item, i) => (
                    <div key={i} className="p-md border border-outline-variant rounded-lg bg-surface-container-lowest">
                      <h4 className="font-bold text-lg mb-xs">{item.target_role}</h4>
                      <div className="flex items-center justify-between mb-sm">
                        <span className="text-sm font-medium text-on-surface-variant">Readiness Score</span>
                        <span className={`text-sm font-bold ${item.readiness_score >= 80 ? 'text-success' : item.readiness_score >= 50 ? 'text-warning' : 'text-error'}`}>{item.readiness_score}%</span>
                      </div>
                      {/* Progress Bar */}
                      <div className="w-full bg-surface-variant rounded-full h-2 mb-md">
                        <div className={`h-2 rounded-full ${item.readiness_score >= 80 ? 'bg-success' : item.readiness_score >= 50 ? 'bg-warning' : 'bg-error'}`} style={{ width: `${item.readiness_score}%` }}></div>
                      </div>
                      
                      {/* Component Scores */}
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-xs mb-md border-t border-outline-variant/50 pt-sm mt-sm">
                        <div className="text-center">
                          <div className="text-[10px] uppercase text-on-surface-variant mb-0.5">Skills</div>
                          <div className="text-sm font-bold text-primary">{item.components?.skill_coverage || 0}%</div>
                        </div>
                        <div className="text-center border-l border-r border-outline-variant/30">
                          <div className="text-[10px] uppercase text-on-surface-variant mb-0.5">Resume</div>
                          <div className="text-sm font-bold text-secondary">{item.components?.resume_score || 0}%</div>
                        </div>
                        <div className="text-center">
                          <div className="text-[10px] uppercase text-on-surface-variant mb-0.5">Experience</div>
                          <div className="text-sm font-bold text-success">{item.components?.experience_score || 0}%</div>
                        </div>
                      </div>

                      {item.recommended_skills && item.recommended_skills.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-on-surface-variant mb-1">Recommended Skills</p>
                          <div className="flex flex-wrap gap-1">
                            {item.recommended_skills.map((skill, j) => (
                              <span key={j} className="text-[10px] px-2 py-0.5 rounded bg-secondary-container/30 text-on-secondary-container">{skill}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="bg-surface border border-outline-variant rounded-xl p-lg">
            <h3 className="text-2xl font-bold mb-lg">Fast Growing Careers</h3>
            {loading ? (
              <div className="space-y-sm">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            ) : (
              <div className="space-y-sm">
                {fastGrowing.length === 0 ? (
                  <p className="text-sm text-on-surface-variant">No roles with sufficient posting data yet.</p>
                ) : fastGrowing.map((item, i) => (
                  <div key={i} className="flex justify-between items-center p-md border border-outline-variant rounded-lg">
                    <div>
                      <span className="font-bold">{item.title}</span>
                      <p className="text-xs text-on-surface-variant">{item.total_postings} postings (last 90 days)</p>
                    </div>
                    <span className={`text-xs font-bold px-2 py-1 rounded ${
                      item.growth_signal === 'Fast Growing' ? 'bg-success/10 text-success' :
                      item.growth_signal === 'Growing' ? 'bg-secondary/10 text-secondary' :
                      'bg-surface-variant text-on-surface-variant'
                    }`}>{item.growth_signal}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-xl">
            <div className="bg-surface border border-outline-variant rounded-xl p-lg">
              <h3 className="text-xl font-bold mb-md">Top Hiring Companies</h3>
              {loading ? (
                <div className="space-y-sm">
                  {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-5 w-full" />)}
                </div>
              ) : (
                <ul className="space-y-xs text-sm">
                  {topCompanies.slice(0, 5).map((c, i) => <li key={i} className="flex justify-between"><span>{c.name}</span> <span className="font-medium">{c.count}</span></li>)}
                </ul>
              )}
            </div>
            
            <div className="bg-surface border border-outline-variant rounded-xl p-lg">
              <h3 className="text-xl font-bold mb-md">Top Hiring Cities</h3>
              {loading ? (
                <div className="space-y-sm">
                  {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-5 w-full" />)}
                </div>
              ) : (
                <ul className="space-y-xs text-sm">
                  {topLocations.slice(0, 5).map((l, i) => <li key={i} className="flex justify-between"><span>{l.name}</span> <span className="font-medium">{l.count}</span></li>)}
                </ul>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-xl">
          {/* Phase 8.5: Profile Completeness */}
          {user && completenessData && (
            <div className="bg-primary-container/10 border border-primary/20 rounded-xl p-lg">
              <h3 className="text-xl font-bold mb-md">Profile Completeness</h3>
              <div className="flex items-center justify-between mb-sm">
                <span className="text-sm font-medium text-on-surface">Overall Score</span>
                <span className="text-sm font-bold text-primary">{completenessData.completeness_score}%</span>
              </div>
              <div className="w-full bg-surface-variant rounded-full h-2 mb-md">
                <div className="bg-primary h-2 rounded-full transition-all duration-1000" style={{ width: `${completenessData.completeness_score}%` }}></div>
              </div>
              {completenessData.missing_items && completenessData.missing_items.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-on-surface-variant mb-xs uppercase tracking-wider">Next Steps</p>
                  <ul className="space-y-1">
                    {completenessData.missing_items.slice(0,3).map((item, i) => (
                      <li key={i} className="text-sm text-on-surface flex items-center gap-xs">
                        <span className="material-symbols-outlined text-primary text-[14px]">arrow_right</span> {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="bg-surface border border-outline-variant rounded-xl p-lg">
            <h3 className="text-xl font-bold mb-md">Top Skills in Demand</h3>
            {loading ? (
              <div className="flex flex-wrap gap-sm">
                {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-6 w-20 rounded-full" />)}
              </div>
            ) : (
              <div className="flex flex-wrap gap-sm">
                {topSkills.slice(0, 10).map((s, i) => (
                  <span key={i} className="bg-primary/10 text-primary px-sm py-xs rounded text-xs font-medium">
                    {s.name} ({s.count})
                  </span>
                ))}
              </div>
            )}
          </div>
          
          <div className="bg-surface border border-outline-variant rounded-xl p-lg">
            <h3 className="text-xl font-bold mb-md">Salary Trends</h3>
            {loading ? (
              <div className="space-y-sm">
                {[1,2,3,4].map(i => <Skeleton key={i} className="h-8 w-full" />)}
              </div>
            ) : (
              <ul className="space-y-sm text-sm">
                {salaryTrends.map((s, i) => (
                  <li key={i} className="flex justify-between items-center p-sm bg-surface-container rounded">
                    <span>{s.range}</span> <span className="font-bold">{s.count}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>

      {/* FAB search */}
      <Link to="/app/opportunities" className="fixed bottom-lg right-lg w-14 h-14 bg-primary text-on-primary rounded-full shadow-2xl flex items-center justify-center hover:scale-105 transition-transform z-50">
        <span className="material-symbols-outlined text-[32px]">search</span>
      </Link>
    </div>
  )
}
