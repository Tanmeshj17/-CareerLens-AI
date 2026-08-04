import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getApplications, updateApplication } from '../api';

export default function ApplicationTracker() {
  const [view, setView] = useState('board');
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchApps = async () => {
    try {
      const data = await getApplications();
      setApps(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApps();
  }, []);

  const handleStatusChange = async (appId, newStatus) => {
    try {
      // Optimistic update
      setApps(apps.map(a => a.id === appId ? { ...a, status: newStatus } : a));
      await updateApplication(appId, { status: newStatus });
    } catch (e) {
      console.error(e);
      fetchApps(); // Revert on failure
    }
  };

  const handleNotesChange = async (appId, newNotes) => {
    try {
      setApps(apps.map(a => a.id === appId ? { ...a, notes: newNotes } : a));
      await updateApplication(appId, { notes: newNotes });
    } catch (e) {
      console.error(e);
      fetchApps(); // Revert on failure
    }
  };

  return (
    <div className="space-y-lg animate-fade-in-up">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-on-surface">Application Tracker</h1>
          <p className="text-on-surface-variant">Manage and track your job applications.</p>
        </div>
        <div className="flex gap-2 bg-surface-container p-1 rounded-lg">
          <button onClick={() => setView('board')} className={`px-4 py-2 rounded-md font-bold text-sm transition-colors cursor-pointer ${view === 'board' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}>Board</button>
          <button onClick={() => setView('list')} className={`px-4 py-2 rounded-md font-bold text-sm transition-colors cursor-pointer ${view === 'list' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}>List</button>
        </div>
      </header>

      {!loading && apps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-3xl text-center space-y-md">
          <span className="material-symbols-outlined text-5xl text-outline">inbox</span>
          <h3 className="text-xl font-bold text-on-background">No saved applications</h3>
          <p className="text-on-surface-variant">You haven't saved or applied to any jobs yet.</p>
          <Link to="/app/opportunities" className="bg-primary text-on-primary px-lg py-sm rounded-lg font-medium hover:bg-primary-container transition-colors">
            Browse Opportunities
          </Link>
        </div>
      ) : view === 'board' ? (
        <div className="flex gap-md overflow-x-auto pb-4 custom-scrollbar">
          {['Saved', 'Applied', 'Interview', 'Selected', 'Rejected'].map(status => (
            <div key={status} className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md kanban-column flex flex-col gap-sm min-w-[280px]">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-bold text-sm uppercase tracking-wider text-on-surface-variant">{status}</h3>
                <span className="bg-surface-container px-2 py-0.5 rounded-full text-xs font-bold">{apps.filter(a => a.status === status).length}</span>
              </div>
              {loading ? (
                <div className="animate-pulse h-20 bg-surface-variant rounded-lg"></div>
              ) : (
                apps.filter(a => a.status === status).map(app => (
                  <div key={app.id} className="bg-surface border border-outline-variant p-sm rounded-lg shadow-sm hover:shadow-md transition-shadow flex flex-col">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-on-surface">
                          {app.opportunity ? (
                            <Link to={`/app/opportunities/${app.opportunity.id}`} className="hover:text-primary transition-colors">
                              {app.opportunity.title}
                            </Link>
                          ) : 'Unknown Job'}
                        </h4>
                        <p className="text-sm text-on-surface-variant">{app.opportunity?.company || 'Unknown Company'}</p>
                      </div>
                      {app.opportunity && (
                        <Link to={`/app/opportunities/${app.opportunity.id}`} className="text-on-surface-variant hover:text-primary p-1">
                          <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                        </Link>
                      )}
                    </div>
                    
                    <textarea 
                      placeholder="Add notes..."
                      value={app.notes || ''}
                      onChange={(e) => setApps(apps.map(a => a.id === app.id ? { ...a, notes: e.target.value } : a))}
                      onBlur={(e) => handleNotesChange(app.id, e.target.value)}
                      className="mt-2 text-xs bg-surface-container-lowest border border-outline-variant rounded p-1 w-full resize-none outline-none focus:border-primary"
                      rows={2}
                    />

                    <div className="flex justify-between items-center mt-3 pt-2 border-t border-outline-variant/50">
                      <span className="text-[10px] text-on-surface-variant">{new Date(app.applied_date).toLocaleDateString()}</span>
                      <select 
                        value={app.status} 
                        onChange={(e) => handleStatusChange(app.id, e.target.value)}
                        className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded outline-none cursor-pointer"
                      >
                        {['Saved', 'Applied', 'Interview', 'Selected', 'Rejected'].map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden">
          <table className="w-full text-left border-collapse min-w-[600px]">
            <thead className="bg-surface-container-low text-xs uppercase tracking-wider text-on-surface-variant">
              <tr>
                <th className="p-md font-bold">Company</th>
                <th className="p-md font-bold">Position</th>
                <th className="p-md font-bold">Status</th>
                <th className="p-md font-bold">Date Applied</th>
                <th className="p-md font-bold">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {loading ? (
                <tr><td colSpan="5" className="p-md text-center"><span className="animate-pulse">Loading...</span></td></tr>
              ) : (
                apps.map(app => (
                  <tr key={app.id} className="hover:bg-surface-container-low transition-colors">
                    <td className="p-md font-bold">{app.opportunity?.company || 'Unknown'}</td>
                    <td className="p-md">
                      {app.opportunity ? (
                        <Link to={`/app/opportunities/${app.opportunity.id}`} className="hover:text-primary transition-colors flex items-center gap-1">
                          {app.opportunity.title}
                          <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                        </Link>
                      ) : 'Unknown Job'}
                    </td>
                    <td className="p-md">
                      <select 
                        value={app.status} 
                        onChange={(e) => handleStatusChange(app.id, e.target.value)}
                        className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold outline-none cursor-pointer"
                      >
                        {['Saved', 'Applied', 'Interview', 'Selected', 'Rejected'].map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    </td>
                    <td className="p-md text-sm">{new Date(app.applied_date).toLocaleDateString()}</td>
                    <td className="p-md">
                      <input 
                        type="text"
                        placeholder="Add note..."
                        value={app.notes || ''}
                        onChange={(e) => setApps(apps.map(a => a.id === app.id ? { ...a, notes: e.target.value } : a))}
                        onBlur={(e) => handleNotesChange(app.id, e.target.value)}
                        className="text-xs bg-transparent border-b border-transparent focus:border-primary w-full outline-none"
                      />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
