import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState(0)

  const features = [
    { icon: 'explore', title: 'Smart Job Discovery', desc: 'Our proprietary AI analyzes 50+ data points to match you with opportunities that align with your true potential.', bullets: ['Hyper-personalized matching', 'Hidden market insights'], large: true },
    { icon: 'description', title: 'Resume Analysis', desc: 'Instant feedback on your CV. Get ATS-optimization tips and clarity on how your experience maps to industry requirements.', large: false },
    { icon: 'school', title: 'Skill Learning', desc: 'Close the gap between your current skills and your target role with curated learning paths.', tags: ['Python', 'Data Viz', 'Agile', 'SQL'], large: false },
    { icon: 'map', title: 'Career Roadmaps', desc: 'Visualize your long-term career trajectory. See milestones required to reach leadership roles.', large: true },
  ]

  const testimonials = [
    { name: 'Sarah Jenkins', role: 'Product Designer at FinTech', quote: 'The resume analysis was a game-changer. I went from zero responses to three interviews in one week.' },
    { name: 'Marcus Rivera', role: 'DevOps Engineer', quote: 'I loved the skill roadmap feature. It told me exactly what I needed to learn to transition from Support to DevOps.' },
    { name: 'Aisha Thompson', role: 'Sr. Marketing Manager', quote: 'CareerLens feels like having a personal mentor 24/7. It helped me negotiate a 20% higher salary.' },
  ]

  const faqs = [
    { q: 'How does the AI matching work?', a: 'Our AI processes millions of job descriptions and successful hire profiles to understand the semantic relationship between skills, experience, and role requirements. It provides a "Match Score" based on your unique profile.' },
    { q: 'Is my data secure?', a: 'Yes. We use industry-standard encryption and never sell your personal data. Your resume is processed privately to provide insights only accessible to you.' },
    { q: 'Can I use it for internship hunting?', a: 'Absolutely. We have over 5,000 internship listings tailored for students and early-career professionals, with specific filters for remote and summer roles.' },
    { q: 'What is the Trust Score?', a: 'Trust Score indicates the reliability of an opportunity source. Official company career pages get 100, LinkedIn gets 90, while other portals range from 60-85.' },
  ]

  return (
    <div className="bg-surface text-on-surface overflow-x-hidden">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-surface/80 backdrop-blur-md border-b border-outline-variant flex justify-between items-center h-16 px-lg w-full">
        <div className="flex items-center gap-md">
          <span className="text-2xl font-bold text-primary">CareerLens AI</span>
        </div>
        <nav className="hidden md:flex items-center gap-xl">
          <a className="text-sm font-medium font-[Geist] text-primary font-bold active-tab-line" href="#home">Home</a>
          <a className="text-sm font-medium font-[Geist] text-on-surface-variant hover:text-primary transition-colors" href="#features">Features</a>
          <a className="text-sm font-medium font-[Geist] text-on-surface-variant hover:text-primary transition-colors" href="#testimonials">Reviews</a>
          <a className="text-sm font-medium font-[Geist] text-on-surface-variant hover:text-primary transition-colors" href="#faq">FAQ</a>
        </nav>
        <div className="flex items-center gap-md">
          <Link to="/login" className="text-sm font-medium font-[Geist] text-on-surface-variant hover:text-primary transition-colors hidden sm:block">Login</Link>
          <Link to="/register" className="bg-primary text-on-primary px-lg py-sm rounded-lg text-sm font-medium font-[Geist] hover:opacity-90 transition-all">
            Get Started
          </Link>
        </div>
      </header>

      <main className="max-w-[1440px] mx-auto">
        {/* Hero Section */}
        <section id="home" className="relative pt-2xl pb-3xl px-lg overflow-hidden">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto space-y-md animate-fade-in-up">
            <div className="inline-flex items-center px-md py-xs rounded-full bg-secondary-container text-on-secondary-container text-xs font-medium font-[Geist] mb-md">
              <span className="material-symbols-outlined text-[16px] mr-xs" style={{fontVariationSettings: "'FILL' 1"}}>spark</span>
              Next-Gen Job Matching is Here
            </div>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-on-background leading-tight">
              Search Once. Learn <span className="text-primary">Smart.</span> Get Hired.
            </h1>
            <p className="text-lg text-on-surface-variant max-w-2xl">
              Experience the future of career growth with CareerLens AI. We combine deep market intelligence with personalized skill paths to land your dream role.
            </p>
            <div className="flex flex-col sm:flex-row gap-md pt-md">
              <Link to="/app/opportunities" className="bg-primary text-on-primary px-xl py-md rounded-lg text-sm font-medium font-[Geist] hover:opacity-90 transition-all flex items-center gap-sm">
                Find Opportunities
                <span className="material-symbols-outlined">trending_flat</span>
              </Link>
              <Link to="/app/careers" className="bg-white border border-outline-variant text-on-surface px-xl py-md rounded-lg text-sm font-medium font-[Geist] hover:bg-surface-container-low transition-all">
                Explore Careers
              </Link>
            </div>
          </div>

          {/* Search Panel */}
          <div className="mt-3xl max-w-5xl mx-auto glass-effect p-sm rounded-xl shadow-xl flex flex-col md:flex-row items-center gap-sm">
            <div className="flex-1 w-full flex items-center px-md py-sm bg-white rounded-lg border border-transparent focus-within:border-primary-container transition-all">
              <span className="material-symbols-outlined text-outline mr-sm">work</span>
              <input className="w-full bg-transparent border-none focus:ring-0 focus:outline-none text-base text-on-surface" placeholder="Job title, keywords, or company" type="text" />
            </div>
            <div className="w-px h-8 bg-outline-variant hidden md:block"></div>
            <div className="flex-1 w-full flex items-center px-md py-sm bg-white rounded-lg border border-transparent focus-within:border-primary-container transition-all">
              <span className="material-symbols-outlined text-outline mr-sm">location_on</span>
              <input className="w-full bg-transparent border-none focus:ring-0 focus:outline-none text-base text-on-surface" placeholder="Location or Remote" type="text" />
            </div>
            <Link to="/app/opportunities" className="w-full md:w-auto bg-primary text-on-primary px-xl py-sm rounded-lg text-sm font-medium font-[Geist] hover:shadow-lg transition-all text-center">
              Search Jobs
            </Link>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-xl bg-surface-container-low">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-xl px-lg text-center stagger-children">
            <div className="space-y-xs">
              <div className="text-3xl font-semibold text-primary">10k+</div>
              <div className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-widest">Active Jobs</div>
            </div>
            <div className="space-y-xs">
              <div className="text-3xl font-semibold text-primary">5k+</div>
              <div className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-widest">Internship Openings</div>
            </div>
            <div className="space-y-xs">
              <div className="text-3xl font-semibold text-primary">50k+</div>
              <div className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase tracking-widest">Successful Users</div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="py-3xl px-lg">
          <div className="text-center mb-2xl">
            <h2 className="text-3xl font-semibold text-on-background">Everything you need to level up</h2>
            <p className="text-base text-on-surface-variant mt-sm">AI-driven tools tailored for the modern professional</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-12 gap-lg max-w-[1440px] mx-auto stagger-children">
            {/* Feature 1: Job Discovery */}
            <div className="md:col-span-8 bg-white border border-outline-variant rounded-xl p-xl hover:shadow-lg transition-all group flex flex-col md:flex-row gap-xl items-center">
              <div className="flex-1 space-y-md text-center md:text-left">
                <div className="w-12 h-12 rounded-lg bg-primary-container flex items-center justify-center text-on-primary">
                  <span className="material-symbols-outlined">explore</span>
                </div>
                <h3 className="text-2xl font-semibold">Smart Job Discovery</h3>
                <p className="text-base text-on-surface-variant leading-relaxed">
                  Our proprietary AI analyzes 50+ data points to match you with opportunities that align with your true potential, not just your past.
                </p>
                <ul className="space-y-sm text-left">
                  <li className="flex items-center gap-sm text-sm"><span className="material-symbols-outlined text-primary text-[18px]">check_circle</span> Hyper-personalized matching</li>
                  <li className="flex items-center gap-sm text-sm"><span className="material-symbols-outlined text-primary text-[18px]">check_circle</span> Hidden market insights</li>
                </ul>
              </div>
              <div className="flex-1 relative w-full aspect-video md:aspect-square bg-gradient-to-br from-primary/5 to-primary/15 rounded-lg overflow-hidden border border-outline-variant flex items-center justify-center">
                <span className="material-symbols-outlined text-7xl text-primary/20">travel_explore</span>
              </div>
            </div>
            {/* Feature 2: Resume Analysis */}
            <div className="md:col-span-4 bg-white border border-outline-variant rounded-xl p-xl hover:shadow-lg transition-all group space-y-md">
              <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">description</span>
              </div>
              <h3 className="text-2xl font-semibold">Resume Analysis</h3>
              <p className="text-base text-on-surface-variant">
                Instant feedback on your CV. Get ATS-optimization tips and clarity on how your experience maps to industry requirements.
              </p>
              <div className="pt-md border-t border-outline-variant">
                <div className="bg-primary/5 p-md rounded-lg ai-shimmer">
                  <div className="flex items-center gap-sm mb-xs">
                    <span className="material-symbols-outlined text-primary text-[16px]" style={{fontVariationSettings: "'FILL' 1"}}>spark</span>
                    <span className="text-xs font-medium font-[Geist] text-primary">AI Insight</span>
                  </div>
                  <div className="h-2 w-full bg-outline-variant/30 rounded-full mb-xs"></div>
                  <div className="h-2 w-3/4 bg-outline-variant/30 rounded-full"></div>
                </div>
              </div>
            </div>
            {/* Feature 3: Skill Learning */}
            <div className="md:col-span-4 bg-white border border-outline-variant rounded-xl p-xl hover:shadow-lg transition-all group space-y-md">
              <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">school</span>
              </div>
              <h3 className="text-2xl font-semibold">Skill Learning</h3>
              <p className="text-base text-on-surface-variant">
                Close the gap between your current skills and your target role with curated learning paths from top-tier educational partners.
              </p>
              <div className="flex gap-sm flex-wrap pt-sm">
                {['Python', 'Data Viz', 'Agile', 'SQL'].map(tag => (
                  <span key={tag} className="px-sm py-xs bg-surface-container rounded text-xs font-medium font-[Geist] text-on-surface-variant">{tag}</span>
                ))}
              </div>
            </div>
            {/* Feature 4: Career Roadmaps */}
            <div className="md:col-span-8 bg-white border border-outline-variant rounded-xl p-xl hover:shadow-lg transition-all group flex flex-col md:flex-row-reverse gap-xl items-center">
              <div className="flex-1 space-y-md text-center md:text-left">
                <div className="w-12 h-12 rounded-lg bg-primary-container flex items-center justify-center text-on-primary">
                  <span className="material-symbols-outlined">map</span>
                </div>
                <h3 className="text-2xl font-semibold">Career Roadmaps</h3>
                <p className="text-base text-on-surface-variant leading-relaxed">
                  Visualize your long-term career trajectory. See where your current path leads and discover the milestones required to reach executive leadership.
                </p>
                <Link to="/app/careers" className="text-primary text-sm font-medium font-[Geist] flex items-center gap-xs mt-md hover:gap-sm transition-all">
                  Build my roadmap <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </Link>
              </div>
              <div className="flex-1 w-full aspect-video bg-gradient-to-br from-primary/5 to-primary/15 rounded-lg overflow-hidden border border-outline-variant flex items-center justify-center">
                <span className="material-symbols-outlined text-7xl text-primary/20">route</span>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="py-3xl bg-white border-y border-outline-variant">
          <div className="px-lg">
            <div className="flex flex-col md:flex-row justify-between items-end mb-2xl gap-md">
              <div>
                <h2 className="text-3xl font-semibold text-on-background">Voices of Success</h2>
                <p className="text-base text-on-surface-variant mt-sm">Real stories from professionals who transformed their careers.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg stagger-children">
              {testimonials.map((t, i) => (
                <div key={i} className="p-xl bg-surface-bright border border-outline-variant rounded-xl flex flex-col justify-between hover:shadow-lg transition-all">
                  <p className="text-base text-on-surface-variant italic mb-xl leading-relaxed">"{t.quote}"</p>
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold">
                      {t.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <div className="text-sm font-medium font-[Geist] text-on-background">{t.name}</div>
                      <div className="text-xs font-medium font-[Geist] text-on-surface-variant">{t.role}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="py-3xl px-lg max-w-4xl mx-auto">
          <h2 className="text-3xl font-semibold text-on-background text-center mb-2xl">Common Questions</h2>
          <div className="space-y-sm">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-white border border-outline-variant rounded-lg overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? -1 : i)}
                  className="flex justify-between items-center p-md cursor-pointer hover:bg-surface-container-low transition-colors w-full text-left"
                >
                  <span className="text-sm font-medium font-[Geist] text-on-background">{faq.q}</span>
                  <span className={`material-symbols-outlined transition-transform ${openFaq === i ? 'rotate-180' : ''}`}>expand_more</span>
                </button>
                {openFaq === i && (
                  <div className="p-md pt-0 text-base text-on-surface-variant border-t border-outline-variant/30 mt-xs">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="mx-lg my-3xl relative overflow-hidden bg-on-background text-on-primary p-3xl rounded-2xl flex flex-col items-center text-center">
          <div className="relative z-10 space-y-md">
            <h2 className="text-3xl md:text-5xl font-semibold text-white">Start Your Career Journey Today</h2>
            <p className="text-lg text-surface-dim max-w-xl mx-auto">
              Join thousands of professionals using CareerLens AI to navigate their next big move.
            </p>
            <div className="pt-xl flex flex-col sm:flex-row gap-md justify-center">
              <Link to="/register" className="bg-primary text-on-primary px-2xl py-md rounded-lg text-sm font-medium font-[Geist] hover:scale-105 transition-transform">
                Get Started Free
              </Link>
              <Link to="/login" className="bg-transparent border border-outline text-white px-2xl py-md rounded-lg text-sm font-medium font-[Geist] hover:bg-white/10 transition-all">
                Sign In
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-surface border-t border-outline-variant pt-3xl pb-xl px-lg">
        <div className="max-w-[1440px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-xl">
          <div className="col-span-2 md:col-span-1 space-y-md">
            <div className="text-2xl font-bold text-primary">CareerLens AI</div>
            <p className="text-sm text-on-surface-variant">
              Empowering the workforce of tomorrow with intelligent, data-driven career guidance.
            </p>
          </div>
          <div className="space-y-md">
            <div className="text-sm font-bold font-[Geist] text-on-background">Platform</div>
            <ul className="space-y-sm">
              <li><Link className="text-sm text-on-surface-variant hover:text-primary transition-colors" to="/app/opportunities">Jobs Board</Link></li>
              <li><Link className="text-sm text-on-surface-variant hover:text-primary transition-colors" to="/app/learn">Skills Library</Link></li>
              <li><Link className="text-sm text-on-surface-variant hover:text-primary transition-colors" to="/app/careers">Careers</Link></li>
            </ul>
          </div>
          <div className="space-y-md">
            <div className="text-sm font-bold font-[Geist] text-on-background">Company</div>
            <ul className="space-y-sm">
              <li><a className="text-sm text-on-surface-variant hover:text-primary transition-colors" href="#">About Us</a></li>
              <li><a className="text-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Contact</a></li>
              <li><a className="text-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Blog</a></li>
            </ul>
          </div>
          <div className="space-y-md">
            <div className="text-sm font-bold font-[Geist] text-on-background">Legal</div>
            <ul className="space-y-sm">
              <li><a className="text-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Privacy Policy</a></li>
              <li><a className="text-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-[1440px] mx-auto mt-3xl pt-xl border-t border-outline-variant flex flex-col md:flex-row justify-between items-center gap-md">
          <p className="text-xs font-medium font-[Geist] text-on-surface-variant">© 2024 CareerLens AI. All rights reserved.</p>
          <div className="flex items-center gap-sm text-xs font-medium font-[Geist] text-on-surface-variant">
            Made with <span className="material-symbols-outlined text-error text-[16px]" style={{fontVariationSettings: "'FILL' 1"}}>favorite</span> for growth
          </div>
        </div>
      </footer>
    </div>
  )
}
