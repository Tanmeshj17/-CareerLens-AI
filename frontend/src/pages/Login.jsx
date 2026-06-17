import { useState, useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../App'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login } = useContext(AuthContext)
  const navigate = useNavigate()

  const handleLogin = (e) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      login(email, password)
      setLoading(false)
      navigate('/app')
    }, 1000)
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex">
      {/* Left Side: Branding */}
      <section className="hidden lg:flex lg:w-1/2 bg-on-background relative overflow-hidden items-center justify-center p-2xl">
        <div className="relative z-10 max-w-lg">
          <div className="mb-xl">
            <span className="text-2xl font-bold text-primary-fixed">CareerLens AI</span>
          </div>
          <h1 className="text-5xl font-bold text-white mb-lg leading-tight">
            Unlock your career potential with AI.
          </h1>
          <p className="text-lg text-surface-variant mb-2xl">
            Experience the next generation of career growth. We use sophisticated data analysis to match your skills with the world's most ambitious opportunities.
          </p>
          {/* AI Insight */}
          <div className="glass-effect rounded-xl p-lg shimmer-border max-w-sm">
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
      <main className="w-full lg:w-1/2 flex items-center justify-center p-lg sm:p-2xl bg-white relative">
        <div className="w-full max-w-md animate-fade-in-up">
          <div className="mb-xl lg:hidden">
            <span className="text-2xl font-bold text-primary">CareerLens AI</span>
          </div>
          <div className="mb-xl">
            <h2 className="text-3xl font-semibold text-on-surface mb-xs">Welcome back</h2>
            <p className="text-base text-on-surface-variant">Please enter your details to sign in.</p>
          </div>

          <button className="w-full flex items-center justify-center gap-md py-md px-lg border border-outline-variant rounded-lg text-sm font-medium font-[Geist] text-on-surface hover:bg-surface-container-low transition-colors duration-200 mb-xl">
            <img alt="Google Logo" className="w-5 h-5" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBub5gEiv-2Vjp98zG-Z7ym0E9Mx_IU-k4Zpr78GhmXkp-flOcePACRGqARUWjYNacLZGlKeA5wIGnU-bvo_3tX6R2_8uboMkzO5uYo5xbeUxRaU_qqkvWPnN1nNMQlhuePfgPvI0haHSe7wm_y2TmHumbPB0wmhXbZg9sQwIDvAR7A4iz8c5nACC2YN5ad7bUpCLuIFglbBp2h73AF-QNTyCqNszGyOR3U7Q9TvE1ZAn0OeEGuOtmCNaBO8ZQNtgQbcHZnzL2-db8" />
            Continue with Google
          </button>

          <div className="relative flex items-center mb-xl">
            <div className="flex-grow border-t border-outline-variant"></div>
            <span className="flex-shrink mx-md text-sm font-medium font-[Geist] text-outline capitalize">or login with email</span>
            <div className="flex-grow border-t border-outline-variant"></div>
          </div>

          <form onSubmit={handleLogin} className="space-y-lg">
            <div className="space-y-xs">
              <label className="text-sm font-medium font-[Geist] text-on-surface" htmlFor="email">Email Address</label>
              <input 
                id="email" 
                type="email" 
                required 
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full px-md py-sm border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-base" 
                placeholder="alex@company.com" 
              />
            </div>
            <div className="space-y-xs">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium font-[Geist] text-on-surface" htmlFor="password">Password</label>
                <a className="text-xs font-medium font-[Geist] text-primary hover:underline cursor-pointer">Forgot Password?</a>
              </div>
              <div className="relative">
                <input 
                  id="password" 
                  type={showPassword ? "text" : "password"} 
                  required 
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full px-md py-sm border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-base" 
                  placeholder="••••••••" 
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-md top-1/2 -translate-y-1/2 text-outline-variant hover:text-outline transition-colors"
                >
                  <span className="material-symbols-outlined text-[20px]">{showPassword ? 'visibility_off' : 'visibility'}</span>
                </button>
              </div>
            </div>
            <div className="flex items-center gap-md">
              <input id="remember" type="checkbox" className="w-4 h-4 text-primary border-outline-variant rounded focus:ring-primary" />
              <label htmlFor="remember" className="text-sm text-on-surface-variant">Remember me for 30 days</label>
            </div>
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-primary-container text-white py-md px-lg rounded-lg text-sm font-medium font-[Geist] hover:bg-primary transition-all active:scale-[0.98] shadow-sm flex items-center justify-center h-12"
            >
              {loading ? <span className="material-symbols-outlined animate-spin">progress_activity</span> : 'Login'}
            </button>
          </form>
          
          <div className="mt-2xl text-center">
            <p className="text-sm text-on-surface-variant">
              Don't have an account? <Link to="/register" className="text-sm font-medium font-[Geist] text-primary hover:underline">Register</Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
