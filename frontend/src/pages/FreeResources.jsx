import { useState, useContext, useRef } from 'react'
import { AuthContext } from '../App'

import { getFreeResources } from '../api'
import { useEffect } from 'react'

const CATEGORIES = ['All', 'Documentation', 'YouTube Channels', 'GitHub Repos', 'Courses', 'Tools', 'Communities', 'Podcasts']

const CATEGORY_ICONS = {
  All: 'apps', Documentation: 'description', 'YouTube Channels': 'smart_display',
  'GitHub Repos': 'hub', Courses: 'school', Tools: 'build',
  Communities: 'groups', Podcasts: 'podcasts',
}

const COLLECTIONS = [
  {
    title: 'Best for Beginners',
    icon: 'rocket_launch',
    ids: [3, 6, 7, 8, 11, 14],
  },
  {
    title: 'Advanced Deep Dives',
    icon: 'psychology',
    ids: [5, 10, 13, 16, 2],
  },
  {
    title: 'Quick Reads & References',
    icon: 'bolt',
    ids: [1, 9, 17, 18, 15],
  },
]

const DIFFICULTY_COLORS = {
  Beginner: 'bg-emerald-500/20 text-emerald-400',
  Intermediate: 'bg-amber-500/20 text-amber-400',
  Advanced: 'bg-rose-500/20 text-rose-400',
  'All Levels': 'bg-sky-500/20 text-sky-400',
}

/* ─── Star Renderer ─── */
function Stars({ rating }) {
  const full = Math.floor(rating)
  const hasHalf = rating - full >= 0.3
  return (
    <span className="inline-flex items-center gap-0.5">
      {Array.from({ length: 5 }, (_, i) => (
        <span key={i} className={`material-symbols-outlined text-[14px] ${i < full ? 'text-amber-400' : i === full && hasHalf ? 'text-amber-400' : 'text-white/20'}`}
          style={{ fontVariationSettings: i < full ? "'FILL' 1" : i === full && hasHalf ? "'FILL' 1" : "'FILL' 0" }}>
          {i < full ? 'star' : i === full && hasHalf ? 'star_half' : 'star'}
        </span>
      ))}
      <span className="text-[11px] font-medium text-on-surface-variant ml-1">{rating}</span>
    </span>
  )
}

/* ─── Main Component ─── */
export default function FreeResources() {
  const { user } = useContext(AuthContext)
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('All')
  const [bookmarks, setBookmarks] = useState(new Set())
  const [showBookmarksOnly, setShowBookmarksOnly] = useState(false)
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const scrollRefs = useRef({})
  const mainScrollRef = useRef(null)

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getFreeResources()
        setResources(data.map((r, i) => ({
          ...r,
          id: r.id || i,
          featured: i < 5,
          icon: CATEGORY_ICONS[r.category] || 'menu_book',
          category: r.category || 'Courses'
        })))
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const toggleBookmark = (id) =>
    setBookmarks((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })

  /* ─── Filter logic ─── */
  const filtered = resources.filter((r) => {
    // Phase 11.3.8: Never show INVALID_RESOURCE items
    if (r.status === 'INVALID_RESOURCE') return false
    const matchesSearch =
      !search ||
      r.title?.toLowerCase().includes(search.toLowerCase()) ||
      r.provider?.toLowerCase().includes(search.toLowerCase()) ||
      r.description?.toLowerCase().includes(search.toLowerCase())
    const matchesTab = activeTab === 'All' || r.category === activeTab
    const matchesBookmark = !showBookmarksOnly || bookmarks.has(r.id)
    return matchesSearch && matchesTab && matchesBookmark
  })

  const featured = resources.filter((r) => r.featured && r.availability_status !== 'BROKEN' && r.status !== 'INVALID_RESOURCE')

  const scrollCollection = (title, dir) => {
    const el = scrollRefs.current[title]
    if (el) el.scrollBy({ left: dir * 320, behavior: 'smooth' })
  }

  return (
    <div className="space-y-xl pb-xl animate-fade-in-up">
      {/* ══════════ HEADER ══════════ */}
      <div className="relative overflow-hidden rounded-xl p-xl glass-effect border border-white/[0.06]">
        {/* decorative blobs */}
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-48 h-48 bg-primary-container/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 max-w-2xl">
          <div className="flex items-center gap-sm mb-xs">
            <span className="material-symbols-outlined text-primary text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>local_library</span>
            <span className="text-xs font-semibold font-[Geist] uppercase tracking-widest text-primary">Curated Collection</span>
          </div>
          <h1 className="text-3xl font-bold text-on-surface tracking-tight">Free Resources</h1>
          <p className="text-on-surface-variant mt-xs text-sm leading-relaxed max-w-lg">
            Hand-picked documentation, courses, channels, tools and communities — everything you need to level up, completely free.
          </p>

          {/* Search */}
          <div className="relative mt-lg max-w-md">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-xl">search</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search resources, topics, providers…"
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-white/[0.06] border border-white/[0.08] text-on-surface text-sm placeholder:text-on-surface-variant/60 focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40 transition"
            />
            {search && (
              <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface transition">
                <span className="material-symbols-outlined text-lg">close</span>
              </button>
            )}
          </div>
        </div>

        {/* stats strip */}
        <div className="relative z-10 flex flex-wrap gap-lg mt-lg">
          {[
            { label: 'Resources', value: resources.length, icon: 'inventory_2' },
            { label: 'Categories', value: CATEGORIES.length - 1, icon: 'category' },
            { label: 'Bookmarked', value: bookmarks.size, icon: 'bookmark' },
          ].map((s) => (
            <div key={s.label} className="flex items-center gap-sm">
              <span className="material-symbols-outlined text-primary/70 text-lg">{s.icon}</span>
              <span className="text-lg font-bold text-on-surface">{s.value}</span>
              <span className="text-xs text-on-surface-variant font-[Geist]">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════ CATEGORY TABS + BOOKMARK TOGGLE ══════════ */}
      <div className="flex overflow-x-auto no-scrollbar md:flex-wrap items-center gap-sm pb-1 -my-0.5">
        {CATEGORIES.map((cat) => {
          const active = activeTab === cat
          return (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-semibold font-[Geist] transition-all duration-200 border ${
                active
                  ? 'bg-primary text-on-primary border-primary shadow-lg shadow-primary/20'
                  : 'bg-white/[0.04] text-on-surface-variant border-white/[0.08] hover:bg-white/[0.08] hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">{CATEGORY_ICONS[cat]}</span>
              {cat}
            </button>
          )
        })}

        {/* bookmark toggle */}
        <div className="ml-auto">
          <button
            onClick={() => setShowBookmarksOnly((v) => !v)}
            className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-semibold font-[Geist] transition-all duration-200 border ${
              showBookmarksOnly
                ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                : 'bg-white/[0.04] text-on-surface-variant border-white/[0.08] hover:bg-white/[0.08]'
            }`}
          >
            <span
              className="material-symbols-outlined text-[16px]"
              style={{ fontVariationSettings: showBookmarksOnly ? "'FILL' 1" : "'FILL' 0" }}
            >
              favorite
            </span>
            {showBookmarksOnly ? `Bookmarks (${bookmarks.size})` : 'Show Bookmarks'}
          </button>
        </div>
      </div>

      {/* ══════════ FEATURED RESOURCES ══════════ */}
      {activeTab === 'All' && !showBookmarksOnly && !search && (
        <section className="space-y-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-sm">
              <span className="material-symbols-outlined text-amber-400 text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
              <h2 className="text-lg font-bold text-on-surface">Featured Picks</h2>
            </div>
            {featured.length > 1 && (
              <div className="flex items-center gap-xs">
                <button onClick={() => {
                  const el = scrollRefs.current['Featured Picks'];
                  if (el) el.scrollBy({ left: -340, behavior: 'smooth' });
                }}
                  className="w-8 h-8 rounded-full bg-white/[0.06] hover:bg-white/[0.15] flex items-center justify-center transition text-on-surface-variant hover:text-on-surface border border-white/[0.08]">
                  <span className="material-symbols-outlined text-lg">chevron_left</span>
                </button>
                <button onClick={() => {
                  const el = scrollRefs.current['Featured Picks'];
                  if (el) el.scrollBy({ left: 340, behavior: 'smooth' });
                }}
                  className="w-8 h-8 rounded-full bg-white/[0.06] hover:bg-white/[0.15] flex items-center justify-center transition text-on-surface-variant hover:text-on-surface border border-white/[0.08]">
                  <span className="material-symbols-outlined text-lg">chevron_right</span>
                </button>
              </div>
            )}
          </div>
          
          <div className="relative group/featured">
            {/* Left gradient fade + click area */}
            <button
              onClick={() => {
                const el = scrollRefs.current['Featured Picks'];
                if (el) el.scrollBy({ left: -340, behavior: 'smooth' });
              }}
              className="hidden md:flex absolute left-0 top-0 bottom-0 w-12 z-10 items-center justify-start pl-1 bg-gradient-to-r from-background/80 to-transparent transition-opacity duration-300 cursor-pointer"
              aria-label="Scroll left"
            >
              <span className="w-8 h-8 rounded-full bg-surface/90 border border-white/[0.1] shadow-lg flex items-center justify-center text-on-surface-variant hover:text-primary transition">
                <span className="material-symbols-outlined text-xl">chevron_left</span>
              </span>
            </button>

            <div 
              ref={(el) => (scrollRefs.current['Featured Picks'] = el)}
              className="flex gap-md overflow-x-auto pb-sm scroll-smooth custom-scrollbar min-h-[320px]"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="shrink-0 w-80 rounded-xl bg-white/[0.02] animate-pulse border border-white/[0.05]" />
                ))
              ) : (
                featured.map((r, idx) => (
                <div
                  key={r.id}
                  className="group shrink-0 w-80 relative overflow-hidden rounded-xl border border-white/[0.06] hover:border-white/[0.12] transition-all duration-300 hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-1"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  {/* gradient banner */}
                  <div className={`relative h-36 bg-gradient-to-br ${r.gradient} flex items-end p-lg`}>
                    <div className="absolute inset-0 bg-black/30" />
                    <div className="absolute top-3 right-3 z-10">
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleBookmark(r.id) }}
                        className="w-8 h-8 rounded-full bg-black/30 backdrop-blur flex items-center justify-center hover:bg-black/50 transition"
                      >
                        <span className="material-symbols-outlined text-white text-lg" style={{ fontVariationSettings: bookmarks.has(r.id) ? "'FILL' 1" : "'FILL' 0" }}>
                          favorite
                        </span>
                      </button>
                    </div>
                    <div className="absolute top-3 left-3 z-10">
                      <span className="px-2 py-0.5 rounded-full bg-white/20 backdrop-blur text-white text-[10px] font-bold font-[Geist] uppercase tracking-wider">
                        ★ Featured
                      </span>
                    </div>
                    <div className="relative z-10">
                      <span className="material-symbols-outlined text-white/80 text-4xl mb-1 drop-shadow-lg" style={{ fontVariationSettings: "'FILL' 1" }}>{r.icon}</span>
                    </div>
                  </div>

                  {/* body */}
                  <div className="p-lg glass-effect space-y-sm">
                    <div className="flex items-start justify-between gap-sm">
                      <div>
                        <h3 className="text-base font-bold text-on-surface group-hover:text-primary transition">{r.title}</h3>
                        <p className="text-xs text-on-surface-variant mt-0.5">{r.provider}</p>
                      </div>
                      <a href={r.url} target="_blank" rel="noopener noreferrer"
                        className="shrink-0 w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary hover:bg-primary hover:text-on-primary transition">
                        <span className="material-symbols-outlined text-lg">open_in_new</span>
                      </a>
                    </div>
                    <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">{r.description}</p>
                    <div className="flex justify-between items-start mb-2">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border border-white/10 ${DIFFICULTY_COLORS[r.difficulty] || 'bg-white/5 text-white/60'}`}>
                          {r.difficulty}
                        </span>
                        <div className="flex gap-1">
                          {r.country === 'India' && <span className="text-[10px] font-bold bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded border border-orange-500/30">🇮🇳 India</span>}
                          {r.affordability && <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${r.affordability === 'FREE' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-white/10 text-white/80'}`}>{r.affordability}</span>}
                        </div>
                    </div>
                  </div>
                </div>
              )))}
            </div>

            {/* Right gradient fade + click area */}
            <button
              onClick={() => {
                const el = scrollRefs.current['Featured Picks'];
                if (el) el.scrollBy({ left: 340, behavior: 'smooth' });
              }}
              className="hidden md:flex absolute right-0 top-0 bottom-0 w-12 z-10 items-center justify-end pr-1 bg-gradient-to-l from-background/80 to-transparent transition-opacity duration-300 cursor-pointer"
              aria-label="Scroll right"
            >
              <span className="w-8 h-8 rounded-full bg-surface/90 border border-white/[0.1] shadow-lg flex items-center justify-center text-on-surface-variant hover:text-primary transition">
                <span className="material-symbols-outlined text-xl">chevron_right</span>
              </span>
            </button>
          </div>
        </section>
      )}

      {/* ══════════ RESOURCE SLIDER ══════════ */}
      <section className="space-y-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary text-xl">grid_view</span>
            <h2 className="text-lg font-bold text-on-surface">
              {showBookmarksOnly ? 'Your Bookmarks' : activeTab === 'All' ? 'All Resources' : activeTab}
            </h2>
            <span className="text-xs text-on-surface-variant font-[Geist] bg-white/[0.06] px-2 py-0.5 rounded-full">{filtered.length}</span>
          </div>
          {filtered.length > 3 && (
            <div className="flex items-center gap-xs">
              <button onClick={() => mainScrollRef.current?.scrollBy({ left: -340, behavior: 'smooth' })}
                className="w-8 h-8 rounded-full bg-white/[0.06] hover:bg-white/[0.15] flex items-center justify-center transition text-on-surface-variant hover:text-on-surface border border-white/[0.08]">
                <span className="material-symbols-outlined text-lg">chevron_left</span>
              </button>
              <button onClick={() => mainScrollRef.current?.scrollBy({ left: 340, behavior: 'smooth' })}
                className="w-8 h-8 rounded-full bg-white/[0.06] hover:bg-white/[0.15] flex items-center justify-center transition text-on-surface-variant hover:text-on-surface border border-white/[0.08]">
                <span className="material-symbols-outlined text-lg">chevron_right</span>
              </button>
            </div>
          )}
        </div>

        {loading ? (
          <div className="relative group/slider">
            <div className="flex gap-md overflow-x-auto pb-sm scroll-smooth min-h-[220px]" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="shrink-0 w-80 h-52 rounded-xl bg-white/[0.02] animate-pulse border border-white/[0.05]" />
              ))}
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 glass-effect rounded-xl border border-white/[0.06]">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant/40 mb-md">search_off</span>
            <p className="text-on-surface-variant text-sm">No resources match your filters.</p>
            <button onClick={() => { setSearch(''); setActiveTab('All'); setShowBookmarksOnly(false) }}
              className="mt-md text-xs text-primary font-semibold hover:underline">Clear all filters</button>
          </div>
        ) : (
          <div className="relative group/slider">
            {/* Left gradient fade + click area */}
            <button
              onClick={() => mainScrollRef.current?.scrollBy({ left: -340, behavior: 'smooth' })}
              className="hidden md:flex absolute left-0 top-0 bottom-0 w-12 z-10 items-center justify-start pl-1 bg-gradient-to-r from-background/80 to-transparent opacity-0 group-hover/slider:opacity-100 transition-opacity duration-300 cursor-pointer"
              aria-label="Scroll left"
            >
              <span className="w-8 h-8 rounded-full bg-surface/90 border border-white/[0.1] shadow-lg flex items-center justify-center text-on-surface-variant hover:text-primary transition">
                <span className="material-symbols-outlined text-xl">chevron_left</span>
              </span>
            </button>

            {/* Scrollable container */}
            <div
              ref={mainScrollRef}
              className="flex gap-md overflow-x-auto pb-sm scroll-smooth min-h-[220px]"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
              {filtered.map((r, idx) => (
                <div
                  key={r.id}
                  className="group shrink-0 w-80 glass-effect rounded-xl border border-white/[0.06] hover:border-white/[0.12] p-lg flex flex-col transition-all duration-300 hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-0.5 animate-fade-in-up"
                  style={{ animationDelay: `${idx * 40}ms` }}
                >
                  {/* top row */}
                  <div className="flex items-start gap-sm mb-sm">
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${r.gradient} flex items-center justify-center shrink-0 shadow-lg`}>
                      <span className="material-symbols-outlined text-white text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>{r.icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-bold text-on-surface truncate group-hover:text-primary transition">{r.title}</h3>
                      <p className="text-[11px] text-on-surface-variant truncate">{r.provider}</p>
                    </div>
                    <button
                      onClick={() => toggleBookmark(r.id)}
                      className="shrink-0 mt-0.5 transition hover:scale-110"
                      title={bookmarks.has(r.id) ? 'Remove bookmark' : 'Bookmark'}
                    >
                      <span
                        className={`material-symbols-outlined text-xl transition ${bookmarks.has(r.id) ? 'text-rose-400' : 'text-on-surface-variant/40 hover:text-rose-400'}`}
                        style={{ fontVariationSettings: bookmarks.has(r.id) ? "'FILL' 1" : "'FILL' 0" }}
                      >
                        favorite
                      </span>
                    </button>
                  </div>

                  {/* description */}
                  <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2 mb-sm flex-1">{r.description}</p>

                  {/* meta row */}
                  <div className="flex items-center flex-wrap gap-1.5 mb-sm">
                    <span className="text-[10px] font-bold font-[Geist] px-2 py-0.5 rounded-full bg-primary/10 text-primary">{r.category}</span>
                      <div className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
                        <span className="material-symbols-outlined text-[16px] text-primary">person</span>
                        {r.provider}
                      </div>
                      <div className="flex items-center justify-between mt-auto pt-2 border-t border-outline-variant/30">
                        <Stars rating={r.rating} />
                        <div className="flex gap-1">
                          {r.country === 'India' && <span className="text-[10px] font-bold bg-orange-100 text-orange-800 px-1.5 py-0.5 rounded">🇮🇳</span>}
                          {r.affordability && <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${r.affordability === 'FREE' ? 'bg-success/10 text-success' : 'bg-surface-variant'}`}>{r.affordability}</span>}
                        </div>
                      </div>
                    </div>
                  
                  {/* bottom row */}
                  <div className="flex items-center justify-between pt-sm border-t border-white/[0.06]">
                    <Stars rating={r.rating} />
                    <a
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] font-semibold font-[Geist] text-primary hover:text-on-primary hover:bg-primary px-2.5 py-1 rounded-lg transition bg-primary/10"
                    >
                      Visit
                      <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>

            {/* Right gradient fade + click area */}
            <button
              onClick={() => mainScrollRef.current?.scrollBy({ left: 340, behavior: 'smooth' })}
              className="hidden md:flex absolute right-0 top-0 bottom-0 w-12 z-10 items-center justify-end pr-1 bg-gradient-to-l from-background/80 to-transparent opacity-0 group-hover/slider:opacity-100 transition-opacity duration-300 cursor-pointer"
              aria-label="Scroll right"
            >
              <span className="w-8 h-8 rounded-full bg-surface/90 border border-white/[0.1] shadow-lg flex items-center justify-center text-on-surface-variant hover:text-primary transition">
                <span className="material-symbols-outlined text-xl">chevron_right</span>
              </span>
            </button>
          </div>
        )}
      </section>

      {/* ══════════ CURATED COLLECTIONS ══════════ */}
      {activeTab === 'All' && !showBookmarksOnly && !search && (
        <section className="space-y-lg">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>collections_bookmark</span>
            <h2 className="text-lg font-bold text-on-surface">Curated Collections</h2>
          </div>

          {COLLECTIONS.map((col) => {
            const items = col.ids.map((id) => resources.find((r) => r.id === id)).filter(Boolean)
            return (
              <div key={col.title} className="space-y-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-sm">
                    <span className="material-symbols-outlined text-lg text-on-surface-variant">{col.icon}</span>
                    <h3 className="text-sm font-bold text-on-surface">{col.title}</h3>
                    <span className="text-[10px] text-on-surface-variant font-[Geist] bg-white/[0.06] px-2 py-0.5 rounded-full">{items.length} resources</span>
                  </div>
                  <div className="flex items-center gap-xs">
                    <button onClick={() => scrollCollection(col.title, -1)}
                      className="w-7 h-7 rounded-full bg-white/[0.06] hover:bg-white/[0.12] flex items-center justify-center transition text-on-surface-variant">
                      <span className="material-symbols-outlined text-lg">chevron_left</span>
                    </button>
                    <button onClick={() => scrollCollection(col.title, 1)}
                      className="w-7 h-7 rounded-full bg-white/[0.06] hover:bg-white/[0.12] flex items-center justify-center transition text-on-surface-variant">
                      <span className="material-symbols-outlined text-lg">chevron_right</span>
                    </button>
                  </div>
                </div>

                <div
                  ref={(el) => (scrollRefs.current[col.title] = el)}
                  className="flex gap-md overflow-x-auto custom-scrollbar pb-sm scroll-smooth min-h-[90px]"
                >
                  {loading ? (
                    Array.from({ length: 4 }).map((_, i) => (
                      <div key={i} className="shrink-0 w-72 h-20 rounded-xl bg-white/[0.02] animate-pulse border border-white/[0.05]" />
                    ))
                  ) : (
                    items.map((r) => (
                      <a
                        key={r.id}
                        href={r.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group shrink-0 w-72 glass-effect rounded-xl border border-white/[0.06] hover:border-white/[0.12] p-md flex items-start gap-sm transition-all duration-300 hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-0.5"
                      >
                        <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${r.gradient} flex items-center justify-center shrink-0`}>
                          <span className="material-symbols-outlined text-white text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>{r.icon}</span>
                        </div>
                        <div className="min-w-0">
                          <h4 className="text-sm font-bold text-on-surface truncate group-hover:text-primary transition">{r.title}</h4>
                          <p className="text-[11px] text-on-surface-variant mt-0.5 truncate">{r.provider}</p>
                          <div className="mt-1.5">
                            <Stars rating={r.rating} />
                          </div>
                        </div>
                      </a>
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </section>
      )}

      {/* ══════════ FOOTER CTA ══════════ */}
      <div className="glass-effect rounded-xl border border-white/[0.06] p-lg flex flex-col sm:flex-row items-center justify-between gap-md">
        <div className="flex items-center gap-sm">
          <span className="material-symbols-outlined text-primary text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>lightbulb</span>
          <div>
            <p className="text-sm font-bold text-on-surface">Know a great free resource?</p>
            <p className="text-xs text-on-surface-variant">Help the community by suggesting resources you love.</p>
          </div>
        </div>
        <button className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-primary text-on-primary text-xs font-bold font-[Geist] hover:shadow-lg hover:shadow-primary/30 transition-all duration-200 hover:-translate-y-0.5">
          <span className="material-symbols-outlined text-lg">add</span>
          Suggest a Resource
        </button>
      </div>
    </div>
  )
}
