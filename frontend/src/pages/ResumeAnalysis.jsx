import { useState } from 'react';
import { analyzeResume, getResumeGapAnalysis, getResumeReadiness } from '../api';

export default function ResumeAnalysis() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [gapData, setGapData] = useState(null);
  const [readinessData, setReadinessData] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setAnalyzing(true);
      try {
        const analyzeRes = await analyzeResume(selectedFile);
        const resumeId = analyzeRes.id || analyzeRes.resume_id;
        
        // Fetch gap analysis and readiness
        const [gapRes, readinessRes] = await Promise.all([
          getResumeGapAnalysis(resumeId).catch(() => null),
          getResumeReadiness(resumeId).catch(() => null)
        ]);

        setResult({
          score: analyzeRes.ats_score,
          skills: analyzeRes.extracted_skills || [],
          strengths: analyzeRes.strengths || ['Formatting looks generally solid', 'Contains relevant keywords'],
          weaknesses: analyzeRes.weaknesses || ['Some bullet points could be quantified'],
          suggestions: analyzeRes.suggestions || ['Add specific metrics to achievements'],
          targetRole: analyzeRes.target_role || 'Software Engineer',
          skillGaps: analyzeRes.skill_gaps || [],
          certs: analyzeRes.extracted_certifications || [],
          experience: analyzeRes.extracted_experience || [],
          education: analyzeRes.extracted_education || [],
        });
        setGapData(gapRes);
        setReadinessData(readinessRes);
      } catch (err) {
        console.error(err);
        alert('Failed to analyze resume.');
      } finally {
        setAnalyzing(false);
      }
    }
  };

  return (
    <div className="space-y-lg animate-fade-in-up">
      <header>
        <h1 className="text-3xl font-bold text-on-surface">Resume ATS Analysis</h1>
        <p className="text-on-surface-variant">Upload your resume to get instant optimization tips.</p>
      </header>

      {!result && !analyzing && (
        <div className="border-2 border-dashed border-outline-variant rounded-xl p-xl flex flex-col items-center justify-center bg-surface-container-low hover:bg-surface-container transition-colors cursor-pointer relative">
          <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleUpload} accept=".pdf,.doc,.docx" />
          <span className="material-symbols-outlined text-4xl text-primary mb-sm">upload_file</span>
          <p className="text-lg font-bold text-on-surface">Drop your resume here or click to browse</p>
          <p className="text-sm text-on-surface-variant mt-1">Accepted formats: PDF, DOCX</p>
        </div>
      )}

      {analyzing && (
        <div className="p-xl text-center space-y-md">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-lg font-bold animate-pulse">Analyzing your resume with AI...</p>
        </div>
      )}

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
          <div className="md:col-span-1 space-y-md">
            <div className="glass-effect p-lg rounded-xl text-center">
              <h3 className="font-bold text-on-surface-variant uppercase tracking-wider text-sm mb-4">ATS Score</h3>
              <div className="relative w-40 h-40 mx-auto flex items-center justify-center rounded-full border-8 border-primary/20">
                <div className="absolute inset-0 rounded-full border-8 border-primary border-t-transparent transform rotate-45" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }}></div>
                <span className="text-4xl font-bold text-primary">{result.score}</span>
              </div>
            </div>
            
            <div className="glass-effect p-md rounded-xl text-center border border-outline-variant">
              <h3 className="font-bold text-on-surface-variant uppercase tracking-wider text-xs mb-1">Target Role Match</h3>
              <div className="text-lg font-bold text-primary">{result.targetRole}</div>
            </div>

            {readinessData && (
              <div className="glass-effect p-lg rounded-xl text-center bg-surface-container-low border border-outline-variant">
                <h3 className="font-bold text-on-surface-variant uppercase tracking-wider text-sm mb-2">Market Readiness</h3>
                <div className="text-3xl font-black mb-1 text-success">{readinessData.readiness_score}/100</div>
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-success/10 text-success border border-success/20">
                  {readinessData.level}
                </div>
              </div>
            )}

            <div className="glass-effect p-md rounded-xl">
              <h3 className="font-bold text-on-surface-variant mb-sm">Extracted Skills ({result.skills.length})</h3>
              <div className="flex flex-wrap gap-2">
                {result.skills.map(s => <span key={s} className="px-3 py-1 bg-surface-container-high text-on-surface rounded-full text-xs font-medium border border-outline-variant">{s}</span>)}
              </div>
            </div>
            <button onClick={() => setResult(null)} className="w-full py-2 bg-outline/10 hover:bg-outline/20 rounded-lg font-bold transition-colors">Analyze Another</button>
          </div>
          
          <div className="md:col-span-2 space-y-md">
            {gapData && (
              <div className="bg-surface border border-outline-variant rounded-xl p-lg space-y-md">
                <h3 className="text-xl font-bold border-b border-outline-variant/50 pb-2">Skill Gap Analysis</h3>
                
                <div>
                  <h4 className="text-sm font-bold text-on-surface-variant mb-2">✅ Matching Market Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {gapData.matching_skills?.map(s => <span key={s} className="px-2 py-1 bg-success/10 text-success border border-success/20 rounded text-xs font-bold">{s}</span>)}
                    {gapData.matching_skills?.length === 0 && <span className="text-sm text-on-surface-variant">No top market skills matched.</span>}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-on-surface-variant mb-2">❌ Missing Market Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {gapData.missing_skills?.slice(0, 15).map(s => <span key={s} className="px-2 py-1 bg-error/10 text-error border border-error/20 rounded text-xs font-bold">{s}</span>)}
                  </div>
                </div>

                <div className="bg-primary/5 p-md rounded-lg border border-primary/20">
                  <h4 className="text-sm font-bold text-primary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-sm">bolt</span> Recommended to Learn</h4>
                  <div className="flex flex-wrap gap-2">
                    {gapData.recommended_skills?.map(s => <span key={s} className="px-2 py-1 bg-primary text-on-primary rounded text-xs font-bold shadow-sm">{s}</span>)}
                  </div>
                </div>
              </div>
            )}
            <div className="bg-surface-container-low border-l-4 border-success p-md rounded-r-xl shadow-sm">
              <h3 className="font-bold text-success flex items-center gap-2 mb-2"><span className="material-symbols-outlined">check_circle</span> Strengths</h3>
              <ul className="list-disc pl-5 space-y-1">
                {result.strengths.map(s => <li key={s} className="text-sm">{s}</li>)}
              </ul>
            </div>
            
            <div className="bg-surface-container-low border-l-4 border-error p-md rounded-r-xl shadow-sm">
              <h3 className="font-bold text-error flex items-center gap-2 mb-2"><span className="material-symbols-outlined">warning</span> Areas to Improve</h3>
              <ul className="list-disc pl-5 space-y-1">
                {result.weaknesses.map(s => <li key={s} className="text-sm">{s}</li>)}
              </ul>
            </div>
            
            <div className="bg-surface-container-low border-l-4 border-warning p-md rounded-r-xl shadow-sm">
              <h3 className="font-bold text-warning flex items-center gap-2 mb-2"><span className="material-symbols-outlined">lightbulb</span> AI Suggestions</h3>
              <ul className="list-disc pl-5 space-y-1">
                {result.suggestions.map(s => <li key={s} className="text-sm">{s}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
