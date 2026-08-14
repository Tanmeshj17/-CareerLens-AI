import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../App'
import { loginUser, getCurrentUser, resendVerificationEmail } from '../api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Alert } from '../components/ui/Alert'
import CareerLensLogo from '../components/CareerLensLogo'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [showResend, setShowResend] = useState(false)
  const [resendStatus, setResendStatus] = useState('')
  const { login } = useContext(AuthContext)
  const navigate = useNavigate()

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
      if (err.message && err.message.toLowerCase().includes('not verified')) {
        setShowResend(true)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setResendStatus('Sending...')
    try {
      await resendVerificationEmail(email)
      setResendStatus('Verification email sent! Please check your inbox.')
    } catch (err) {
      setResendStatus('Failed to send: ' + err.message)
    }
  }

  const [showForgotModal, setShowForgotModal] = useState(false)
  const [forgotEmail, setForgotEmail] = useState('')
  const [forgotLoading, setForgotLoading] = useState(false)
  const [forgotMsg, setForgotMsg] = useState('')
  const [forgotError, setForgotError] = useState('')
  const [forgotDebugUrl, setForgotDebugUrl] = useState('')

  const handleForgotSubmit = async (e) => {
    e.preventDefault()
    setForgotLoading(true)
    setForgotError('')
    setForgotMsg('')
    setForgotDebugUrl('')
    try {
      const { forgotPassword } = await import('../api')
      const res = await forgotPassword(forgotEmail)
      setForgotMsg(res.message || 'Reset link sent!')
      if (res.debug_reset_url) {
        setForgotDebugUrl(res.debug_reset_url)
      }
    } catch (err) {
      setForgotError(err.message || 'Failed to request reset')
    } finally {
      setForgotLoading(false)
    }
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex flex-col lg:flex-row">
      {/* Left Side: Branding */}
      <section className="w-full lg:w-[45%] xl:w-1/2 bg-on-background relative overflow-hidden flex items-center justify-center p-xl md:p-2xl min-w-0 min-h-[320px] lg:min-h-screen">
        <div className="relative z-10 max-w-lg w-full">
          <div className="mb-xl">
            <CareerLensLogo size="lg" variant="white" />
          </div>
          <h1 className="hero-title font-bold text-white mb-lg leading-tight">
            Unlock your career potential with AI.
          </h1>
          <p className="text-lg text-surface-variant mb-2xl">
            Experience the next generation of career growth. We use sophisticated data analysis to match your skills with the world's most ambitious opportunities.
          </p>
          {/* AI Insight */}
          <div className="glass-effect rounded-xl p-lg max-w-sm w-full">
            <div className="flex items-center gap-md mb-sm">
              <span className="material-symbols-outlined text-primary-fixed" style={{fontVariationSettings: "'FILL' 1"}}>auto_awesome</span>
              <span className="text-sm font-medium font-[Geist] text-primary-fixed">AI Insight</span>
            </div>
            <p className="text-sm text-white opacity-80">
              "Your background in Data Engineering makes you a 94% match for Lead AI Architect roles in emerging tech hubs."
            </p>
          </div>
        </div>
        <div className="absolute bottom-0 left-0 w-full h-1/3 bg-gradient-to-t from-on-background to-transparent pointer-events-none"></div>
      </section>

      {/* Right Side: Login Form */}
      <main className="w-full lg:w-[55%] xl:w-1/2 flex items-center justify-center p-lg sm:p-2xl bg-white relative min-w-0">
        <div className="w-full max-w-md animate-fade-in-up">
          <div className="mb-lg lg:hidden">
            <CareerLensLogo size="md" />
          </div>
          <div className="mb-xl">
            <h2 className="text-2xl sm:text-3xl font-semibold text-on-surface mb-xs">Welcome back</h2>
            <p className="text-sm sm:text-base text-on-surface-variant">Please enter your details to sign in.</p>
          </div>

          <Button variant="secondary" disabled className="w-full gap-md mb-xl h-12">
            <img alt="Google Logo" className="w-5 h-5 grayscale" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBub5gEiv-2Vjp98zG-Z7ym0E9Mx_IU-k4Zpr78GhmXkp-flOcePACRGqARUWjYNacLZGlKeA5wIGnU-bvo_3tX6R2_8uboMkzO5uYo5xbeUxRaU_qqkvWPnN1nNMQlhuePfgPvI0haHSe7wm_y2TmHumbPB0wmhXbZg9sQwIDvAR7A4iz8c5nACC2YN5ad7bUpCLuIFglbBp2h73AF-QNTyCqNszGyOR3U7Q9TvE1ZAn0OeEGuOtmCNaBO8ZQNtgQbcHZnzL2-db8" />
            Continue with Google — Coming Soon
          </Button>

          <div className="relative flex items-center mb-xl">
            <div className="flex-grow border-t border-outline-variant"></div>
            <span className="flex-shrink mx-md text-sm font-medium font-[Geist] text-outline capitalize">or login with email</span>
            <div className="flex-grow border-t border-outline-variant"></div>
          </div>

          {errorMsg && (
            <Alert 
              type="error"
              message={errorMsg}
              action={showResend && (
                <div>
                  <button onClick={handleResend} type="button" className="text-xs font-semibold underline hover:text-error/80 transition focus:outline-none focus:ring-2 focus:ring-error rounded px-1">
                    Resend Verification Email
                  </button>
                  {resendStatus && <p className="mt-1 text-xs opacity-90">{resendStatus}</p>}
                </div>
              )}
            />
          )}

          <form onSubmit={handleLogin} className="space-y-lg">
            <div className="space-y-xs">
              <Input 
                id="email" 
                label="Email Address"
                type="email" 
                required 
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="alex@company.com" 
              />
            </div>
            <div className="space-y-xs relative">
              <div className="flex justify-between items-center mb-1">
                <label className="text-sm font-medium font-[Geist] text-on-surface" htmlFor="password">Password</label>
                <Link 
                  to="/forgot-password" 
                  className="text-xs font-medium font-[Geist] text-primary hover:underline cursor-pointer focus:outline-none"
                >
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <Input 
                  id="password" 
                  type={showPassword ? "text" : "password"} 
                  required 
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••" 
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-md top-1/2 -translate-y-1/2 text-outline-variant hover:text-outline transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-full p-1 flex items-center justify-center"
                >
                  <span className="material-symbols-outlined text-[20px]">{showPassword ? 'visibility_off' : 'visibility'}</span>
                </button>
              </div>
            </div>
            <div className="flex items-center gap-md">
              <input id="remember" type="checkbox" className="w-4 h-4 text-primary border-outline-variant rounded focus:ring-primary focus:ring-2 focus:ring-offset-2 transition-all" />
              <label htmlFor="remember" className="text-sm text-on-surface-variant">Remember me for 30 days</label>
            </div>
            <Button 
              type="submit" 
              variant="primary"
              isLoading={loading}
              className="w-full h-12"
            >
              Login
            </Button>
          </form>
          
          <div className="mt-2xl text-center">
            <p className="text-sm text-on-surface-variant">
              Don't have an account? <Link to="/register" className="text-sm font-medium font-[Geist] text-primary hover:underline">Register</Link>
            </p>
          </div>
        </div>
      </main>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl p-xl max-w-md w-full shadow-2xl relative border border-outline-variant space-y-md">
            <button 
              onClick={() => setShowForgotModal(false)}
              className="absolute top-4 right-4 text-on-surface-variant hover:text-on-surface rounded-full p-1 transition"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
            <div className="text-center space-y-1">
              <span className="material-symbols-outlined text-3xl text-primary">lock_reset</span>
              <h3 className="text-xl font-bold text-on-surface">Forgot Password</h3>
              <p className="text-xs text-on-surface-variant">Enter your email to receive a password reset link.</p>
            </div>

            {forgotError && <Alert type="error" message={forgotError} />}
            {forgotMsg && <Alert type="success" message={forgotMsg} />}

            {forgotDebugUrl && (
              <div className="p-3 bg-primary-container/20 border border-primary/30 rounded-xl text-xs space-y-1">
                <span className="font-bold text-primary block">Direct Reset Link:</span>
                <a href={forgotDebugUrl} className="text-primary underline break-all font-mono">
                  {forgotDebugUrl}
                </a>
              </div>
            )}

            <form onSubmit={handleForgotSubmit} className="space-y-md">
              <Input
                label="Email Address"
                type="email"
                required
                value={forgotEmail}
                onChange={(e) => setForgotEmail(e.target.value)}
                placeholder="alex@company.com"
              />
              <Button type="submit" variant="primary" isLoading={forgotLoading} className="w-full h-11">
                Send Reset Link
              </Button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
