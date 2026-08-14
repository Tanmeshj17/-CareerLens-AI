import React from 'react';

/**
 * CareerLensLogo — Modern Vector Brand Mark
 * Inspired by the dynamic Gradient "C" enclosing an upward-pointing Navigation Compass Arrow,
 * representing precision focus, clear career direction, and forward growth.
 *
 * Tagline: "See Your Career Clearly."
 *
 * Props:
 * - size: 'xs' (20px), 'sm' (28px), 'md' (36px), 'lg' (48px), 'xl' (56px) or custom pixel number
 * - variant: 'full' (icon + text inline), 'icon' (mark only), 'white' (white icon + white text for dark hero), 'stacked' (vertical lockup with tagline)
 * - showTagline: boolean (displays 'See Your Career Clearly.')
 * - tagline: string (override default tagline)
 * - className: custom wrapper classes
 * - showText: boolean (default true for 'full', false for 'icon')
 */
export default function CareerLensLogo({
  size = 'md',
  variant = 'full',
  className = '',
  showText = true,
  showTagline = false,
  tagline = 'See Your Career Clearly.',
  onClick = null,
}) {
  // Dimension mappings
  const sizeMap = {
    xs: { icon: 20, text: 'text-sm', badge: 'text-[9px] px-1 py-0.2', tagline: 'text-[8px]' },
    sm: { icon: 26, text: 'text-base', badge: 'text-[10px] px-1.5 py-0.2', tagline: 'text-[9px]' },
    md: { icon: 34, text: 'text-xl', badge: 'text-xs px-2 py-0.5', tagline: 'text-[10px]' },
    lg: { icon: 44, text: 'text-2xl', badge: 'text-xs px-2.5 py-0.5', tagline: 'text-xs' },
    xl: { icon: 56, text: 'text-3xl', badge: 'text-sm px-3 py-1', tagline: 'text-sm' },
  };

  const dim = typeof size === 'number'
    ? { icon: size, text: 'text-xl', badge: 'text-xs px-2 py-0.5', tagline: 'text-[10px]' }
    : (sizeMap[size] || sizeMap.md);

  const isWhite = variant === 'white';
  const isIconOnly = variant === 'icon' || !showText;
  const isStacked = variant === 'stacked';

  return (
    <div
      onClick={onClick}
      className={`inline-flex ${isStacked ? 'flex-col items-center text-center' : 'items-center'} gap-2.5 select-none transition-transform ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      {/* ── Gradient "C" + Upward Compass Navigation Mark ── */}
      <svg
        width={dim.icon}
        height={dim.icon}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform duration-300 hover:scale-105"
        aria-label="CareerLens Logo"
      >
        <defs>
          {/* Main Gradient for Outer "C" ring */}
          <linearGradient id="cl-c-gradient" x1="15" y1="15" x2="85" y2="85" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isWhite ? '#ffffff' : '#0066FF'} />
            <stop offset="40%" stopColor={isWhite ? '#ffffff' : '#2563EB'} />
            <stop offset="75%" stopColor={isWhite ? '#e2e8f0' : '#6366F1'} />
            <stop offset="100%" stopColor={isWhite ? '#cbd5e1' : '#9333EA'} />
          </linearGradient>

          {/* Top-left Facet Gradient for Arrow */}
          <linearGradient id="cl-arrow-top" x1="34" y1="45" x2="64" y2="30" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isWhite ? '#ffffff' : '#0052D4'} />
            <stop offset="100%" stopColor={isWhite ? '#e0f2fe' : '#38BDF8'} />
          </linearGradient>

          {/* Bottom-right Facet Gradient for Arrow */}
          <linearGradient id="cl-arrow-bottom" x1="48" y1="64" x2="64" y2="30" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isWhite ? '#cbd5e1' : '#9333EA'} />
            <stop offset="100%" stopColor={isWhite ? '#ffffff' : '#4F46E5'} />
          </linearGradient>

          {/* Depth Drop Shadow */}
          <filter id="cl-brand-shadow" x="0" y="0" width="100" height="100" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
            <feDropShadow dx="0" dy="2.5" stdDeviation="3.5" floodColor={isWhite ? '#000000' : '#2563EB'} floodOpacity={isWhite ? 0.2 : 0.25} />
          </filter>
        </defs>

        {/* Outer Circular "C" Glyph */}
        <path
          d="M 74 28 A 33 33 0 1 0 74 72"
          stroke="url(#cl-c-gradient)"
          strokeWidth="14.5"
          strokeLinecap="round"
          fill="none"
          filter="url(#cl-brand-shadow)"
        />

        {/* Inner Directional Compass Arrow (Top-left facet) */}
        <path
          d="M 64 30 L 34 45 L 45 48 Z"
          fill="url(#cl-arrow-top)"
        />

        {/* Inner Directional Compass Arrow (Bottom-right facet) */}
        <path
          d="M 64 30 L 45 48 L 48 64 Z"
          fill="url(#cl-arrow-bottom)"
        />
      </svg>

      {/* ── Brand Wordmark & Tagline ── */}
      {!isIconOnly && (
        <div className={`flex flex-col ${isStacked ? 'items-center mt-1' : 'justify-center'} leading-none`}>
          <div className="flex items-center gap-1.5">
            <span className={`font-extrabold tracking-tight font-['Plus_Jakarta_Sans',sans-serif] ${dim.text}`}>
              <span className={isWhite ? 'text-white' : 'text-[#0B132B]'}>Career</span>
              <span className={isWhite ? 'text-white' : 'text-transparent bg-clip-text bg-gradient-to-r from-[#2563EB] to-[#9333EA]'}>
                Lens
              </span>
            </span>
            <span className={`font-black rounded-md tracking-wider uppercase font-[Geist] ${dim.badge} ${
              isWhite
                ? 'bg-white/20 text-white border border-white/40'
                : 'bg-primary text-on-primary shadow-sm shadow-primary/20'
            }`}>
              AI
            </span>
          </div>

          {(showTagline || isStacked) && (
            <span className={`font-semibold tracking-wider font-['Plus_Jakarta_Sans',sans-serif] mt-1 ${dim.tagline} ${
              isWhite ? 'text-white/80' : 'text-slate-500'
            }`}>
              {tagline}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
