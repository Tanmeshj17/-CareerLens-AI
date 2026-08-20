/**
 * Google Analytics 4 (GA4) Integration for CareerLens AI
 * Supports automatic route tracking, custom event tracking, and user engagement metrics.
 */

const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID || 'G-0000000000'

let isInitialized = false

/**
 * Dynamically loads Google Analytics gtag.js script
 */
export function initGA() {
  if (isInitialized || typeof window === 'undefined') return

  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID
  if (!measurementId || measurementId === 'G-0000000000') {
    // If no custom measurement ID is provided yet, set up a stub gtag
    window.dataLayer = window.dataLayer || []
    window.gtag = function () {
      window.dataLayer.push(arguments)
    }
    return
  }

  // Inject Google Tag script
  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`
  document.head.appendChild(script)

  window.dataLayer = window.dataLayer || []
  window.gtag = function () {
    window.dataLayer.push(arguments)
  }

  window.gtag('js', new Date())
  window.gtag('config', measurementId, {
    send_page_view: false, // Managed manually via RouteTracker for SPA accuracy
  })

  isInitialized = true
}

/**
 * Tracks a Single Page Application (SPA) route change / page view
 * @param {string} path - URL path e.g. '/app/opportunities'
 * @param {string} [title] - Page title e.g. 'Opportunities Hub'
 */
export function trackPageView(path, title = '') {
  if (typeof window === 'undefined' || typeof window.gtag !== 'function') return

  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID
  if (!measurementId || measurementId === 'G-0000000000') return

  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: title || document.title,
    page_location: window.location.href,
  })
}

/**
 * Tracks custom user interactions and business events
 * @param {string} action - Event action e.g. 'apply_click', 'resume_analyzed'
 * @param {object} [params] - Additional event parameters
 */
export function trackEvent(action, params = {}) {
  if (typeof window === 'undefined' || typeof window.gtag !== 'function') return

  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID
  if (!measurementId || measurementId === 'G-0000000000') return

  window.gtag('event', action, params)
}

/**
 * Sets user properties in Google Analytics
 * @param {string} userId - Anonymized user ID
 * @param {object} [properties] - Custom user attributes (e.g. role, careerGoal)
 */
export function setAnalyticsUser(userId, properties = {}) {
  if (typeof window === 'undefined' || typeof window.gtag !== 'function') return

  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID
  if (!measurementId || measurementId === 'G-0000000000') return

  window.gtag('set', 'user_properties', {
    user_id: userId,
    ...properties,
  })
}
