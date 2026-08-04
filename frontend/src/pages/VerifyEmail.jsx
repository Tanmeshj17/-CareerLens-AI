import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { verifyEmail } from '../api'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState('loading')
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setErrorMsg('No verification token provided in the URL.')
      return
    }

    let isMounted = true
    const doVerify = async () => {
      try {
        await verifyEmail(token)
        if (isMounted) setStatus('success')
      } catch (err) {
        if (isMounted) {
          setStatus('error')
          setErrorMsg(err.message || 'Verification failed. The link may be expired or invalid.')
        }
      }
    }
    doVerify()

    return () => {
      isMounted = false
    }
  }, [token])

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex items-center justify-center p-xl">
      <div className="max-w-md w-full bg-white p-2xl rounded-xl shadow-sm border border-outline-variant text-center">
        {status === 'loading' && (
          <div className="flex flex-col items-center">
            <span className="material-symbols-outlined text-primary text-4xl animate-spin mb-md">progress_activity</span>
            <h2 className="text-xl font-bold mb-xs">Verifying your email</h2>
            <p className="text-sm text-on-surface-variant">Please wait a moment...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center animate-fade-in-up">
            <span className="material-symbols-outlined text-primary text-5xl mb-sm" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
            <h2 className="text-2xl font-bold mb-xs">Email Verified!</h2>
            <p className="text-sm text-on-surface-variant mb-xl">
              Your account has been successfully verified. You can now log in.
            </p>
            <Link to="/login" className="w-full bg-primary text-white py-md px-lg rounded-lg text-sm font-medium font-[Geist] hover:bg-primary/90 transition-all inline-block">
              Proceed to Login
            </Link>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center animate-fade-in-up">
            <span className="material-symbols-outlined text-error text-5xl mb-sm" style={{fontVariationSettings: "'FILL' 1"}}>error</span>
            <h2 className="text-2xl font-bold text-error mb-xs">Verification Failed</h2>
            <p className="text-sm text-on-surface-variant mb-xl">
              {errorMsg}
            </p>
            <Link to="/login" className="w-full border border-outline-variant text-on-surface py-md px-lg rounded-lg text-sm font-medium font-[Geist] hover:bg-surface-container transition-all inline-block">
              Return to Login
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
