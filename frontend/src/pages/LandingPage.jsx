import { Link } from 'react-router-dom'
import { useState } from 'react'
import Footer from '../components/Footer'

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState(0)

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

  const services = [
    {
      icon: 'explore',
      color: 'bg-sky-50 text-sky-600 border-sky-100',
      title: 'Smart Job Discovery',
      desc: 'Live ATS integrations indexing direct employer requisitions across India with zero middleman spam.',
      link: '/app/opportunities',
      linkText: 'Explore Jobs'
    },
    {
      icon: 'description',
      color: 'bg-emerald-50 text-emerald-600 border-emerald-100',
      title: 'ATS Resume Analysis',
      desc: '5-category scoring heuristic based on Lever & Greenhouse algorithms with clear fix recommendations.',
      link: '/app/resume',
      linkText: 'Scan Resume'
    },
    {
      icon: 'map',
      color: 'bg-indigo-50 text-indigo-600 border-indigo-100',
      title: 'Skill Gap Roadmaps',
      desc: 'Benchmark your stack against 350+ industry requirements and discover exact target frameworks.',
      link: '/app/careers',
      linkText: 'Build Roadmap'
    },
    {
      icon: 'school',
      color: 'bg-amber-50 text-amber-600 border-amber-100',
      title: 'Free Curated Learning',
      desc: 'Handpicked free courses and official certifications from Google, AWS, and Meta.',
      link: '/app/resources',
      linkText: 'View Resources'
    },
  ]

  const testimonials = [
    {
      name: 'Rohan Sharma',
      role: 'Backend Engineer at Paytm',
      loc: 'Bengaluru',
      badge: '96% Role Fit',
      quote: 'CareerLens showed me exactly which ATS keywords I was missing for Senior Go/Node roles. Applied directly and got an interview in 48 hours.'
    },
    {
      name: 'Ananya Verma',
      role: 'Data Analyst at EXL',
      loc: 'Gurugram',
      badge: '92% Resume Match',
      quote: 'The 5-metric ATS score breakdown is terrifyingly accurate. Quantifying my bullet points bumped my ATS score from 58 to 88.'
    },
    {
      name: 'Priya Nair',
      role: 'SDE-1 at Razorpay',
      loc: 'Remote India',
      badge: '100% Direct Apply',
      quote: 'Finally a platform that does not flood you with 2-week-old reposts. Every direct link I clicked was actually live and accepting applications.'
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
      q: 'Are the apply links genuinely direct to employers?',
      a: 'Yes. Every job listing points directly to official employer ATS endpoints (e.g. jobs.lever.co, boards.greenhouse.io, or verified company career portals) rather than third-party aggregators.'
    },
    {
      q: 'Is CareerLens AI free to use?',
      a: 'Yes! You can search live opportunities, run ATS resume checks, analyze skill gaps, and access free learning resources without any paywalls.'
    }
  ]

  return (
    <div className="bg-[#f8faff] text-[#0f172a] font-['Plus_Jakarta_Sans',sans-serif] selection:bg-[#0050cb] selection:text-white min-h-screen overflow-x-hidden">
      
      {/* ── Top Navbar (Matching reference) ── */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-100 transition-all">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#0050cb] to-[#0284c7] flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <span className="material-symbols-outlined text-white text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                auto_awesome
              </span>
            </div>
            <span className="text-xl font-extrabold tracking-tight text-[#0b1c30]">
              CareerLens <span className="text-[#0284c7]">AI</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600">
            <a href="#home" className="text-[#0050cb] font-bold">Home</a>
            <a href="#services" className="hover:text-[#0050cb] transition-colors">Services</a>
            <a href="#about" className="hover:text-[#0050cb] transition-colors">About Us</a>
            <a href="#testimonials" className="hover:text-[#0050cb] transition-colors">Reviews</a>
            <a href="#faq" className="hover:text-[#0050cb] transition-colors">FAQ</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm font-bold text-slate-700 hover:text-[#0050cb] transition-colors hidden sm:block px-3 py-2">
              Log In
            </Link>
            <Link 
              to="/register" 
              className="bg-[#0050cb] hover:bg-[#003fa4] text-white px-6 py-2.5 rounded-xl text-sm font-bold shadow-md shadow-blue-600/20 hover:shadow-lg hover:shadow-blue-600/30 transition-all active:scale-95"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>


      {/* ── Hero Section (Architectural Corporate Background Layout) ── */}
      <section id="home" className="relative min-h-[580px] sm:min-h-[640px] flex items-center overflow-hidden">
        
        {/* Background Image with Clean Left Fade */}
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/hero_architectural.jpg" 
            alt="Modern Glass Technology Campus" 
            className="w-full h-full object-cover object-right md:object-center"
          />
          {/* Gradient Overlay: Solid white/blue on left fading across to transparent on right */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#f8faff] via-[#f8faff]/95 sm:via-[#f8faff]/85 to-transparent md:w-[65%] w-full" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#f8faff] via-transparent to-transparent h-24 bottom-0" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-16 w-full">
          <div className="max-w-xl space-y-6">
            
            {/* Small Label */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-xs font-extrabold text-[#0050cb] tracking-wide">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>REAL-TIME JOB INTELLIGENCE ENGINE</span>
            </div>

            {/* Main Headline (Styled after reference image) */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#0b1c30] tracking-tight leading-[1.12]">
              Innovating Careers, <br />
              <span className="text-[#0284c7]">Inspiring Tomorrow</span>
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
              We deliver real-time ATS intelligence and verified opportunities that drive career growth, empower job seekers, and create lasting impact across India.
            </p>

            {/* Buttons Row */}
            <div className="flex flex-col sm:flex-row items-center gap-4 pt-2">
              <Link 
                to="/app/opportunities" 
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-[#0050cb] hover:bg-[#003fa4] text-white font-bold text-sm shadow-lg shadow-blue-600/25 hover:shadow-blue-600/35 transition-all text-center active:scale-95"
              >
                Our Services
              </Link>
              <Link 
                to="/app/resume" 
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-white/90 hover:bg-white border border-slate-300 text-slate-800 font-bold text-sm shadow-sm transition-all flex items-center justify-center gap-2 active:scale-95 hover:border-slate-400"
              >
                <span className="material-symbols-outlined text-[#0050cb] text-lg">play_arrow</span>
                <span>Watch Overview</span>
              </Link>
            </div>

          </div>
        </div>

      </section>


      {/* ── Floating Stats Card (Overlapping Hero, matching reference) ── */}
      <section className="relative z-20 -mt-8 max-w-6xl mx-auto px-6">
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/70 border border-slate-100 p-6 sm:p-8 grid grid-cols-2 md:grid-cols-4 gap-6 items-center">
          
          <div className="flex items-center gap-4 border-r border-slate-100 pr-4 last:border-r-0">
            <div className="w-12 h-12 rounded-xl bg-sky-50 text-[#0284c7] flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">group</span>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-[#0b1c30]">1,000+</div>
              <div className="text-xs text-slate-500 font-medium">Verified Active Jobs</div>
            </div>
          </div>

          <div className="flex items-center gap-4 border-r border-slate-100 pr-4 last:border-r-0">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">work</span>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-[#0b1c30]">500+</div>
              <div className="text-xs text-slate-500 font-medium">Internship Openings</div>
            </div>
          </div>

          <div className="flex items-center gap-4 border-r border-slate-100 pr-4 last:border-r-0">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">trophy</span>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-[#0b1c30]">95%+</div>
              <div className="text-xs text-slate-500 font-medium">India Requisitions</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">public</span>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-[#0b1c30]">100%</div>
              <div className="text-xs text-slate-500 font-medium">Direct Apply Links</div>
            </div>
          </div>

        </div>
      </section>


      {/* ── WHAT WE DO: 4-Card Solutions Grid (Matching reference layout) ── */}
      <section id="services" className="py-24 max-w-7xl mx-auto px-6">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-14">
          <div className="max-w-xl space-y-2">
            <span className="text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">WHAT WE DO</span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0b1c30] tracking-tight">
              Solutions that <br className="hidden sm:inline" />
              Drive <span className="text-[#0284c7]">Real Impact</span>
            </h2>
          </div>
          <div className="max-w-md space-y-3 text-slate-600 text-sm">
            <p>From live ATS indexing to precision career roadmaps, we provide end-to-end intelligence built for modern tech professionals.</p>
            <Link to="/app/opportunities" className="inline-flex items-center gap-1.5 text-[#0050cb] font-bold hover:gap-2.5 transition-all text-sm">
              <span>Explore All Services</span>
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </Link>
          </div>
        </div>

        {/* 4 Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {services.map((s, idx) => (
            <div 
              key={idx} 
              className="bg-white rounded-2xl p-7 border border-slate-100 shadow-md shadow-slate-100/50 hover:shadow-xl hover:border-slate-200 transition-all group flex flex-col justify-between"
            >
              <div className="space-y-4">
                <div className={`w-12 h-12 rounded-xl border flex items-center justify-center ${s.color}`}>
                  <span className="material-symbols-outlined text-2xl">{s.icon}</span>
                </div>
                <h3 className="text-lg font-bold text-[#0b1c30] group-hover:text-[#0050cb] transition-colors">
                  {s.title}
                </h3>
                <p className="text-slate-500 text-xs leading-relaxed">
                  {s.desc}
                </p>
              </div>

              <div className="pt-6 mt-4 border-t border-slate-50">
                <Link to={s.link} className="text-xs font-bold text-[#0050cb] hover:text-[#003fa4] inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                  <span>{s.linkText}</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </Link>
              </div>
            </div>
          ))}
        </div>

      </section>


      {/* ── ABOUT SECTION: Your Trusted Partner (Matching reference image) ── */}
      <section id="about" className="py-20 bg-white border-y border-slate-100">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Text */}
          <div className="lg:col-span-6 space-y-6">
            <span className="text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">ABOUT CAREERLENS</span>
            
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0b1c30] tracking-tight leading-tight">
              Your Trusted Partner for <br />
              <span className="text-[#0284c7]">Sustainable Tech Growth</span>
            </h2>

            <p className="text-slate-600 text-sm leading-relaxed">
              At CareerLens AI, we combine live ATS parsing with transparent data heuristics to eliminate hiring friction, unlock verified opportunities, and help professionals achieve long-term career success.
            </p>

            <ul className="space-y-3 pt-2">
              {[
                'Client-Centric 100% Direct Apply Links (Zero Middlemen)',
                'Strict Geofencing Across Bengaluru, NCR, Hyd & Remote',
                'Transparent 5-Category ATS Resume Score Breakdown',
                'Continuous Freshness Expiry for Stale Job Posts'
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-3 text-xs font-bold text-slate-700">
                  <div className="w-5 h-5 rounded-full bg-blue-50 text-[#0050cb] flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-sm font-bold">check</span>
                  </div>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <div className="pt-2">
              <Link 
                to="/register" 
                className="inline-flex items-center justify-center px-8 py-3.5 rounded-xl bg-[#0050cb] hover:bg-[#003fa4] text-white font-bold text-sm shadow-md shadow-blue-600/20 transition-all active:scale-95"
              >
                Get Started Free
              </Link>
            </div>
          </div>

          {/* Right Image with Floating Badge */}
          <div className="lg:col-span-6 relative">
            <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-slate-100 group">
              <img 
                src="/images/campus_card.jpg" 
                alt="Corporate Technology Headquarters" 
                className="w-full h-[380px] object-cover transition-transform duration-500 group-hover:scale-105"
              />

              {/* Floating Badge (Matching reference image) */}
              <div className="absolute bottom-6 right-6 bg-white/95 backdrop-blur-md rounded-2xl p-5 shadow-xl border border-slate-100 text-left max-w-[220px]">
                <div className="text-3xl font-extrabold text-[#0050cb]">100%</div>
                <div className="text-xs font-bold text-slate-900 mt-1">Live Verified ATS Feeds</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Delivering authentic career opportunities across India.</div>
              </div>
            </div>
          </div>

        </div>
      </section>


      {/* ── TRUSTED BY LEADING BRANDS BAR (Matching reference image) ── */}
      <section className="py-14 border-b border-slate-100 bg-[#f8faff]">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-8">
            TRUSTED BY TECH HUBS & PROFILES FROM
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-14 opacity-70 hover:opacity-100 transition-opacity">
            {hiringCompanies.map((c) => (
              <div key={c.name} className="flex items-center gap-2">
                <span className="font-extrabold text-slate-800 text-base tracking-tight">{c.name}</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-[#0050cb] border border-blue-100">{c.tag}</span>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* ── Testimonials ── */}
      <section id="testimonials" className="py-24 max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <span className="text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">TESTIMONIALS</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0b1c30]">
            Trusted by Professionals Across India
          </h2>
          <p className="text-slate-600 text-sm">Real career stories from candidates who used CareerLens AI to land direct offers.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div key={i} className="p-7 bg-white rounded-2xl border border-slate-100 shadow-md shadow-slate-100/50 flex flex-col justify-between space-y-4 hover:shadow-lg transition-all">
              <div className="space-y-3">
                <span className="inline-block px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-[#0050cb] text-xs font-bold">
                  {t.badge}
                </span>
                <p className="text-slate-600 text-xs leading-relaxed italic">"{t.quote}"</p>
              </div>
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <div className="font-bold text-[#0b1c30] text-sm">{t.name}</div>
                  <div className="text-xs text-slate-400">{t.role}</div>
                </div>
                <span className="text-xs font-semibold text-slate-500">{t.loc}</span>
              </div>
            </div>
          ))}
        </div>
      </section>


      {/* ── FAQ ── */}
      <section id="faq" className="py-20 px-6 max-w-4xl mx-auto border-t border-slate-100">
        <div className="text-center mb-14 space-y-2">
          <span className="text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">FAQ</span>
          <h2 className="text-3xl font-extrabold text-[#0b1c30]">Frequently Asked Questions</h2>
          <p className="text-slate-500 text-xs">Everything you need to know about our data sources and scoring algorithm.</p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openFaq === index
            return (
              <div key={index} className="rounded-xl bg-white border border-slate-100 shadow-sm overflow-hidden">
                <button
                  onClick={() => setOpenFaq(isOpen ? -1 : index)}
                  className="w-full p-5 text-left font-bold text-slate-800 text-sm flex justify-between items-center gap-4 hover:text-[#0050cb] transition-colors"
                >
                  <span>{faq.q}</span>
                  <span className="material-symbols-outlined text-slate-400 shrink-0">
                    {isOpen ? 'remove' : 'add'}
                  </span>
                </button>
                {isOpen && (
                  <div className="px-5 pb-5 text-xs text-slate-600 leading-relaxed border-t border-slate-100 pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>


      {/* ── Final CTA ── */}
      <section className="py-20 px-6 max-w-5xl mx-auto">
        <div className="relative rounded-3xl p-10 sm:p-14 bg-gradient-to-r from-[#0050cb] to-[#0284c7] text-center space-y-6 overflow-hidden shadow-2xl shadow-blue-500/20 text-white">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Ready to Accelerate Your Tech Career?
          </h2>
          <p className="text-blue-100 text-sm max-w-xl mx-auto leading-relaxed">
            Join thousands of engineering and data professionals finding real opportunities with transparent ATS guidance.
          </p>
          <div className="pt-2">
            <Link 
              to="/register" 
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-white text-[#0050cb] font-extrabold text-sm hover:bg-blue-50 hover:scale-[1.02] active:scale-95 transition-all shadow-lg"
            >
              <span>Get Started Now — It's Free</span>
              <span className="material-symbols-outlined text-lg">arrow_forward</span>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
