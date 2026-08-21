import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { initGA, trackPageView } from '../utils/analytics'
import { recordPageView } from '../api'

export default function RouteTracker() {
  const location = useLocation()

  useEffect(() => {
    initGA()
  }, [])

  useEffect(() => {
    const fullPath = location.pathname + location.search
    trackPageView(fullPath)
    // First-party internal page view recording for Admin Analytics
    recordPageView(location.pathname)
  }, [location])

  return null
}

