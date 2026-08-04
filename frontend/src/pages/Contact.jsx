import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

export default function Contact() {
  return (
    <div className="max-w-3xl mx-auto px-lg py-2xl animate-fade-in-up min-h-screen">
      <h1 className="text-4xl font-bold mb-sm text-primary">Contact Us</h1>
      <p className="text-on-surface-variant mb-xl">Have a question or feedback? We'd love to hear from you.</p>
      <form onSubmit={(e) => e.preventDefault()} className="glass-effect p-xl rounded-xl border border-outline-variant space-y-md">
        <Input label="Name" placeholder="Your full name" />
        <Input label="Email" type="email" placeholder="you@company.com" />
        <div>
          <label className="block text-sm font-medium text-on-surface mb-1">Message</label>
          <textarea rows="5" className="w-full p-2 border border-outline-variant rounded-lg bg-surface focus:ring-2 focus:ring-primary focus:outline-none transition-all" placeholder="How can we help?"></textarea>
        </div>
        <Button type="submit" variant="primary" className="px-6">Send Message</Button>
      </form>
    </div>
  );
}
