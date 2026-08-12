import { useState } from 'react';
import { analyzeResume, getResumeGapAnalysis, getResumeReadiness } from '../api';

function getScoreColor(score) {
  if (score >= 80) return 'text-emerald-400';
  if (score >= 60) return 'text-sky-400';
  if (score >= 40) return 'text-amber-400';
  return 'text-rose-400';
}

function getScoreStroke(score) {
  if (score >= 80) return '#34d399';
  if (score >= 60) return '#38bdf8';
  if (score >= 40) return '#fbbf24';
  return '#fb7185';
}

function ScoreRing({ score }) {
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div className="relative w-40 h-40 mx-auto flex items-center justify-center">
      <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="currentColor" strokeWidth="10" className="text-white/8" />
        <circle
          cx="60" cy="60" r={radius} fill="none" strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ stroke: getScoreStroke(score), transition: 'stroke-dashoffset 1s ease-in-out' }}
        />
      </svg>
      <span className={`text-4xl font-bold ${getScoreColor(score)}`}>{score}</span>
    </div>
  );
}

export default function ResumeAnalysis() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [gapData, setGapData] = useState(null);
  const [readinessData, setReadinessData] = useState(null);

  const handleUpload = async (e) => {
    const selectedFile = e.target.files && e.target.files[0];
    if (!selectedFile) return;

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
        targetRole: analyzeRes.target_role || (gapRes?.target_role) || 'Software Engineer',
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

  return (
    <div className="space-y-lg animate-fade-in-up">

      {/* Header */}
      <header>
        <h1 className="text-3xl font-bold text-on-surface">Resume ATS Analysis</h1>
        <p className="text-on-surface-variant">Upload your resume to get instant ATS score, skill gap, and AI feedback.</p>
      </header>

      {/* Upload Zone */}
      {!result && !analyzing && (
        <div className="border-2 border-dashed border-outline-variant rounded-xl p-xl flex flex-col items-center justify-center bg-surface-container-low hover:bg-surface-container transition-colors cursor-pointer relative">
          <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleUpload} accept=".pdf,.doc,.docx" />
          <span className="material-symbols-outlined text-4xl text-primary mb-sm">upload_file</span>
          <p className="text-lg font-bold text-on-surface">Drop your resume here or click to browse</p>
          <p className="text-sm text-on-surface-variant mt-1">Accepted formats: PDF, DOCX</p>
        </div>
      )}

      {/* Analyzing spinner */}
      {analyzing && (
        <div className="p-xl text-center space-y-md">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-lg font-bold animate-pulse">Analyzing your resume with AI...</p>
          <p className="text-sm text-on-surface-variant">Detecting 300+ skills, scoring ATS fit, checking skill gaps…</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">

          {/* ─── Left Column ─── */}
          <div className="md:col-span-1 space-y-md">

            {/* ATS Score */}
            <div className="glass-effect p-lg rounded-xl text-center space-y-sm">
              <h3 className="font-bold text-on-surface-variant uppercase tracking-wider text-sm">ATS Score</h3>
              <ScoreRing score={result.score} />
              <p className={`text-xs font-bold uppercase tracking-wider ${getScoreColor(result.score)}`}>
                {result.score >= 80 ? 'Excellent' : result.score >= 60 ? 'Good' : result.score >= 40 ? 'Average' : 'Needs Work'}
              </p>
            </div>

            {/* Target Role */}
            <div className="glass-effect p-md rounded-xl text-center border border-outline-variant">
              <h3 className="font-bold text-on-surface-variant uppercase tracking-wider text-xs mb-1">Target Role Match</h3>
              <div className="text-lg font-bold text-primary">{result.targetRole}</div>
            </div>

            {/* Market Readiness */}
            {readinessData && (
              <div className="glass-effect p-lg rounded-xl text-center bg-surface-container-low border border-outline-variant">
                <h3 className="font-bold text-on-surface-variant uppercase tracking-wider text-sm mb-2">Market Readiness</h3>
                <div className={`text-3xl font-black mb-1 ${getScoreColor(readinessData.readiness_score)}`}>
                  {readinessData.readiness_score}/100
                </div>
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-success/10 text-success border border-success/20">
                  {readinessData.level}
                </div>
              </div>
            )}

            {/* Extracted Skills */}
            <div className="glass-effect p-md rounded-xl">
              <h3 className="font-bold text-on-surface-variant mb-sm flex items-center gap-2">
                Extracted Skills
                <span className="px-2 py-0.5 rounded-full text-xs bg-primary/12 text-primary font-medium">{result.skills.length}</span>
              </h3>
              {result.skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {result.skills.map(s => (
                    <span key={s} className="px-3 py-1 bg-surface-container-high text-on-surface rounded-full text-xs font-medium border border-outline-variant">{s}</span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-on-surface-variant">No skills detected. Try a text-based PDF resume.</p>
              )}
            </div>

            {/* Certs */}
            {result.certs.length > 0 && (
              <div className="glass-effect p-md rounded-xl">
                <h3 className="font-bold text-on-surface-variant mb-sm">Certifications Detected</h3>
                <div className="flex flex-wrap gap-2">
                  {result.certs.map(c => (
                    <span key={c} className="px-2 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded text-xs font-bold">{c}</span>
                  ))}
                </div>
              </div>
            )}

            <label className="block cursor-pointer">
              <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.doc,.docx" />
              <div className="w-full py-2 bg-outline/10 hover:bg-outline/20 rounded-lg font-bold transition-colors text-center text-sm text-on-surface-variant">
                Analyze Another Resume
              </div>
            </label>
          </div>

          {/* ─── Right Column ─── */}
          <div className="md:col-span-2 space-y-md">

            {/* Skill Gap */}
            {gapData && (
              <div className="bg-surface border border-outline-variant rounded-xl p-lg space-y-md">
                <div className="flex items-center justify-between border-b border-outline-variant/50 pb-2">
                  <h3 className="text-xl font-bold">Skill Gap Analysis</h3>
                  {gapData.coverage_percentage !== undefined && (
                    <span className={`text-sm font-bold ${getScoreColor(gapData.coverage_percentage)}`}>
                      {Math.round(gapData.coverage_percentage)}% covered
                    </span>
                  )}
                </div>

                {/* Coverage bar */}
                {gapData.coverage_percentage !== undefined && (
                  <div className="h-2 rounded-full bg-white/8 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{ width: `${gapData.coverage_percentage}%`, background: getScoreStroke(gapData.coverage_percentage) }}
                    />
                  </div>
                )}

                <div>
                  <h4 className="text-sm font-bold text-on-surface-variant mb-2 flex items-center gap-1">
                    <span className="material-symbols-outlined text-emerald-400 text-sm">check_circle</span>
                    Matching Market Skills
                    <span className="ml-1 px-2 py-0.5 rounded-full text-xs bg-emerald-500/12 text-emerald-400">{gapData.matching_skills?.length || 0}</span>
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {gapData.matching_skills?.map(s => (
                      <span key={s} className="px-2 py-1 bg-success/10 text-success border border-success/20 rounded text-xs font-bold">{s}</span>
                    ))}
                    {!gapData.matching_skills?.length && <span className="text-sm text-on-surface-variant">No top market skills matched yet.</span>}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-on-surface-variant mb-2 flex items-center gap-1">
                    <span className="material-symbols-outlined text-error text-sm">cancel</span>
                    Missing Market Skills
                    <span className="ml-1 px-2 py-0.5 rounded-full text-xs bg-error/12 text-error">{gapData.missing_skills?.length || 0}</span>
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {gapData.missing_skills?.slice(0, 15).map(s => (
                      <span key={s} className="px-2 py-1 bg-error/10 text-error border border-error/20 rounded text-xs font-bold">{s}</span>
                    ))}
                  </div>
                </div>

                {gapData.recommended_skills?.length > 0 && (
                  <div className="bg-primary/5 p-md rounded-lg border border-primary/20">
                    <h4 className="text-sm font-bold text-primary mb-2 flex items-center gap-1">
                      <span className="material-symbols-outlined text-sm">bolt</span>
                      Recommended to Learn
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {gapData.recommended_skills.map(s => (
                        <span key={s} className="px-2 py-1 bg-primary text-on-primary rounded text-xs font-bold shadow-sm">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Strengths */}
            {result.strengths.length > 0 && (
              <div className="bg-surface-container-low border-l-4 border-success p-md rounded-r-xl shadow-sm">
                <h3 className="font-bold text-success flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined">check_circle</span> Strengths
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  {result.strengths.map((s, i) => <li key={i} className="text-sm">{s}</li>)}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {result.weaknesses.length > 0 && (
              <div className="bg-surface-container-low border-l-4 border-error p-md rounded-r-xl shadow-sm">
                <h3 className="font-bold text-error flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined">warning</span> Areas to Improve
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  {result.weaknesses.map((s, i) => <li key={i} className="text-sm">{s}</li>)}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {result.suggestions.length > 0 && (
              <div className="bg-surface-container-low border-l-4 border-warning p-md rounded-r-xl shadow-sm">
                <h3 className="font-bold text-warning flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined">lightbulb</span> AI Suggestions
                </h3>
                <ul className="list-disc pl-5 space-y-1">
                  {result.suggestions.map((s, i) => <li key={i} className="text-sm">{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
