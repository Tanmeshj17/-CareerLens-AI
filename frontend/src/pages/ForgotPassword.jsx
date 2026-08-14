import { useState } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Alert } from '../components/ui/Alert'
import CareerLensLogo from '../components/CareerLensLogo'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [debugUrl, setDebugUrl] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrorMsg('')
    setSuccessMsg('')
    setDebugUrl('')

    try {
      const res = await forgotPassword(email)
      setSuccessMsg(res.message || 'If an account exists, a password reset link has been sent.')
      if (res.debug_reset_url) {
        setDebugUrl(res.debug_reset_url)
      }
    } catch (err) {
      setErrorMsg(err.message || 'Failed to request password reset.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex items-center justify-center p-4 sm:p-md">
      <div className="w-full max-w-md bg-white rounded-2xl p-6 sm:p-xl shadow-lg border border-outline-variant animate-fade-in-up">
        <div className="mb-lg text-center">
          <div className="flex justify-center mb-md">
            <CareerLensLogo size="md" />
          </div>
          <h2 className="text-2xl font-semibold text-on-surface">Forgot Password?</h2>
          <p className="text-sm text-on-surface-variant mt-1">
            Enter your account email address and we will send you a password reset link.
          </p>
        </div>

        {errorMsg && <Alert type="error" message={errorMsg} />}
        {successMsg && <Alert type="success" message={successMsg} />}

        {debugUrl && (
          <div className="my-md p-md bg-primary-container/20 border border-primary/30 rounded-xl text-left text-xs space-y-1">
            <span className="font-bold text-primary block">Direct Reset Link:</span>
            <a href={debugUrl} className="text-primary underline break-all font-mono">
              {debugUrl}
            </a>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-lg mt-md">
          <Input
            id="email"
            label="Email Address"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="alex@company.com"
          />

          <Button type="submit" variant="primary" isLoading={loading} className="w-full h-12">
            Send Reset Link
          </Button>
        </form>

        <div className="mt-xl text-center">
          <Link to="/login" className="text-sm font-medium text-primary hover:underline flex items-center justify-center gap-1">
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  )
}
