import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { getFastGrowingCareers, getCareerRoadmap } from '../api';

const DOMAIN_CATEGORIES = [
  'All',
  'Software Engineering',
  'Data & AI',
  'Cloud & DevOps',
  'Product & Management',
  'Cybersecurity'
];

const DOMAIN_MAPPING = {
  'software engineer': 'Software Engineering',
  'full stack developer': 'Software Engineering',
  'frontend developer': 'Software Engineering',
  'backend developer': 'Software Engineering',
  'sde': 'Software Engineering',
  'sde-1': 'Software Engineering',
  'sde-2': 'Software Engineering',
  'java developer': 'Software Engineering',
  'python developer': 'Software Engineering',
  'software developer': 'Software Engineering',
  'data scientist': 'Data & AI',
  'data engineer': 'Data & AI',
  'data analyst': 'Data & AI',
  'machine learning engineer': 'Data & AI',
  'ml engineer': 'Data & AI',
  'ai engineer': 'Data & AI',
  'artificial intelligence engineer': 'Data & AI',
  'mlops engineer': 'Data & AI',
  'applied scientist': 'Data & AI',
  'research scientist': 'Data & AI',
  'computer vision engineer': 'Data & AI',
  'senior data engineer': 'Data & AI',
  'senior data analyst': 'Data & AI',
  'product manager': 'Product & Management',
  'senior product manager': 'Product & Management',
  'associate product manager': 'Product & Management',
  'technical product manager': 'Product & Management',
  'apm': 'Product & Management',
  'product owner': 'Product & Management',
  'business analyst': 'Product & Management',
  'analytics consultant': 'Product & Management',
  'systems engineer': 'Cloud & DevOps',
  'data platform engineer': 'Cloud & DevOps',
};

const SALARY_ESTIMATES = {
  'Software Engineering': '₹12 - ₹35 LPA',
  'Data & AI': '₹15 - ₹42 LPA',
  'Cloud & DevOps': '₹14 - ₹38 LPA',
  'Product & Management': '₹18 - ₹45 LPA',
  'Cybersecurity': '₹14 - ₹36 LPA',
};

const QUIZ_QUESTIONS = [
  {
    id: 'interest',
    title: '1. What type of work excites you most?',
    options: [
      { label: 'Building web apps, user interfaces, and full stack systems', domain: 'Software Engineering' },
      { label: 'Analyzing data, training ML models, and generative AI', domain: 'Data & AI' },
      { label: 'Designing cloud infrastructure, CI/CD pipelines, and scalability', domain: 'Cloud & DevOps' },
      { label: 'Leading product features, user research, and tech strategy', domain: 'Product & Management' },
    ]
  },
  {
    id: 'experience',
    title: '2. What is your current experience level?',
    options: [
      { label: 'Student / Early Career (0 - 1 years)', level: 'entry' },
      { label: 'Junior Engineer (1 - 3 years)', level: 'junior' },
      { label: 'Mid-Level Professional (3 - 5 years)', level: 'mid' },
      { label: 'Senior / Lead (5+ years)', level: 'senior' },
    ]
  },
  {
    id: 'strength',
    title: '3. What is your strongest core technical strength?',
    options: [
      { label: 'Coding in Python, JavaScript, Java, or C++', domain: 'Software Engineering' },
      { label: 'Statistics, SQL, data structures, and mathematical algorithms', domain: 'Data & AI' },
      { label: 'Linux systems, Docker, AWS/GCP, and networking', domain: 'Cloud & DevOps' },
      { label: 'Communication, user empathy, roadmap planning, and analytics', domain: 'Product & Management' },
    ]
  }
];

export default function CareerExplorer() {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [selectedRole, setSelectedRole] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [roadmapLoading, setRoadmapLoading] = useState(false);

  // Career Assessment state
  const [showAssessment, setShowAssessment] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);

  useEffect(() => {
    async function loadRoles() {
      try {
        setLoading(true);
        const data = await getFastGrowingCareers();
        const rolesList = data.roles || [];
        const mapped = rolesList.map(item => {
          const titleLower = item.title.toLowerCase();
          const domain = DOMAIN_MAPPING[titleLower] || 'Software Engineering';
          const salary = SALARY_ESTIMATES[domain] || '₹12 - ₹30 LPA';
          return {
            id: item.title,
            title: item.title,
            domain,
            salary,
            growth: item.growth_signal,
            totalPostings: item.total_postings,
            recentPostings: item.recent_postings,
          };
        });
        setRoles(mapped);
        if (mapped.length > 0) {
          handleSelectRole(mapped[0]);
        }
      } catch (err) {
        console.error('Failed to load careers:', err);
      } finally {
        setLoading(false);
      }
    }
    loadRoles();
  }, []);

  const handleSelectRole = async (role) => {
    setSelectedRole(role);
    setRoadmapLoading(true);
    try {
      const data = await getCareerRoadmap(role.title);
      setRoadmap(data);
    } catch (err) {
      console.error('Failed to load roadmap:', err);
      setRoadmap(null);
    } finally {
      setRoadmapLoading(false);
    }
  };

  const handleCompleteAssessment = () => {
    const primaryDomain = quizAnswers.interest || quizAnswers.strength || 'Software Engineering';
    setQuizResult({
      recommendedDomain: primaryDomain,
      level: quizAnswers.experience || 'junior',
    });
    setSelectedDomain(primaryDomain);
    setShowAssessment(false);
  };

  const filteredRoles = useMemo(() => {
    return roles.filter(role => {
      const matchesSearch = !searchQuery || role.title.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesDomain = selectedDomain === 'All' || role.domain === selectedDomain;
      return matchesSearch && matchesDomain;
    });
  }, [roles, searchQuery, selectedDomain]);

  return (
    <div className="space-y-lg animate-fade-in-up pb-16">
      {/* ─── Hero Header ─── */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-on-surface font-[Geist]">
            Career Explorer & Roadmaps
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Explore fast-growing tech roles, interactive learning paths, and live industry demand.
          </p>
        </div>

        <button
          onClick={() => setShowAssessment(!showAssessment)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold bg-primary text-on-primary hover:brightness-110 shadow-sm transition-all self-start md:self-auto"
        >
          <span className="material-symbols-outlined text-base">psychology</span>
          {showAssessment ? 'Close Match Assessment' : '🎯 1-Min Career Match Quiz'}
        </button>
      </header>

      {/* ─── Interactive Career Match Assessment (Modal / Accordion) ─── */}
      {showAssessment && (
        <div className="bg-surface-container-lowest border-2 border-primary/30 rounded-2xl p-4 sm:p-lg space-y-md animate-fade-in shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-primary">
              <span className="material-symbols-outlined text-2xl">auto_awesome</span>
              <h2 className="text-lg font-bold text-on-surface font-[Geist]">Career Compatibility Assessment</h2>
            </div>
            <button
              onClick={() => setShowAssessment(false)}
              className="text-on-surface-variant hover:text-on-surface p-1"
            >
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>
          <p className="text-xs text-on-surface-variant">
            Answer 3 quick questions to discover your highest-compatibility tech roles.
          </p>

          <div className="space-y-4 pt-2">
            {QUIZ_QUESTIONS.map(q => (
              <div key={q.id} className="space-y-2">
                <p className="text-xs font-bold text-on-surface">{q.title}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {q.options.map((opt, i) => {
                    const val = opt.domain || opt.level;
                    const isSelected = quizAnswers[q.id] === val;
                    return (
                      <button
                        key={i}
                        onClick={() => setQuizAnswers(prev => ({ ...prev, [q.id]: val }))}
                        className={`text-left p-2.5 rounded-xl border text-xs font-medium transition-all ${
                          isSelected
                            ? 'bg-primary/10 border-primary text-primary font-bold shadow-sm'
                            : 'bg-surface-container hover:bg-surface-container-high border-outline-variant/60 text-on-surface-variant'
                        }`}
                      >
                        {opt.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-outline-variant flex justify-end gap-2">
            <button
              onClick={() => {
                setQuizAnswers({});
                setQuizResult(null);
                setShowAssessment(false);
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-on-surface-variant hover:bg-surface-container"
            >
              Reset
            </button>
            <button
              onClick={handleCompleteAssessment}
              disabled={Object.keys(quizAnswers).length < 2}
              className="px-4 py-2 rounded-lg text-xs font-bold bg-primary text-on-primary disabled:opacity-50 hover:brightness-110"
            >
              Show My Career Matches →
            </button>
          </div>
        </div>
      )}

      {/* ─── Match Result Banner ─── */}
      {quizResult && (
        <div className="flex items-center justify-between p-3 sm:p-4 rounded-xl bg-primary/10 border border-primary/20 text-xs sm:text-sm">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">verified</span>
            <span>
              Top Match Domain: <strong className="text-primary">{quizResult.recommendedDomain}</strong> ({filteredRoles.length} matching roles)
            </span>
          </div>
          <button
            onClick={() => {
              setQuizResult(null);
              setSelectedDomain('All');
            }}
            className="text-xs text-primary font-bold hover:underline"
          >
            Clear Filter
          </button>
        </div>
      )}

      {/* ─── Search & Domain Filter Bar ─── */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="flex-1 max-w-md relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-base">
            search
          </span>
          <input
            type="text"
            placeholder="Search roles (e.g. AI Engineer, Full Stack, SDE)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-xl bg-surface-container border border-outline-variant/60 focus:outline-none focus:border-primary text-on-surface"
          />
        </div>

        <div className="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
          {DOMAIN_CATEGORIES.map(domain => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap ${
                selectedDomain === domain
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'
              }`}
            >
              {domain}
            </button>
          ))}
        </div>
      </div>

      {/* ─── Role Cards Grid ─── */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-44 bg-surface-container rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filteredRoles.length === 0 ? (
        <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-8 text-center space-y-3">
          <span className="material-symbols-outlined text-4xl text-on-surface-variant">search_off</span>
          <h3 className="font-bold text-on-surface">No career paths found matching &ldquo;{searchQuery}&rdquo;</h3>
          <p className="text-xs text-on-surface-variant">Try selecting another domain or clearing your search filter.</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedDomain('All');
            }}
            className="px-4 py-2 rounded-lg text-xs font-bold bg-primary text-on-primary hover:brightness-110"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRoles.map(role => {
            const isSelected = selectedRole?.title === role.title;
            return (
              <div
                key={role.id}
                onClick={() => handleSelectRole(role)}
                className={`bg-surface-container-lowest border p-4 sm:p-md rounded-2xl cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'border-primary ring-2 ring-primary/20 shadow-md bg-primary/[0.02]'
                    : 'border-outline-variant hover:border-primary/50'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-primary font-[Geist]">
                        {role.domain}
                      </span>
                      <h3 className="font-bold text-base sm:text-lg text-on-surface capitalize leading-snug">
                        {role.title}
                      </h3>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 shrink-0">
                      {role.growth}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 my-3 pt-2 border-t border-outline-variant/40 text-xs">
                    <div>
                      <span className="text-on-surface-variant text-[10px] block">Estimated Salary</span>
                      <span className="font-bold text-on-surface">{role.salary}</span>
                    </div>
                    <div>
                      <span className="text-on-surface-variant text-[10px] block">Live Openings</span>
                      <span className="font-bold text-primary">{role.totalPostings} active</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2 border-t border-outline-variant/40">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectRole(role);
                    }}
                    className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-bold text-center transition-colors ${
                      isSelected
                        ? 'bg-primary text-on-primary'
                        : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                    }`}
                  >
                    {isSelected ? 'Roadmap Selected' : 'View Roadmap'}
                  </button>

                  <Link
                    to={`/app/opportunities?query=${encodeURIComponent(role.title)}`}
                    onClick={(e) => e.stopPropagation()}
                    className="py-1.5 px-2.5 rounded-lg text-xs font-bold bg-surface-container hover:bg-primary hover:text-on-primary text-primary transition-colors flex items-center justify-center gap-0.5"
                    title={`Search open ${role.title} jobs`}
                  >
                    <span>Jobs</span>
                    <span className="material-symbols-outlined text-[13px]">open_in_new</span>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ─── Roadmap Generator Details ─── */}
      {selectedRole && (
        <section className="mt-8 bg-surface-container-lowest border border-outline-variant rounded-2xl p-4 sm:p-lg space-y-md animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-outline-variant/60">
            <div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">route</span>
                <h2 className="text-lg sm:text-xl font-bold text-on-surface font-[Geist] capitalize">
                  Learning Roadmap: {selectedRole.title}
                </h2>
              </div>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Structured step-by-step career path and essential competencies.
              </p>
            </div>

            <Link
              to={`/app/opportunities?query=${encodeURIComponent(selectedRole.title)}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary/10 text-primary font-bold text-xs hover:bg-primary hover:text-on-primary transition-colors self-start sm:self-auto"
            >
              <span>Explore {selectedRole.title} Openings</span>
              <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
            </Link>
          </div>

          {roadmapLoading ? (
            <div className="space-y-3 py-4">
              <div className="h-6 bg-surface-container rounded w-3/4 animate-pulse" />
              <div className="h-20 bg-surface-container rounded-xl animate-pulse" />
              <div className="h-20 bg-surface-container rounded-xl animate-pulse" />
            </div>
          ) : roadmap ? (
            <div className="space-y-lg pt-2">
              {roadmap.description && (
                <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  {roadmap.description}
                </p>
              )}

              {/* Strategies and Concepts Cards */}
              {(roadmap.strategies || roadmap.what_to_learn) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {roadmap.strategies && (
                    <div className="bg-surface-container p-4 rounded-xl space-y-2 border border-outline-variant/40">
                      <h3 className="font-bold text-xs sm:text-sm text-primary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-base">lightbulb</span>
                        Key Preparation Strategies
                      </h3>
                      <ul className="space-y-1.5 text-xs text-on-surface-variant list-disc pl-4">
                        {roadmap.strategies.map((strategy, idx) => (
                          <li key={idx}>{strategy}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {roadmap.what_to_learn && (
                    <div className="bg-surface-container p-4 rounded-xl space-y-2 border border-outline-variant/40">
                      <h3 className="font-bold text-xs sm:text-sm text-secondary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-base">menu_book</span>
                        Essential Concepts to Master
                      </h3>
                      <ul className="space-y-1.5 text-xs text-on-surface-variant list-disc pl-4">
                        {roadmap.what_to_learn.map((concept, idx) => (
                          <li key={idx}>{concept}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Step-by-Step Execution */}
              {roadmap.steps && roadmap.steps.length > 0 && (
                <div className="space-y-3 pt-2">
                  <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider font-[Geist]">
                    Step-by-Step Execution Milestone
                  </h3>

                  <div className="space-y-3">
                    {roadmap.steps.map((step, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl bg-surface-container-low border border-outline-variant/60 flex flex-col sm:flex-row sm:items-start gap-3 hover:border-primary/40 transition-colors"
                      >
                        <div className="w-7 h-7 rounded-full bg-primary text-on-primary font-bold text-xs flex items-center justify-center shrink-0">
                          {step.step_number || idx + 1}
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                            <h4 className="font-bold text-sm text-on-surface">{step.title}</h4>
                            {step.estimated_weeks && (
                              <span className="text-[11px] font-semibold text-primary px-2 py-0.5 bg-primary/10 rounded-full self-start sm:self-auto">
                                ~{step.estimated_weeks} weeks
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-on-surface-variant leading-relaxed">
                            {step.description}
                          </p>
                          {step.skills && step.skills.length > 0 && (
                            <div className="flex flex-wrap gap-1.5 pt-1.5">
                              {step.skills.map(s => (
                                <span
                                  key={s}
                                  className="text-[10px] font-medium px-2 py-0.5 rounded bg-surface border border-outline-variant/60 text-on-surface-variant"
                                >
                                  {s}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-on-surface-variant py-4 text-center">
              Roadmap details currently being compiled for {selectedRole.title}.
            </p>
          )}
        </section>
      )}
    </div>
  );
}

