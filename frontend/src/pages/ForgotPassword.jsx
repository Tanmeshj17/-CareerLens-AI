import { useState } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../api'
import CareerLensLogo from '../components/CareerLensLogo'

export default function ForgotPassword() {
  const [email, setEmail]           = useState('')
  const [loading, setLoading]       = useState(false)
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg]     = useState('')
  const [debugUrl, setDebugUrl]     = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrorMsg('')
    setSuccessMsg('')
    setDebugUrl('')
    try {
      const res = await forgotPassword(email)
      setSuccessMsg(res.message || 'If an account exists, a password reset link has been sent.')
      if (res.debug_reset_url) setDebugUrl(res.debug_reset_url)
    } catch (err) {
      setErrorMsg(err.message || 'Failed to request password reset.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#e8eeff] via-[#f0f4ff] to-[#e6eeff] flex items-center justify-center p-4 font-['Plus_Jakarta_Sans',sans-serif]">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-[2rem] shadow-[0_32px_80px_rgba(0,50,180,0.18)] p-8 sm:p-10">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <CareerLensLogo size="md" />
          </div>

          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#0050cb] to-[#6366f1] flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-3xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>lock_reset</span>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-center text-slate-800 mb-1">Forgot Password?</h2>
          <p className="text-sm text-center text-slate-400 mb-7">
            Enter your email and we'll send you a reset link.
          </p>

          {/* Error */}
          {errorMsg && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700">
              {errorMsg}
            </div>
          )}

          {/* Success */}
          {successMsg && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-start gap-2">
              <span className="material-symbols-outlined text-[16px] mt-0.5 text-emerald-500" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
              {successMsg}
            </div>
          )}

          {/* Debug URL */}
          {debugUrl && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs space-y-1">
              <span className="font-bold text-[#0050cb] block">Direct Reset Link:</span>
              <a href={debugUrl} className="text-[#0050cb] underline break-all font-mono">{debugUrl}</a>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Floating label email */}
            <div className="relative w-full">
              <input
                id="forgot-email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                placeholder=" "
                className="peer w-full h-[52px] px-4 pt-5 pb-1 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-sm outline-none transition-all
                  focus:border-[#0050cb] focus:bg-white focus:shadow-[0_0_0_3px_rgba(0,80,203,0.12)]
                  placeholder-transparent"
              />
              <label
                htmlFor="forgot-email"
                className="absolute left-4 top-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#0050cb] transition-all
                  peer-placeholder-shown:top-[14px] peer-placeholder-shown:text-sm peer-placeholder-shown:font-normal peer-placeholder-shown:tracking-normal peer-placeholder-shown:text-slate-400
                  peer-focus:top-1.5 peer-focus:text-[10px] peer-focus:font-semibold peer-focus:uppercase peer-focus:tracking-wider peer-focus:text-[#0050cb]"
              >
                Email Address
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-xl font-bold text-sm text-white
                bg-gradient-to-r from-[#0050cb] to-[#6366f1]
                hover:from-[#003fa0] hover:to-[#4f46e5]
                shadow-[0_4px_20px_rgba(0,80,203,0.35)]
                hover:shadow-[0_6px_28px_rgba(0,80,203,0.45)]
                transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0
                disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none
                flex items-center justify-center gap-2"
            >
              {loading ? (
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
              ) : 'Send Reset Link'}
            </button>
          </form>

          <div className="mt-7 text-center">
            <Link to="/login" className="inline-flex items-center gap-1 text-xs font-semibold text-[#0050cb] hover:underline">
              <span className="material-symbols-outlined text-[14px]">arrow_back</span>
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
