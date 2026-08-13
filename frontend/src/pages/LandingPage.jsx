import { Link } from 'react-router-dom'
import { useState } from 'react'
import Footer from '../components/Footer'

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [locationQuery, setLocationQuery] = useState('')

  const hiringCompanies = [
    { name: 'Paytm', tag: 'FinTech' },
    { name: 'PhonePe', tag: 'Payments' },
    { name: 'Razorpay', tag: 'FinTech' },
    { name: 'Meesho', tag: 'E-Commerce' },
    { name: 'CRED', tag: 'FinTech' },
    { name: 'Postman', tag: 'Developer Tools' },
    { name: 'Urban Company', tag: 'Services' },
  ]

  const features = [
    {
      id: 'job-discovery',
      title: 'Smart Role Matching',
      subtitle: 'Real Requisitions Only',
      desc: 'Our intelligence engine indexes live API endpoints from top engineering ATS platforms across India. No dead links, no recruiter spam.',
      bullets: [
        '100% Verified direct-to-employer apply links',
        'Strict India location filtering (Bengaluru, NCR, Mumbai, Hyderabad, Remote)',
        'Real-time position freshness tracking'
      ],
      badge: 'LIVE ENGINE'
    },
    {
      id: 'ats-scanner',
      title: 'Authentic 5-Metric ATS Scanner',
      subtitle: 'ATS Industry Heuristics',
      desc: 'Based on actual algorithms used by Jobscan, Lever, and Greenhouse. Get granular sub-scores across contact formatting, skill density, impact metrics, and brevity.',
      bullets: [
        'Transparent sub-score breakdowns (0–100 scale)',
        'Action verb & numerical impact item detector',
        'Missing keyword recommendations by role'
      ],
      badge: 'PROPRIETARY PARSER'
    },
    {
      id: 'career-roadmaps',
      title: 'Precision Skill Gap Analysis',
      subtitle: 'Role Taxonomy',
      desc: 'Map your current technical stack against 350+ industry requirements. Identify exact missing frameworks needed to reach your target compensation tier.',
      bullets: [
        'Curated learning paths from top free platforms',
        'Target role readiness calculator',
        'Direct links to certifications and resources'
      ],
      badge: 'CAREER INTELLIGENCE'
    }
  ]

  const testimonials = [
    {
      name: 'Rohan Sharma',
      role: 'Backend Engineer at Paytm',
      location: 'Bengaluru',
      quote: 'CareerLens showed me exactly which ATS keywords I was missing for Senior Node.js roles. Applied directly through the verified link and got an interview in 48 hours.',
      matchScore: '96% Role Fit'
    },
    {
      name: 'Ananya Verma',
      role: 'Data Analyst at EXL',
      location: 'Gurugram',
      quote: 'The ATS score breakdown is terrifyingly accurate. Quantifying my bullet points bumped my ATS score from 58 to 88.',
      matchScore: '92% Resume Match'
    },
    {
      name: 'Priya Nair',
      role: 'SDE-1 at Razorpay',
      location: 'Remote India',
      quote: 'Finally a platform that doesnt flood you with 6-day-old reposts. Every direct link I clicked was actually open and accepting applications.',
      matchScore: '98% Direct Apply'
    }
  ]

  const faqs = [
    {
      q: 'How does CareerLens AI guarantee 95%+ India-specific jobs?',
      a: 'We parse live ATS APIs (Lever, Greenhouse, Unstop, Remotive) using strict regional geofencing filters that mandate verified locations like Bengaluru, NCR, Mumbai, Hyderabad, Pune, or Remote (India).'
    },
    {
      q: 'How does the ATS Resume Scoring engine work?',
      a: 'Our parser evaluates your CV across 5 standard categories: Contact & Links (15%), Section Completeness (15%), Skills Density (35%), Quantifiable Impact (20%), and Brevity (15%). It provides transparent sub-scores so you know exactly why your resume scored what it did.'
    },
    {
      q: 'Are the apply links genuinely direct?',
      a: 'Yes. Every job listing points directly to official employer ATS endpoints (e.g. jobs.lever.co, boards.greenhouse.io, or verified company career portals) rather than third-party aggregators.'
    },
    {
      q: 'Is CareerLens AI free to use?',
      a: 'Yes! You can search live opportunities, run ATS resume checks, analyze skill gaps, and access free learning resources without any paywalls.'
    }
  ]

  return (
    <div className="bg-[#0B0F19] text-slate-100 min-h-screen font-['Plus_Jakarta_Sans',sans-serif] selection:bg-indigo-500 selection:text-white overflow-x-hidden">
      
      {/* Glow Orbs background effect */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-tr from-indigo-600/20 via-sky-500/10 to-transparent blur-[120px] rounded-full" />
        <div className="absolute top-[40%] right-[-200px] w-[600px] h-[600px] bg-sky-600/10 blur-[150px] rounded-full" />
      </div>

      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-[#0B0F19]/80 backdrop-blur-xl border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-sky-400 p-[1px] shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all">
              <div className="w-full h-full bg-[#0F172A] rounded-[11px] flex items-center justify-center">
                <span className="material-symbols-outlined text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-sky-400 text-2xl font-bold">
                  auto_awesome
                </span>
              </div>
            </div>
            <span className="text-xl font-bold tracking-tight text-white font-['Plus_Jakarta_Sans']">
              CareerLens<span className="text-sky-400">.ai</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#ats-engine" className="hover:text-white transition-colors">ATS Analyzer</a>
            <a href="#companies" className="hover:text-white transition-colors">Top MNCs</a>
            <a href="#testimonials" className="hover:text-white transition-colors">Reviews</a>
            <a href="#faq" className="hover:text-white transition-colors">FAQ</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm font-semibold text-slate-300 hover:text-white transition-colors hidden sm:block px-3 py-2">
              Log In
            </Link>
            <Link 
              to="/register" 
              className="relative inline-flex items-center justify-center p-0.5 overflow-hidden text-sm font-semibold rounded-xl group bg-gradient-to-br from-indigo-500 to-sky-400 group-hover:from-indigo-500 group-hover:to-sky-400 hover:text-white text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 transition-all active:scale-95"
            >
              <span className="relative px-5 py-2.5 transition-all ease-in duration-75 bg-[#0F172A] rounded-[10px] group-hover:bg-opacity-0">
                Get Started Free →
              </span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10">

        {/* ─── Hero Section ─── */}
        <section className="pt-16 pb-20 px-6 max-w-7xl mx-auto text-center">
          
          {/* Top Pill */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900/90 border border-slate-800 text-xs font-semibold text-sky-400 mb-8 shadow-inner">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>Real-Time Job Intelligence Engine (2026 Edition)</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.1] max-w-5xl mx-auto mb-6">
            Search Once. Learn <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-sky-400 to-emerald-400">Smart.</span> Get Hired in India.
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed mb-10 font-normal">
            Skip dead job portals and recruiter spam. CareerLens AI aggregates real, verified employer requisitions across India with authentic 5-category ATS resume scoring.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
            <Link 
              to="/app/opportunities" 
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-sky-500 text-white font-bold text-base shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-2"
            >
              <span>Explore Verified Jobs</span>
              <span className="material-symbols-outlined text-xl">arrow_forward</span>
            </Link>
            <Link 
              to="/app/resume" 
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-slate-900/80 border border-slate-700/80 hover:border-slate-500 text-slate-200 hover:text-white font-bold text-base hover:bg-slate-800 transition-all flex items-center justify-center gap-2"
            >
              <span className="material-symbols-outlined text-xl text-sky-400">description</span>
              <span>Test Resume ATS Score</span>
            </Link>
          </div>

          {/* Live Search Bar Preview */}
          <div className="max-w-3xl mx-auto bg-slate-900/90 border border-slate-800 rounded-2xl p-2 sm:p-3 shadow-2xl backdrop-blur-xl mb-16">
            <div className="flex flex-col sm:flex-row items-center gap-2">
              <div className="flex-1 w-full flex items-center px-4 py-3 bg-slate-950/80 rounded-xl border border-slate-800 focus-within:border-indigo-500/60 transition-colors">
                <span className="material-symbols-outlined text-slate-400 mr-3">search</span>
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Job title, skills (e.g. React, Python, Data Analyst)..." 
                  className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
                />
              </div>
              <div className="flex-1 w-full flex items-center px-4 py-3 bg-slate-950/80 rounded-xl border border-slate-800 focus-within:border-indigo-500/60 transition-colors">
                <span className="material-symbols-outlined text-slate-400 mr-3">location_on</span>
                <input 
                  type="text" 
                  value={locationQuery}
                  onChange={(e) => setLocationQuery(e.target.value)}
                  placeholder="Bengaluru, NCR, Hyderabad, Remote..." 
                  className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
                />
              </div>
              <Link 
                to={`/app/opportunities?q=${encodeURIComponent(searchQuery)}&loc=${encodeURIComponent(locationQuery)}`}
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm transition-all shrink-0 text-center"
              >
                Search Jobs
              </Link>
            </div>
            <div className="flex flex-wrap items-center gap-2 mt-3 px-2 text-xs text-slate-400">
              <span className="font-semibold text-slate-500">Popular:</span>
              {['Backend Engineer', 'Data Analyst', 'React Developer', 'DevOps', 'Remote India'].map((chip) => (
                <Link 
                  key={chip} 
                  to={`/app/opportunities?q=${encodeURIComponent(chip)}`}
                  className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  {chip}
                </Link>
              ))}
            </div>
          </div>

          {/* 3D Interactive UI Showcase Box */}
          <div className="relative max-w-5xl mx-auto rounded-2xl p-2 bg-gradient-to-b from-indigo-500/30 via-sky-500/10 to-transparent shadow-2xl group">
            <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-[#0F172A] shadow-2xl transition-transform duration-500 group-hover:scale-[1.01]">
              <img 
                src="/images/hero_3d.jpg" 
                alt="CareerLens AI 3D Dashboard Interface" 
                className="w-full h-auto object-cover rounded-xl"
              />
              
              {/* Floating Badges on Image */}
              <div className="absolute top-6 left-6 hidden sm:flex items-center gap-3 px-4 py-2.5 rounded-xl bg-[#0F172A]/90 border border-slate-700/80 backdrop-blur-md shadow-xl text-left">
                <div className="w-9 h-9 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-base">
                  96%
                </div>
                <div>
                  <div className="text-xs font-bold text-white">Match Score Identified</div>
                  <div className="text-[10px] text-slate-400">AI Skill & Experience Alignment</div>
                </div>
              </div>

              <div className="absolute bottom-6 right-6 hidden sm:flex items-center gap-3 px-4 py-2.5 rounded-xl bg-[#0F172A]/90 border border-slate-700/80 backdrop-blur-md shadow-xl text-left">
                <div className="w-9 h-9 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center">
                  <span className="material-symbols-outlined text-lg">verified</span>
                </div>
                <div>
                  <div className="text-xs font-bold text-white">Direct Employer Link</div>
                  <div className="text-[10px] text-slate-400">Verified official ATS URL</div>
                </div>
              </div>
            </div>
          </div>

        </section>


        {/* ─── Company Logos Bar ─── */}
        <section id="companies" className="py-10 border-y border-slate-800/80 bg-slate-950/40">
          <div className="max-w-7xl mx-auto px-6 text-center">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">
              Indexing live requisitions from top tech platforms & unicorns
            </p>
            <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-12 opacity-80 hover:opacity-100 transition-opacity">
              {hiringCompanies.map((c) => (
                <div key={c.name} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="font-bold text-slate-200 text-sm font-['Plus_Jakarta_Sans']">{c.name}</span>
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">{c.tag}</span>
                </div>
              ))}
            </div>
          </div>
        </section>


        {/* ─── Stats Grid Section ─── */}
        <section className="py-16 px-6 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-2 hover:border-slate-700 transition-colors">
              <div className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-sky-400">
                1,000+
              </div>
              <div className="text-sm font-bold text-slate-200">Verified Active Jobs</div>
              <div className="text-xs text-slate-400">Direct ATS integrations updated continuously</div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-2 hover:border-slate-700 transition-colors">
              <div className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-emerald-400">
                95%+
              </div>
              <div className="text-sm font-bold text-slate-200">India Location Specific</div>
              <div className="text-xs text-slate-400">Strict regional filtering (Bengaluru, NCR, Hyd, Remote)</div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-2 hover:border-slate-700 transition-colors">
              <div className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-indigo-400">
                5-Metric
              </div>
              <div className="text-sm font-bold text-slate-200">ATS Resume Scoring</div>
              <div className="text-xs text-slate-400">Transparent breakdown heuristics (Impact, Brevity, Skills)</div>
            </div>
          </div>
        </section>


        {/* ─── Detailed Feature Showcase ─── */}
        <section id="features" className="py-20 px-6 max-w-7xl mx-auto space-y-24">

          {/* Feature 1: ATS Resume Engine */}
          <div id="ats-engine" className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-6 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-xs font-bold text-indigo-400 uppercase tracking-wider">
                {features[1].badge}
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                {features[1].title}
              </h2>
              <p className="text-slate-400 text-base leading-relaxed">
                {features[1].desc}
              </p>
              <ul className="space-y-3">
                {features[1].bullets.map((b, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="material-symbols-outlined text-emerald-400 text-xl shrink-0 mt-0.5">check_circle</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <div className="pt-2">
                <Link to="/app/resume" className="inline-flex items-center gap-2 text-sky-400 font-bold text-sm hover:text-sky-300 transition-colors">
                  <span>Analyze Your Resume Now</span>
                  <span className="material-symbols-outlined text-lg">arrow_forward</span>
                </Link>
              </div>
            </div>

            <div className="lg:col-span-6 relative">
              <div className="p-2 rounded-2xl bg-gradient-to-tr from-emerald-500/20 via-sky-500/20 to-indigo-500/20 border border-slate-800 shadow-2xl">
                <img 
                  src="/images/ats_3d.jpg" 
                  alt="3D ATS Resume Analysis Mockup" 
                  className="w-full h-auto object-cover rounded-xl shadow-2xl"
                />
              </div>
            </div>
          </div>


          {/* Feature 2: Smart Job Matching */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center lg:flex-row-reverse">
            <div className="lg:col-span-6 lg:order-2 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-sky-500/10 border border-sky-500/20 text-xs font-bold text-sky-400 uppercase tracking-wider">
                {features[0].badge}
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                {features[0].title}
              </h2>
              <p className="text-slate-400 text-base leading-relaxed">
                {features[0].desc}
              </p>
              <ul className="space-y-3">
                {features[0].bullets.map((b, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="material-symbols-outlined text-sky-400 text-xl shrink-0 mt-0.5">check_circle</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <div className="pt-2">
                <Link to="/app/opportunities" className="inline-flex items-center gap-2 text-indigo-400 font-bold text-sm hover:text-indigo-300 transition-colors">
                  <span>View Verified Job Board</span>
                  <span className="material-symbols-outlined text-lg">arrow_forward</span>
                </Link>
              </div>
            </div>

            <div className="lg:col-span-6 lg:order-1">
              <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-2xl">
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-xs font-bold text-slate-400 uppercase">Live Matches Found</span>
                  <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Verified Direct Links
                  </span>
                </div>

                {[
                  { title: 'Senior Data Engineer', company: 'Paytm', loc: 'Bengaluru', match: '96%', tags: ['Python', 'Spark', 'AWS'] },
                  { title: 'Backend Software Engineer', company: 'Razorpay', loc: 'Remote India', match: '94%', tags: ['Go', 'Microservices'] },
                  { title: 'Full Stack Engineer (React/Node)', company: 'Postman', loc: 'Bengaluru / Hybrid', match: '91%', tags: ['React', 'Node.js'] },
                ].map((item, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div>
                      <div className="font-bold text-white text-sm">{item.title}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{item.company} • {item.loc}</div>
                      <div className="flex gap-1.5 mt-2">
                        {item.tags.map(t => (
                          <span key={t} className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">{t}</span>
                        ))}
                      </div>
                    </div>
                    <div className="shrink-0 text-right">
                      <span className="px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold block">
                        {item.match} Match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </section>


        {/* ─── Testimonials Section ─── */}
        <section id="testimonials" className="py-20 px-6 max-w-7xl mx-auto border-t border-slate-800/80">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
              Trusted by Professionals Across India
            </h2>
            <p className="text-slate-400 text-base">
              Real career growth stories from candidates who used CareerLens AI to land direct offers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <div 
                key={i} 
                className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="inline-block px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold">
                    {t.matchScore}
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed italic">
                    "{t.quote}"
                  </p>
                </div>
                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white text-sm">{t.name}</div>
                    <div className="text-xs text-slate-400">{t.role}</div>
                  </div>
                  <span className="text-xs font-semibold text-slate-500">{t.location}</span>
                </div>
              </div>
            ))}
          </div>
        </section>


        {/* ─── FAQ Section ─── */}
        <section id="faq" className="py-20 px-6 max-w-4xl mx-auto border-t border-slate-800/80">
          <div className="text-center mb-14 space-y-3">
            <h2 className="text-3xl font-extrabold text-white">Frequently Asked Questions</h2>
            <p className="text-slate-400 text-sm">Everything you need to know about our data sources and scoring algorithm.</p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => {
              const isOpen = openFaq === index
              return (
                <div 
                  key={index} 
                  className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden transition-colors"
                >
                  <button
                    onClick={() => setOpenFaq(isOpen ? -1 : index)}
                    className="w-full p-5 text-left font-bold text-white text-base flex justify-between items-center gap-4 hover:text-sky-400 transition-colors"
                  >
                    <span>{faq.q}</span>
                    <span className="material-symbols-outlined text-slate-400 shrink-0">
                      {isOpen ? 'remove' : 'add'}
                    </span>
                  </button>
                  {isOpen && (
                    <div className="px-5 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800/60 pt-3">
                      {faq.a}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>


        {/* ─── Final CTA Box ─── */}
        <section className="py-20 px-6 max-w-5xl mx-auto">
          <div className="relative rounded-3xl p-10 sm:p-14 bg-gradient-to-r from-indigo-900/80 via-slate-900 to-sky-900/80 border border-indigo-500/30 text-center space-y-6 overflow-hidden shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/10 to-transparent pointer-events-none" />
            <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight relative z-10">
              Ready to Accelerate Your Tech Career?
            </h2>
            <p className="text-slate-300 text-base max-w-2xl mx-auto relative z-10 leading-relaxed">
              Join thousands of engineering and data professionals finding real opportunities with transparent ATS guidance.
            </p>
            <div className="pt-4 relative z-10">
              <Link 
                to="/register" 
                className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-slate-950 font-extrabold text-base hover:bg-slate-100 hover:scale-[1.02] active:scale-95 transition-all shadow-xl"
              >
                <span>Get Started Now — It's Free</span>
                <span className="material-symbols-outlined text-xl">arrow_forward</span>
              </Link>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}
