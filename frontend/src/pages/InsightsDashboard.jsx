import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  getInsightsStats, 
  getInsightsSkills, 
  getInsightsCompanies, 
  getInsightsLocations, 
  getInsightsTrends, 
  getInsightsSalary, 
  getFastGrowingCareers 
} from '../api';

export default function InsightsDashboard() {
  const [stats, setStats] = useState(null);
  const [skills, setSkills] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [locations, setLocations] = useState([]);
  const [trends, setTrends] = useState([]);
  const [salary, setSalary] = useState([]);
  const [fastGrowing, setFastGrowing] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [
          statsRes, 
          skillsRes, 
          companiesRes, 
          locationsRes, 
          trendsRes, 
          salaryRes, 
          fastGrowingRes
        ] = await Promise.allSettled([
          getInsightsStats(),
          getInsightsSkills(),
          getInsightsCompanies(),
          getInsightsLocations(),
          getInsightsTrends(),
          getInsightsSalary(),
          getFastGrowingCareers()
        ]);

        if (statsRes.status === 'fulfilled') setStats(statsRes.value);
        if (skillsRes.status === 'fulfilled' && Array.isArray(skillsRes.value)) setSkills(skillsRes.value);
        if (companiesRes.status === 'fulfilled' && Array.isArray(companiesRes.value)) setCompanies(companiesRes.value);
        if (locationsRes.status === 'fulfilled' && Array.isArray(locationsRes.value)) setLocations(locationsRes.value);
        if (trendsRes.status === 'fulfilled' && Array.isArray(trendsRes.value)) setTrends(trendsRes.value);
        if (salaryRes.status === 'fulfilled' && Array.isArray(salaryRes.value)) setSalary(salaryRes.value);
        if (fastGrowingRes.status === 'fulfilled' && fastGrowingRes.value?.roles) setFastGrowing(fastGrowingRes.value.roles);
      } catch (err) {
        console.error('Error loading insights:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalOpps = stats?.total_opportunities || 0;
  const maxSkillCount = skills.length > 0 ? Math.max(...skills.map(s => s.count), 1) : 1;
  const maxCompanyCount = companies.length > 0 ? Math.max(...companies.map(c => c.count), 1) : 1;
  const maxLocCount = locations.length > 0 ? Math.max(...locations.map(l => l.count), 1) : 1;
  const displayTrends = (trends || []).slice(-7);
  const maxTrendCount = displayTrends.length > 0 ? Math.max(...displayTrends.map(t => t.count), 1) : 1;
  const totalSalaryOpps = salary.reduce((acc, curr) => acc + (curr.count || 0), 0) || 1;

  if (loading) {
    return (
      <div className="space-y-lg animate-fade-in p-2 sm:p-4">
        <div className="h-10 w-64 bg-surface-container-high rounded-lg animate-pulse" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-md">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="h-28 bg-surface-container rounded-2xl animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg">
          <div className="h-80 bg-surface-container rounded-2xl animate-pulse" />
          <div className="h-80 bg-surface-container rounded-2xl animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-lg animate-fade-in-up pb-12">
      {/* ─── Header & Telemetry Pill ─── */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
              Market Insights & Analytics
            </h1>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Live DB
            </span>
          </div>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Real-time market intelligence aggregated across verified opportunities and hiring trends.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-surface-container p-1 rounded-xl self-start sm:self-auto overflow-x-auto no-scrollbar">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
              activeTab === 'overview'
                ? 'bg-surface text-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
              activeTab === 'skills'
                ? 'bg-surface text-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            In-Demand Skills
          </button>
          <button
            onClick={() => setActiveTab('companies')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
              activeTab === 'companies'
                ? 'bg-surface text-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Top Employers
          </button>
          <button
            onClick={() => setActiveTab('roles')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
              activeTab === 'roles'
                ? 'bg-surface text-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Growth Careers
          </button>
        </div>
      </header>

      {/* ─── 5-Metric Executive KPI Row ─── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-md">
        <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-4 sm:p-md flex flex-col justify-between hover:border-primary/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">
              Opportunities
            </span>
            <span className="material-symbols-outlined text-primary text-xl">work_outline</span>
          </div>
          <div className="mt-2">
            <p className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
              {(stats?.total_opportunities || 0).toLocaleString()}
            </p>
            <span className="text-[11px] text-emerald-600 font-medium">Active postings</span>
          </div>
        </div>

        <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-4 sm:p-md flex flex-col justify-between hover:border-primary/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">
              Tech Jobs
            </span>
            <span className="material-symbols-outlined text-blue-500 text-xl">code</span>
          </div>
          <div className="mt-2">
            <p className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
              {(stats?.total_jobs || 0).toLocaleString()}
            </p>
            <span className="text-[11px] text-on-surface-variant">Full-time roles</span>
          </div>
        </div>

        <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-4 sm:p-md flex flex-col justify-between hover:border-primary/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">
              Internships
            </span>
            <span className="material-symbols-outlined text-amber-500 text-xl">school</span>
          </div>
          <div className="mt-2">
            <p className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
              {(stats?.total_internships || 0).toLocaleString()}
            </p>
            <span className="text-[11px] text-on-surface-variant">Early career</span>
          </div>
        </div>

        <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-4 sm:p-md flex flex-col justify-between hover:border-primary/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">
              Companies
            </span>
            <span className="material-symbols-outlined text-indigo-500 text-xl">corporate_fare</span>
          </div>
          <div className="mt-2">
            <p className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
              {(stats?.total_companies || 0).toLocaleString()}
            </p>
            <span className="text-[11px] text-on-surface-variant">Verified employers</span>
          </div>
        </div>

        <div className="col-span-2 sm:col-span-1 bg-surface-container-lowest border border-outline-variant rounded-2xl p-4 sm:p-md flex flex-col justify-between hover:border-primary/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant font-[Geist]">
              Locations
            </span>
            <span className="material-symbols-outlined text-purple-500 text-xl">location_on</span>
          </div>
          <div className="mt-2">
            <p className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
              {(stats?.total_locations || 0).toLocaleString()}
            </p>
            <span className="text-[11px] text-on-surface-variant">Global & Remote</span>
          </div>
        </div>
      </div>

      {/* ─── MAIN CONTENT ACCORDING TO ACTIVE TAB ─── */}
      {activeTab === 'overview' && (
        <div className="space-y-lg">
          {/* Row 1: Skills vs Hiring Trends */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg">
            {/* Top Skills Demand */}
            <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-md">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">data_thresholding</span>
                    <h2 className="text-lg font-bold text-on-surface font-[Geist]">Top Skills in Demand</h2>
                  </div>
                  <span className="text-xs text-on-surface-variant">From live listings</span>
                </div>

                <div className="space-y-3">
                  {skills.slice(0, 8).map((skill, idx) => {
                    const pct = Math.min((skill.count / maxSkillCount) * 100, 100);
                    return (
                      <div key={idx} className="flex flex-col gap-1">
                        <div className="flex justify-between items-center text-xs">
                          <span className="font-semibold text-on-surface flex items-center gap-1.5">
                            <span className="w-4 text-[10px] text-on-surface-variant">#{idx + 1}</span>
                            {skill.name}
                          </span>
                          <span className="text-on-surface-variant font-medium">{skill.count} postings</span>
                        </div>
                        <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-cyan-500 rounded-full transition-all duration-500"
                            style={{ width: `${Math.max(pct, 6)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                  {skills.length === 0 && (
                    <p className="text-xs text-on-surface-variant py-4 text-center">No skill data available currently.</p>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-outline-variant/50 flex items-center justify-between text-xs">
                <span className="text-on-surface-variant">Target your learning path to top skills</span>
                <Link to="/app/learn" className="text-primary font-bold hover:underline flex items-center gap-0.5">
                  Explore Learning Roadmaps <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                </Link>
              </div>
            </div>

            {/* Posting Trends */}
            <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-md">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">ssid_chart</span>
                    <h2 className="text-lg font-bold text-on-surface font-[Geist]">Posting Velocity (Last 7 Days)</h2>
                  </div>
                  <span className="text-xs text-on-surface-variant">Daily volume</span>
                </div>

                <div className="relative pt-6 pb-2">
                  <div className="h-44 sm:h-48 flex items-end gap-1.5 sm:gap-3 border-b border-outline-variant pb-2">
                    {displayTrends.map((trend, idx) => {
                      const heightPct = Math.min((trend.count / maxTrendCount) * 100, 100);
                      return (
                        <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group relative min-w-0">
                          {/* Tooltip */}
                          <div className="absolute top-0 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-[10px] font-bold py-0.5 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20 shadow-md">
                            {trend.count} jobs
                          </div>
                          {/* Bar */}
                          <div
                            className="w-full max-w-[42px] bg-primary/25 group-hover:bg-primary rounded-t-md transition-all duration-300 flex flex-col justify-end"
                            style={{ height: `${Math.max(heightPct, 8)}%` }}
                          >
                            <div className="h-1 bg-primary rounded-t-md" />
                          </div>
                          {/* Date Label */}
                          <span className="text-[10px] sm:text-xs text-on-surface-variant font-medium truncate w-full text-center">
                            {trend.date ? new Date(trend.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : ''}
                          </span>
                        </div>
                      );
                    })}
                    {displayTrends.length === 0 && (
                      <p className="text-xs text-on-surface-variant self-center w-full text-center">No trend telemetry available.</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-outline-variant/50 flex items-center justify-between text-xs text-on-surface-variant">
                <span>Updated every hour from real crawl runs</span>
                <span className="font-semibold text-primary">Live Sync Active</span>
              </div>
            </div>
          </div>

          {/* Row 2: Top Employers & Location Distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
            {/* Top Employers */}
            <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">domain</span>
                  <h3 className="font-bold text-on-surface font-[Geist]">Top Hiring Companies</h3>
                </div>
                <Link to="/app/opportunities" className="text-xs text-primary font-semibold hover:underline">
                  View all
                </Link>
              </div>

              <div className="space-y-2.5">
                {companies.slice(0, 5).map((comp, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded-xl bg-surface-container hover:bg-surface-container-high transition-colors">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary font-bold flex items-center justify-center text-sm shrink-0">
                        {comp.name[0]}
                      </div>
                      <span className="text-xs font-bold text-on-surface truncate">{comp.name}</span>
                    </div>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary shrink-0">
                      {comp.count} openings
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Hubs / Locations */}
            <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">map</span>
                  <h3 className="font-bold text-on-surface font-[Geist]">Top Hiring Hubs</h3>
                </div>
                <span className="text-xs text-on-surface-variant">By volume</span>
              </div>

              <div className="space-y-2.5">
                {locations.slice(0, 5).map((loc, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded-xl bg-surface-container hover:bg-surface-container-high transition-colors">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="material-symbols-outlined text-on-surface-variant text-base">pin_drop</span>
                      <span className="text-xs font-semibold text-on-surface truncate">{loc.name}</span>
                    </div>
                    <span className="text-xs font-bold text-on-surface-variant shrink-0">
                      {loc.count} roles
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Experience / Seniority Distribution */}
            <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md md:col-span-2 lg:col-span-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">pie_chart</span>
                  <h3 className="font-bold text-on-surface font-[Geist]">Seniority Distribution</h3>
                </div>
              </div>

              <div className="space-y-3 pt-1">
                {salary.map((s, idx) => {
                  const pct = Math.round((s.count / totalSalaryOpps) * 100);
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-medium text-on-surface truncate">{s.range}</span>
                        <span className="font-bold text-primary">{pct}% ({s.count})</span>
                      </div>
                      <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            idx === 0 ? 'bg-amber-500' : idx === 1 ? 'bg-primary' : 'bg-purple-600'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Row 3: Fast Growing Roles Snippet */}
          {fastGrowing.length > 0 && (
            <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-amber-500">trending_up</span>
                  <h3 className="font-bold text-on-surface font-[Geist]">Fast Growing Career Paths</h3>
                </div>
                <button
                  onClick={() => setActiveTab('roles')}
                  className="text-xs text-primary font-bold hover:underline"
                >
                  View full analysis →
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {fastGrowing.slice(0, 6).map((role, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl border border-outline-variant/60 bg-surface-container-low hover:border-primary/40 transition-all flex items-center justify-between"
                  >
                    <div className="min-w-0 pr-2">
                      <h4 className="font-bold text-xs sm:text-sm text-on-surface capitalize truncate">{role.title}</h4>
                      <p className="text-[11px] text-on-surface-variant mt-0.5">{role.recent_postings} recent openings</p>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 shrink-0">
                      {role.growth_signal}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─── TAB: SKILLS ─── */}
      {activeTab === 'skills' && (
        <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-on-surface font-[Geist]">Top Technical & Core Skills Breakdown</h2>
              <p className="text-xs text-on-surface-variant">Extracted across all active opportunities currently listed on CareerLens.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 pt-2">
            {skills.map((skill, idx) => {
              const pct = Math.min((skill.count / maxSkillCount) * 100, 100);
              return (
                <div key={idx} className="flex flex-col gap-1 p-2 rounded-xl hover:bg-surface-container transition-colors">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-on-surface flex items-center gap-2">
                      <span className="w-5 text-center text-[10px] font-bold px-1 py-0.5 bg-surface-container-high rounded text-on-surface-variant">
                        {idx + 1}
                      </span>
                      {skill.name}
                    </span>
                    <span className="font-bold text-primary">{skill.count} postings</span>
                  </div>
                  <div className="w-full h-2.5 bg-surface-container-high rounded-full overflow-hidden mt-1">
                    <div
                      className="h-full bg-gradient-to-r from-primary to-cyan-500 rounded-full"
                      style={{ width: `${Math.max(pct, 5)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─── TAB: COMPANIES ─── */}
      {activeTab === 'companies' && (
        <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md">
          <div>
            <h2 className="text-lg font-bold text-on-surface font-[Geist]">Top Hiring Companies Ranking</h2>
            <p className="text-xs text-on-surface-variant">Companies with the highest volume of open tech and engineering positions.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
            {companies.map((comp, idx) => (
              <div key={idx} className="bg-surface-container border border-outline-variant/60 p-4 rounded-2xl flex flex-col justify-between hover:border-primary transition-all">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary text-on-primary font-bold flex items-center justify-center text-base shrink-0">
                    {comp.name[0]}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-sm text-on-surface truncate">{comp.name}</h3>
                    <p className="text-xs text-primary font-semibold">{comp.count} open roles</p>
                  </div>
                </div>
                <Link
                  to={`/app/opportunities?query=${encodeURIComponent(comp.name)}`}
                  className="mt-4 w-full py-1.5 px-3 rounded-lg text-xs font-bold bg-surface text-center text-on-surface hover:bg-primary hover:text-on-primary transition-colors flex items-center justify-center gap-1"
                >
                  Search Jobs <span className="material-symbols-outlined text-[14px]">search</span>
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── TAB: ROLES ─── */}
      {activeTab === 'roles' && (
        <div className="bg-surface-container-lowest border border-outline-variant p-4 sm:p-lg rounded-2xl space-y-md">
          <div>
            <h2 className="text-lg font-bold text-on-surface font-[Geist]">Fast Growing Tech Careers & Roles</h2>
            <p className="text-xs text-on-surface-variant">Evaluation based on recent hiring velocity and 90-day demand momentum.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            {fastGrowing.map((role, idx) => (
              <div key={idx} className="bg-surface-container border border-outline-variant/60 p-4 rounded-2xl space-y-3 hover:border-primary/40 transition-all">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-bold text-sm text-on-surface capitalize">{role.title}</h3>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 shrink-0">
                    {role.growth_signal}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-outline-variant/40 text-xs">
                  <div>
                    <span className="text-on-surface-variant block text-[10px]">Recent Postings</span>
                    <span className="font-bold text-on-surface">{role.recent_postings}</span>
                  </div>
                  <div>
                    <span className="text-on-surface-variant block text-[10px]">Total Postings</span>
                    <span className="font-bold text-on-surface">{role.total_postings}</span>
                  </div>
                </div>
                <Link
                  to={`/app/opportunities?query=${encodeURIComponent(role.title)}`}
                  className="w-full py-1.5 px-3 rounded-lg text-xs font-bold bg-surface text-center text-primary hover:bg-primary hover:text-on-primary transition-colors flex items-center justify-center gap-1"
                >
                  View Matching Opportunities <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

