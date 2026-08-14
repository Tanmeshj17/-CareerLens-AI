import React from 'react';

/**
 * CareerLensLogo — Modern Vector Brand Mark
 * Inspired by an Optical Focus Lens (precision, AI discovery, search clarity)
 * combined with a Professional Necktie (career growth, executive leadership).
 *
 * Props:
 * - size: 'xs' (20px), 'sm' (28px), 'md' (36px), 'lg' (48px), 'xl' (56px) or custom pixel number
 * - variant: 'full' (icon + text), 'icon' (mark only), 'white' (white icon + white text for dark hero)
 * - className: custom wrapper classes
 * - showText: boolean (default true for 'full', false for 'icon')
 */
export default function CareerLensLogo({
  size = 'md',
  variant = 'full',
  className = '',
  showText = true,
  onClick = null,
}) {
  // Dimension mappings
  const sizeMap = {
    xs: { icon: 20, text: 'text-sm', badge: 'text-[9px] px-1 py-0.2' },
    sm: { icon: 28, text: 'text-base', badge: 'text-[10px] px-1.5 py-0.5' },
    md: { icon: 36, text: 'text-xl', badge: 'text-xs px-2 py-0.5' },
    lg: { icon: 44, text: 'text-2xl', badge: 'text-xs px-2.5 py-0.5' },
    xl: { icon: 56, text: 'text-3xl', badge: 'text-sm px-3 py-1' },
  };

  const dim = typeof size === 'number' ? { icon: size, text: 'text-xl', badge: 'text-xs px-2 py-0.5' } : (sizeMap[size] || sizeMap.md);
  const isWhite = variant === 'white';
  const isIconOnly = variant === 'icon' || !showText;

  return (
    <div
      onClick={onClick}
      className={`inline-flex items-center gap-2.5 select-none transition-transform ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      {/* ── Lens + Tie Vector Icon Mark ── */}
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
          {/* Primary Gradient (Electric Sapphire) */}
          <linearGradient id="cl-lens-primary" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0066ff" />
            <stop offset="100%" stopColor="#003fa4" />
          </linearGradient>

          {/* Cyan Glow / Reflection */}
          <linearGradient id="cl-lens-cyan" x1="20" y1="20" x2="80" y2="80" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#0050cb" />
          </linearGradient>

          {/* Tie Fill Gradient */}
          <linearGradient id="cl-tie-grad" x1="50" y1="24" x2="50" y2="76" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="60%" stopColor="#e0f2fe" />
            <stop offset="100%" stopColor="#bae6fd" />
          </linearGradient>

          {/* Drop shadow for depth */}
          <filter id="cl-shadow" x="0" y="0" width="100" height="100" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
            <feDropShadow dx="0" dy="3" stdDeviation="4" floodColor="#0050cb" floodOpacity="0.25" />
          </filter>
        </defs>

        {/* Outer Optical Lens Focus Ring with Aperture Notches */}
        <circle
          cx="50"
          cy="50"
          r="42"
          stroke={isWhite ? '#ffffff' : 'url(#cl-lens-primary)'}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray="46 12 46 12"
        />

        {/* Optical Lens Disc / Glass Core */}
        <circle
          cx="50"
          cy="50"
          r="34"
          fill={isWhite ? 'rgba(255, 255, 255, 0.15)' : 'url(#cl-lens-cyan)'}
          filter={isWhite ? '' : 'url(#cl-shadow)'}
        />

        {/* Lens Light Reflection Arc */}
        <path
          d="M 28 32 A 26 26 0 0 1 68 24"
          stroke="#ffffff"
          strokeWidth="3"
          strokeLinecap="round"
          strokeOpacity="0.75"
        />

        {/* ── Professional Necktie Silhouette at Focal Center ── */}
        {/* Tie Knot (trapezoid at collar) */}
        <path
          d="M 43 30 L 57 30 L 55 38 L 45 38 Z"
          fill={isWhite ? '#ffffff' : '#ffffff'}
          filter="drop-shadow(0 1px 2px rgba(0,0,0,0.15))"
        />

        {/* Tie Blade & Point (modern slim tapered necktie) */}
        <path
          d="M 45 38 L 55 38 L 57 62 L 50 72 L 43 62 Z"
          fill={isWhite ? '#ffffff' : 'url(#cl-tie-grad)'}
          filter="drop-shadow(0 2px 4px rgba(0,24,73,0.25))"
        />

        {/* Subtle Tie Center Fold / Crease Line */}
        <line
          x1="50"
          y1="38"
          x2="50"
          y2="70"
          stroke="#0050cb"
          strokeWidth="1.5"
          strokeOpacity="0.35"
          strokeLinecap="round"
        />

        {/* Optical Focus Brackets (Corners) */}
        <path d="M 16 28 L 16 16 L 28 16" stroke={isWhite ? '#ffffff' : '#38bdf8'} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M 84 28 L 84 16 L 72 16" stroke={isWhite ? '#ffffff' : '#38bdf8'} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M 16 72 L 16 84 L 28 84" stroke={isWhite ? '#ffffff' : '#38bdf8'} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M 84 72 L 84 84 L 72 84" stroke={isWhite ? '#ffffff' : '#38bdf8'} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>

      {/* ── Brand Typography ── */}
      {!isIconOnly && (
        <div className="flex items-center gap-1.5 leading-none">
          <span className={`font-extrabold tracking-tight font-['Plus_Jakarta_Sans',sans-serif] ${dim.text} ${isWhite ? 'text-white' : 'text-[#0b1c30]'}`}>
            CareerLens
          </span>
          <span className={`font-black rounded-md tracking-wider uppercase font-[Geist] ${dim.badge} ${
            isWhite
              ? 'bg-white/20 text-white border border-white/40'
              : 'bg-primary text-on-primary shadow-sm shadow-primary/20'
          }`}>
            AI
          </span>
        </div>
      )}
    </div>
  );
}
