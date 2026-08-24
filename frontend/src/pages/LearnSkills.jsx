import { useState, useEffect } from 'react';
import { getLearningRecommendations } from '../api';
import { Skeleton } from '../components/ui/Skeleton';
import { Alert } from '../components/ui/Alert';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';

export default function LearnSkills() {
  const [role, setRole] = useState('Data Engineer');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const result = await getLearningRecommendations(role);
        setData(result);
      } catch (e) {
        console.error("Failed to load learning recommendations", e);
        setError("Failed to load recommendations. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [role]);

  return (
    <div className="space-y-lg animate-fade-in-up">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-on-surface">Data-Driven Learning Engine</h1>
          <p className="text-on-surface-variant">Targeted upskilling paths based on real market requirements.</p>
        </div>
        <div className="relative w-full md:w-64">
          <select 
            className="w-full pl-4 pr-10 py-2 bg-surface-container-low border border-outline-variant rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="Data Engineer">Data Engineer</option>
            <option value="Data Analyst">Data Analyst</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Developer">Backend Developer</option>
            <option value="Full Stack Developer">Full Stack Developer</option>
            <option value="DevOps Engineer">DevOps Engineer</option>
            <option value="Cloud Engineer">Cloud Engineer</option>
            <option value="Site Reliability Engineer (SRE)">Site Reliability Engineer (SRE)</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="Machine Learning Engineer">Machine Learning Engineer</option>
            <option value="Cybersecurity Analyst">Cybersecurity Analyst</option>
            <option value="QA Engineer / SDET">QA Engineer / SDET</option>
            <option value="Performance Test Engineer">Performance Test Engineer</option>
            <option value="QA Automation Engineer">QA Automation Engineer</option>
            <option value="Manual QA Tester">Manual QA Tester</option>
            <option value="Android Developer">Android Developer</option>
            <option value="iOS Developer">iOS Developer</option>
            <option value="Cross-Platform Mobile Developer">Cross-Platform Mobile Developer</option>
            <option value="Product Manager">Product Manager</option>
            <option value="UI/UX Designer">UI/UX Designer</option>
            <option value="SAP Consultant">SAP Consultant</option>
          </select>
          <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none">expand_more</span>
        </div>
      </header>

      {loading ? (
        <div className="space-y-lg py-md">
          <Skeleton className="h-24 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : !data ? null : (
        <div className="space-y-xl">
          <section>
            <h2 className="text-xl font-bold mb-md flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">psychology</span>
              Required Skills for {role}
            </h2>
            <div className="flex flex-wrap gap-sm">
              {data.required_skills.map((s, i) => (
                <div key={i} className={`px-4 py-2 rounded-full border text-sm font-medium ${s.importance === 'Required' ? 'bg-primary-container/20 border-primary text-primary' : 'bg-surface-container border-outline-variant text-on-surface-variant'}`}>
                  {s.skill}
                </div>
              ))}
            </div>
          </section>

          <section>
            <div className="mb-md flex flex-col md:flex-row md:items-center justify-between gap-2">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">school</span>
                Top Verified Resources
              </h2>
              {data.match_type && (
                <span className="text-sm font-medium bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full">
                  {data.match_type}
                </span>
              )}
            </div>
            {data.resources && data.resources.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md">
                {data.resources.map((res, i) => (
                  <a href={res.url} target="_blank" rel="noopener noreferrer" key={i} className="bg-white border border-outline-variant p-md rounded-xl flex flex-col h-full hover:border-primary/50 hover:shadow-lg transition-all cursor-pointer group">
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">{res.difficulty || 'All Levels'}</span>
                        <div className="flex gap-1">
                          {res.country === 'India' && <span className="text-xs font-bold bg-orange-100 text-orange-800 px-2 py-1 rounded-full border border-orange-200">🇮🇳 India</span>}
                          <span className={`text-xs font-bold px-2 py-1 rounded-full ${res.affordability === 'FREE' ? 'bg-success/10 text-success' : res.affordability === 'LOW_COST' ? 'bg-blue-100 text-blue-800' : 'bg-error/10 text-error'}`}>{res.affordability || (res.is_free ? 'FREE' : 'PAID')}</span>
                        </div>
                      </div>
                      <h3 className="font-bold text-lg leading-tight mb-2 group-hover:text-primary transition-colors">{res.title}</h3>
                      <p className="text-sm text-on-surface-variant line-clamp-2">{res.description}</p>
                      {res.match_reason && (
                        <div className="mt-2 bg-surface-container-low p-2 rounded text-xs text-on-surface-variant border border-outline-variant/30">
                          <span className="font-semibold text-primary">Why: </span>
                          {res.match_reason}
                        </div>
                      )}
                    </div>
                    <div className="mt-4 pt-4 border-t border-outline-variant/30 flex justify-between items-center text-xs text-on-surface-variant">
                      <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">video_library</span> {res.provider}</span>
                      <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">schedule</span> {res.duration || 'Self-paced'}</span>
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 bg-surface-container-lowest border border-dashed border-outline-variant rounded-xl text-center">
                <span className="material-symbols-outlined text-4xl text-on-surface-variant/50 mb-2">menu_book</span>
                <p className="text-on-surface-variant font-medium">No verified courses are currently available for this role.</p>
                <p className="text-xs text-on-surface-variant/70 mt-1">More learning resources are being added by our intelligence engine.</p>
              </div>
            )}
          </section>

          <section>
            <div className="mb-md flex flex-col md:flex-row md:items-center justify-between gap-2">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">workspace_premium</span>
                Recommended Certifications
              </h2>
              {data.match_type && (
                <span className="text-sm font-medium bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full">
                  {data.match_type}
                </span>
              )}
            </div>
            {data.certifications && data.certifications.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
                {data.certifications.map((cert, i) => (
                  <a href={cert.url} target="_blank" rel="noopener noreferrer" key={i} className="bg-gradient-to-br from-surface-container-lowest to-surface-container border border-outline-variant p-md rounded-xl flex flex-col h-full hover:border-primary/50 hover:shadow-lg transition-all cursor-pointer group relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-bl-full -z-10 group-hover:bg-primary/10 transition-colors"></div>
                    <div className="flex-1 z-10">
                      <h3 className="font-bold text-lg leading-tight mb-2 group-hover:text-primary transition-colors pr-8">{cert.name}</h3>
                      <div className="flex items-center gap-2 mb-4">
                        <span className="text-sm font-medium text-on-surface-variant">{cert.provider}</span>
                        {cert.exam_required && <span className="text-xs bg-warning/10 text-warning px-2 py-0.5 rounded-full border border-warning/20">Exam Required</span>}
                      </div>
                      
                      <div className="space-y-2 mt-4 text-sm text-on-surface-variant">
                        <div className="flex justify-between items-center bg-white/50 p-2 rounded border border-outline-variant/30">
                          <span className="font-[Geist]">Affordability</span>
                          <span className={`font-bold px-2 py-0.5 rounded-full text-xs ${cert.affordability === 'FREE' ? 'bg-success/10 text-success' : cert.affordability === 'LOW_COST' ? 'bg-blue-100 text-blue-800' : 'bg-warning/10 text-warning'}`}>{cert.affordability || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between items-center bg-white/50 p-2 rounded border border-outline-variant/30">
                          <span className="font-[Geist]">Cost</span>
                          <span className="font-bold text-on-surface">
                            {cert.price_inr ? `₹${cert.price_inr.toLocaleString()}` : (cert.is_free ? 'Free' : (cert.cost || 'Varies'))}
                          </span>
                        </div>
                        <div className="flex justify-between items-center bg-white/50 p-2 rounded border border-outline-variant/30">
                          <span className="font-[Geist]">Difficulty</span>
                          <span className="font-bold text-on-surface">{cert.difficulty || 'Intermediate'}</span>
                        </div>
                        {(cert.free_learning_available || cert.financial_aid_available) && (
                          <div className="flex flex-col gap-1 mt-2 text-xs">
                            {cert.free_learning_available && <span className="flex items-center gap-1 text-success"><span className="material-symbols-outlined text-xs">check_circle</span> Free learning available</span>}
                            {cert.financial_aid_available && <span className="flex items-center gap-1 text-primary"><span className="material-symbols-outlined text-xs">check_circle</span> Financial Aid available</span>}
                          </div>
                        )}
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 bg-surface-container-lowest border border-dashed border-outline-variant rounded-xl text-center">
                <span className="material-symbols-outlined text-4xl text-on-surface-variant/50 mb-2">workspace_premium</span>
                <p className="text-on-surface-variant font-medium">No verified certifications are currently available for this role.</p>
                <p className="text-xs text-on-surface-variant/70 mt-1">Our intelligence engine is actively sourcing new certifications.</p>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
