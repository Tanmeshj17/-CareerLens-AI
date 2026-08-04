import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser, loginUser, getCurrentUser } from '../api'
import { AuthContext } from '../App'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Alert } from '../components/ui/Alert'

export default function Register() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const navigate = useNavigate()
  const { login } = useContext(AuthContext)

  const [registrationSuccess, setRegistrationSuccess] = useState(false)

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrorMsg('')
    try {
      await registerUser(email, name, password)
      setRegistrationSuccess(true)
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex flex-col lg:flex-row">
      <main className="w-full lg:w-[55%] xl:w-1/2 flex items-center justify-center p-lg sm:p-2xl bg-white relative min-w-0">
        <div className="w-full max-w-md animate-fade-in-up">
          <div className="mb-xl lg:hidden">
            <span className="text-2xl font-bold text-primary">CareerLens AI</span>
          </div>
          <div className="mb-xl">
            <h2 className="text-3xl font-semibold text-on-surface mb-xs">Create an Account</h2>
            <p className="text-base text-on-surface-variant">Join CareerLens AI to transform your career path.</p>
          </div>

          <Button variant="secondary" disabled className="w-full gap-md mb-xl h-12">
            <img alt="Google Logo" className="w-5 h-5 grayscale" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBub5gEiv-2Vjp98zG-Z7ym0E9Mx_IU-k4Zpr78GhmXkp-flOcePACRGqARUWjYNacLZGlKeA5wIGnU-bvo_3tX6R2_8uboMkzO5uYo5xbeUxRaU_qqkvWPnN1nNMQlhuePfgPvI0haHSe7wm_y2TmHumbPB0wmhXbZg9sQwIDvAR7A4iz8c5nACC2YN5ad7bUpCLuIFglbBp2h73AF-QNTyCqNszGyOR3U7Q9TvE1ZAn0OeEGuOtmCNaBO8ZQNtgQbcHZnzL2-db8" />
            Sign up with Google — Coming Soon
          </Button>

          <div className="relative flex items-center mb-xl">
            <div className="flex-grow border-t border-outline-variant"></div>
            <span className="flex-shrink mx-md text-sm font-medium font-[Geist] text-outline capitalize">or register with email</span>
            <div className="flex-grow border-t border-outline-variant"></div>
          </div>

          {registrationSuccess ? (
            <div className="text-center bg-primary-container/10 p-lg rounded-xl border border-primary/20">
              <span className="material-symbols-outlined text-primary text-5xl mb-sm" style={{fontVariationSettings: "'FILL' 1"}}>mark_email_read</span>
              <h3 className="text-xl font-bold text-on-surface mb-xs">Account created successfully</h3>
              <p className="text-sm text-on-surface-variant mb-lg">
                Please check your email and click the verification link before logging in.
              </p>
              <Link to="/login" className="inline-block bg-primary text-white py-sm px-lg rounded-lg text-sm font-medium font-[Geist] hover:bg-primary/90 transition-all">
                Go to Login
              </Link>
            </div>
          ) : (
            <>
              {errorMsg && <Alert type="error" message={errorMsg} />}
              <form onSubmit={handleRegister} className="space-y-lg">
              <div className="space-y-xs">
                <Input required value={name} onChange={e => setName(e.target.value)} type="text" label="Full Name" placeholder="Your full name" />
              </div>
              <div className="space-y-xs">
                <Input required value={email} onChange={e => setEmail(e.target.value)} type="email" label="Email Address" placeholder="alex@company.com" />
              </div>
              <div className="space-y-xs relative">
                <label className="text-sm font-medium font-[Geist] text-on-surface block mb-1">Password</label>
                <div className="relative">
                  <Input required value={password} onChange={e => setPassword(e.target.value)} type={showPassword ? "text" : "password"} placeholder="••••••••" />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-md top-1/2 -translate-y-1/2 text-outline-variant hover:text-outline transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-full p-1 flex items-center justify-center">
                    <span className="material-symbols-outlined text-[20px]">{showPassword ? 'visibility_off' : 'visibility'}</span>
                  </button>
                </div>
              </div>
              
              <Button isLoading={loading} type="submit" className="w-full h-12">
                Register
              </Button>
            </form>
            </>
          )}
          
          <div className="mt-2xl text-center">
            <p className="text-sm text-on-surface-variant">
              Already have an account? <Link to="/login" className="text-sm font-medium font-[Geist] text-primary hover:underline">Log In</Link>
            </p>
          </div>
        </div>
      </main>

      <section className="w-full lg:w-[45%] xl:w-1/2 bg-on-background relative overflow-hidden flex items-center justify-center p-xl md:p-2xl min-w-0 min-h-[350px] lg:min-h-screen">
        <div className="relative z-10 max-w-lg w-full">
          <div className="mb-xl">
            <span className="text-2xl font-bold text-primary-fixed block max-w-full overflow-hidden text-ellipsis whitespace-nowrap">CareerLens AI</span>
          </div>
          <h1 className="hero-title font-bold text-white mb-lg leading-tight">
            Your intelligence advantage in the job market.
          </h1>
          <p className="text-lg text-surface-variant mb-2xl">
            Join thousands of professionals securing roles at top enterprises using data-driven insights and AI matching.
          </p>
        </div>
        <div className="absolute bottom-0 left-0 w-full h-1/3 bg-gradient-to-t from-on-background to-transparent pointer-events-none"></div>
      </section>
    </div>
  )
}
