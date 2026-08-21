import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../App'
import { loginUser, getCurrentUser, resendVerificationEmail } from '../api'
import CareerLensLogo from '../components/CareerLensLogo'

/* ─── Floating label input ─────────────────────────────────────────────── */
function FloatingInput({ id, label, type = 'text', value, onChange, required, rightEl }) {
  return (
    <div className="relative w-full">
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        placeholder=" "
        autoComplete={type === 'password' ? 'current-password' : 'email'}
        className="peer w-full h-14 px-4 pt-5 pb-1 rounded-xl border border-slate-200 bg-slate-50/80
          text-slate-800 text-base outline-none transition-all
          focus:border-[#0050cb] focus:bg-white focus:shadow-[0_0_0_3px_rgba(0,80,203,0.10)]
          placeholder-transparent"
        style={{ paddingRight: rightEl ? '3rem' : undefined }}
      />
      <label
        htmlFor={id}
        className="absolute left-4 top-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#0050cb]
          pointer-events-none transition-all duration-200
          peer-placeholder-shown:top-4 peer-placeholder-shown:text-sm peer-placeholder-shown:font-normal
          peer-placeholder-shown:tracking-normal peer-placeholder-shown:text-slate-400
          peer-focus:top-1.5 peer-focus:text-[10px] peer-focus:font-semibold
          peer-focus:uppercase peer-focus:tracking-wider peer-focus:text-[#0050cb]"
      >
        {label}
      </label>
      {rightEl && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">{rightEl}</div>
      )}
    </div>
  )
}

/* ─── Eye toggle button ────────────────────────────────────────────────── */
function EyeBtn({ show, toggle }) {
  return (
    <button
      type="button"
      onClick={toggle}
      className="text-slate-400 hover:text-[#0050cb] transition-colors p-1.5 rounded-full
        focus:outline-none focus:ring-2 focus:ring-[#0050cb]/30 touch-manipulation"
    >
      <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
        {show ? 'visibility_off' : 'visibility'}
      </span>
    </button>
  )
}

export default function Login() {
  const [isAdminMode, setIsAdminMode]   = useState(false)
  const [email, setEmail]               = useState('')
  const [password, setPassword]         = useState('')
  const [showPw, setShowPw]             = useState(false)
  const [loading, setLoading]           = useState(false)
  const [errorMsg, setErrorMsg]         = useState('')
  const [showResend, setShowResend]     = useState(false)
  const [resendStatus, setResendStatus] = useState('')
  const { login } = useContext(AuthContext)
  const navigate  = useNavigate()

  const handleToggleAdminMode = (toAdmin) => {
    setIsAdminMode(toAdmin)
    setErrorMsg('')
    if (toAdmin) {
      if (!email) setEmail('careerlensadmin')
    } else {
      if (email === 'careerlensadmin') setEmail('')
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true); setErrorMsg(''); setShowResend(false); setResendStatus('')
    try {
      await loginUser(email, password)
      const userData = await getCurrentUser()
      login(userData)
      if (userData?.role === 'admin') {
        navigate('/app/admin', { replace: true })
      } else {
        navigate('/app', { replace: true })
      }
    } catch (err) {
      setErrorMsg(err.message || 'Login failed')
      if (err.message?.toLowerCase().includes('not verified')) setShowResend(true)
    } finally { setLoading(false) }
  }

  const handleResend = async () => {
    setResendStatus('Sending…')
    try {
      await resendVerificationEmail(email)
      setResendStatus('Verification email sent! Check your inbox.')
    } catch (err) { setResendStatus('Failed: ' + err.message) }
  }

  return (
    <div
      className="min-h-screen min-h-[100dvh] w-full flex flex-col lg:flex-row
        font-['Plus_Jakarta_Sans',sans-serif] bg-gradient-to-br from-[#e8eeff] via-[#f0f4ff] to-[#e6eeff]"
    >
      {/* ── MOBILE: compact brand strip at top ─────────────────────────── */}
      <div className="lg:hidden w-full bg-gradient-to-r from-[#0050cb] via-[#3b5cf6] to-[#6366f1] px-6 pt-10 pb-8 flex flex-col items-center text-white text-center">
        <div className="mb-3">
          <CareerLensLogo size="md" variant="white" showTagline />
        </div>
        <p className="text-xs text-white/70 max-w-xs">
          Sign in to continue your career journey.
        </p>
      </div>

      {/* ── FORM PANEL ─────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-center px-5 sm:px-8 py-8 lg:py-12 bg-white lg:max-w-[55%] xl:max-w-1/2">
        <div className="w-full max-w-sm sm:max-w-md">

          {/* Desktop logo */}
          <div className="hidden lg:block mb-6">
            <CareerLensLogo size="md" />
          </div>

          {/* Mode Switcher: User vs Admin */}
          <div className="flex p-1 mb-6 rounded-xl bg-slate-100 border border-slate-200/80">
            <button
              type="button"
              onClick={() => handleToggleAdminMode(false)}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                !isAdminMode
                  ? 'bg-white text-[#0050cb] shadow-sm font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">person</span>
              User Login
            </button>
            <button
              type="button"
              onClick={() => handleToggleAdminMode(true)}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                isAdminMode
                  ? 'bg-[#0050cb] text-white shadow-sm font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">admin_panel_settings</span>
              Admin Portal
            </button>
          </div>

          <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-1">
            {isAdminMode ? 'Admin Command Center' : 'Welcome back'}
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            {isAdminMode
              ? 'Enter root administrator credentials to access system analytics.'
              : 'Sign in to continue your career journey.'}
          </p>

          {/* Error */}
          {errorMsg && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex flex-col gap-1 animate-fade-in">
              <span>{errorMsg}</span>
              {showResend && (
                <div>
                  <button
                    onClick={handleResend} type="button"
                    className="underline font-semibold hover:text-red-900 transition focus:outline-none"
                  >Resend Verification Email</button>
                  {resendStatus && <p className="mt-0.5 text-xs opacity-80">{resendStatus}</p>}
                </div>
              )}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <FloatingInput
              id="login-email"
              label={isAdminMode ? 'Admin Username or Email' : 'Email Address'}
              type="text"
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
              rightEl={<EyeBtn show={showPw} toggle={() => setShowPw(!showPw)} />}
            />

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none touch-manipulation">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-slate-300 text-[#0050cb]
                    focus:ring-[#0050cb] focus:ring-offset-0 touch-manipulation"
                />
                <span className="text-sm text-slate-500">Remember me</span>
              </label>
              {!isAdminMode && (
                <Link
                  to="/forgot-password"
                  className="text-sm font-semibold text-[#0050cb] hover:text-[#003fa0] transition-colors"
                >
                  Forgot Password?
                </Link>
              )}
            </div>

            <button
              type="submit" disabled={loading}
              className={`w-full h-14 rounded-xl font-bold text-base text-white
                ${isAdminMode
                  ? 'bg-gradient-to-r from-slate-900 via-[#0050cb] to-slate-900 hover:from-slate-800 hover:to-slate-800'
                  : 'bg-gradient-to-r from-[#0050cb] to-[#6366f1] hover:from-[#003fa0] hover:to-[#4f46e5]'
                }
                active:scale-[0.98]
                shadow-[0_4px_20px_rgba(0,80,203,0.35)]
                hover:shadow-[0_6px_28px_rgba(0,80,203,0.45)]
                transition-all duration-200 touch-manipulation
                disabled:opacity-60 disabled:cursor-not-allowed
                flex items-center justify-center gap-2`}
            >
              {loading
                ? <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                : (isAdminMode ? 'Access Admin Dashboard' : 'Sign In')}
            </button>
          </form>

          {!isAdminMode && (
            <p className="mt-7 text-center text-sm text-slate-400">
              Don't have an account?{' '}
              <Link to="/register" className="font-bold text-[#0050cb] hover:underline">
                Create Account
              </Link>
            </p>
          )}

          {isAdminMode && (
            <div className="mt-6 p-3 rounded-xl bg-slate-50 border border-slate-200/60 text-center">
              <span className="text-xs text-slate-500 font-mono">
                Root Account: <strong className="text-slate-700">careerlensadmin</strong>
              </span>
            </div>
          )}
        </div>
      </div>

      {/* ── DESKTOP BRAND PANEL (right) ─────────────────────────────────── */}
      <div
        className="hidden lg:flex flex-col items-center justify-center flex-1
          relative overflow-hidden p-12 text-white
          bg-gradient-to-br from-[#0050cb] via-[#3b5cf6] to-[#6366f1]"
      >
        {/* Blobs */}
        <div className="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-white/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full bg-[#6366f1]/40 blur-3xl pointer-events-none" />

        <div className="relative z-10 text-center max-w-sm">
          <div className="mx-auto mb-8 w-20 h-20 rounded-full bg-white/15 backdrop-blur-sm
            flex items-center justify-center ring-2 ring-white/30 shadow-xl">
            <span className="material-symbols-outlined text-4xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>
              {isAdminMode ? 'security' : 'rocket_launch'}
            </span>
          </div>

          <h2 className="text-3xl font-bold leading-tight mb-4">
            {isAdminMode ? 'Admin Portal' : 'New Here?'}
          </h2>
          <p className="text-sm text-white/70 leading-relaxed mb-8">
            {isAdminMode
              ? 'Complete system control, live job intake velocity, and real-time user database analytics.'
              : 'Join thousands of professionals who use CareerLens AI to discover opportunities, analyze their resume, and chart their path to success.'}
          </p>

          {!isAdminMode && (
            <>
              <div className="flex items-center gap-8 justify-center mb-10">
                {[['10K+','Users'],['95%','Match Rate'],['500+','Companies']].map(([val, lbl]) => (
                  <div key={lbl} className="text-center">
                    <div className="text-xl font-bold">{val}</div>
                    <div className="text-[10px] text-white/60 uppercase tracking-wider">{lbl}</div>
                  </div>
                ))}
              </div>

              <Link
                to="/register"
                className="inline-flex items-center gap-2 h-12 px-8 rounded-xl font-bold text-sm
                  border-2 border-white/60 text-white
                  hover:bg-white hover:text-[#0050cb] transition-all duration-200
                  shadow-[0_4px_16px_rgba(0,0,0,0.2)]"
              >
                Create Account
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

