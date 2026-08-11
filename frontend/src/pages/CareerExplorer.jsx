import { useState, useEffect } from 'react';
import { getFastGrowingCareers, getCareerRoadmap } from '../api';

export default function CareerExplorer() {
  const [step, setStep] = useState(1);
  const [selectedRole, setSelectedRole] = useState(null);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [roadmap, setRoadmap] = useState(null);
  const [roadmapLoading, setRoadmapLoading] = useState(false);

  const handleSelectRole = async (role) => {
    setSelectedRole(role);
    setRoadmapLoading(true);
    try {
      const data = await getCareerRoadmap(role.title);
      setRoadmap(data);
    } catch(err) {
      console.error("Failed to load roadmap", err);
    } finally {
      setRoadmapLoading(false);
    }
  };

  useEffect(() => {
    if (step === 2) {
      setLoading(true);
      getFastGrowingCareers()
        .then(data => {
          const rolesList = data.roles || [];
          const mapped = rolesList.map(item => ({
            id: item.title,
            title: item.title,
            salary: 'Market Standard',
            growth: item.growth_signal,
            totalPostings: item.total_postings,
            recentPostings: item.recent_postings,
            skills: []
          }));
          setRoles(mapped.length ? mapped : []);
        })
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [step]);

  return (
    <div className="space-y-lg animate-fade-in-up">
      <header>
        <h1 className="text-3xl font-bold text-on-surface">Career Explorer</h1>
        <p className="text-on-surface-variant">Discover your ideal career path based on your skills and interests.</p>
      </header>

      {step === 1 && (
        <div className="bg-surface-container-low border border-outline-variant rounded-xl p-lg text-center max-w-2xl mx-auto my-xl glass-effect">
          <h2 className="text-2xl font-bold mb-2">Find Your True Calling</h2>
          <p className="text-on-surface-variant mb-6">Take our 3-minute career matching quiz to find roles that fit your personality and skills.</p>
          <button onClick={() => setStep(2)} className="bg-primary text-on-primary px-8 py-3 rounded-full font-bold text-lg hover:bg-primary-container transition-transform hover:scale-105">Start Career Quiz</button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-lg">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Recommended Career Paths</h2>
            <button onClick={() => setStep(1)} className="text-sm font-bold text-primary hover:underline">Retake Quiz</button>
          </div>
          
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
              {[1, 2, 3].map(i => <div key={i} className="animate-pulse h-40 bg-surface-variant rounded-xl"></div>)}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg stagger-children">
              {roles.map((role, i) => (
                <div 
                  key={i} 
                  onClick={() => handleSelectRole(role)}
                  className={`bg-surface-container-lowest border ${selectedRole?.title === role.title ? 'border-primary shadow-md ring-2 ring-primary/20' : 'border-outline-variant hover:border-primary/50'} rounded-xl p-lg cursor-pointer transition-all`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-bold text-xl">{role.title}</h3>
                    {role.growth === 'Fast Growing' && <span className="px-2 py-1 bg-success/10 text-success text-xs font-bold rounded-full">Trending</span>}
                  </div>
                  <div className="space-y-2 mb-4">
                    <p className="text-sm flex justify-between"><span className="text-on-surface-variant">Avg Salary:</span> <span className="font-bold">{role.salary}</span></p>
                    <p className="text-sm flex justify-between"><span className="text-on-surface-variant">Growth:</span> <span className="font-bold text-success">{role.growth}</span></p>
                    <p className="text-sm flex justify-between"><span className="text-on-surface-variant">Total Postings:</span> <span className="font-bold text-primary">{role.totalPostings}</span></p>
                    <p className="text-sm flex justify-between"><span className="text-on-surface-variant">Recent Postings:</span> <span className="font-bold text-secondary">{role.recentPostings}</span></p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {selectedRole && (
            <div className="mt-xl bg-surface-container-low border border-outline-variant rounded-xl p-lg animate-fade-in-up">
              <h3 className="text-xl font-bold mb-md">Career Roadmap: {selectedRole.title}</h3>
              {roadmapLoading ? (
                <div className="animate-pulse space-y-4">
                  <div className="h-20 bg-surface-variant rounded-xl"></div>
                  <div className="h-20 bg-surface-variant rounded-xl"></div>
                </div>
              ) : roadmap ? (
                <div className="space-y-md">
                  <p className="text-sm text-on-surface-variant mb-md">{roadmap.description}</p>
                  
                  {(roadmap.strategies || roadmap.what_to_learn) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-md mb-xl">
                      {roadmap.strategies && (
                        <div className="glass-effect p-md rounded-xl border border-primary/20 bg-primary/5">
                          <h4 className="font-bold text-primary flex items-center gap-xs mb-sm">
                            <span className="material-symbols-outlined text-[20px]">lightbulb</span>
                            Strategies for Success
                          </h4>
                          <ul className="space-y-xs text-sm text-on-surface-variant list-disc pl-md">
                            {roadmap.strategies.map((strategy, idx) => (
                              <li key={idx}>{strategy}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {roadmap.what_to_learn && (
                        <div className="glass-effect p-md rounded-xl border border-secondary/20 bg-secondary/5">
                          <h4 className="font-bold text-secondary flex items-center gap-xs mb-sm">
                            <span className="material-symbols-outlined text-[20px]">menu_book</span>
                            Key Concepts to Learn
                          </h4>
                          <ul className="space-y-xs text-sm text-on-surface-variant list-disc pl-md">
                            {roadmap.what_to_learn.map((concept, idx) => (
                              <li key={idx}>{concept}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  <h3 className="text-lg font-bold mb-md mt-lg">Step-by-Step Execution</h3>
                  <div className="flex flex-col space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-primary before:to-transparent">
                    {roadmap.steps.map((step, idx) => (
                      <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-surface bg-primary text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 font-bold text-sm">
                          {step.step_number}
                        </div>
                        <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] glass-effect p-4 rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="font-bold text-md text-primary">{step.title}</h4>
                            <span className="text-xs font-medium bg-primary/10 text-primary px-2 py-1 rounded-full">{step.estimated_weeks} weeks</span>
                          </div>
                          <p className="text-sm text-on-surface-variant mb-2">{step.description}</p>
                          <div className="flex flex-wrap gap-1">
                            {step.skills.map(s => <span key={s} className="text-xs bg-surface-variant text-on-surface-variant px-2 py-1 rounded border border-outline-variant/50">{s}</span>)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
