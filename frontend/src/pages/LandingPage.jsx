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
    { name: 'Postman', tag: 'Dev Tools' },
    { name: 'BrowserStack', tag: 'QA Tech' },
    { name: 'Urban Company', tag: 'Services' },
  ]

  const faqs = [
    {
      q: 'How does CareerLens AI guarantee 95%+ India-specific jobs?',
      a: 'We parse live ATS APIs (Lever, Greenhouse, Unstop, Remotive) using strict regional geofencing filters that mandate verified locations like Bengaluru, NCR, Mumbai, Hyderabad, Pune, or Remote (India).',
    },
    {
      q: 'How does the ATS Resume Scoring engine work?',
      a: 'Our parser evaluates your CV across 5 standard categories: Contact & Links (15%), Section Completeness (15%), Skills Density (35%), Quantifiable Impact (20%), and Brevity (15%). It provides transparent sub-scores so you know exactly why your resume scored what it did.',
    },
    {
      q: 'Are the apply links genuinely direct?',
      a: 'Yes. Every job listing points directly to official employer ATS endpoints (e.g. jobs.lever.co, boards.greenhouse.io, or verified company career portals) rather than third-party aggregators.',
    },
    {
      q: 'Is CareerLens AI free to use?',
      a: 'Yes! You can search live opportunities, run ATS resume checks, analyze skill gaps, and access free learning resources without any paywalls.',
    },
  ]

  return (
    <div className="bg-surface text-on-surface overflow-x-hidden">

      {/* ── Header ── */}
      <header className="sticky top-0 z-40 bg-surface/90 backdrop-blur-md border-b border-outline-variant flex justify-between items-center h-16 px-lg w-full">
        <Link to="/" className="flex items-center gap-sm">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-md">
            <span className="material-symbols-outlined text-on-primary text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
          </div>
          <span className="text-xl font-bold text-on-background tracking-tight">CareerLens <span className="text-primary">AI</span></span>
        </Link>

        <nav className="hidden md:flex items-center gap-xl">
          <a className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors" href="#features">Features</a>
          <a className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors" href="#companies">Companies</a>
          <a className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors" href="#testimonials">Reviews</a>
          <a className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors" href="#faq">FAQ</a>
        </nav>

        <div className="flex items-center gap-md">
          <Link to="/login" className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors hidden sm:block">Login</Link>
          <Link to="/register" className="bg-primary text-on-primary px-lg py-sm rounded-lg text-sm font-semibold hover:bg-primary-container hover:text-on-primary-container transition-all shadow-md">
            Get Started
          </Link>
        </div>
      </header>

      <main className="max-w-[1440px] mx-auto">

        {/* ── Hero Section ── */}
        <section id="home" className="relative pt-2xl pb-3xl px-lg overflow-hidden">

          {/* Subtle background glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/5 blur-[100px] rounded-full pointer-events-none" />

          <div className="relative z-10 flex flex-col lg:flex-row items-center gap-2xl max-w-7xl mx-auto">

            {/* Left: Text Content */}
            <div className="flex-1 space-y-lg text-center lg:text-left animate-fade-in-up">

              {/* Pill badge */}
              <div className="inline-flex items-center gap-sm px-md py-xs rounded-full bg-primary-container/30 border border-primary/20 text-xs font-bold text-primary uppercase tracking-wider">
                <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
                Real-Time Job Intelligence Engine (2026 Edition)
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-on-background leading-[1.1]">
                Search Once. Learn <span className="text-primary">Smart.</span> Get Hired in India.
              </h1>

              <p className="text-lg text-on-surface-variant leading-relaxed max-w-xl mx-auto lg:mx-0">
                Skip dead job portals and recruiter spam. CareerLens AI aggregates real, verified employer requisitions across India with authentic 5-category ATS resume scoring.
              </p>

              <div className="flex flex-col sm:flex-row gap-md pt-sm justify-center lg:justify-start">
                <Link
                  to="/app/opportunities"
                  className="bg-primary text-on-primary px-xl py-md rounded-xl text-sm font-bold hover:bg-primary-container hover:text-on-primary-container transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-sm"
                >
                  Explore Verified Jobs
                  <span className="material-symbols-outlined text-xl">arrow_forward</span>
                </Link>
                <Link
                  to="/app/resume"
                  className="bg-white border border-outline-variant text-on-surface px-xl py-md rounded-xl text-sm font-bold hover:bg-surface-container-low transition-all flex items-center justify-center gap-sm"
                >
                  <span className="material-symbols-outlined text-primary text-xl">description</span>
                  Test ATS Score
                </Link>
              </div>

              {/* Trust row */}
              <div className="flex flex-wrap items-center gap-md pt-sm justify-center lg:justify-start text-xs text-on-surface-variant">
                <span className="flex items-center gap-xs font-medium">
                  <span className="material-symbols-outlined text-success text-base" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  100% Verified Direct Apply Links
                </span>
                <span className="flex items-center gap-xs font-medium">
                  <span className="material-symbols-outlined text-primary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>location_on</span>
                  95%+ India-Specific Jobs
                </span>
                <span className="flex items-center gap-xs font-medium">
                  <span className="material-symbols-outlined text-warning text-base" style={{ fontVariationSettings: "'FILL' 1" }}>bolt</span>
                  Free Forever
                </span>
              </div>
            </div>

            {/* Right: 3D Dashboard Image */}
            <div className="flex-1 relative w-full max-w-2xl animate-fade-in-up" style={{ animationDelay: '150ms' }}>
              <div className="relative rounded-2xl overflow-hidden border border-outline-variant shadow-2xl shadow-primary/10 bg-surface-container-lowest p-1">
                <img
                  src="/images/hero_3d.jpg"
                  alt="CareerLens AI Dashboard - 3D Interface Preview"
                  className="w-full h-auto object-cover rounded-xl"
                />

                {/* Floating Badge: Match Score */}
                <div className="absolute top-4 left-4 flex items-center gap-sm px-md py-sm rounded-xl bg-white/95 backdrop-blur-sm border border-outline-variant shadow-lg text-left">
                  <div className="w-9 h-9 rounded-lg bg-success/15 text-success flex items-center justify-center font-bold text-sm shrink-0">
                    96%
                  </div>
                  <div>
                    <div className="text-xs font-bold text-on-surface">AI Match Score</div>
                    <div className="text-[10px] text-on-surface-variant">Skill & Experience Aligned</div>
                  </div>
                </div>

                {/* Floating Badge: Verified Link */}
                <div className="absolute bottom-4 right-4 flex items-center gap-sm px-md py-sm rounded-xl bg-white/95 backdrop-blur-sm border border-outline-variant shadow-lg text-left">
                  <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-on-surface">Direct Employer Link</div>
                    <div className="text-[10px] text-on-surface-variant">Official ATS • No Middleman</div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Search Bar */}
          <div className="relative z-10 max-w-3xl mx-auto mt-3xl">
            <div className="bg-white border border-outline-variant rounded-2xl p-sm shadow-xl flex flex-col sm:flex-row items-center gap-sm">
              <div className="flex-1 w-full flex items-center px-md py-sm bg-surface-container-lowest rounded-xl border border-transparent focus-within:border-primary/40 transition-all">
                <span className="material-symbols-outlined text-outline mr-sm">search</span>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-transparent text-sm text-on-surface placeholder-outline focus:outline-none"
                  placeholder="Job title, skills (e.g. React, Python, Data Analyst)..."
                />
              </div>
              <div className="flex-1 w-full flex items-center px-md py-sm bg-surface-container-lowest rounded-xl border border-transparent focus-within:border-primary/40 transition-all">
                <span className="material-symbols-outlined text-outline mr-sm">location_on</span>
                <input
                  type="text"
                  value={locationQuery}
                  onChange={(e) => setLocationQuery(e.target.value)}
                  className="w-full bg-transparent text-sm text-on-surface placeholder-outline focus:outline-none"
                  placeholder="Bengaluru, NCR, Hyderabad, Remote India..."
                />
              </div>
              <Link
                to={`/app/opportunities?q=${encodeURIComponent(searchQuery)}&loc=${encodeURIComponent(locationQuery)}`}
                className="w-full sm:w-auto px-xl py-sm bg-primary text-on-primary font-bold text-sm rounded-xl hover:bg-primary-container hover:text-on-primary-container transition-all text-center shrink-0 shadow-md"
              >
                Search Jobs
              </Link>
            </div>
            <div className="flex flex-wrap gap-sm mt-md px-sm text-xs text-on-surface-variant">
              <span className="font-semibold text-outline">Trending:</span>
              {['Backend Engineer', 'Data Analyst', 'React Developer', 'DevOps', 'Remote India'].map((chip) => (
                <Link
                  key={chip}
                  to={`/app/opportunities?q=${encodeURIComponent(chip)}`}
                  className="px-sm py-xs rounded-lg bg-surface-container-low hover:bg-surface-container border border-outline-variant hover:border-primary/30 text-on-surface-variant hover:text-primary transition-all"
                >
                  {chip}
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── Stats Section ── */}
        <section className="py-xl bg-surface-container-low border-y border-outline-variant">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-xl px-lg text-center max-w-5xl mx-auto">
            <div className="space-y-xs">
              <div className="text-3xl font-bold text-primary">1,000+</div>
              <div className="text-xs font-semibold text-on-surface uppercase tracking-widest">Verified Active Jobs</div>
              <div className="text-xs text-on-surface-variant">Direct ATS integrations updated live</div>
            </div>
            <div className="space-y-xs">
              <div className="text-3xl font-bold text-primary">95%+</div>
              <div className="text-xs font-semibold text-on-surface uppercase tracking-widest">India Location Specific</div>
              <div className="text-xs text-on-surface-variant">Bengaluru, NCR, Hyd, Pune, Remote</div>
            </div>
            <div className="space-y-xs">
              <div className="text-3xl font-bold text-primary">5-Metric</div>
              <div className="text-xs font-semibold text-on-surface uppercase tracking-widest">ATS Resume Scoring</div>
              <div className="text-xs text-on-surface-variant">Impact, Skills, Brevity & more</div>
            </div>
          </div>
        </section>

        {/* ── Companies Bar ── */}
        <section id="companies" className="py-xl px-lg">
          <p className="text-xs font-bold text-on-surface-variant uppercase tracking-widest text-center mb-lg">
            Indexing live positions from top Indian tech companies
          </p>
          <div className="flex flex-wrap items-center justify-center gap-md">
            {hiringCompanies.map((c) => (
              <div key={c.name} className="flex items-center gap-sm px-md py-sm rounded-xl bg-white border border-outline-variant hover:border-primary/30 hover:shadow-md transition-all">
                <span className="font-bold text-on-surface text-sm">{c.name}</span>
                <span className="text-[10px] font-semibold px-sm py-xs rounded bg-primary-container/30 text-primary">{c.tag}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ── Feature 1: ATS Scanner ── */}
        <section id="features" className="py-3xl px-lg max-w-7xl mx-auto">
          <div className="text-center mb-2xl">
            <h2 className="text-3xl font-bold text-on-background">Everything You Need to Land the Role</h2>
            <p className="text-base text-on-surface-variant mt-sm">AI-driven tools built specifically for Indian tech job seekers</p>
          </div>

          {/* ATS Feature Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2xl items-center mb-3xl">
            <div className="space-y-lg">
              <div className="inline-flex items-center gap-sm px-md py-xs rounded-full bg-primary-container/30 border border-primary/20 text-xs font-bold text-primary uppercase tracking-wider">
                Proprietary ATS Parser
              </div>
              <h3 className="text-3xl font-bold text-on-background">
                Authentic 5-Metric ATS Resume Scoring
              </h3>
              <p className="text-on-surface-variant leading-relaxed">
                Based on real algorithms used by Lever and Greenhouse. Get granular sub-scores across contact formatting, skill density, impact metrics, and brevity — not just a black-box number.
              </p>
              <ul className="space-y-md">
                {[
                  'Transparent sub-score breakdowns (0–100 scale)',
                  'Action verb & numerical impact item detector',
                  'Missing keyword recommendations by role',
                ].map((b, i) => (
                  <li key={i} className="flex items-start gap-sm text-sm text-on-surface">
                    <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <Link
                to="/app/resume"
                className="inline-flex items-center gap-sm text-primary text-sm font-bold hover:gap-md transition-all"
              >
                Analyze Your Resume
                <span className="material-symbols-outlined text-lg">arrow_forward</span>
              </Link>
            </div>

            <div className="relative rounded-2xl overflow-hidden border border-outline-variant shadow-xl shadow-primary/5 bg-surface-container-lowest p-1">
              <img
                src="/images/ats_3d.jpg"
                alt="3D ATS Resume Analyzer UI"
                className="w-full h-auto object-cover rounded-xl"
              />
              <div className="absolute top-4 right-4 flex items-center gap-sm px-md py-sm rounded-xl bg-white/95 backdrop-blur-sm border border-outline-variant shadow-md">
                <span className="material-symbols-outlined text-success text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                <div>
                  <div className="text-xs font-bold text-on-surface">ATS Score: 92%</div>
                  <div className="text-[10px] text-on-surface-variant">Excellent — Ready to Apply</div>
                </div>
              </div>
            </div>
          </div>

          {/* Smart Job Matching Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2xl items-center">
            <div className="lg:order-2 space-y-lg">
              <div className="inline-flex items-center gap-sm px-md py-xs rounded-full bg-primary-container/30 border border-primary/20 text-xs font-bold text-primary uppercase tracking-wider">
                Live Engine
              </div>
              <h3 className="text-3xl font-bold text-on-background">
                Smart Role Matching — India Only
              </h3>
              <p className="text-on-surface-variant leading-relaxed">
                We index live ATS APIs from Lever, Greenhouse, and Unstop with strict India geofencing. No recycled postings. No dead links. Every card leads to an official employer apply page.
              </p>
              <ul className="space-y-md">
                {[
                  '100% Direct-to-employer apply links (no middleman)',
                  'Strict India location filtering — Bengaluru, NCR, Hyd, Remote',
                  'Real-time position freshness (stale jobs expire in 7 days)',
                ].map((b, i) => (
                  <li key={i} className="flex items-start gap-sm text-sm text-on-surface">
                    <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <Link
                to="/app/opportunities"
                className="inline-flex items-center gap-sm text-primary text-sm font-bold hover:gap-md transition-all"
              >
                View Live Job Board
                <span className="material-symbols-outlined text-lg">arrow_forward</span>
              </Link>
            </div>

            {/* Mock live job cards */}
            <div className="lg:order-1 space-y-md">
              {[
                { title: 'Senior Data Engineer', company: 'Paytm', loc: 'Bengaluru', match: '96%', tags: ['Python', 'Spark', 'AWS'], color: 'text-success' },
                { title: 'Backend Software Engineer', company: 'Razorpay', loc: 'Remote India', match: '94%', tags: ['Go', 'Microservices'], color: 'text-primary' },
                { title: 'Full Stack Engineer', company: 'Postman', loc: 'Bengaluru / Hybrid', match: '91%', tags: ['React', 'Node.js'], color: 'text-warning' },
              ].map((job, idx) => (
                <div key={idx} className="p-lg rounded-xl bg-white border border-outline-variant hover:border-primary/30 hover:shadow-md transition-all flex items-center justify-between gap-lg">
                  <div>
                    <div className="font-bold text-on-surface text-sm">{job.title}</div>
                    <div className="text-xs text-on-surface-variant mt-xs">{job.company} • {job.loc}</div>
                    <div className="flex gap-xs mt-sm flex-wrap">
                      {job.tags.map((t) => (
                        <span key={t} className="text-[10px] font-semibold px-sm py-xs rounded bg-surface-container-low text-on-surface-variant border border-outline-variant">{t}</span>
                      ))}
                    </div>
                  </div>
                  <div className="shrink-0">
                    <span className={`text-xs font-bold px-sm py-xs rounded-full bg-surface-container-low border border-outline-variant ${job.color}`}>
                      {job.match} Match
                    </span>
                  </div>
                </div>
              ))}
              <div className="flex items-center gap-xs text-xs text-on-surface-variant px-xs">
                <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
                Live positions — Updated continuously from official ATS APIs
              </div>
            </div>
          </div>
        </section>

        {/* ── Testimonials ── */}
        <section id="testimonials" className="py-3xl bg-white border-y border-outline-variant px-lg">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-2xl">
              <h2 className="text-3xl font-bold text-on-background">Trusted by Professionals Across India</h2>
              <p className="text-base text-on-surface-variant mt-sm">Real results from candidates who used CareerLens AI</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
              {[
                { name: 'Rohan Sharma', role: 'Backend Engineer at Paytm', loc: 'Bengaluru', badge: '96% Role Fit', quote: 'CareerLens showed me exactly which ATS keywords I was missing. Applied directly via the verified link and got an interview in 48 hours.' },
                { name: 'Ananya Verma', role: 'Data Analyst at EXL', loc: 'Gurugram', badge: '92% Resume Match', quote: 'The ATS score breakdown is terrifyingly accurate. Quantifying my bullet points bumped my score from 58 to 88.' },
                { name: 'Priya Nair', role: 'SDE-1 at Razorpay', loc: 'Remote India', badge: '100% Direct Apply', quote: 'Finally a platform that doesn\'t flood you with stale reposts. Every link I clicked was live and accepting applications.' },
              ].map((t, i) => (
                <div key={i} className="p-xl bg-surface-bright border border-outline-variant rounded-xl flex flex-col justify-between hover:shadow-lg hover:border-primary/20 transition-all space-y-md">
                  <div className="space-y-md">
                    <span className="inline-block px-md py-xs rounded-full bg-primary-container/20 border border-primary/20 text-primary text-xs font-bold">
                      {t.badge}
                    </span>
                    <p className="text-sm text-on-surface-variant italic leading-relaxed">"{t.quote}"</p>
                  </div>
                  <div className="pt-md border-t border-outline-variant flex items-center justify-between">
                    <div>
                      <div className="font-bold text-on-surface text-sm">{t.name}</div>
                      <div className="text-xs text-on-surface-variant">{t.role}</div>
                    </div>
                    <span className="text-xs text-on-surface-variant font-medium">{t.loc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── FAQ ── */}
        <section id="faq" className="py-3xl px-lg max-w-4xl mx-auto">
          <div className="text-center mb-2xl">
            <h2 className="text-3xl font-bold text-on-background">Frequently Asked Questions</h2>
            <p className="text-sm text-on-surface-variant mt-sm">About our data sources, ATS scoring, and how we work.</p>
          </div>
          <div className="space-y-md">
            {faqs.map((faq, index) => {
              const isOpen = openFaq === index
              return (
                <div key={index} className="rounded-xl bg-white border border-outline-variant overflow-hidden">
                  <button
                    onClick={() => setOpenFaq(isOpen ? -1 : index)}
                    className="w-full p-lg text-left font-bold text-on-surface text-sm flex justify-between items-center gap-md hover:text-primary transition-colors"
                  >
                    <span>{faq.q}</span>
                    <span className="material-symbols-outlined text-outline shrink-0">
                      {isOpen ? 'remove' : 'add'}
                    </span>
                  </button>
                  {isOpen && (
                    <div className="px-lg pb-lg text-sm text-on-surface-variant leading-relaxed border-t border-outline-variant pt-md">
                      {faq.a}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>

        {/* ── Final CTA ── */}
        <section className="py-3xl px-lg max-w-5xl mx-auto">
          <div className="relative rounded-2xl p-xl sm:p-2xl bg-primary text-center space-y-lg overflow-hidden shadow-2xl shadow-primary/30">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-container/30 to-transparent pointer-events-none" />
            <h2 className="text-3xl sm:text-4xl font-bold text-on-primary relative z-10">
              Ready to Accelerate Your Tech Career in India?
            </h2>
            <p className="text-on-primary/80 text-base max-w-2xl mx-auto relative z-10 leading-relaxed">
              Join thousands of engineering and data professionals finding real, verified opportunities with transparent ATS guidance.
            </p>
            <div className="pt-sm relative z-10">
              <Link
                to="/register"
                className="inline-flex items-center gap-sm px-xl py-md rounded-xl bg-white text-primary font-bold text-base hover:bg-surface-container-lowest hover:scale-[1.02] active:scale-95 transition-all shadow-xl"
              >
                Get Started — It's Free
                <span className="material-symbols-outlined text-xl">arrow_forward</span>
              </Link>
            </div>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  )
}
