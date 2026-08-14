import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../App'
import { loginUser, getCurrentUser, resendVerificationEmail } from '../api'
import CareerLensLogo from '../components/CareerLensLogo'

/* ─── Tiny inline components so no external UI deps ─────────────────────── */
function FloatingInput({ id, label, type = 'text', value, onChange, required, placeholder, rightEl }) {
  return (
    <div className="relative w-full group">
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        placeholder=" "
        autoComplete={type === 'password' ? 'current-password' : 'email'}
        className="peer w-full h-[52px] px-4 pt-5 pb-1 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-sm outline-none transition-all
          focus:border-[#0050cb] focus:bg-white focus:shadow-[0_0_0_3px_rgba(0,80,203,0.12)]
          placeholder-transparent pr-11"
      />
      <label
        htmlFor={id}
        className="absolute left-4 top-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#0050cb] transition-all
          peer-placeholder-shown:top-[14px] peer-placeholder-shown:text-sm peer-placeholder-shown:font-normal peer-placeholder-shown:tracking-normal peer-placeholder-shown:text-slate-400 peer-placeholder-shown:uppercase-none
          peer-focus:top-1.5 peer-focus:text-[10px] peer-focus:font-semibold peer-focus:uppercase peer-focus:tracking-wider peer-focus:text-[#0050cb]"
      >
        {label}
      </label>
      {rightEl && <div className="absolute right-3 top-1/2 -translate-y-1/2">{rightEl}</div>}
    </div>
  )
}

export default function Login() {
  const [email, setEmail]           = useState('')
  const [password, setPassword]     = useState('')
  const [showPw, setShowPw]         = useState(false)
  const [loading, setLoading]       = useState(false)
  const [errorMsg, setErrorMsg]     = useState('')
  const [showResend, setShowResend] = useState(false)
  const [resendStatus, setResendStatus] = useState('')
  const { login } = useContext(AuthContext)
  const navigate  = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrorMsg('')
    setShowResend(false)
    setResendStatus('')
    try {
      await loginUser(email, password)
      const userData = await getCurrentUser()
      login(userData)
      navigate('/app')
    } catch (err) {
      setErrorMsg(err.message || 'Login failed')
      if (err.message?.toLowerCase().includes('not verified')) setShowResend(true)
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setResendStatus('Sending…')
    try {
      await resendVerificationEmail(email)
      setResendStatus('Verification email sent! Check your inbox.')
    } catch (err) {
      setResendStatus('Failed: ' + err.message)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#e8eeff] via-[#f0f4ff] to-[#e6eeff] flex items-center justify-center p-4 font-['Plus_Jakarta_Sans',sans-serif]">

      {/* Card */}
      <div className="relative w-full max-w-4xl min-h-[580px] rounded-[2rem] shadow-[0_32px_80px_rgba(0,50,180,0.18)] overflow-hidden flex bg-white">

        {/* ── LEFT: Form panel ────────────────────────────────────── */}
        <div className="relative z-10 flex flex-col justify-center w-full lg:w-1/2 px-8 sm:px-12 py-12 bg-white">
          {/* Logo */}
          <div className="mb-8">
            <CareerLensLogo size="md" />
          </div>

          <h2 className="text-2xl font-bold text-slate-800 mb-1">Welcome back</h2>
          <p className="text-sm text-slate-400 mb-7">Sign in to continue your career journey.</p>

          {/* Error */}
          {errorMsg && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex flex-col gap-1">
              <span>{errorMsg}</span>
              {showResend && (
                <div>
                  <button onClick={handleResend} type="button" className="underline font-semibold hover:text-red-900 transition">
                    Resend Verification Email
                  </button>
                  {resendStatus && <p className="mt-0.5 opacity-80">{resendStatus}</p>}
                </div>
              )}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <FloatingInput
              id="login-email"
              label="Email Address"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />

            <FloatingInput
              id="login-password"
              label="Password"
              type={showPw ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              rightEl={
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="text-slate-400 hover:text-[#0050cb] transition-colors p-1 rounded-full focus:outline-none"
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showPw ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              }
            />

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-slate-300 text-[#0050cb] focus:ring-[#0050cb] focus:ring-offset-0"
                />
                <span className="text-xs text-slate-500">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-xs font-semibold text-[#0050cb] hover:text-[#003fa0] transition-colors">
                Forgot Password?
              </Link>
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
              ) : 'Sign In'}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-[#0050cb] hover:underline">
              Create Account
            </Link>
          </p>
        </div>

        {/* ── RIGHT: Brand panel (hidden on mobile) ───────────────── */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden flex-col items-center justify-center p-12 text-white bg-gradient-to-br from-[#0050cb] via-[#3b5cf6] to-[#6366f1]">
          {/* Decorative blobs */}
          <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute -bottom-16 -left-16 w-72 h-72 rounded-full bg-[#6366f1]/40 blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-[#0050cb]/20 blur-2xl pointer-events-none" />

          <div className="relative z-10 text-center">
            {/* Icon ring */}
            <div className="mx-auto mb-8 w-20 h-20 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center ring-2 ring-white/30 shadow-xl">
              <span className="material-symbols-outlined text-4xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>
                rocket_launch
              </span>
            </div>

            <h2 className="text-3xl font-bold leading-tight mb-4">
              New Here?
            </h2>
            <p className="text-sm text-white/75 max-w-xs leading-relaxed mb-8">
              Join thousands of professionals who use CareerLens AI to discover opportunities, analyze their resume, and chart their path to success.
            </p>

            {/* Stats row */}
            <div className="flex items-center gap-6 justify-center mb-10">
              {[['10K+','Users'],['95%','Match Rate'],['500+','Companies']].map(([val, lbl]) => (
                <div key={lbl} className="text-center">
                  <div className="text-lg font-bold text-white">{val}</div>
                  <div className="text-[10px] text-white/60 uppercase tracking-wider">{lbl}</div>
                </div>
              ))}
            </div>

            <Link
              to="/register"
              className="inline-flex items-center gap-2 h-11 px-8 rounded-xl font-bold text-sm border-2 border-white/60 text-white
                hover:bg-white hover:text-[#0050cb] transition-all duration-200
                shadow-[0_4px_16px_rgba(0,0,0,0.2)] hover:shadow-[0_6px_24px_rgba(0,0,0,0.3)]"
            >
              Create Account
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
