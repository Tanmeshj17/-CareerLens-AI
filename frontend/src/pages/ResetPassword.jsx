import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { resetPassword } from '../api'
import CareerLensLogo from '../components/CareerLensLogo'

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
        autoComplete={autoComplete || 'new-password'}
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
      {rightEl && <div className="absolute right-3 top-1/2 -translate-y-1/2">{rightEl}</div>}
    </div>
  )
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const urlToken = searchParams.get('token') || ''

  const [manualToken, setManualToken]       = useState(urlToken)
  const [newPassword, setNewPassword]       = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword]     = useState(false)
  const [loading, setLoading]               = useState(false)
  const [successMsg, setSuccessMsg]         = useState('')
  const [errorMsg, setErrorMsg]             = useState('')
  const navigate = useNavigate()

  const activeToken = urlToken || manualToken

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!activeToken) { setErrorMsg('Please enter your reset token.'); return }
    if (newPassword !== confirmPassword) { setErrorMsg('Passwords do not match.'); return }
    if (newPassword.length < 6) { setErrorMsg('Password must be at least 6 characters.'); return }
    setLoading(true); setErrorMsg(''); setSuccessMsg('')
    try {
      const res = await resetPassword(activeToken, newPassword)
      setSuccessMsg(res.message || 'Password successfully reset!')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      setErrorMsg(err.message || 'Failed to reset password. Link may be invalid or expired.')
    } finally { setLoading(false) }
  }

  return (
    <div
      className="min-h-screen min-h-[100dvh] w-full flex flex-col items-center justify-center
        font-['Plus_Jakarta_Sans',sans-serif]
        bg-gradient-to-br from-[#e8eeff] via-[#f0f4ff] to-[#e6eeff]
        px-4 py-8"
    >
      <div className="w-full max-w-sm sm:max-w-md">
        <div className="bg-white rounded-2xl sm:rounded-[2rem] shadow-[0_24px_64px_rgba(0,50,180,0.15)] p-7 sm:p-10">

          <div className="flex justify-center mb-7">
            <CareerLensLogo size="md" />
          </div>

          <div className="flex justify-center mb-5">
            <div className="w-16 h-16 rounded-full
              bg-gradient-to-br from-[#0050cb] to-[#6366f1]
              flex items-center justify-center shadow-lg shadow-[#0050cb]/30">
              <span className="material-symbols-outlined text-3xl text-white" style={{fontVariationSettings:"'FILL' 1"}}>
                lock
              </span>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-center text-slate-800 mb-1">Reset Password</h2>
          <p className="text-sm text-center text-slate-400 mb-7 leading-relaxed">
            Enter your new password below to regain access.
          </p>

          {errorMsg && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-2">
              <span className="material-symbols-outlined text-[16px] mt-0.5 flex-shrink-0" style={{fontVariationSettings:"'FILL' 1"}}>error</span>
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-sm text-emerald-700 flex items-start gap-2">
              <span className="material-symbols-outlined text-[16px] mt-0.5 flex-shrink-0 text-emerald-500" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
              {successMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <FloatingInput
              id="new-password" label="New Password"
              type={showPassword ? 'text' : 'password'}
              value={newPassword} onChange={e => setNewPassword(e.target.value)} required
              rightEl={
                <button
                  type="button" onClick={() => setShowPassword(!showPassword)}
                  className="text-slate-400 hover:text-[#0050cb] transition-colors p-1.5 rounded-full
                    focus:outline-none focus:ring-2 focus:ring-[#0050cb]/30 touch-manipulation"
                >
                  <span className="material-symbols-outlined" style={{fontSize:20}}>
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              }
            />
            <FloatingInput
              id="confirm-password" label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required
            />

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
                : 'Reset Password'}
            </button>
          </form>

          <div className="mt-7 text-center">
            <Link
              to="/login"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#0050cb] hover:underline touch-manipulation"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
