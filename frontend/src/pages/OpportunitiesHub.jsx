import { useState } from 'react'

export default function OpportunitiesHub() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setSearched(true)
    }, 800)
  }

  const resetFilters = () => {
    setSearched(false)
  }

  const jobs = [
    {
      role: 'Senior Product Designer',
      company: 'Nebula Systems',
      logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCRPZh_ORjDnKNLxjdXrkgsCJ3iv-_fWD1BZGxHsminEXUAzazgZJBaRMtJyCSHqK8yAz6WssIh6nEiltmxABTMfKDfIaTgMAXU6LVGDS_72GHTou7q6t6yw8IfU6SYdFSl8kn53JJPYf32l0yAMX7AulpWtphQ8-JByjWbiGMHw-67rw-0sP5y7vxfD1RBbnswOGHiw_sUAy21tyO6aHEY-6P25WE0MwZn-jJ_tubDUzCkOMQrZqxAx1vPNbEy2_rveH1vPazRZMw',
      location: 'San Francisco, CA',
      exp: '5-8 yrs',
      salary: '$140k - $190k',
      match: '98%',
      matchType: 'Match',
      source: 'LinkedIn',
      time: '2 hours ago',
      color: 'primary'
    },
    {
      role: 'AI Research Intern',
      company: 'Aura Intelligence',
      logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBKLklGDx5NrIiHQ80RaslpiWYcExt2q9-a5qL80dhYrPE48ugHqCzZB4hiXW0yGNqq5W-KpNEF7QRbwkdQcj2rMt8sUHR-sXqlxoByu_ZHb19hQs7KQDfJlXZSh8592b-uR5kn0DwSkVIzbq5LRN81RCLZJjO3KteuPbb2DHwfGWA9eDany4V8GY8AU3f9JRtbwEGEgzENub2afy_lecFhiEc9xYuvE5TcxHFN12He7sS8tOEX0XEqOzRFdWJTMb_--3HxxU7KcrE',
      location: 'Remote',
      exp: '0-1 yrs',
      salary: '$45/hr - $60/hr',
      match: 'Recommended',
      matchType: 'Recommended',
      source: 'Indeed',
      time: '5 hours ago',
      color: 'secondary'
    },
    {
      role: 'Frontend Apprentice',
      company: 'BrightScale Labs',
      logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCqWE1md9mggaCFBoHo-u0VPbaPwS0a-y3oZKzOBYKXNz7SGtQ7CndOqCaKRzVA30NcRLABM23j6w5octfkN4rBNSEJma7-pGoO9mauP6lvCV9EwGXIZY77dqE12p6lJu00TwzVo25BIMH_dvjLygTCHf-98nGhr5QHpbrP2C1DGtcA9mAAdgphBvVir1asE060VTb36DQciCxbvZXoeTwIql9ms5GV1G3Gz658QmXHUkYx21mzmKs4518UVBUYtppxQE4O7pOu5UI',
      location: 'Austin, TX',
      exp: '0-1 yrs',
      salary: '$70k - $85k',
      match: 'Trainee',
      matchType: 'Trainee',
      source: 'Direct Apply',
      time: '1 day ago',
      color: 'tertiary'
    },
    {
      role: 'Data Science Lead',
      company: 'Quantify Analytics',
      logo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBYZjM7cI74MSLtxsTdw__ojw5p8twCut9HhluY8-CRHe06-6BetMpSrDB6Zxifd4wEeh02RUFN5ZJebZb9qjYF6Uccp5Ztzh5MrYDXA-wtN0_W6tX-6mNXu6zxeGPvxQ6E0qKs3W1LjS2eY-ogNKZ5xZXc4tR1WTd0G8EJiRsQJKY5s2qb7TPZTr1O4eBpeKbN5KJcJTkpOJyHmg_8C3RPcIf1c8-_uDU0yu0mevNdCejyP1Rw_4DFm9atcWi-DrXWjcFq4RTpZI0',
      location: 'New York, NY',
      exp: '8+ yrs',
      salary: '$200k - $250k',
      match: 'Urgent',
      matchType: 'Urgent',
      source: 'LinkedIn',
      time: '3 hours ago',
      color: 'error'
    }
  ]

  const getColorClasses = (color) => {
    switch (color) {
      case 'primary': return 'bg-primary/10 text-primary border-primary/20'
      case 'secondary': return 'bg-secondary-container text-on-secondary-container border-transparent'
      case 'tertiary': return 'bg-tertiary-fixed text-on-tertiary-fixed border-transparent'
      case 'error': return 'bg-error-container text-on-error-container border-transparent'
      default: return 'bg-surface-container text-on-surface border-transparent'
    }
  }

  return (
    <div className="space-y-lg flex flex-col min-h-full">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-md animate-fade-in-up">
        <div>
          <h2 className="text-3xl font-semibold text-on-background">Opportunities Hub</h2>
          <p className="text-base text-on-surface-variant">Discover AI-matched roles tailored to your skills and career trajectory.</p>
        </div>
        <div className="flex items-center gap-sm bg-primary-container/10 px-md py-sm rounded-lg border border-primary/20">
          <span className="material-symbols-outlined text-primary" style={{fontVariationSettings: "'FILL' 1"}}>auto_awesome</span>
          <span className="text-sm font-medium font-[Geist] text-primary">12 New Smart Matches</span>
        </div>
      </div>

      {/* Search & Filter Header */}
      <section className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm space-y-md animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-md">
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Job Role</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline text-sm">badge</span>
              <input type="text" className="w-full pl-xl pr-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none" placeholder="e.g. Product Designer" />
            </div>
          </div>
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Location</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline text-sm">location_on</span>
              <input type="text" className="w-full pl-xl pr-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none" placeholder="City or Remote" />
            </div>
          </div>
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Experience</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-outline text-sm">stairs</span>
              <input type="text" className="w-full pl-xl pr-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none" placeholder="e.g. 2-5 years" />
            </div>
          </div>
          <div className="space-y-xs">
            <label className="text-xs font-medium font-[Geist] text-on-surface-variant uppercase">Job Type</label>
            <select className="w-full px-sm py-md bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-1 focus:ring-primary text-sm outline-none appearance-none cursor-pointer">
              <option>Full Time</option>
              <option>Internship</option>
              <option>Apprenticeship</option>
              <option>Trainee</option>
              <option>Remote</option>
            </select>
          </div>
        </div>
        <div className="flex justify-between items-center pt-md border-t border-outline-variant/30">
          <div className="flex gap-sm">
            <button className="px-md py-sm bg-secondary-fixed text-on-secondary-fixed rounded-full text-sm font-medium font-[Geist] hover:bg-secondary-fixed-dim transition-colors">Filters</button>
            <button className="px-md py-sm text-on-surface-variant text-sm font-medium font-[Geist] hover:text-primary transition-colors cursor-pointer" onClick={resetFilters}>Clear All</button>
          </div>
          <button 
            onClick={handleSearch}
            disabled={loading}
            className="bg-primary text-on-primary px-xl py-sm rounded-lg text-sm font-medium font-[Geist] shadow-lg shadow-primary/20 hover:bg-primary-container transition-all flex items-center min-w-[140px] justify-center"
          >
            {loading ? <span className="material-symbols-outlined animate-spin">progress_activity</span> : 'Search Results'}
          </button>
        </div>
      </section>

      {/* Main Feed or Empty State */}
      {searched ? (
        <div className="flex-1 flex flex-col items-center justify-center py-3xl text-center space-y-md animate-fade-in-up">
          <div className="w-24 h-24 rounded-full bg-surface-container flex items-center justify-center">
            <span className="material-symbols-outlined text-4xl text-outline">search_off</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-on-background">No results found</h3>
            <p className="text-base text-on-surface-variant max-w-sm mx-auto">We couldn't find any opportunities matching your current filters. Try adjusting your search criteria.</p>
          </div>
          <button className="bg-primary text-on-primary px-xl py-sm rounded-lg text-sm font-medium font-[Geist] hover:bg-primary-container transition-all" onClick={resetFilters}>Clear All Filters</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-lg stagger-children flex-1 pb-xl">
          {jobs.map((job, i) => (
            <div key={i} className="bg-white p-lg rounded-xl border border-outline-variant hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5 transition-all flex flex-col justify-between group">
              <div className="flex justify-between items-start gap-md">
                <div className="flex gap-md">
                  <div className="w-14 h-14 rounded-lg bg-surface-container-high flex items-center justify-center border border-outline-variant overflow-hidden shrink-0">
                    <img alt="Company logo" className="w-10 h-10 object-contain" src={job.logo} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-on-background group-hover:text-primary transition-colors cursor-pointer">{job.role}</h3>
                    <p className="text-base text-on-surface-variant font-medium">{job.company}</p>
                    <div className="flex flex-wrap gap-sm mt-sm">
                      <span className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
                        <span className="material-symbols-outlined text-[14px]">location_on</span> {job.location}
                      </span>
                      <span className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
                        <span className="material-symbols-outlined text-[14px]">stairs</span> {job.exp}
                      </span>
                      <span className="flex items-center gap-xs text-xs font-medium font-[Geist] text-on-surface-variant bg-surface-container-low px-sm py-xs rounded">
                        <span className="material-symbols-outlined text-[14px]">payments</span> {job.salary}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-sm shrink-0">
                  <div className={`px-sm py-xs rounded text-[10px] font-bold uppercase tracking-wider border ${getColorClasses(job.color)}`}>
                    {job.matchType === 'Match' ? job.match : job.matchType}
                  </div>
                  <button className="p-xs text-outline hover:text-error transition-colors">
                    <span className="material-symbols-outlined">favorite</span>
                  </button>
                </div>
              </div>
              <div className="mt-lg pt-lg border-t border-outline-variant/30 flex justify-between items-center">
                <div className="flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px] text-outline">language</span>
                  <span className="text-xs font-medium font-[Geist] text-outline">{job.source} • {job.time}</span>
                </div>
                <div className="flex gap-sm">
                  <button className="p-sm border border-outline-variant rounded-lg text-on-surface-variant hover:bg-surface-container transition-colors">
                    <span className="material-symbols-outlined text-sm">bookmark</span>
                  </button>
                  <button className="px-lg py-sm bg-primary text-on-primary rounded-lg text-sm font-medium font-[Geist] hover:bg-primary-container transition-all">Apply Now</button>
                </div>
              </div>
            </div>
          ))}
          
          <div className="col-span-full flex justify-center pt-xl">
            <button className="flex items-center gap-sm px-xl py-md border border-outline-variant rounded-full text-on-surface-variant text-sm font-medium font-[Geist] hover:bg-surface-container transition-all group">
              <span>Load More Opportunities</span>
              <span className="material-symbols-outlined group-hover:translate-y-1 transition-transform">keyboard_arrow_down</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
