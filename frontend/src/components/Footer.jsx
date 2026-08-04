import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-surface-container-lowest border-t border-outline-variant py-xl mt-auto">
      <div className="max-w-7xl mx-auto px-lg">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-xl">
          <div className="md:col-span-1">
            <span className="text-xl font-bold text-primary-fixed mb-sm block">CareerLens AI</span>
            <p className="text-sm text-on-surface-variant mb-md">
              Unlock your career potential with AI-driven insights, job matching, and structured learning paths.
            </p>
          </div>
          <div>
            <h4 className="font-bold mb-md text-on-surface">Platform</h4>
            <ul className="space-y-sm text-sm text-on-surface-variant">
              <li><Link to="/app" className="hover:text-primary transition-colors">Dashboard</Link></li>
              <li><Link to="/app/opportunities" className="hover:text-primary transition-colors">Jobs & Internships</Link></li>
              <li><Link to="/app/resume" className="hover:text-primary transition-colors">Resume Analysis</Link></li>
              <li><Link to="/app/learn" className="hover:text-primary transition-colors">Skill Hub</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold mb-md text-on-surface">Resources</h4>
            <ul className="space-y-sm text-sm text-on-surface-variant">
              <li><Link to="/app/interview-prep" className="hover:text-primary transition-colors">Interview Prep</Link></li>
              <li><Link to="/app/certifications" className="hover:text-primary transition-colors">Certifications</Link></li>
              <li><Link to="/app/resources" className="hover:text-primary transition-colors">Free Resources</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold mb-md text-on-surface">Company</h4>
            <ul className="space-y-sm text-sm text-on-surface-variant">
              <li><Link to="/about" className="hover:text-primary transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="hover:text-primary transition-colors">Contact</Link></li>
              <li><Link to="/privacy" className="hover:text-primary transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-primary transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-outline-variant mt-xl pt-lg flex flex-col md:flex-row justify-between items-center text-sm text-on-surface-variant">
          <p>&copy; {new Date().getFullYear()} CareerLens AI. All rights reserved.</p>
          <div className="flex space-x-md mt-sm md:mt-0">
            <span className="material-symbols-outlined cursor-pointer hover:text-primary">language</span>
            <span className="material-symbols-outlined cursor-pointer hover:text-primary">share</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
