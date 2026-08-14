import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser, loginUser, getCurrentUser } from '../api'
import { AuthContext } from '../App'
import CareerLensLogo from '../components/CareerLensLogo'

/* ─── Floating label input ──────────────────────────────────────────────── */
function FloatingInput({ id, label, type = 'text', value, onChange, required, rightEl }) {
  return (
    <div className="relative w-full group">
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        placeholder=" "
        autoComplete={type === 'password' ? 'new-password' : type === 'email' ? 'email' : 'name'}
        className="peer w-full h-[52px] px-4 pt-5 pb-1 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-sm outline-none transition-all
          focus:border-[#0050cb] focus:bg-white focus:shadow-[0_0_0_3px_rgba(0,80,203,0.12)]
          placeholder-transparent pr-11"
      />
      <label
        htmlFor={id}
        className="absolute left-4 top-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#0050cb] transition-all
          peer-placeholder-shown:top-[14px] peer-placeholder-shown:text-sm peer-placeholder-shown:font-normal peer-placeholder-shown:tracking-normal peer-placeholder-shown:text-slate-400
          peer-focus:top-1.5 peer-focus:text-[10px] peer-focus:font-semibold peer-focus:uppercase peer-focus:tracking-wider peer-focus:text-[#0050cb]"
      >
        {label}
      </label>
      {rightEl && <div className="absolute right-3 top-1/2 -translate-y-1/2">{rightEl}</div>}
    </div>
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
    setLoading(true)
    setErrorMsg('')
    try {
      await registerUser(email, name, password)
      setSuccess(true)
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#e8eeff] via-[#f0f4ff] to-[#e6eeff] flex items-center justify-center p-4 font-['Plus_Jakarta_Sans',sans-serif]">

      {/* Card */}
      <div className="relative w-full max-w-4xl min-h-[580px] rounded-[2rem] shadow-[0_32px_80px_rgba(0,50,180,0.18)] overflow-hidden flex bg-white">

        {/* ── LEFT: Brand panel (hidden on mobile) ────────────────── */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden flex-col items-center justify-center p-12 text-white bg-gradient-to-br from-[#0050cb] via-[#3b5cf6] to-[#6366f1]">
          {/* Decorative blobs */}
          <div className="absolute -top-20 -left-20 w-64 h-64 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute -bottom-16 -right-16 w-72 h-72 rounded-full bg-[#6366f1]/40 blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-[#0050cb]/20 blur-2xl pointer-events-none" />

          <div className="relative z-10 text-center">
            {/* Animated sparkle icon */}
            <div className="mx-auto mb-8 w-20 h-20 rounded-full bg-white/15 backdrop-blur-sm flex items-center justify-center ring-2 ring-white/30 shadow-xl">
              <span className="material-symbols-outlined text-4xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>
                auto_awesome
              </span>
            </div>

            <h2 className="text-3xl font-bold leading-tight mb-4">
              Welcome Back!
            </h2>
            <p className="text-sm text-white/75 max-w-xs leading-relaxed mb-8">
              Already have an account? Sign in to access your personalized career dashboard, saved opportunities, and AI-powered insights.
            </p>

            {/* Feature chips */}
            <div className="flex flex-col gap-3 mb-10 max-w-[220px] mx-auto text-left">
              {[
                ['insights_bar_chart','AI Job Matching'],
                ['description','ATS Resume Analysis'],
                ['route','Career Roadmaps'],
              ].map(([icon, text]) => (
                <div key={text} className="flex items-center gap-3 bg-white/10 rounded-xl px-4 py-2.5 backdrop-blur-sm">
                  <span className="material-symbols-outlined text-[18px] text-white/80" style={{fontVariationSettings:"'FILL' 1"}}>{icon}</span>
                  <span className="text-xs font-medium text-white/90">{text}</span>
                </div>
              ))}
            </div>

            <Link
              to="/login"
              className="inline-flex items-center gap-2 h-11 px-8 rounded-xl font-bold text-sm border-2 border-white/60 text-white
                hover:bg-white hover:text-[#0050cb] transition-all duration-200
                shadow-[0_4px_16px_rgba(0,0,0,0.2)] hover:shadow-[0_6px_24px_rgba(0,0,0,0.3)]"
            >
              <span className="material-symbols-outlined text-[18px]">arrow_back</span>
              Sign In
            </Link>
          </div>
        </div>

        {/* ── RIGHT: Form panel ───────────────────────────────────── */}
        <div className="relative z-10 flex flex-col justify-center w-full lg:w-1/2 px-8 sm:px-12 py-12 bg-white">
          {/* Logo (mobile only) */}
          <div className="mb-8 lg:mb-6">
            <CareerLensLogo size="md" />
          </div>

          {success ? (
            /* ── Success State ── */
            <div className="text-center py-6">
              <div className="mx-auto mb-6 w-20 h-20 rounded-full bg-gradient-to-br from-[#0050cb] to-[#6366f1] flex items-center justify-center shadow-lg">
                <span className="material-symbols-outlined text-4xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">Account Created!</h2>
              <p className="text-sm text-slate-400 mb-8 max-w-xs mx-auto">
                Your CareerLens AI account is ready. Sign in to start your journey.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 h-12 px-8 rounded-xl font-bold text-sm text-white
                  bg-gradient-to-r from-[#0050cb] to-[#6366f1]
                  hover:from-[#003fa0] hover:to-[#4f46e5]
                  shadow-[0_4px_20px_rgba(0,80,203,0.35)]
                  hover:shadow-[0_6px_28px_rgba(0,80,203,0.45)]
                  transition-all duration-200 transform hover:-translate-y-0.5"
              >
                Go to Sign In
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-bold text-slate-800 mb-1">Create Account</h2>
              <p className="text-sm text-slate-400 mb-7">Join CareerLens AI — See Your Career Clearly.</p>

              {/* Error */}
              {errorMsg && (
                <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700">
                  {errorMsg}
                </div>
              )}

              <form onSubmit={handleRegister} className="space-y-4">
                <FloatingInput
                  id="reg-name"
                  label="Full Name"
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                />

                <FloatingInput
                  id="reg-email"
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />

                <FloatingInput
                  id="reg-password"
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

                {/* Password strength hint */}
                {password.length > 0 && (
                  <div className="flex gap-1.5 pt-0.5">
                    {[1,2,3,4].map(n => (
                      <div
                        key={n}
                        className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                          password.length >= n * 3
                            ? n <= 1 ? 'bg-red-400' : n <= 2 ? 'bg-orange-400' : n <= 3 ? 'bg-yellow-400' : 'bg-emerald-400'
                            : 'bg-slate-200'
                        }`}
                      />
                    ))}
                    <span className="text-[10px] text-slate-400 self-center ml-1 min-w-[40px]">
                      {password.length < 4 ? 'Weak' : password.length < 7 ? 'Fair' : password.length < 10 ? 'Good' : 'Strong'}
                    </span>
                  </div>
                )}

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
                  ) : 'Create Account'}
                </button>
              </form>

              <p className="mt-8 text-center text-xs text-slate-400">
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
