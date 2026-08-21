import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser, getCurrentUser } from '../api'
import { AuthContext } from '../App'
import CareerLensLogo from '../components/CareerLensLogo'
import GoogleSignInButton from '../components/GoogleSignInButton'

/* ─── Floating label input ─────────────────────────────────────────────── */
function FloatingInput({ id, label, type = 'text', value, onChange, required, rightEl, autoComplete }) {
  return (
    <div className="relative w-full">
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        placeholder=" "
        autoComplete={autoComplete || (type === 'password' ? 'new-password' : type === 'email' ? 'email' : 'name')}
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

function EyeBtn({ show, toggle }) {
  return (
    <button
      type="button" onClick={toggle}
      className="text-slate-400 hover:text-[#0050cb] transition-colors p-1.5 rounded-full
        focus:outline-none focus:ring-2 focus:ring-[#0050cb]/30 touch-manipulation"
    >
      <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
        {show ? 'visibility_off' : 'visibility'}
      </span>
    </button>
  )
}

export default function Register() {
  const [name, setName]         = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw]     = useState(false)
  const [loading, setLoading]   = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [success, setSuccess]   = useState(false)
  const { login } = useContext(AuthContext)
  const navigate  = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true); setErrorMsg('')
    try {
      await registerUser(email, name, password)
      setSuccess(true)
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed')
    } finally { setLoading(false) }
  }

  /* Password strength */
  const strength = password.length === 0 ? 0 : password.length < 6 ? 1 : password.length < 10 ? 2 : password.length < 14 ? 3 : 4
  const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong'][strength]
  const strengthColor = ['', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-emerald-400'][strength]

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
          Create your free account and start your career journey.
        </p>
      </div>

      {/* ── DESKTOP BRAND PANEL (left) ─────────────────────────────────── */}
      <div
        className="hidden lg:flex flex-col items-center justify-center flex-shrink-0
          relative overflow-hidden p-12 text-white w-[45%] xl:w-1/2
          bg-gradient-to-br from-[#0050cb] via-[#3b5cf6] to-[#6366f1]"
      >
        <div className="absolute -top-24 -left-24 w-72 h-72 rounded-full bg-white/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -right-20 w-80 h-80 rounded-full bg-[#6366f1]/40 blur-3xl pointer-events-none" />

        <div className="relative z-10 text-center max-w-sm">
          <div className="mx-auto mb-8 w-20 h-20 rounded-full bg-white/15 backdrop-blur-sm
            flex items-center justify-center ring-2 ring-white/30 shadow-xl">
            <span className="material-symbols-outlined text-4xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>
              auto_awesome
            </span>
          </div>

          <h2 className="text-3xl font-bold leading-tight mb-4">Welcome Back!</h2>
          <p className="text-sm text-white/70 leading-relaxed mb-8">
            Already have an account? Sign in to access your personalized career dashboard, saved opportunities, and AI-powered insights.
          </p>

          <div className="flex flex-col gap-3 mb-10 max-w-[220px] mx-auto text-left">
            {[
              ['insights_bar_chart','AI Job Matching'],
              ['description','ATS Resume Analysis'],
              ['route','Career Roadmaps'],
            ].map(([icon, text]) => (
              <div key={text} className="flex items-center gap-3 bg-white/10 rounded-xl px-4 py-2.5 backdrop-blur-sm">
                <span className="material-symbols-outlined text-white/80" style={{fontSize:18,fontVariationSettings:"'FILL' 1"}}>{icon}</span>
                <span className="text-xs font-medium text-white/90">{text}</span>
              </div>
            ))}
          </div>

          <Link
            to="/login"
            className="inline-flex items-center gap-2 h-12 px-8 rounded-xl font-bold text-sm
              border-2 border-white/60 text-white
              hover:bg-white hover:text-[#0050cb] transition-all duration-200
              shadow-[0_4px_16px_rgba(0,0,0,0.2)]"
          >
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            Sign In
          </Link>
        </div>
      </div>

      {/* ── FORM PANEL ─────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-center px-5 sm:px-8 py-8 lg:py-12 bg-white">
        <div className="w-full max-w-sm sm:max-w-md">

          {/* Desktop logo */}
          <div className="hidden lg:block mb-8">
            <CareerLensLogo size="md" />
          </div>

          {success ? (
            /* ── Success state ── */
            <div className="text-center py-4">
              <div className="mx-auto mb-6 w-20 h-20 rounded-full
                bg-gradient-to-br from-[#0050cb] to-[#6366f1]
                flex items-center justify-center shadow-lg">
                <span className="material-symbols-outlined text-4xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>
                  check_circle
                </span>
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">Account Created!</h2>
              <p className="text-sm text-slate-400 mb-8 max-w-xs mx-auto">
                Your CareerLens AI account is ready. Sign in to start your journey.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 h-14 px-8 rounded-xl font-bold text-base text-white
                  bg-gradient-to-r from-[#0050cb] to-[#6366f1]
                  hover:from-[#003fa0] hover:to-[#4f46e5] active:scale-[0.98]
                  shadow-[0_4px_20px_rgba(0,80,203,0.35)] touch-manipulation"
              >
                Go to Sign In
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-1">Create Account</h2>
              <p className="text-sm text-slate-400 mb-6">See Your Career Clearly with CareerLens AI.</p>

              {errorMsg && (
                <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
                  {errorMsg}
                </div>
              )}

              {/* Continue with Google */}
              <div className="mb-4">
                <GoogleSignInButton
                  text="Sign up with Google"
                  onSuccess={(user) => {
                    login(user)
                  }}
                  onError={(err) => setErrorMsg(err)}
                />
              </div>

              <div className="my-5 flex items-center gap-3">
                <div className="h-px flex-1 bg-slate-200" />
                <span className="text-[11px] uppercase font-bold tracking-wider text-slate-400 font-[Geist]">
                  or register with email
                </span>
                <div className="h-px flex-1 bg-slate-200" />
              </div>

              <form onSubmit={handleRegister} className="space-y-4">
                <FloatingInput
                  id="reg-name" label="Full Name" type="text"
                  value={name} onChange={e => setName(e.target.value)} required
                  autoComplete="name"
                />
                <FloatingInput
                  id="reg-email" label="Email Address" type="email"
                  value={email} onChange={e => setEmail(e.target.value)} required
                  autoComplete="email"
                />
                <FloatingInput
                  id="reg-password" label="Password"
                  type={showPw ? 'text' : 'password'}
                  value={password} onChange={e => setPassword(e.target.value)} required
                  autoComplete="new-password"
                  rightEl={<EyeBtn show={showPw} toggle={() => setShowPw(!showPw)} />}
                />

                {/* Password strength bar */}
                {password.length > 0 && (
                  <div className="flex items-center gap-2 px-1">
                    <div className="flex gap-1 flex-1">
                      {[1,2,3,4].map(n => (
                        <div
                          key={n}
                          className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                            n <= strength ? strengthColor : 'bg-slate-200'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-medium text-slate-400 w-10 text-right">{strengthLabel}</span>
                  </div>
                )}

                <button
                  type="submit" disabled={loading}
                  className="w-full h-14 rounded-xl font-bold text-base text-white
                    bg-gradient-to-r from-[#0050cb] to-[#6366f1]
                    hover:from-[#003fa0] hover:to-[#4f46e5] active:scale-[0.98]
                    shadow-[0_4px_20px_rgba(0,80,203,0.35)]
                    hover:shadow-[0_6px_28px_rgba(0,80,203,0.45)]
                    transition-all duration-200 touch-manipulation
                    disabled:opacity-60 disabled:cursor-not-allowed
                    flex items-center justify-center gap-2"
                >
                  {loading
                    ? <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                      </svg>
                    : 'Create Account'}
                </button>
              </form>

              <p className="mt-7 text-center text-sm text-slate-400">
                Already have an account?{' '}
                <Link to="/login" className="font-bold text-[#0050cb] hover:underline">
                  Sign In
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
