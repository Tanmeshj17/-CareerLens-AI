import { Link } from 'react-router-dom'
import { useState } from 'react'
import Footer from '../components/Footer'
import CareerLensLogo from '../components/CareerLensLogo'

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState(0)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

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
      
      {/* ── Top Navbar (Fully Responsive) ── */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-100 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <CareerLensLogo size="md" />
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600">
            <a href="#home" className="text-[#0050cb] font-bold">Home</a>
            <a href="#services" className="hover:text-[#0050cb] transition-colors">Services</a>
            <a href="#about" className="hover:text-[#0050cb] transition-colors">About Us</a>
            <a href="#testimonials" className="hover:text-[#0050cb] transition-colors">Reviews</a>
            <a href="#faq" className="hover:text-[#0050cb] transition-colors">FAQ</a>
          </nav>

          {/* Desktop & Mobile Actions */}
          <div className="flex items-center gap-2 sm:gap-4">
            <Link to="/login" className="text-xs sm:text-sm font-bold text-slate-700 hover:text-[#0050cb] transition-colors px-2 sm:px-3 py-1.5">
              Log In
            </Link>
            <Link 
              to="/register" 
              className="bg-[#0050cb] hover:bg-[#003fa4] text-white px-3.5 sm:px-6 py-2 sm:py-2.5 rounded-xl text-xs sm:text-sm font-bold shadow-md shadow-blue-600/20 hover:shadow-lg hover:shadow-blue-600/30 transition-all active:scale-95 shrink-0"
            >
              Get Started
            </Link>

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-700 hover:text-[#0050cb] hover:bg-slate-100 rounded-lg transition-colors ml-1"
              aria-label="Toggle navigation menu"
            >
              <span className="material-symbols-outlined text-2xl">
                {mobileMenuOpen ? 'close' : 'menu'}
              </span>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-b border-slate-200 px-4 py-4 space-y-3 shadow-lg animate-fade-in-up">
            <a 
              href="#home" 
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-bold text-[#0050cb] hover:bg-slate-50 rounded-lg px-3"
            >
              Home
            </a>
            <a 
              href="#services" 
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-semibold text-slate-700 hover:text-[#0050cb] hover:bg-slate-50 rounded-lg px-3"
            >
              Services
            </a>
            <a 
              href="#about" 
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-semibold text-slate-700 hover:text-[#0050cb] hover:bg-slate-50 rounded-lg px-3"
            >
              About Us
            </a>
            <a 
              href="#testimonials" 
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-semibold text-slate-700 hover:text-[#0050cb] hover:bg-slate-50 rounded-lg px-3"
            >
              Reviews
            </a>
            <a 
              href="#faq" 
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-semibold text-slate-700 hover:text-[#0050cb] hover:bg-slate-50 rounded-lg px-3"
            >
              FAQ
            </a>
            <div className="pt-2 border-t border-slate-100 flex gap-2">
              <Link 
                to="/app/opportunities" 
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 py-2.5 text-center bg-blue-50 text-[#0050cb] rounded-lg text-xs font-bold"
              >
                Browse Opportunities
              </Link>
            </div>
          </div>
        )}
      </header>


      {/* ── Hero Section (Fluid Mobile-to-Desktop Background Layout) ── */}
      <section id="home" className="relative min-h-[500px] sm:min-h-[580px] lg:min-h-[640px] flex items-center overflow-hidden">
        
        {/* Background Image with Responsive Dual-Axis Gradient Mask */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img 
            src="/images/hero_architectural.jpg" 
            alt="Modern Glass Technology Campus" 
            className="w-full h-full object-cover object-center sm:object-right"
          />
          {/* Mobile Overlay: Vertical gentle wash so text is 100% readable on phones */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#f8faff]/95 via-[#f8faff]/88 to-[#f8faff] sm:hidden" />
          {/* Desktop Overlay: Left-to-right fade */}
          <div className="hidden sm:block absolute inset-0 bg-gradient-to-r from-[#f8faff] via-[#f8faff]/90 to-transparent md:w-[65%] w-full" />
          <div className="hidden sm:block absolute inset-0 bg-gradient-to-t from-[#f8faff] via-transparent to-transparent h-24 bottom-0" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-12 sm:py-16 lg:py-20 w-full">
          <div className="max-w-xl space-y-4 sm:space-y-6 text-center sm:text-left">
            
            {/* Small Label */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50/90 border border-blue-200/80 text-[10px] sm:text-xs font-extrabold text-[#0050cb] tracking-wide backdrop-blur-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>REAL-TIME JOB INTELLIGENCE ENGINE</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold text-[#0b1c30] tracking-tight leading-[1.15] sm:leading-[1.12]">
              Innovating Careers, <br className="hidden xs:inline" />
              <span className="text-[#0284c7]">Inspiring Tomorrow</span>
            </h1>

            {/* Subtitle */}
            <p className="text-sm sm:text-base md:text-lg text-slate-600 leading-relaxed font-normal max-w-lg mx-auto sm:mx-0">
              We deliver real-time ATS intelligence and verified opportunities that drive career growth, empower job seekers, and create lasting impact across India.
            </p>

            {/* Buttons Row (Full width on small phones, inline on larger screens) */}
            <div className="flex flex-col xs:flex-row items-center gap-3 sm:gap-4 pt-2 justify-center sm:justify-start">
              <Link 
                to="/app/opportunities" 
                className="w-full xs:w-auto px-6 sm:px-8 py-3 sm:py-3.5 rounded-xl bg-[#0050cb] hover:bg-[#003fa4] text-white font-bold text-xs sm:text-sm shadow-lg shadow-blue-600/25 hover:shadow-blue-600/35 transition-all text-center active:scale-95"
              >
                Our Services
              </Link>
              <Link 
                to="/app/resume" 
                className="w-full xs:w-auto px-5 sm:px-6 py-3 sm:py-3.5 rounded-xl bg-white/95 hover:bg-white border border-slate-300 text-slate-800 font-bold text-xs sm:text-sm shadow-sm transition-all flex items-center justify-center gap-2 active:scale-95 hover:border-slate-400"
              >
                <span className="material-symbols-outlined text-[#0050cb] text-base sm:text-lg">play_arrow</span>
                <span>Watch Overview</span>
              </Link>
            </div>

          </div>
        </div>

      </section>


      {/* ── Floating Stats Card (Mobile 2x2 Grid, Desktop 4 Columns) ── */}
      <section className="relative z-20 -mt-6 sm:-mt-8 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/70 border border-slate-100 p-4 sm:p-7 grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 items-center">
          
          <div className="flex items-center gap-2.5 sm:gap-4 border-r border-slate-100 pr-2 sm:pr-4">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-sky-50 text-[#0284c7] flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl sm:text-2xl">group</span>
            </div>
            <div>
              <div className="text-lg sm:text-2xl font-extrabold text-[#0b1c30]">1,000+</div>
              <div className="text-[10px] sm:text-xs text-slate-500 font-medium leading-tight">Verified Jobs</div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-4 md:border-r md:border-slate-100 pr-2 sm:pr-4">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl sm:text-2xl">work</span>
            </div>
            <div>
              <div className="text-lg sm:text-2xl font-extrabold text-[#0b1c30]">500+</div>
              <div className="text-[10px] sm:text-xs text-slate-500 font-medium leading-tight">Internships</div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-4 border-r border-slate-100 pr-2 sm:pr-4 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl sm:text-2xl">trophy</span>
            </div>
            <div>
              <div className="text-lg sm:text-2xl font-extrabold text-[#0b1c30]">95%+</div>
              <div className="text-[10px] sm:text-xs text-slate-500 font-medium leading-tight">India Roles</div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-4 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-xl sm:text-2xl">public</span>
            </div>
            <div>
              <div className="text-lg sm:text-2xl font-extrabold text-[#0b1c30]">100%</div>
              <div className="text-[10px] sm:text-xs text-slate-500 font-medium leading-tight">Direct Apply</div>
            </div>
          </div>

        </div>
      </section>


      {/* ── WHAT WE DO: 4-Card Solutions Grid ── */}
      <section id="services" className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 sm:gap-6 mb-10 sm:mb-14">
          <div className="max-w-xl space-y-1.5 sm:space-y-2">
            <span className="text-[11px] sm:text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">WHAT WE DO</span>
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#0b1c30] tracking-tight">
              Solutions that <br className="hidden sm:inline" />
              Drive <span className="text-[#0284c7]">Real Impact</span>
            </h2>
          </div>
          <div className="max-w-md space-y-2 text-slate-600 text-xs sm:text-sm">
            <p>From live ATS indexing to precision career roadmaps, we provide end-to-end intelligence built for modern tech professionals.</p>
            <Link to="/app/opportunities" className="inline-flex items-center gap-1.5 text-[#0050cb] font-bold hover:gap-2.5 transition-all text-xs sm:text-sm">
              <span>Explore All Services</span>
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </Link>
          </div>
        </div>

        {/* 4 Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {services.map((s, idx) => (
            <div 
              key={idx} 
              className="bg-white rounded-2xl p-5 sm:p-7 border border-slate-100 shadow-sm hover:shadow-xl hover:border-slate-200 transition-all group flex flex-col justify-between"
            >
              <div className="space-y-3 sm:space-y-4">
                <div className={`w-11 h-11 sm:w-12 sm:h-12 rounded-xl border flex items-center justify-center ${s.color}`}>
                  <span className="material-symbols-outlined text-xl sm:text-2xl">{s.icon}</span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-[#0b1c30] group-hover:text-[#0050cb] transition-colors">
                  {s.title}
                </h3>
                <p className="text-slate-500 text-xs leading-relaxed">
                  {s.desc}
                </p>
              </div>

              <div className="pt-4 sm:pt-6 mt-4 border-t border-slate-50">
                <Link to={s.link} className="text-xs font-bold text-[#0050cb] hover:text-[#003fa4] inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                  <span>{s.linkText}</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </Link>
              </div>
            </div>
          ))}
        </div>

      </section>


      {/* ── ABOUT SECTION: Your Trusted Partner ── */}
      <section id="about" className="py-16 sm:py-20 bg-white border-y border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 grid grid-cols-1 lg:grid-cols-12 gap-8 sm:gap-12 items-center">
          
          {/* Left Text */}
          <div className="lg:col-span-6 space-y-4 sm:space-y-6">
            <span className="text-[11px] sm:text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">ABOUT CAREERLENS</span>
            
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#0b1c30] tracking-tight leading-tight">
              Your Trusted Partner for <br />
              <span className="text-[#0284c7]">Sustainable Tech Growth</span>
            </h2>

            <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
              At CareerLens AI, we combine live ATS parsing with transparent data heuristics to eliminate hiring friction, unlock verified opportunities, and help professionals achieve long-term career success.
            </p>

            <ul className="space-y-2.5 sm:space-y-3 pt-1">
              {[
                'Client-Centric 100% Direct Apply Links (Zero Middlemen)',
                'Strict Geofencing Across Bengaluru, NCR, Hyd & Remote',
                'Transparent 5-Category ATS Resume Score Breakdown',
                'Continuous Freshness Expiry for Stale Job Posts'
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-2.5 sm:gap-3 text-xs font-bold text-slate-700">
                  <div className="w-5 h-5 rounded-full bg-blue-50 text-[#0050cb] flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-xs sm:text-sm font-bold">check</span>
                  </div>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <div className="pt-2">
              <Link 
                to="/register" 
                className="inline-flex items-center justify-center w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-3.5 rounded-xl bg-[#0050cb] hover:bg-[#003fa4] text-white font-bold text-xs sm:text-sm shadow-md shadow-blue-600/20 transition-all active:scale-95 text-center"
              >
                Get Started Free
              </Link>
            </div>
          </div>

          {/* Right Image with Fluid Responsive Floating Badge */}
          <div className="lg:col-span-6 relative mt-4 lg:mt-0">
            <div className="relative rounded-2xl sm:rounded-3xl overflow-hidden shadow-xl border border-slate-100 group">
              <img 
                src="/images/campus_card.jpg" 
                alt="Corporate Technology Headquarters" 
                className="w-full h-[260px] sm:h-[340px] md:h-[380px] object-cover transition-transform duration-500 group-hover:scale-105"
              />

              {/* Floating Badge (Auto-scales on mobile) */}
              <div className="absolute bottom-3 right-3 sm:bottom-6 sm:right-6 bg-white/95 backdrop-blur-md rounded-xl sm:rounded-2xl p-3 sm:p-5 shadow-xl border border-slate-100 text-left max-w-[170px] sm:max-w-[220px]">
                <div className="text-xl sm:text-3xl font-extrabold text-[#0050cb]">100%</div>
                <div className="text-[11px] sm:text-xs font-bold text-slate-900 mt-0.5 sm:mt-1 leading-tight">Live Verified ATS Feeds</div>
                <div className="text-[9px] sm:text-[10px] text-slate-500 mt-0.5 hidden xs:block">Delivering authentic career opportunities across India.</div>
              </div>
            </div>
          </div>

        </div>
      </section>


      {/* ── TRUSTED BY LEADING BRANDS BAR ── */}
      <section className="py-10 sm:py-14 border-b border-slate-100 bg-[#f8faff]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 text-center">
          <p className="text-[10px] sm:text-xs font-bold text-slate-400 uppercase tracking-widest mb-6 sm:mb-8">
            TRUSTED BY TECH HUBS & PROFILES FROM
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-8 lg:gap-12 opacity-75 hover:opacity-100 transition-opacity">
            {hiringCompanies.map((c) => (
              <div key={c.name} className="flex items-center gap-1.5 sm:gap-2 px-2 py-1">
                <span className="font-extrabold text-slate-800 text-xs sm:text-base tracking-tight">{c.name}</span>
                <span className="text-[9px] sm:text-[10px] font-semibold px-1.5 sm:px-2 py-0.5 rounded-full bg-blue-50 text-[#0050cb] border border-blue-100">{c.tag}</span>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* ── Testimonials ── */}
      <section id="testimonials" className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-10 sm:mb-16 space-y-2 sm:space-y-3">
          <span className="text-[11px] sm:text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">TESTIMONIALS</span>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#0b1c30]">
            Trusted by Professionals Across India
          </h2>
          <p className="text-slate-600 text-xs sm:text-sm">Real career stories from candidates who used CareerLens AI to land direct offers.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
          {testimonials.map((t, i) => (
            <div key={i} className="p-5 sm:p-7 bg-white rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-between space-y-4 hover:shadow-lg transition-all">
              <div className="space-y-3">
                <span className="inline-block px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-[#0050cb] text-[10px] sm:text-xs font-bold">
                  {t.badge}
                </span>
                <p className="text-slate-600 text-xs sm:text-sm leading-relaxed italic">"{t.quote}"</p>
              </div>
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <div className="font-bold text-[#0b1c30] text-xs sm:text-sm">{t.name}</div>
                  <div className="text-[10px] sm:text-xs text-slate-400">{t.role}</div>
                </div>
                <span className="text-[10px] sm:text-xs font-semibold text-slate-500">{t.loc}</span>
              </div>
            </div>
          ))}
        </div>
      </section>


      {/* ── FAQ ── */}
      <section id="faq" className="py-14 sm:py-20 px-4 sm:px-6 max-w-4xl mx-auto border-t border-slate-100">
        <div className="text-center mb-10 sm:mb-14 space-y-1.5 sm:space-y-2">
          <span className="text-[11px] sm:text-xs font-extrabold text-[#0050cb] uppercase tracking-widest block">FAQ</span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0b1c30]">Frequently Asked Questions</h2>
          <p className="text-slate-500 text-xs">Everything you need to know about our data sources and scoring algorithm.</p>
        </div>

        <div className="space-y-3 sm:space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openFaq === index
            return (
              <div key={index} className="rounded-xl bg-white border border-slate-100 shadow-sm overflow-hidden">
                <button
                  onClick={() => setOpenFaq(isOpen ? -1 : index)}
                  className="w-full p-4 sm:p-5 text-left font-bold text-slate-800 text-xs sm:text-sm flex justify-between items-center gap-3 hover:text-[#0050cb] transition-colors"
                >
                  <span>{faq.q}</span>
                  <span className="material-symbols-outlined text-slate-400 shrink-0 text-base sm:text-xl">
                    {isOpen ? 'remove' : 'add'}
                  </span>
                </button>
                {isOpen && (
                  <div className="px-4 sm:px-5 pb-4 sm:pb-5 text-xs text-slate-600 leading-relaxed border-t border-slate-100 pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>


      {/* ── Final CTA ── */}
      <section className="py-12 sm:py-20 px-4 sm:px-6 max-w-5xl mx-auto">
        <div className="relative rounded-2xl sm:rounded-3xl p-7 sm:p-14 bg-gradient-to-r from-[#0050cb] to-[#0284c7] text-center space-y-4 sm:space-y-6 overflow-hidden shadow-xl shadow-blue-500/20 text-white">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight">
            Ready to Accelerate Your Tech Career?
          </h2>
          <p className="text-blue-100 text-xs sm:text-sm max-w-xl mx-auto leading-relaxed">
            Join thousands of engineering and data professionals finding real opportunities with transparent ATS guidance.
          </p>
          <div className="pt-2">
            <Link 
              to="/register" 
              className="inline-flex items-center justify-center gap-2 w-full xs:w-auto px-6 sm:px-8 py-3 sm:py-3.5 rounded-xl bg-white text-[#0050cb] font-extrabold text-xs sm:text-sm hover:bg-blue-50 hover:scale-[1.02] active:scale-95 transition-all shadow-lg"
            >
              <span>Get Started Now — It's Free</span>
              <span className="material-symbols-outlined text-base sm:text-lg">arrow_forward</span>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
