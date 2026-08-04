import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { getCoverageReport } from '../api';

export default function AdminPanel() {
  const { user } = useContext(AuthContext);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const data = await getCoverageReport();
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-xl text-center">Loading Coverage Report...</div>;
  if (!report) return <div className="p-xl text-center text-error">Failed to load coverage report</div>;

  return (
    <div className="space-y-lg animate-fade-in-up">
      <header>
        <h1 className="text-3xl font-bold text-on-surface">Data Coverage Dashboard</h1>
        <p className="text-on-surface-variant">Real-time metrics on job index quality and ATS pipeline health.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-md stagger-children">
        <div className="glass-effect p-md rounded-xl border border-primary/20">
          <div className="text-sm font-medium font-[Geist] text-on-surface-variant">Total Active Jobs</div>
          <div className="text-3xl font-bold text-primary mt-xs">{report.total_active_jobs.toLocaleString()}</div>
        </div>
        <div className="glass-effect p-md rounded-xl border border-success/20">
          <div className="text-sm font-medium font-[Geist] text-on-surface-variant">Verified Jobs (Trust &gt;80)</div>
          <div className="text-3xl font-bold text-success mt-xs">{report.total_verified_jobs.toLocaleString()}</div>
        </div>
        <div className="glass-effect p-md rounded-xl">
          <div className="text-sm font-medium font-[Geist] text-on-surface-variant">Active Companies</div>
          <div className="text-3xl font-bold text-on-surface mt-xs">{report.companies_active.toLocaleString()}</div>
        </div>
        <div className="glass-effect p-md rounded-xl border border-error/20">
          <div className="text-sm font-medium font-[Geist] text-on-surface-variant">Failing Collectors</div>
          <div className="text-3xl font-bold text-error mt-xs">{report.companies_failed.toLocaleString()}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg">
        {/* ATS Distribution */}
        <section className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm">
          <h2 className="text-xl font-bold text-on-background mb-md border-b border-outline-variant/30 pb-sm">Jobs by ATS Type</h2>
          <div className="space-y-sm max-h-64 overflow-y-auto pr-2 custom-scrollbar">
            {Object.entries(report.jobs_by_ats || {}).map(([ats, count]) => (
              <div key={ats} className="flex justify-between items-center p-sm bg-surface-container-lowest rounded-lg border border-outline-variant/50">
                <span className="font-medium font-[Geist]">{ats || 'Unknown'}</span>
                <span className="text-primary font-bold">{count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Failed Companies */}
        <section className="bg-error-container/10 p-lg rounded-xl border border-error/20 shadow-sm">
          <h2 className="text-xl font-bold text-on-error-container mb-md border-b border-error/20 pb-sm flex justify-between items-center">
            <span>Failing Companies</span>
            <span className="text-xs bg-error text-white px-2 py-1 rounded-full">{report.failed_companies?.length || 0}</span>
          </h2>
          {report.failed_companies?.length > 0 ? (
            <div className="space-y-sm max-h-64 overflow-y-auto pr-2 custom-scrollbar">
              {report.failed_companies.map((company, i) => (
                <div key={i} className="flex justify-between items-center p-sm bg-white rounded-lg border border-error/10 text-on-error-container">
                  <span className="font-medium font-[Geist]">{company}</span>
                  <span className="material-symbols-outlined text-sm text-error">warning</span>
                </div>
              ))}
            </div>
          ) : (
             <div className="text-center text-success py-xl flex flex-col items-center">
                <span className="material-symbols-outlined text-4xl mb-sm">check_circle</span>
                All configured company pipelines are healthy.
             </div>
          )}
        </section>
      </div>
    </div>
  );
}
