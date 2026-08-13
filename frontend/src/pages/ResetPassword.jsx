import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { resetPassword } from '../api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Alert } from '../components/ui/Alert'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setErrorMsg('Passwords do not match.')
      return
    }
    if (newPassword.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.')
      return
    }

    setLoading(true)
    setErrorMsg('')
    setSuccessMsg('')

    try {
      const res = await resetPassword(token, newPassword)
      setSuccessMsg(res.message || 'Password successfully reset!')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err) {
      setErrorMsg(err.message || 'Failed to reset password. Link may be invalid or expired.')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="bg-surface-bright text-on-surface min-h-screen flex items-center justify-center p-md">
        <div className="w-full max-w-md bg-white rounded-2xl p-xl shadow-lg border border-outline-variant text-center">
          <Alert type="error" message="Invalid request. Missing password reset token." />
          <Link to="/login" className="mt-md text-sm font-medium text-primary hover:underline inline-block">
            Back to Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex items-center justify-center p-md">
      <div className="w-full max-w-md bg-white rounded-2xl p-xl shadow-lg border border-outline-variant animate-fade-in-up">
        <div className="mb-lg text-center">
          <span className="text-2xl font-bold text-primary block mb-xs">CareerLens AI</span>
          <h2 className="text-2xl font-semibold text-on-surface">Reset Password</h2>
          <p className="text-sm text-on-surface-variant mt-1">
            Enter your new password below.
          </p>
        </div>

        {errorMsg && <Alert type="error" message={errorMsg} />}
        {successMsg && <Alert type="success" message={successMsg} />}

        <form onSubmit={handleSubmit} className="space-y-lg mt-md">
          <div className="relative">
            <Input
              id="newPassword"
              label="New Password"
              type={showPassword ? 'text' : 'password'}
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-md top-9 text-outline-variant hover:text-outline transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">
                {showPassword ? 'visibility_off' : 'visibility'}
              </span>
            </button>
          </div>

          <Input
            id="confirmPassword"
            label="Confirm New Password"
            type={showPassword ? 'text' : 'password'}
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
          />

          <Button type="submit" variant="primary" isLoading={loading} className="w-full h-12">
            Reset Password
          </Button>
        </form>

        <div className="mt-xl text-center">
          <Link to="/login" className="text-sm font-medium text-primary hover:underline">
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  )
}
