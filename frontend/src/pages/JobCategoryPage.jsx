import React, { useState, useEffect } from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import { getCategorySeoData } from '../api'
import CareerLensLogo from '../components/CareerLensLogo'
import Footer from '../components/Footer'

export default function JobCategoryPage() {
  const params = useParams()
  const location = useLocation()

  // Determine categoryType and slug from URL path or params
  const categoryType = params.categoryType || (
    location.pathname.includes('/jobs/location/') ? 'location' :
    location.pathname.includes('/jobs/company/') ? 'company' : 'role'
  )
  const currentSlug = params.slug || 'software-engineer'

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterType, setFilterType] = useState('All')

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    getCategorySeoData(categoryType, currentSlug)
      .then((res) => {
        if (!isMounted) return
        setData(res)
        setLoading(false)

        // Dynamically update document title & meta tags
        if (res?.meta_title) {
          document.title = res.meta_title
        }
        const metaDesc = document.querySelector('meta[name="description"]')
        if (metaDesc && res?.meta_description) {
          metaDesc.setAttribute('content', res.meta_description)
        }

        // Inject / Update Canonical tag
        let canonicalTag = document.querySelector('link[rel="canonical"]')
        if (!canonicalTag) {
          canonicalTag = document.createElement('link')
          canonicalTag.setAttribute('rel', 'canonical')
          document.head.appendChild(canonicalTag)
        }
        if (res?.canonical_url) {
          canonicalTag.setAttribute('href', res.canonical_url)
        }

        // Inject / Update Schema.org ItemList JSON-LD
        let schemaScript = document.getElementById('seo-itemlist-schema')
        if (!schemaScript) {
          schemaScript = document.createElement('script')
          schemaScript.id = 'seo-itemlist-schema'
          schemaScript.type = 'application/ld+json'
          document.head.appendChild(schemaScript)
        }
        if (res?.schema_json_ld) {
          schemaScript.textContent = JSON.stringify(res.schema_json_ld)
        }
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Category not found or below minimum active threshold.')
        setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [categoryType, currentSlug])

  // Filter opportunities client-side for immediate responsive UX
  const filteredOpportunities = React.useMemo(() => {
    if (!data?.opportunities) return []
    if (filterType === 'All') return data.opportunities
    return data.opportunities.filter((opp) =>
      opp.job_type?.toLowerCase().includes(filterType.toLowerCase())
    )
  }, [data, filterType])

  return (
    <div className="min-h-screen bg-[#f8faff] text-[#0f172a] font-['Plus_Jakarta_Sans',sans-serif] flex flex-col">
      {/* ── Top Header Navigation ──────────────────────────────────── */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <CareerLensLogo size="sm" showTagline={false} />
          </Link>
          <div className="flex items-center gap-3">
            <Link
              to="/app/opportunities"
              className="text-xs sm:text-sm font-semibold text-slate-600 hover:text-[#0050cb] transition-colors"
            >
              All Jobs
            </Link>
            <Link
              to="/app/resume"
              className="text-xs sm:text-sm font-semibold text-slate-600 hover:text-[#0050cb] transition-colors hidden sm:inline-block"
            >
              Resume ATS Scanner
            </Link>
            <Link
              to="/login"
              className="px-4 py-2 text-xs sm:text-sm font-bold text-white bg-[#0050cb] hover:bg-[#003fa0] rounded-xl shadow-xs transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* ── Main Content Area ───────────────────────────────────────── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {loading ? (
          <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
            <div className="w-12 h-12 border-4 border-[#0050cb] border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-slate-500 font-medium font-[Geist]">
              Loading active {currentSlug.replace(/-/g, ' ')} opportunities...
            </p>
          </div>
        ) : error ? (
          <div className="bg-white rounded-3xl p-8 sm:p-12 text-center max-w-xl mx-auto border border-slate-200 shadow-sm space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-3xl">search_off</span>
            </div>
            <h2 className="text-xl font-bold text-slate-800">No Active Category Found</h2>
            <p className="text-xs sm:text-sm text-slate-500 leading-relaxed font-[Geist]">
              This category does not currently have enough active job openings to meet our indexation threshold.
            </p>
            <div className="pt-2">
              <Link
                to="/app/opportunities"
                className="inline-flex items-center gap-2 px-6 py-3 bg-[#0050cb] text-white rounded-xl text-xs font-bold shadow-md hover:bg-[#003fa0] transition-all"
              >
                Browse All Live Jobs
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-8 animate-fade-in">
            {/* Breadcrumb Navigation */}
            <nav className="flex items-center gap-2 text-xs text-slate-400 font-medium font-[Geist]">
              <Link to="/" className="hover:text-slate-600 transition-colors">Home</Link>
              <span>/</span>
              <Link to="/app/opportunities" className="hover:text-slate-600 transition-colors">Jobs</Link>
              <span>/</span>
              <span className="capitalize">{categoryType}</span>
              <span>/</span>
              <span className="text-slate-700 font-semibold">{data.role_name}</span>
            </nav>

            {/* ── Page Hero Header ───────────────────────────────────── */}
            <section className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200/80 shadow-xs relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-blue-100/50 via-indigo-50/30 to-transparent rounded-full blur-3xl pointer-events-none" />

              <div className="relative max-w-3xl space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-[#0050cb] text-[11px] font-bold tracking-wide uppercase font-[Geist]">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  Live Hiring Demand
                </div>

                <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
                  {data.h1}
                </h1>

                <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-[Geist]">
                  {data.meta_description}
                </p>

                {/* Key Insights Bar */}
                <div className="pt-4 flex flex-wrap items-center gap-4 sm:gap-8 text-xs text-slate-500 font-[Geist] border-t border-slate-100">
                  <div>
                    <span className="text-slate-400">Total Active Postings: </span>
                    <strong className="text-slate-800 text-sm font-bold">
                      {data.total_active_listings?.toLocaleString()}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-400">Top Employers: </span>
                    <strong className="text-slate-800 text-sm font-bold">
                      {data.top_companies?.length ? `${data.top_companies.length}+ Companies` : 'Multiple'}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-400">Data Freshness: </span>
                    <span className="text-emerald-700 font-semibold">Updated Today</span>
                  </div>
                </div>
              </div>
            </section>

            {/* ── Content Grid: Filters + Listings + Sidebar ──────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left Column: Job Listings */}
              <div className="lg:col-span-8 space-y-4">
                {/* Filter Pills */}
                <div className="flex items-center justify-between gap-4 pb-2 border-b border-slate-200/60">
                  <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
                    {['All', 'Full-time', 'Internship'].map((type) => (
                      <button
                        key={type}
                        onClick={() => setFilterType(type)}
                        className={`px-4 py-1.5 rounded-full text-xs font-bold font-[Geist] transition-all cursor-pointer ${
                          filterType === type
                            ? 'bg-[#0050cb] text-white shadow-xs'
                            : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                        }`}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                  <span className="text-xs text-slate-400 font-medium shrink-0 font-[Geist]">
                    Showing {filteredOpportunities.length} opportunities
                  </span>
                </div>

                {/* Job Cards List */}
                <div className="space-y-3">
                  {filteredOpportunities.map((opp) => (
                    <article
                      key={opp.id}
                      className="bg-white rounded-2xl p-5 border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all duration-200 space-y-3"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <h2 className="text-base sm:text-lg font-bold text-slate-800 hover:text-[#0050cb] transition-colors leading-snug">
                            {opp.title}
                          </h2>
                          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 font-medium font-[Geist]">
                            <span className="font-bold text-slate-700">{opp.company}</span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">location_on</span>
                              {opp.location || 'Remote'}
                            </span>
                            <span>•</span>
                            <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[11px] font-semibold">
                              {opp.job_type || 'Full-time'}
                            </span>
                          </div>
                        </div>

                        {opp.trust_score && opp.trust_score >= 80 && (
                          <div
                            className="shrink-0 px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-bold font-[Geist] flex items-center gap-1"
                            title="Opportunity Score"
                          >
                            <span className="material-symbols-outlined text-[14px]">verified</span>
                            <span>{opp.trust_score}% Trust</span>
                          </div>
                        )}
                      </div>

                      {opp.required_skills && (
                        <div className="flex flex-wrap items-center gap-1.5 pt-1">
                          {opp.required_skills.split(',').slice(0, 5).map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 rounded-md bg-blue-50/70 text-[#0050cb] text-[11px] font-semibold font-[Geist]"
                            >
                              {skill.trim()}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="pt-2 flex items-center justify-between border-t border-slate-100">
                        <span className="text-[11px] text-slate-400 font-[Geist]">
                          {opp.posted_date ? `Posted ${new Date(opp.posted_date).toLocaleDateString()}` : 'Active Opening'}
                        </span>

                        <a
                          href={opp.apply_url || `/app/opportunities?search=${encodeURIComponent(opp.company)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-[#0050cb] text-white rounded-xl text-xs font-bold hover:bg-[#003fa0] transition-colors shadow-xs"
                        >
                          <span>Apply Directly</span>
                          <span className="material-symbols-outlined text-xs">open_in_new</span>
                        </a>
                      </div>
                    </article>
                  ))}
                </div>

                {/* Bottom Pagination / View All CTA */}
                <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-100 text-center space-y-2 mt-6">
                  <h3 className="text-sm font-bold text-slate-800">
                    Want to see all {data.total_active_listings?.toLocaleString()} {data.role_name} openings?
                  </h3>
                  <p className="text-xs text-slate-500 font-[Geist]">
                    Use the interactive Opportunities Hub to filter by salary, experience level, and exact tech stack.
                  </p>
                  <div className="pt-2">
                    <Link
                      to={`/app/opportunities?search=${encodeURIComponent(data.role_name)}`}
                      className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#0050cb] text-white rounded-xl text-xs font-bold shadow-sm hover:bg-[#003fa0] transition-all"
                    >
                      Open Full Search Filters
                      <span className="material-symbols-outlined text-xs">arrow_forward</span>
                    </Link>
                  </div>
                </div>
              </div>

              {/* Right Column: High-Value Contextual Insights & Internal Links */}
              <aside className="lg:col-span-4 space-y-6">
                {/* Resume Analyzer CTA (Conversion Bridge) */}
                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#0050cb] flex items-center justify-center">
                    <span className="material-symbols-outlined text-xl">description</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-800">
                    Applying to {data.role_name}?
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed font-[Geist]">
                    Scan your resume against real {data.role_name} job descriptions to test ATS keyword match and formatting before applying.
                  </p>
                  <Link
                    to="/app/resume"
                    className="w-full inline-flex items-center justify-center gap-2 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition-colors"
                  >
                    Scan Resume with AI
                    <span className="material-symbols-outlined text-xs">arrow_forward</span>
                  </Link>
                </div>

                {/* Top Hiring Companies */}
                {data.top_companies?.length > 0 && (
                  <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-[Geist]">
                      Top Hiring Companies
                    </h3>
                    <div className="space-y-2">
                      {data.top_companies.map((comp, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-700">{comp.name}</span>
                          <span className="text-[11px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                            {comp.count} jobs
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Top Locations (for Role/Company pages) */}
                {data.top_locations?.length > 0 && categoryType !== 'location' && (
                  <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-[Geist]">
                      Top Job Locations
                    </h3>
                    <div className="space-y-2">
                      {data.top_locations.map((loc, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-700">{loc.name}</span>
                          <span className="text-[11px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                            {loc.count} jobs
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Core In-Demand Skills */}
                {data.skills?.length > 0 && (
                  <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-[Geist]">
                      Core In-Demand Skills
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {data.skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium font-[Geist]"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Related Qualified Roles (Internal SEO Mesh) */}
                {data.related_roles?.length > 0 && (
                  <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-[Geist]">
                      Explore Related Roles
                    </h3>
                    <ul className="space-y-2">
                      {data.related_roles.map((rel) => (
                        <li key={rel.slug}>
                          <Link
                            to={`/jobs/role/${rel.slug}`}
                            className="text-xs font-semibold text-[#0050cb] hover:underline flex items-center justify-between"
                          >
                            <span>{rel.label} Jobs</span>
                            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Related Qualified Locations (Internal SEO Mesh) */}
                {data.related_locations?.length > 0 && (
                  <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-[Geist]">
                      Explore Top Locations
                    </h3>
                    <ul className="space-y-2">
                      {data.related_locations.map((loc) => (
                        <li key={loc.slug}>
                          <Link
                            to={`/jobs/location/${loc.slug}`}
                            className="text-xs font-semibold text-[#0050cb] hover:underline flex items-center justify-between"
                          >
                            <span>Jobs in {loc.label}</span>
                            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </aside>
            </div>
          </div>
        )}
      </main>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <Footer />
    </div>
  )
}
