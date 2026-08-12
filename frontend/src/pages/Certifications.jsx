import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { getCertifications } from '../api';

const categories = ['All', 'Free', 'Paid', 'Cloud', 'Data', 'Security', 'DevOps', 'AI/ML', 'Project Management'];

const categoryIcons = {
  All: 'apps',
  Free: 'volunteer_activism',
  Paid: 'payments',
  Cloud: 'cloud',
  Data: 'database',
  Security: 'shield',
  DevOps: 'terminal',
  'AI/ML': 'psychology',
  'Project Management': 'assignment',
};

const difficultyColors = {
  Beginner: { bg: 'bg-emerald-500/15', text: 'text-emerald-400', border: 'border-emerald-500/30' },
  Intermediate: { bg: 'bg-sky-500/15', text: 'text-sky-400', border: 'border-sky-500/30' },
  Advanced: { bg: 'bg-violet-500/15', text: 'text-violet-400', border: 'border-violet-500/30' },
};

const providerIcons = {
  'AWS': 'cloud',
  'Microsoft': 'deployed_code',
  'Google Cloud': 'cloud_circle',
  'CompTIA': 'shield_lock',
  'CNCF': 'view_in_ar',
  'Cloud Native Computing Foundation (CNCF)': 'view_in_ar',
  'HashiCorp': 'terminal',
  'PMI': 'assignment',
  'ISC2': 'verified_user',
  'ISC²': 'verified_user',
  'Cisco': 'router',
  'Oracle': 'database',
  'Snowflake': 'ac_unit',
  'Databricks': 'database',
  'Scrum Alliance': 'groups',
  'Google': 'psychology',
};

const providerAccents = {
  'AWS': '#FF9900',
  'Microsoft': '#0078D4',
  'Google Cloud': '#4285F4',
  'CompTIA': '#C8202F',
  'CNCF': '#326CE5',
  'Cloud Native Computing Foundation (CNCF)': '#326CE5',
  'HashiCorp': '#7B42BC',
  'PMI': '#0077C0',
  'ISC2': '#009639',
  'ISC²': '#009639',
  'Cisco': '#049FD9',
  'Oracle': '#F80000',
  'Snowflake': '#29B5E8',
  'Databricks': '#FF3621',
  'Scrum Alliance': '#4DB8FF',
  'Google': '#34A853',
};

const featuredGradients = [
  'from-amber-500/20 via-orange-500/10 to-yellow-500/20',
  'from-blue-500/20 via-cyan-500/10 to-green-500/20',
  'from-sky-500/20 via-blue-500/10 to-indigo-500/20',
];

function guessCategoryFromCert(cert) {
  const name = (cert.name || '').toLowerCase();
  const skills = (cert.skills_covered || []).join(' ').toLowerCase();
  const all = name + ' ' + skills;
  if (all.includes('aws') || all.includes('azure') || all.includes('gcp') || all.includes('cloud')) return 'Cloud';
  if (all.includes('security') || all.includes('cissp') || all.includes('comptia') || all.includes('ccna') || all.includes('network')) return 'Security';
  if (all.includes('kubernetes') || all.includes('terraform') || all.includes('devops') || all.includes('docker')) return 'DevOps';
  if (all.includes('data') || all.includes('snowflake') || all.includes('databricks') || all.includes('sql')) return 'Data';
  if (all.includes('machine learning') || all.includes('tensorflow') || all.includes('ai') || all.includes('ml')) return 'AI/ML';
  if (all.includes('project') || all.includes('scrum') || all.includes('agile') || all.includes('pmp')) return 'Project Management';
  return 'Cloud';
}

function formatCost(cert) {
  if (cert.is_free) return 'Free';
  if (cert.cost) return cert.cost;
  if (cert.price_inr) return `₹${cert.price_inr.toLocaleString('en-IN')}`;
  return 'Paid';
}

function formatDuration(hours) {
  if (!hours) return 'Self-paced';
  if (hours < 20) return '1-2 months';
  if (hours < 60) return '2-3 months';
  if (hours < 120) return '3-5 months';
  return '4-6 months';
}

export default function Certifications() {
  const { user } = useContext(AuthContext);
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [certs, setCerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await getCertifications();
        setCerts(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to load certifications:', err);
        setError('Failed to load certifications. Please try again.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const enrichedCerts = certs.map((c, idx) => ({
    ...c,
    category: guessCategoryFromCert(c),
    icon: providerIcons[c.provider] || 'workspace_premium',
    accent: providerAccents[c.provider] || '#6366f1',
    providerShort: (c.provider || '').split(' ')[0].slice(0, 6),
    duration: formatDuration(c.estimated_hours),
    costLabel: formatCost(c),
    difficulty: c.difficulty || 'Intermediate',
    skills: c.skills_covered || [],
    title: c.name,
    description: c.skills_covered?.length > 0 
      ? `Master ${c.skills_covered.slice(0, 3).join(', ')} and more with this industry-recognized certification from ${c.provider}.`
      : `Industry-recognized certification from ${c.provider}.`,
    featured: idx < 3,
    gradient: featuredGradients[idx % 3],
  }));

  const filteredCerts = enrichedCerts.filter((cert) => {
    const matchesSearch =
      cert.title.toLowerCase().includes(search.toLowerCase()) ||
      cert.provider.toLowerCase().includes(search.toLowerCase()) ||
      cert.skills.some((s) => s.toLowerCase().includes(search.toLowerCase()));
      
    let matchesCategory = false;
    if (activeCategory === 'All') matchesCategory = true;
    else if (activeCategory === 'Free') matchesCategory = cert.is_free;
    else if (activeCategory === 'Paid') matchesCategory = !cert.is_free;
    else matchesCategory = cert.category === activeCategory;
    
    return matchesSearch && matchesCategory;
  });

  const featuredCerts = enrichedCerts.filter((c) => c.featured);
  const gridCerts = activeCategory !== 'All' || search ? filteredCerts : filteredCerts.filter((c) => !c.featured);

  const statsTotal = enrichedCerts.length;
  const statsFree = enrichedCerts.filter((c) => c.is_free).length;
  const statsPaid = statsTotal - statsFree;

  if (loading) {
    return (
      <div className="space-y-xl animate-fade-in-up">
        <div className="rounded-2xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/30 p-xl">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-surface-variant rounded-lg w-64"></div>
            <div className="h-4 bg-surface-variant rounded-lg w-96"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-md">
          {[1,2,3].map(i => <div key={i} className="h-24 bg-surface-variant rounded-xl animate-pulse"></div>)}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-md">
          {[1,2,3,4,5,6].map(i => <div key={i} className="h-56 bg-surface-variant rounded-xl animate-pulse"></div>)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-md">
        <span className="material-symbols-outlined text-rose-400" style={{ fontSize: 48 }}>error</span>
        <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">{error}</p>
        <button onClick={() => window.location.reload()} className="px-4 py-2 rounded-lg bg-[var(--md-sys-color-primary)] text-[var(--md-sys-color-on-primary)] text-sm font-medium">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-xl animate-fade-in-up">
      {/* ─── Header ─── */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[var(--md-sys-color-primary-container)]/20 via-[var(--md-sys-color-primary)]/8 to-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/30 p-xl">
        <div className="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-[var(--md-sys-color-primary)]/6 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full bg-violet-500/6 blur-3xl pointer-events-none" />

        <div className="relative flex flex-col lg:flex-row lg:items-end gap-lg">
          <div className="flex-1 space-y-sm">
            <div className="flex items-center gap-sm">
              <div className="w-12 h-12 rounded-xl bg-[var(--md-sys-color-primary)]/15 flex items-center justify-center">
                <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 28 }}>
                  workspace_premium
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
                  Certifications
                </h1>
                <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">
                  Real, industry-recognized credentials from top providers
                </p>
              </div>
            </div>
          </div>

          {/* Search */}
          <div className="relative w-full lg:w-96">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[var(--md-sys-color-on-surface-variant)]/60" style={{ fontSize: 20 }}>
              search
            </span>
            <input
              type="text"
              placeholder="Search certifications, providers, skills…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/40 text-[var(--md-sys-color-on-surface)] text-sm placeholder:text-[var(--md-sys-color-on-surface-variant)]/50 focus:outline-none focus:ring-2 focus:ring-[var(--md-sys-color-primary)]/40 focus:border-[var(--md-sys-color-primary)]/60 transition-all"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--md-sys-color-on-surface-variant)]/60 hover:text-[var(--md-sys-color-on-surface)] transition-colors"
              >
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>close</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ─── Stats Bar ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-md">
        {[
          { label: 'Total Available', value: statsTotal, icon: 'library_books', color: 'text-[var(--md-sys-color-primary)]', bg: 'bg-[var(--md-sys-color-primary)]/12' },
          { label: 'Free Certifications', value: statsFree, icon: 'volunteer_activism', color: 'text-emerald-400', bg: 'bg-emerald-500/12' },
          { label: 'Paid Certifications', value: statsPaid, icon: 'payments', color: 'text-amber-400', bg: 'bg-amber-500/12' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="group relative overflow-hidden rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg flex items-center gap-md hover:border-[var(--md-sys-color-outline-variant)]/50 transition-all duration-300"
          >
            <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center shrink-0`}>
              <span className={`material-symbols-outlined ${stat.color}`} style={{ fontSize: 24 }}>{stat.icon}</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">{stat.value}</p>
              <p className="text-xs text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ─── Filter Bar ─── */}
      <div className="flex flex-wrap items-center gap-sm">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium font-[Geist] transition-all duration-300 border ${
              activeCategory === cat
                ? 'bg-[var(--md-sys-color-primary)] text-[var(--md-sys-color-on-primary)] border-[var(--md-sys-color-primary)] shadow-lg shadow-[var(--md-sys-color-primary)]/25'
                : 'bg-[var(--md-sys-color-surface-container)] text-[var(--md-sys-color-on-surface-variant)] border-[var(--md-sys-color-outline-variant)]/30 hover:border-[var(--md-sys-color-primary)]/40 hover:text-[var(--md-sys-color-on-surface)]'
            }`}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>{categoryIcons[cat]}</span>
            {cat}
          </button>
        ))}
      </div>

      {/* ─── Featured Certifications ─── */}
      {activeCategory === 'All' && !search && featuredCerts.length > 0 && (
        <div className="space-y-md">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-amber-400" style={{ fontSize: 22 }}>star</span>
            <h2 className="text-lg font-semibold text-[var(--md-sys-color-on-surface)] font-[Geist]">Featured Certifications</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-md">
            {featuredCerts.map((cert) => (
              <div
                key={cert.id}
                className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${cert.gradient} border border-[var(--md-sys-color-outline-variant)]/20 p-lg flex flex-col gap-md hover:border-[var(--md-sys-color-outline-variant)]/50 hover:shadow-xl hover:shadow-black/10 transition-all duration-500 hover:-translate-y-1`}
              >
                <div
                  className="absolute -top-20 -right-20 w-44 h-44 rounded-full blur-3xl opacity-30 pointer-events-none transition-opacity duration-500 group-hover:opacity-50"
                  style={{ background: cert.accent }}
                />

                <div className="relative flex items-center justify-between">
                  <div className="flex items-center gap-sm">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold font-[Geist]" style={{ background: cert.accent + '22', color: cert.accent }}>
                      {cert.providerShort.slice(0, 3)}
                    </div>
                    <span className="text-xs text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">{cert.provider}</span>
                  </div>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium font-[Geist] border ${(difficultyColors[cert.difficulty] || difficultyColors.Intermediate).bg} ${(difficultyColors[cert.difficulty] || difficultyColors.Intermediate).text} ${(difficultyColors[cert.difficulty] || difficultyColors.Intermediate).border}`}>
                    {cert.difficulty}
                  </span>
                </div>

                <div className="relative flex-1 space-y-xs">
                  <h3 className="text-base font-semibold text-[var(--md-sys-color-on-surface)] leading-snug line-clamp-2">
                    {cert.title}
                  </h3>
                  <p className="text-xs text-[var(--md-sys-color-on-surface-variant)] leading-relaxed line-clamp-2">
                    {cert.description}
                  </p>
                </div>

                <div className="relative flex items-center gap-md text-xs text-[var(--md-sys-color-on-surface-variant)]">
                  <span className="flex items-center gap-1">
                    <span className="material-symbols-outlined" style={{ fontSize: 15 }}>schedule</span>
                    {cert.duration}
                  </span>
                  <span className={`flex items-center gap-1 font-semibold ${cert.is_free ? 'text-emerald-400' : 'text-amber-400'}`}>
                    <span className="material-symbols-outlined" style={{ fontSize: 15 }}>payments</span>
                    {cert.costLabel}
                  </span>
                </div>

                <a
                  href={cert.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="relative w-full py-2.5 rounded-xl text-sm font-semibold font-[Geist] text-white transition-all duration-300 hover:shadow-lg text-center block"
                  style={{ background: cert.accent }}
                >
                  View Certification →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Certification Grid ─── */}
      <div className="space-y-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 22 }}>grid_view</span>
            <h2 className="text-lg font-semibold text-[var(--md-sys-color-on-surface)] font-[Geist]">
              {activeCategory === 'All' ? 'All Certifications' : `${activeCategory} Certifications`}
            </h2>
            <span className="ml-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] font-[Geist]">
              {gridCerts.length}
            </span>
          </div>
        </div>

        {gridCerts.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--md-sys-color-outline-variant)]/30 bg-[var(--md-sys-color-surface-container)]/50 py-16 flex flex-col items-center gap-md">
            <span className="material-symbols-outlined text-[var(--md-sys-color-on-surface-variant)]/30" style={{ fontSize: 48 }}>search_off</span>
            <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">No certifications match your filters</p>
            <button
              onClick={() => { setSearch(''); setActiveCategory('All'); }}
              className="text-xs text-[var(--md-sys-color-primary)] hover:underline font-[Geist]"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-md">
            {gridCerts.map((cert, idx) => (
              <div
                key={cert.id}
                className="group relative overflow-hidden rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 flex flex-col hover:border-[var(--md-sys-color-outline-variant)]/50 hover:shadow-lg hover:shadow-black/8 transition-all duration-400 hover:-translate-y-0.5"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                {/* Card Header */}
                <div className="p-md pb-sm space-y-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-sm">
                      <div className="w-9 h-9 rounded-lg bg-[var(--md-sys-color-primary)]/10 flex items-center justify-center">
                        <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 20 }}>
                          {cert.icon}
                        </span>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-[var(--md-sys-color-on-surface-variant)] font-[Geist] font-medium">
                          {cert.providerShort}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium font-[Geist] border ${(difficultyColors[cert.difficulty] || difficultyColors.Intermediate).bg} ${(difficultyColors[cert.difficulty] || difficultyColors.Intermediate).text} ${(difficultyColors[cert.difficulty] || difficultyColors.Intermediate).border}`}>
                        {cert.difficulty}
                      </span>
                    </div>
                  </div>

                  <h3 className="text-sm font-semibold text-[var(--md-sys-color-on-surface)] leading-snug line-clamp-2 min-h-[2.5rem]">
                    {cert.title}
                  </h3>

                  <p className="text-xs text-[var(--md-sys-color-on-surface-variant)]/70 leading-relaxed line-clamp-2">
                    {cert.description}
                  </p>
                </div>

                {/* Skills */}
                <div className="px-md pb-sm flex flex-wrap gap-1">
                  {cert.skills.slice(0, 4).map((skill) => (
                    <span
                      key={skill}
                      className="text-[10px] px-2 py-0.5 rounded-md bg-[var(--md-sys-color-surface-container-low)] text-[var(--md-sys-color-on-surface-variant)] font-[Geist]"
                    >
                      {skill}
                    </span>
                  ))}
                  {cert.skills.length > 4 && (
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-[var(--md-sys-color-surface-container-low)] text-[var(--md-sys-color-on-surface-variant)]/60 font-[Geist]">
                      +{cert.skills.length - 4}
                    </span>
                  )}
                </div>

                {/* Divider */}
                <div className="mx-md border-t border-[var(--md-sys-color-outline-variant)]/15" />

                {/* Footer */}
                <div className="p-md pt-sm flex items-center justify-between mt-auto">
                  <div className="flex items-center gap-md text-xs text-[var(--md-sys-color-on-surface-variant)]">
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined" style={{ fontSize: 14 }}>schedule</span>
                      {cert.duration}
                    </span>
                    <span className={`flex items-center gap-1 font-semibold font-[Geist] ${cert.is_free ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {cert.costLabel}
                    </span>
                  </div>

                  <a
                    href={cert.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium font-[Geist] bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] border border-[var(--md-sys-color-primary)]/25 hover:bg-[var(--md-sys-color-primary)]/20 transition-colors"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 14 }}>open_in_new</span>
                    Get Certified
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ─── Bottom Tip ─── */}
      <div className="rounded-xl bg-gradient-to-r from-[var(--md-sys-color-primary)]/8 to-violet-500/8 border border-[var(--md-sys-color-outline-variant)]/20 p-md flex items-center gap-md">
        <div className="w-10 h-10 rounded-lg bg-[var(--md-sys-color-primary)]/12 flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 22 }}>lightbulb</span>
        </div>
        <div className="flex-1">
          <p className="text-sm text-[var(--md-sys-color-on-surface)]">
            <span className="font-semibold">Pro Tip:</span>{' '}
            <span className="text-[var(--md-sys-color-on-surface-variant)]">
              Stack certifications strategically — pair a cloud cert with a DevOps or security cert to maximize your market value by up to 35%.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
