import { useState, useEffect, useContext, useRef } from 'react';
import { AuthContext } from '../App';
import { getInterviewPrep } from '../api';

const categories = ['Technical', 'Behavioral', 'System Design', 'HR', 'Case Study'];

const categoryMeta = {
  Technical:     { icon: 'code',            color: 'bg-primary',   ring: '#0050cb', completed: 8, total: 12 },
  Behavioral:    { icon: 'psychology',      color: 'bg-info',      ring: '#0ea5e9', completed: 6, total: 10 },
  'System Design': { icon: 'architecture',  color: 'bg-warning',   ring: '#f59e0b', completed: 3, total: 8  },
  HR:            { icon: 'handshake',       color: 'bg-success',   ring: '#16a34a', completed: 5, total: 6  },
  'Case Study':  { icon: 'query_stats',    color: 'bg-error',     ring: '#ba1a1a', completed: 2, total: 5  },
};

const defaultQuestions = [
  // Technical
  { id: 1, category: 'Technical', difficulty: 'Medium', time: '8 min', question: 'Explain the difference between `useEffect` cleanup functions and `componentWillUnmount`. When would each be used?', answer: 'useEffect cleanup runs before every re-render (if deps change) and on unmount, making it more versatile than componentWillUnmount which only fires once. Cleanup functions handle subscription removal, timer clearing, and API call cancellation. The key advantage is that useEffect ties cleanup to the specific effect instance, preventing stale closure bugs common in class components.' },
  { id: 2, category: 'Technical', difficulty: 'Hard', time: '10 min', question: 'How does indexing work under the hood in PostgreSQL/B-Trees, and how do composite indexes impact multi-column query performance?', answer: 'B-Tree indexes maintain a balanced tree structure where leaf nodes contain pointers to table rows. A composite index (colA, colB) follows left-to-right prefix matching rule: queries filtering on colA or (colA + colB) use the index effectively, whereas queries filtering only on colB cannot use the index.' },
  { id: 3, category: 'Technical', difficulty: 'Medium', time: '7 min', question: 'What is the difference between optimistic and pessimistic locking in database transaction management?', answer: 'Pessimistic locking locks the records immediately upon reading (SELECT ... FOR UPDATE) to prevent concurrency conflicts. Optimistic locking assumes conflicts are rare, checking a version timestamp/number column at update time (UPDATE ... WHERE version = old_version) and rolling back if modified.' },
  
  // Behavioral
  { id: 4, category: 'Behavioral', difficulty: 'Medium', time: '6 min', question: 'Tell me about a time you had to push back on a stakeholder\'s request. How did you handle it and what was the outcome?', answer: 'Use the STAR framework: describe the Situation (tight deadline, conflicting requirements), Task (your responsibility), Action (data-driven communication, proposed alternatives, scheduled follow-up), and Result (measurable outcome). Emphasize empathy, active listening, and finding common ground while maintaining technical integrity.' },
  { id: 5, category: 'Behavioral', difficulty: 'Medium', time: '6 min', question: 'Describe a situation where a project failed or missed a critical deadline. What did you learn?', answer: 'Structure with STAR: focus on accountability without blaming others. Highlight what systemic improvements you implemented post-incident (e.g. setting up automated regression tests, improving task breakdown granularity, or adding buffer margins to estimates).' },

  // System Design
  { id: 6, category: 'System Design', difficulty: 'Hard', time: '20 min', question: 'Design a distributed rate limiter (e.g. 100 requests per minute per user IP) for an API gateway.', answer: 'Discuss Token Bucket or Sliding Window Log algorithms. Implement via Redis using Atomic Lua scripts (`EVAL`) to check and increment key counters across multi-node stateless API gateways to prevent race conditions.' },
  { id: 7, category: 'System Design', difficulty: 'Hard', time: '18 min', question: 'How would you design a real-time notifications system delivering push/email/SMS alerts to 10M users?', answer: 'Architecture: Microservices publishing events to Kafka -> Consumer workers querying user notification preferences -> Dispatching to Push services (FCM/APNS), Email gateways (SendGrid/SES), or SMS APIs (Twilio) with exponential backoff retry queues in Celery/RabbitMQ.' },

  // HR
  { id: 8, category: 'HR', difficulty: 'Easy', time: '4 min', question: 'What are your salary expectations for this role, and how do you evaluate compensation packages?', answer: 'State that your expectations are aligned with industry standard market benchmarks for senior roles in India/remote. Emphasize evaluating total compensation (Base Salary, Performance Bonuses, ESOPs/Stocks, Health Benefits, and Learning Allowances).' },
  { id: 9, category: 'HR', difficulty: 'Easy', time: '3 min', question: 'Why are you looking to leave your current position?', answer: 'Keep the response positive and forward-looking. Focus on seeking new technical challenges, greater scope of ownership, faster career growth, and alignment with the target company\'s technology stack and vision.' },

  // Case Study
  { id: 10, category: 'Case Study', difficulty: 'Hard', time: '15 min', question: 'A critical checkout API latency increased from 200ms to 4.5 seconds during a flash sale. How do you debug it live?', answer: '1. Check APM trace spans (New Relic/Datadog) to identify whether latency is in DB queries, third-party payment gateway, or CPU throttling. 2. Inspect DB connection pool starvation. 3. Temporarily enable circuit breaker / fallback caches, and apply rate limiting.' }
];

const tips = [
  { icon: 'lightbulb', title: 'Use the STAR Method', desc: 'Structure behavioral answers with Situation, Task, Action, and Result for maximum clarity.' },
  { icon: 'timer', title: 'Practice Under Time Pressure', desc: 'Real interviews have strict time limits. Use mock sessions to build comfort under constraints.' },
  { icon: 'record_voice_over', title: 'Think Out Loud', desc: 'Interviewers value your thought process as much as the final answer. Speak through your reasoning.' },
  { icon: 'edit_note', title: 'Prepare Questions', desc: 'Always have 3-5 thoughtful questions ready for your interviewer about tech stack & culture.' },
  { icon: 'trending_up', title: 'Quantify Your Impact', desc: 'Use concrete metrics and numbers to demonstrate the impact of your past accomplishments.' },
  { icon: 'architecture', title: 'Start System Design Broad', desc: 'Outline high-level components (load balancer, DB, cache) before diving into deep technical trade-offs.' },
  { icon: 'groups', title: 'Mock with Peers', desc: 'Practice with friends or mentors for realistic feedback you can\'t get from solo prep.' },
  { icon: 'verified', title: 'Be Honest About Gaps', desc: 'If you don\'t know an answer, admit it confidently and explain how you would research it.' }
];

const difficultyStyles = {
  Easy:   'bg-emerald-100 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Hard:   'bg-red-100 text-red-700 border-red-200',
};

/* ─── Circular Progress Ring ─── */
function ProgressRing({ radius = 36, stroke = 5, progress, color }) {
  const normalizedRadius = radius - stroke;
  const circumference = 2 * Math.PI * normalizedRadius;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
      <circle
        stroke="currentColor"
        className="text-surface-container"
        fill="transparent"
        strokeWidth={stroke}
        r={normalizedRadius}
        cx={radius}
        cy={radius}
      />
      <circle
        stroke={color}
        fill="transparent"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${circumference} ${circumference}`}
        strokeDashoffset={offset}
        r={normalizedRadius}
        cx={radius}
        cy={radius}
        className="transition-all duration-1000 ease-out"
      />
    </svg>
  );
}

export default function InterviewPrep() {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('Technical');
  const [expandedCards, setExpandedCards] = useState(new Set());
  const [mockActive, setMockActive] = useState(false);
  const [mockQuestionIndex, setMockQuestionIndex] = useState(0);
  const [mockAnswer, setMockAnswer] = useState('');
  const [timer, setTimer] = useState(0);
  const [timerRunning, setTimerRunning] = useState(false);
  const [mockCompleted, setMockCompleted] = useState(false);
  const timerRef = useRef(null);
  const tabsRef = useRef(null);

  const [questions, setQuestions] = useState(defaultQuestions);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchQuestions() {
      try {
        setLoading(true);
        // Fallback to "Software Developer" if role isn't explicitly set 
        const roleQuery = user?.jobTitle || "Software Developer";
        const data = await getInterviewPrep(roleQuery);
        if (data && data.length > 0) {
          const formatted = data.map((q, i) => ({
            id: i + 1,
            category: q.category,
            difficulty: q.difficulty,
            time: `${q.estimated_time} min`,
            question: q.question,
            answer: q.model_answer
          }));
          setQuestions(formatted);
        }
      } catch (err) {
        console.error("Failed to fetch interview questions", err);
      } finally {
        setLoading(false);
      }
    }
    fetchQuestions();
  }, [user]);

  const filteredQuestions = questions.filter(q => q.category === activeTab);
  const mockQuestions = questions.filter(q => q.category === activeTab);
  const currentMockQ = mockQuestions[mockQuestionIndex];

  // Timer effect
  useEffect(() => {
    if (timerRunning) {
      timerRef.current = setInterval(() => {
        setTimer(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timerRunning]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const toggleExpand = (id) => {
    setExpandedCards(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const startMock = () => {
    setMockActive(true);
    setMockQuestionIndex(0);
    setMockAnswer('');
    setTimer(0);
    setTimerRunning(true);
    setMockCompleted(false);
  };

  const nextMockQuestion = () => {
    if (mockQuestionIndex < mockQuestions.length - 1) {
      setMockQuestionIndex(prev => prev + 1);
      setMockAnswer('');
    } else {
      setTimerRunning(false);
      setMockCompleted(true);
    }
  };

  const exitMock = () => {
    setMockActive(false);
    setTimerRunning(false);
    setTimer(0);
    setMockAnswer('');
    setMockCompleted(false);
  };

  const firstName = user?.full_name?.split(' ')[0] || 'there';

  /* ════════════════════════════════════════════════════════════════════
     MOCK INTERVIEW MODE — full-screen overlay
     ════════════════════════════════════════════════════════════════════ */
  if (mockActive) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex flex-col bg-surface animate-fade-in-up">
        {/* Top bar */}
        <div className="glass-effect sticky top-0 z-10 flex items-center justify-between px-xl py-md border-b border-outline-variant/40">
          <div className="flex items-center gap-md">
            <button onClick={exitMock} className="flex items-center gap-xs text-on-surface-variant hover:text-error transition-colors cursor-pointer">
              <span className="material-symbols-outlined text-[20px]">close</span>
              <span className="font-label text-sm">Exit</span>
            </button>
            <span className="h-5 w-px bg-outline-variant/50" />
            <span className="font-label text-sm text-on-surface-variant">
              Mock Interview — <span className="text-primary font-semibold">{activeTab}</span>
            </span>
          </div>

          {/* Timer */}
          <div className={`flex items-center gap-sm px-lg py-xs rounded-full font-label text-lg tracking-wider ${timer > 300 ? 'bg-red-100 text-red-700' : 'bg-primary/10 text-primary'} transition-colors`}>
            <span className="material-symbols-outlined text-[20px] animate-gentle-pulse">timer</span>
            {formatTime(timer)}
          </div>

          <span className="font-label text-sm text-on-surface-variant">
            Question {mockQuestionIndex + 1} / {mockQuestions.length}
          </span>
        </div>

        {mockCompleted ? (
          /* ─── Completed state ─── */
          <div className="flex-1 flex items-center justify-center p-xl">
            <div className="glass-effect rounded-xl p-3xl text-center max-w-lg animate-fade-in-up">
              <div className="w-20 h-20 rounded-full bg-success/15 flex items-center justify-center mx-auto mb-lg">
                <span className="material-symbols-outlined text-success text-4xl">check_circle</span>
              </div>
              <h2 className="text-2xl font-bold text-on-surface mb-sm">Session Complete!</h2>
              <p className="text-on-surface-variant mb-md">You answered {mockQuestions.length} questions in {formatTime(timer)}.</p>
              <div className="flex gap-md justify-center">
                <button onClick={startMock} className="px-lg py-sm rounded-lg bg-primary text-on-primary font-label text-sm hover:bg-primary-container transition-colors cursor-pointer">
                  Retry
                </button>
                <button onClick={exitMock} className="px-lg py-sm rounded-lg border border-outline-variant text-on-surface-variant font-label text-sm hover:bg-surface-container transition-colors cursor-pointer">
                  Back to Prep
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* ─── Active question ─── */
          <div className="flex-1 flex flex-col lg:flex-row gap-xl p-xl max-w-6xl mx-auto w-full">
            {/* Question panel */}
            <div className="flex-1 flex flex-col gap-lg">
              <div className="glass-effect rounded-xl p-xl">
                <div className="flex items-center gap-sm mb-md">
                  <span className={`px-sm py-xs rounded-full text-xs font-label border ${difficultyStyles[currentMockQ.difficulty]}`}>
                    {currentMockQ.difficulty}
                  </span>
                  <span className="text-xs text-on-surface-variant font-label flex items-center gap-xs">
                    <span className="material-symbols-outlined text-[14px]">schedule</span>
                    {currentMockQ.time}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-on-surface leading-relaxed">{currentMockQ.question}</h3>
              </div>

              {/* Answer area */}
              <div className="flex-1 flex flex-col glass-effect rounded-xl p-xl">
                <label className="font-label text-sm text-on-surface-variant mb-sm flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[18px]">edit_note</span>
                  Your Answer
                </label>
                <textarea
                  className="flex-1 w-full resize-none rounded-lg bg-surface-container-low/60 border border-outline-variant/40 p-md text-on-surface text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-primary/30 transition-shadow custom-scrollbar min-h-[180px]"
                  placeholder="Type your answer here…"
                  value={mockAnswer}
                  onChange={(e) => setMockAnswer(e.target.value)}
                />
                <div className="flex items-center justify-between mt-md">
                  <span className="text-xs text-on-surface-variant font-label">{mockAnswer.length} characters</span>
                  <button
                    onClick={nextMockQuestion}
                    className="flex items-center gap-xs px-lg py-sm rounded-lg bg-primary text-on-primary font-label text-sm hover:bg-primary-container transition-colors cursor-pointer"
                  >
                    {mockQuestionIndex < mockQuestions.length - 1 ? 'Next Question' : 'Finish'}
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Progress sidebar */}
            <div className="w-full lg:w-64 shrink-0">
              <div className="glass-effect rounded-xl p-lg">
                <h4 className="font-label text-sm text-on-surface-variant mb-md">Progress</h4>
                <div className="space-y-sm">
                  {mockQuestions.map((q, i) => (
                    <div key={q.id} className={`flex items-center gap-sm px-sm py-xs rounded-md text-sm transition-colors ${i === mockQuestionIndex ? 'bg-primary/10 text-primary font-semibold' : i < mockQuestionIndex ? 'text-success font-semibold' : 'text-on-surface-variant'}`}>
                      <span className="material-symbols-outlined text-[18px]">
                        {i < mockQuestionIndex ? 'check_circle' : i === mockQuestionIndex ? 'radio_button_checked' : 'radio_button_unchecked'}
                      </span>
                      <span className="truncate">Q{i + 1}: {q.difficulty}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  /* ════════════════════════════════════════════════════════════════════
     MAIN PREP VIEW
     ════════════════════════════════════════════════════════════════════ */
  return (
    <div className="min-h-[calc(100vh-64px)] p-xl space-y-xl animate-fade-in-up">

      {/* ─── Hero / Stats Bar ─── */}
      <section className="glass-effect rounded-xl p-xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-lg">
          <div>
            <h1 className="text-3xl font-bold text-on-surface">
              Interview Prep
            </h1>
            <p className="text-on-surface-variant mt-xs">
              Hey {firstName}, sharpen your skills and ace every round.
            </p>
          </div>

          <button
            onClick={startMock}
            className="flex items-center gap-sm px-xl py-md rounded-xl bg-primary text-on-primary font-label text-sm font-semibold hover:bg-primary-container hover:scale-[1.03] active:scale-100 transition-all shadow-lg shadow-primary/20 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[20px]">play_circle</span>
            Start Mock Interview
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-md mt-lg stagger-children">
          {[
            { icon: 'quiz',         label: 'Questions Practiced', value: '47',    color: 'text-primary' },
            { icon: 'analytics',    label: 'Average Score',       value: '82%',   color: 'text-success' },
            { icon: 'local_fire_department', label: 'Streak',     value: '5 days', color: 'text-warning' },
          ].map((s) => (
            <div key={s.label} className="flex items-center gap-md p-md rounded-lg bg-surface-container-low/60 hover:bg-surface-container transition-colors">
              <div className="w-11 h-11 rounded-lg bg-surface-container flex items-center justify-center">
                <span className={`material-symbols-outlined ${s.color}`}>{s.icon}</span>
              </div>
              <div>
                <p className="text-xs font-label text-on-surface-variant">{s.label}</p>
                <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Category Tabs ─── */}
      <div ref={tabsRef} className="flex gap-sm overflow-x-auto pb-xs custom-scrollbar -mx-xl px-xl">
        {categories.map((cat) => {
          const meta = categoryMeta[cat];
          const isActive = activeTab === cat;
          return (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              className={`shrink-0 flex items-center gap-sm px-lg py-sm rounded-xl font-label text-sm transition-all cursor-pointer
                ${isActive
                  ? 'bg-primary text-on-primary shadow-md shadow-primary/20'
                  : 'glass-effect text-on-surface-variant hover:bg-surface-container-high'}`}
            >
              <span className="material-symbols-outlined text-[18px]">{meta.icon}</span>
              {cat}
              <span className={`ml-xs text-xs rounded-full px-sm py-0.5 ${isActive ? 'bg-white/20' : 'bg-surface-container'}`}>
                {meta.completed}/{meta.total}
              </span>
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-xl">
        {/* ─── Question Cards ─── */}
        <div className="space-y-md stagger-children">
          {filteredQuestions.map((q, idx) => {
            const isExpanded = expandedCards.has(q.id);
            return (
              <div
                key={q.id}
                className="glass-effect rounded-xl overflow-hidden hover:shadow-lg hover:shadow-primary/5 transition-all group"
              >
                {/* Card header */}
                <button
                  onClick={() => toggleExpand(q.id)}
                  className="w-full text-left px-xl py-lg flex items-start gap-lg cursor-pointer"
                >
                  <span className="mt-1 w-8 h-8 shrink-0 rounded-lg bg-surface-container flex items-center justify-center text-sm font-bold text-on-surface-variant group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-on-surface font-medium leading-relaxed">{q.question}</p>
                    <div className="flex flex-wrap items-center gap-sm mt-sm">
                      <span className={`px-sm py-xs rounded-full text-xs font-label border ${difficultyStyles[q.difficulty]}`}>
                        {q.difficulty}
                      </span>
                      <span className="text-xs text-on-surface-variant font-label flex items-center gap-xs">
                        <span className="material-symbols-outlined text-[14px]">schedule</span>
                        {q.time}
                      </span>
                      <span className="text-xs text-on-surface-variant font-label flex items-center gap-xs">
                        <span className="material-symbols-outlined text-[14px]">label</span>
                        {q.category}
                      </span>
                    </div>
                  </div>
                  <span className={`material-symbols-outlined text-on-surface-variant transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}>
                    expand_more
                  </span>
                </button>

                {/* Expandable answer */}
                <div className={`overflow-hidden transition-all duration-300 ease-in-out ${isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'}`}>
                  <div className="px-xl pb-lg ml-[56px]">
                    <div className="rounded-lg bg-primary/5 border border-primary/10 p-md">
                      <div className="flex items-center gap-xs mb-sm text-primary">
                        <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
                        <span className="font-label text-xs font-semibold uppercase tracking-wider">Model Answer</span>
                      </div>
                      <p className="text-sm text-on-surface leading-relaxed">{q.answer}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ─── Right Sidebar ─── */}
        <div className="space-y-xl">
          {/* Progress Tracker */}
          <div className="glass-effect rounded-xl p-xl">
            <h3 className="font-label text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-lg flex items-center gap-xs">
              <span className="material-symbols-outlined text-[18px]">donut_large</span>
              Category Progress
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-lg">
              {categories.map((cat) => {
                const meta = categoryMeta[cat];
                const pct = Math.round((meta.completed / meta.total) * 100);
                return (
                  <div key={cat} className="flex flex-col items-center gap-xs group cursor-default">
                    <div className="relative">
                      <ProgressRing progress={pct} color={meta.ring} />
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-on-surface">
                        {pct}%
                      </span>
                    </div>
                    <span className="text-xs font-label text-on-surface-variant text-center leading-tight group-hover:text-on-surface transition-colors">
                      {cat}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Pro Tips */}
          <div className="glass-effect rounded-xl p-xl">
            <h3 className="font-label text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-lg flex items-center gap-xs">
              <span className="material-symbols-outlined text-[18px] text-warning">emoji_objects</span>
              Pro Tips
            </h3>
            <div className="space-y-md">
              {tips.map((tip) => (
                <div
                  key={tip.title}
                  className="flex gap-md p-md rounded-lg bg-surface-container-low/60 hover:bg-surface-container transition-colors group cursor-default"
                >
                  <div className="w-9 h-9 shrink-0 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/15 transition-colors">
                    <span className="material-symbols-outlined text-primary text-[18px]">{tip.icon}</span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-on-surface">{tip.title}</p>
                    <p className="text-xs text-on-surface-variant leading-relaxed mt-xs">{tip.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
