import { useState } from 'react';
import { analyzeResume, getResumeGapAnalysis, getResumeReadiness } from '../api';

// ─── Score Color Logic ───────────────────────────────────────────────────────
function getScoreColor(score) {
  if (score >= 80) return { color: 'text-emerald-400', bg: 'bg-emerald-500', ring: 'stroke-emerald-400', label: 'Excellent' };
  if (score >= 60) return { color: 'text-sky-400', bg: 'bg-sky-500', ring: 'stroke-sky-400', label: 'Good' };
  if (score >= 40) return { color: 'text-amber-400', bg: 'bg-amber-500', ring: 'stroke-amber-400', label: 'Average' };
  return { color: 'text-rose-400', bg: 'bg-rose-500', ring: 'stroke-rose-400', label: 'Needs Work' };
}

// ─── ATS Score Ring Component ────────────────────────────────────────────────
function ScoreRing({ score }) {
  const { color, ring, label } = getScoreColor(score);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="currentColor" strokeWidth="10" className="text-white/8" />
          <circle
            cx="60" cy="60" r={radius} fill="none" strokeWidth="10"
            strokeDasharray={circumference} strokeDashoffset={offset}
            strokeLinecap="round" className={ring}
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-black font-[Geist] ${color}`}>{score}</span>
          <span className="text-[10px] text-[var(--md-sys-color-on-surface-variant)] uppercase tracking-widest font-[Geist]">/ 100</span>
        </div>
      </div>
      <span className={`text-xs font-bold px-3 py-1 rounded-full ${color} bg-white/5 border border-current/20 font-[Geist]`}>{label}</span>
    </div>
  );
}

// ─── Skill Tag ───────────────────────────────────────────────────────────────
function SkillTag({ skill, variant = 'default' }) {
  const variants = {
    default: 'bg-[var(--md-sys-color-surface-container-high)] text-[var(--md-sys-color-on-surface)] border-[var(--md-sys-color-outline-variant)]/30',
    match: 'bg-emerald-500/12 text-emerald-400 border-emerald-500/25',
    missing: 'bg-rose-500/12 text-rose-400 border-rose-500/25',
    recommend: 'bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] border-[var(--md-sys-color-primary)]/25',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium font-[Geist] border ${variants[variant]}`}>
      {skill}
    </span>
  );
}

export default function ResumeAnalysis() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [gapData, setGapData] = useState(null);
  const [readinessData, setReadinessData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const handleUpload = async (e) => {
    e.preventDefault();
    const selectedFile = e.target.files && e.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setAnalyzing(true);
    setResult(null);
    setGapData(null);
    setReadinessData(null);

    try {
      const analyzeRes = await analyzeResume(selectedFile);
      const resumeId = analyzeRes.id || analyzeRes.resume_id;

      const [gapRes, readinessRes] = await Promise.all([
        getResumeGapAnalysis(resumeId).catch(() => null),
        getResumeReadiness(resumeId).catch(() => null),
      ]);

      setResult({
        score: analyzeRes.ats_score || 0,
        skills: analyzeRes.extracted_skills || [],
        strengths: analyzeRes.strengths || [],
        weaknesses: analyzeRes.weaknesses || [],
        suggestions: analyzeRes.suggestions || [],
        certs: analyzeRes.extracted_certifications || [],
        experience: analyzeRes.extracted_experience || [],
        education: analyzeRes.extracted_education || [],
      });
      setGapData(gapRes);
      setReadinessData(readinessRes);
    } catch (err) {
      console.error(err);
      alert('Failed to analyze resume. Please try uploading again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: 'dashboard' },
    { id: 'gap', label: 'Skill Gap', icon: 'compare_arrows' },
    { id: 'feedback', label: 'AI Feedback', icon: 'lightbulb' },
  ];

  return (
    <div className="space-y-lg animate-fade-in-up">

      {/* ─── Header ─── */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[var(--md-sys-color-primary-container)]/20 via-[var(--md-sys-color-primary)]/8 to-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/30 p-xl">
        <div className="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-[var(--md-sys-color-primary)]/6 blur-3xl pointer-events-none" />
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-[var(--md-sys-color-primary)]/15 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 28 }}>insert_chart</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
              Resume ATS Analysis
            </h1>
            <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">
              AI-powered scoring, skill gap detection, and professional feedback
            </p>
          </div>
        </div>
      </div>

      {/* ─── Upload Zone ─── */}
      {!result && !analyzing && (
        <label className="group block cursor-pointer">
          <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.doc,.docx" />
          <div className="border-2 border-dashed border-[var(--md-sys-color-outline-variant)]/50 rounded-2xl p-16 flex flex-col items-center justify-center bg-[var(--md-sys-color-surface-container)]/50 hover:bg-[var(--md-sys-color-surface-container)] hover:border-[var(--md-sys-color-primary)]/50 transition-all duration-300 group-hover:shadow-lg">
            <div className="w-16 h-16 rounded-2xl bg-[var(--md-sys-color-primary)]/12 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
              <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 34 }}>upload_file</span>
            </div>
            <p className="text-lg font-bold text-[var(--md-sys-color-on-surface)] font-[Geist] mb-1">
              Drop your resume here or click to browse
            </p>
            <p className="text-sm text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">
              Supports PDF and DOCX · Max 5 MB
            </p>
            <div className="mt-6 flex items-center gap-3">
              {['ATS Score', 'Skill Gap Analysis', 'AI Feedback', '300+ Skills Detected'].map(tag => (
                <span key={tag} className="text-xs px-3 py-1.5 rounded-full bg-[var(--md-sys-color-primary)]/10 text-[var(--md-sys-color-primary)] font-[Geist] font-medium border border-[var(--md-sys-color-primary)]/20">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </label>
      )}

      {/* ─── Loading State ─── */}
      {analyzing && (
        <div className="rounded-2xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/30 p-16 flex flex-col items-center gap-6">
          <div className="relative w-20 h-20">
            <div className="w-full h-full rounded-full border-4 border-[var(--md-sys-color-primary)]/20 border-t-[var(--md-sys-color-primary)] animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 28 }}>description</span>
            </div>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-[var(--md-sys-color-on-surface)] font-[Geist] animate-pulse">
              Analyzing your resume...
            </p>
            <p className="text-sm text-[var(--md-sys-color-on-surface-variant)] mt-1 font-[Geist]">
              Detecting skills, evaluating ATS score, and checking skill gaps
            </p>
          </div>
          <div className="flex gap-2">
            {['Extracting Skills', 'Scoring ATS', 'Gap Analysis'].map((step, i) => (
              <div key={step} className="flex items-center gap-1.5 text-xs text-[var(--md-sys-color-on-surface-variant)] px-3 py-1.5 rounded-full bg-white/5 border border-[var(--md-sys-color-outline-variant)]/20 font-[Geist]">
                <div className="w-1.5 h-1.5 rounded-full bg-[var(--md-sys-color-primary)] animate-pulse" style={{ animationDelay: `${i * 200}ms` }} />
                {step}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Results ─── */}
      {result && (
        <div className="space-y-lg">

          {/* ─── Score Overview Cards ─── */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
            {/* ATS Score */}
            <div className="rounded-2xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg flex flex-col items-center gap-md">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">ATS Score</p>
              <ScoreRing score={result.score} />
            </div>

            {/* Skills Breakdown */}
            <div className="rounded-2xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg space-y-md">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">Detection Summary</p>
              {[
                { label: 'Skills Detected', value: result.skills.length, icon: 'code', color: 'text-[var(--md-sys-color-primary)]' },
                { label: 'Certifications', value: result.certs.length, icon: 'workspace_premium', color: 'text-amber-400' },
                { label: 'Education', value: result.education.length, icon: 'school', color: 'text-sky-400' },
              ].map(item => (
                <div key={item.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`material-symbols-outlined ${item.color}`} style={{ fontSize: 18 }}>{item.icon}</span>
                    <span className="text-sm text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">{item.label}</span>
                  </div>
                  <span className={`text-xl font-black font-[Geist] ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>

            {/* Market Readiness */}
            <div className="rounded-2xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg flex flex-col items-center justify-center gap-md">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">Market Readiness</p>
              {readinessData ? (
                <>
                  <div className={`text-5xl font-black font-[Geist] ${getScoreColor(readinessData.readiness_score).color}`}>
                    {readinessData.readiness_score}
                    <span className="text-xl text-[var(--md-sys-color-on-surface-variant)]">/100</span>
                  </div>
                  <span className={`text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded-full border ${getScoreColor(readinessData.readiness_score).color} bg-white/5 border-current/20 font-[Geist]`}>
                    {readinessData.level || 'Intermediate'}
                  </span>
                  {gapData?.target_role && (
                    <div className="text-center">
                      <p className="text-[10px] text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">Best Role Match</p>
                      <p className="text-sm font-bold text-[var(--md-sys-color-primary)] font-[Geist]">{gapData.target_role}</p>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center">
                  <p className="text-4xl font-black font-[Geist] text-[var(--md-sys-color-primary)]">{result.score}%</p>
                  <p className="text-xs text-[var(--md-sys-color-on-surface-variant)] mt-1 font-[Geist]">Based on ATS Score</p>
                </div>
              )}
            </div>
          </div>

          {/* ─── Tabs ─── */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-[var(--md-sys-color-surface-container)]/50 border border-[var(--md-sys-color-outline-variant)]/20 w-fit">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium font-[Geist] transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-[var(--md-sys-color-primary)] text-[var(--md-sys-color-on-primary)] shadow-sm'
                    : 'text-[var(--md-sys-color-on-surface-variant)] hover:text-[var(--md-sys-color-on-surface)]'
                }`}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* ─── Tab: Overview ─── */}
          {activeTab === 'overview' && (
            <div className="space-y-md">
              <div className="rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg">
                <div className="flex items-center gap-2 mb-md">
                  <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 20 }}>code</span>
                  <h3 className="text-base font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
                    Extracted Skills
                    <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] font-medium">{result.skills.length}</span>
                  </h3>
                </div>
                {result.skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.skills.map(skill => <SkillTag key={skill} skill={skill} />)}
                  </div>
                ) : (
                  <div className="py-8 text-center">
                    <span className="material-symbols-outlined text-[var(--md-sys-color-on-surface-variant)]/30 block mb-2" style={{ fontSize: 36 }}>search_off</span>
                    <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">No skills detected. Try uploading a text-based PDF or DOCX resume.</p>
                  </div>
                )}
              </div>

              {result.certs.length > 0 && (
                <div className="rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg">
                  <div className="flex items-center gap-2 mb-md">
                    <span className="material-symbols-outlined text-amber-400" style={{ fontSize: 20 }}>workspace_premium</span>
                    <h3 className="text-base font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">Detected Certifications</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.certs.map(cert => (
                      <span key={cert} className="text-xs px-3 py-1.5 rounded-lg bg-amber-500/12 text-amber-400 border border-amber-500/25 font-medium font-[Geist]">{cert}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ─── Tab: Skill Gap ─── */}
          {activeTab === 'gap' && (
            <div className="space-y-md">
              {gapData ? (
                <>
                  {gapData.coverage_percentage !== undefined && (
                    <div className="rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 20 }}>compare_arrows</span>
                          <h3 className="text-base font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
                            Coverage: {gapData.target_role}
                          </h3>
                        </div>
                        <span className={`text-2xl font-black font-[Geist] ${getScoreColor(gapData.coverage_percentage).color}`}>
                          {Math.round(gapData.coverage_percentage)}%
                        </span>
                      </div>
                      <div className="h-3 rounded-full bg-white/8 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r from-[var(--md-sys-color-primary)] to-emerald-400"
                          style={{ width: `${gapData.coverage_percentage}%` }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
                    <div className="rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg">
                      <div className="flex items-center gap-2 mb-md">
                        <span className="material-symbols-outlined text-emerald-400" style={{ fontSize: 20 }}>check_circle</span>
                        <h4 className="text-sm font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
                          Matching Skills
                          <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-emerald-500/12 text-emerald-400 font-medium">{gapData.matching_skills?.length || 0}</span>
                        </h4>
                      </div>
                      {gapData.matching_skills?.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {gapData.matching_skills.map(s => <SkillTag key={s} skill={s} variant="match" />)}
                        </div>
                      ) : (
                        <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">No matching skills detected against the target role.</p>
                      )}
                    </div>

                    <div className="rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg">
                      <div className="flex items-center gap-2 mb-md">
                        <span className="material-symbols-outlined text-rose-400" style={{ fontSize: 20 }}>cancel</span>
                        <h4 className="text-sm font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
                          Missing Skills
                          <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-rose-500/12 text-rose-400 font-medium">{gapData.missing_skills?.length || 0}</span>
                        </h4>
                      </div>
                      {gapData.missing_skills?.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {gapData.missing_skills.slice(0, 20).map(s => <SkillTag key={s} skill={s} variant="missing" />)}
                        </div>
                      ) : (
                        <p className="text-sm text-emerald-400 font-medium font-[Geist]">🎉 You match all required skills!</p>
                      )}
                    </div>
                  </div>

                  {gapData.recommended_skills?.length > 0 && (
                    <div className="rounded-xl bg-gradient-to-br from-[var(--md-sys-color-primary)]/8 to-violet-500/8 border border-[var(--md-sys-color-primary)]/20 p-lg">
                      <div className="flex items-center gap-2 mb-md">
                        <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 20 }}>bolt</span>
                        <h4 className="text-sm font-bold text-[var(--md-sys-color-primary)] font-[Geist]">Priority Skills to Learn</h4>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {gapData.recommended_skills.map(s => <SkillTag key={s} skill={s} variant="recommend" />)}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-12 text-center">
                  <span className="material-symbols-outlined text-[var(--md-sys-color-on-surface-variant)]/30 block mb-3" style={{ fontSize: 48 }}>compare_arrows</span>
                  <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">Skill gap analysis data unavailable. Ensure you have a career profile set up.</p>
                </div>
              )}
            </div>
          )}

          {/* ─── Tab: AI Feedback ─── */}
          {activeTab === 'feedback' && (
            <div className="space-y-md">
              {[
                {
                  title: 'Strengths',
                  icon: 'check_circle',
                  color: 'text-emerald-400',
                  border: 'border-emerald-500/40',
                  bg: 'from-emerald-500/8',
                  items: result.strengths,
                  empty: 'No specific strengths detected.',
                },
                {
                  title: 'Areas to Improve',
                  icon: 'warning',
                  color: 'text-rose-400',
                  border: 'border-rose-500/40',
                  bg: 'from-rose-500/8',
                  items: result.weaknesses,
                  empty: 'No major weaknesses detected.',
                },
                {
                  title: 'AI Suggestions',
                  icon: 'lightbulb',
                  color: 'text-amber-400',
                  border: 'border-amber-500/40',
                  bg: 'from-amber-500/8',
                  items: result.suggestions,
                  empty: 'No additional suggestions.',
                },
              ].map(section => (
                <div key={section.title} className={`rounded-xl bg-gradient-to-r ${section.bg} to-transparent border-l-4 ${section.border} bg-[var(--md-sys-color-surface-container)] p-lg`}>
                  <div className="flex items-center gap-2 mb-md">
                    <span className={`material-symbols-outlined ${section.color}`} style={{ fontSize: 22 }}>{section.icon}</span>
                    <h3 className={`text-base font-bold ${section.color} font-[Geist]`}>{section.title}</h3>
                  </div>
                  {section.items.length > 0 ? (
                    <ul className="space-y-2">
                      {section.items.map((item, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm text-[var(--md-sys-color-on-surface)] font-[Geist]">
                          <span className={`mt-0.5 w-5 h-5 rounded-full ${section.color} bg-current/10 flex items-center justify-center shrink-0 text-[10px] font-bold`}>{i + 1}</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">{section.empty}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* ─── Analyze Another ─── */}
          <label className="group block cursor-pointer">
            <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.doc,.docx" />
            <div className="flex items-center justify-center gap-2 py-3 rounded-xl border border-dashed border-[var(--md-sys-color-outline-variant)]/40 text-[var(--md-sys-color-on-surface-variant)] hover:text-[var(--md-sys-color-primary)] hover:border-[var(--md-sys-color-primary)]/40 transition-all duration-200 text-sm font-medium font-[Geist]">
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>upload_file</span>
              Analyze Another Resume
            </div>
          </label>
        </div>
      )}
    </div>
  );
}
