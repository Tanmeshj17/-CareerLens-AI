import { useState, useEffect } from 'react';
import { getInsightsStats, getInsightsSkills, getInsightsTrends } from '../api';

export default function InsightsDashboard() {
  const [stats, setStats] = useState(null);
  const [skills, setSkills] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsRes, skillsRes, trendsRes] = await Promise.all([
          getInsightsStats(),
          getInsightsSkills(),
          getInsightsTrends()
        ]);
        setStats(statsRes);
        setSkills(skillsRes);
        setTrends(trendsRes);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div className="p-xl text-center">Loading Insights...</div>;

  return (
    <div className="space-y-lg animate-fade-in-up">
      <header>
        <h1 className="text-3xl font-bold text-on-surface">Market Insights Dashboard</h1>
        <p className="text-on-surface-variant">Data analytics and market trends from our collected opportunities.</p>
      </header>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-md stagger-children">
        <div className="glass-insight p-md rounded-xl">
          <h3 className="text-sm font-bold text-on-surface-variant">Total Opportunities</h3>
          <p className="text-3xl font-bold text-primary mt-2">{stats?.total_opportunities || 0}</p>
        </div>
        <div className="glass-insight p-md rounded-xl">
          <h3 className="text-sm font-bold text-on-surface-variant">Total Jobs</h3>
          <p className="text-3xl font-bold text-primary mt-2">{stats?.total_jobs || 0}</p>
        </div>
        <div className="glass-insight p-md rounded-xl">
          <h3 className="text-sm font-bold text-on-surface-variant">Total Internships</h3>
          <p className="text-3xl font-bold text-primary mt-2">{stats?.total_internships || 0}</p>
        </div>
        <div className="glass-insight p-md rounded-xl">
          <h3 className="text-sm font-bold text-on-surface-variant">Companies</h3>
          <p className="text-3xl font-bold text-primary mt-2">{stats?.total_companies || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg mt-lg">
        <div className="bg-surface-container-low border border-outline-variant p-lg rounded-xl">
          <h2 className="text-xl font-bold mb-md text-on-surface">Top Skills in Demand</h2>
          <div className="space-y-3">
            {skills.map((skill, idx) => (
              <div key={idx} className="flex items-center gap-sm">
                <span className="w-24 text-sm font-medium truncate">{skill.name}</span>
                <div className="flex-1 h-3 bg-surface-container-highest rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary" 
                    style={{ width: `${Math.min((skill.count / (skills[0]?.count || 1)) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-on-surface-variant w-8 text-right">{skill.count}</span>
              </div>
            ))}
            {skills.length === 0 && <p className="text-sm text-on-surface-variant">No skills data available.</p>}
          </div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant p-lg rounded-xl">
          <h2 className="text-xl font-bold mb-md text-on-surface">Posting Trends (Last 7 Days)</h2>
          <div className="h-[250px] flex items-end gap-2 border-b border-outline-variant pb-2">
            {trends.map((trend, idx) => {
              const maxCount = Math.max(...trends.map(t => t.count), 1);
              const heightPct = (trend.count / maxCount) * 100;
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1 group">
                  <div className="w-full bg-secondary-container rounded-t-sm transition-all hover:bg-primary relative" style={{ height: `${heightPct}%`, minHeight: '4px' }}>
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                      {trend.count}
                    </div>
                  </div>
                  <span className="text-[10px] text-on-surface-variant truncate w-full text-center">{trend.date.substring(5)}</span>
                </div>
              );
            })}
            {trends.length === 0 && <p className="text-sm text-on-surface-variant self-center w-full text-center">No trend data available.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
