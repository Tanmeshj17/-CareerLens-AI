import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Register() {
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()

  const handleRegister = (e) => {
    e.preventDefault()
    // Mock registration API call delays
    setTimeout(() => {
      navigate('/login')
    }, 800)
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex">
      <main className="w-full lg:w-1/2 flex items-center justify-center p-lg sm:p-2xl bg-white relative">
        <div className="w-full max-w-md animate-fade-in-up">
          <div className="mb-xl lg:hidden">
            <span className="text-2xl font-bold text-primary">CareerLens AI</span>
          </div>
          <div className="mb-xl">
            <h2 className="text-3xl font-semibold text-on-surface mb-xs">Create an Account</h2>
            <p className="text-base text-on-surface-variant">Join CareerLens AI to transform your career path.</p>
          </div>

          <button className="w-full flex items-center justify-center gap-md py-md px-lg border border-outline-variant rounded-lg text-sm font-medium font-[Geist] text-on-surface hover:bg-surface-container-low transition-colors duration-200 mb-xl">
            <img alt="Google Logo" className="w-5 h-5" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBub5gEiv-2Vjp98zG-Z7ym0E9Mx_IU-k4Zpr78GhmXkp-flOcePACRGqARUWjYNacLZGlKeA5wIGnU-bvo_3tX6R2_8uboMkzO5uYo5xbeUxRaU_qqkvWPnN1nNMQlhuePfgPvI0haHSe7wm_y2TmHumbPB0wmhXbZg9sQwIDvAR7A4iz8c5nACC2YN5ad7bUpCLuIFglbBp2h73AF-QNTyCqNszGyOR3U7Q9TvE1ZAn0OeEGuOtmCNaBO8ZQNtgQbcHZnzL2-db8" />
            Sign up with Google
          </button>

          <div className="relative flex items-center mb-xl">
            <div className="flex-grow border-t border-outline-variant"></div>
            <span className="flex-shrink mx-md text-sm font-medium font-[Geist] text-outline capitalize">or register with email</span>
            <div className="flex-grow border-t border-outline-variant"></div>
          </div>

          <form onSubmit={handleRegister} className="space-y-lg">
            <div className="space-y-xs">
              <label className="text-sm font-medium font-[Geist] text-on-surface">Full Name</label>
              <input required type="text" className="w-full px-md py-sm border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-base" placeholder="Alex Johnson" />
            </div>
            <div className="space-y-xs">
              <label className="text-sm font-medium font-[Geist] text-on-surface">Email Address</label>
              <input required type="email" className="w-full px-md py-sm border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-base" placeholder="alex@company.com" />
            </div>
            <div className="space-y-xs">
              <label className="text-sm font-medium font-[Geist] text-on-surface">Password</label>
              <div className="relative">
                <input required type={showPassword ? "text" : "password"} className="w-full px-md py-sm border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-base" placeholder="••••••••" />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-md top-1/2 -translate-y-1/2 text-outline-variant hover:text-outline transition-colors">
                  <span className="material-symbols-outlined text-[20px]">{showPassword ? 'visibility_off' : 'visibility'}</span>
                </button>
              </div>
            </div>
            
            <button type="submit" className="w-full bg-primary-container text-white py-md px-lg rounded-lg text-sm font-medium font-[Geist] hover:bg-primary transition-all active:scale-[0.98] shadow-sm flex items-center justify-center h-12">
              Register
            </button>
          </form>
          
          <div className="mt-2xl text-center">
            <p className="text-sm text-on-surface-variant">
              Already have an account? <Link to="/login" className="text-sm font-medium font-[Geist] text-primary hover:underline">Log In</Link>
            </p>
          </div>
        </div>
      </main>

      <section className="hidden lg:flex lg:w-1/2 bg-on-background relative overflow-hidden items-center justify-center p-2xl">
        <div className="relative z-10 max-w-lg">
          <div className="mb-xl">
            <span className="text-2xl font-bold text-primary-fixed">CareerLens AI</span>
          </div>
          <h1 className="text-5xl font-bold text-white mb-lg leading-tight">
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
