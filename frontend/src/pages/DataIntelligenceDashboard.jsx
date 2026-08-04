import React, { useState, useEffect } from 'react';
import { API_BASE, getToken } from '../api';
import { Skeleton } from '../components/ui/Skeleton';
import { Alert } from '../components/ui/Alert';
import { Button } from '../components/ui/Button';

async function apiCall(path) {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { 'Authorization': `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export default function DataIntelligenceDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchIntelligence();
  }, []);

  const fetchIntelligence = async () => {
    try {
      setLoading(true);
      const res = await apiCall('/api/intelligence/collectors');
      setData(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to load data intelligence metrics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-[1400px] mx-auto p-lg lg:p-xl space-y-xl animate-fade-in">
        <Skeleton className="h-20 w-1/3" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
          {[1,2,3,4].map(i => <Skeleton key={i} className="h-32 w-full rounded-2xl" />)}
        </div>
        <Skeleton className="h-64 w-full rounded-3xl" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-[1400px] mx-auto p-lg lg:p-xl">
        <Alert 
          type="error" 
          message={error || 'Failed to load intelligence data.'} 
          action={<Button variant="ghost" size="sm" onClick={fetchIntelligence} className="font-bold underline">Retry</Button>}
        />
      </div>
    );
  }

  const { summary, collectors, alerts } = data;

  const getTierColor = (tier) => {
    switch (tier) {
      case 'Tier A': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'Tier B': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'Tier C': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'Tier D': return 'bg-red-500/10 text-red-500 border-red-500/20';
      default: return 'bg-surface-variant text-on-surface-variant border-outline';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'bg-emerald-500';
      case 'Degraded': return 'bg-amber-500';
      case 'Paused': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return <span className="material-symbols-outlined text-emerald-500 text-sm font-bold">trending_up</span>;
      case 'down': return <span className="material-symbols-outlined text-red-500 text-sm font-bold">trending_down</span>;
      default: return <span className="material-symbols-outlined text-gray-500 text-sm font-bold">trending_flat</span>;
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto p-lg lg:p-xl space-y-xl animate-fade-in pb-24">
      {/* Header Section */}
      <div>
        <div className="flex items-center gap-sm text-primary mb-2">
          <span className="material-symbols-outlined text-3xl">monitor_heart</span>
          <h1 className="text-3xl font-[Geist] font-bold">Data Intelligence OS</h1>
        </div>
        <p className="text-on-surface-variant text-lg max-w-3xl">
          Real-time telemetry and predictive health scoring for the Opportunity Acquisition pipeline.
        </p>
      </div>

      {/* Global Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
        {/* Metric Card 1 */}
        <div className="bg-surface-container rounded-2xl p-lg border border-outline-variant shadow-sm flex items-center justify-between group hover:border-primary/50 transition-colors">
          <div>
            <p className="text-sm font-medium text-on-surface-variant uppercase tracking-wider font-[Geist]">Active Collectors</p>
            <div className="flex items-baseline gap-xs mt-1">
              <span className="text-4xl font-bold text-on-surface">{summary.total_collectors}</span>
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-2xl">device_hub</span>
          </div>
        </div>

        {/* Metric Card 2 */}
        <div className="bg-surface-container rounded-2xl p-lg border border-outline-variant shadow-sm flex items-center justify-between group hover:border-primary/50 transition-colors">
          <div>
            <p className="text-sm font-medium text-on-surface-variant uppercase tracking-wider font-[Geist]">Avg Pipeline Score</p>
            <div className="flex items-baseline gap-xs mt-1">
              <span className="text-4xl font-bold text-on-surface">{summary.avg_score.toFixed(1)}</span>
              <span className="text-sm font-medium text-on-surface-variant">/ 100</span>
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-2xl">speed</span>
          </div>
        </div>

        {/* Metric Card 3 */}
        <div className="bg-surface-container rounded-2xl p-lg border border-outline-variant shadow-sm flex items-center justify-between group hover:border-primary/50 transition-colors">
          <div>
            <p className="text-sm font-medium text-on-surface-variant uppercase tracking-wider font-[Geist]">Tier A Sources</p>
            <div className="flex items-baseline gap-xs mt-1">
              <span className="text-4xl font-bold text-on-surface">{summary.tier_a}</span>
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-2xl">military_tech</span>
          </div>
        </div>

        {/* Metric Card 4 */}
        <div className="bg-surface-container rounded-2xl p-lg border border-outline-variant shadow-sm flex items-center justify-between group hover:border-error/50 transition-colors">
          <div>
            <p className="text-sm font-medium text-on-surface-variant uppercase tracking-wider font-[Geist]">Active Alerts</p>
            <div className="flex items-baseline gap-xs mt-1">
              <span className="text-4xl font-bold text-on-surface">{summary.active_alerts}</span>
            </div>
          </div>
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform ${summary.active_alerts > 0 ? 'bg-error-container text-on-error-container' : 'bg-surface-variant text-on-surface-variant'}`}>
            <span className="material-symbols-outlined text-2xl">warning</span>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-xl">
        
        {/* Left Column: Collectors Table */}
        <div className="xl:col-span-2 space-y-lg">
          <div className="bg-surface-container rounded-3xl border border-outline-variant shadow-sm overflow-hidden flex flex-col">
            <div className="p-lg border-b border-outline-variant bg-surface/50 flex justify-between items-center">
              <h2 className="text-xl font-bold text-on-surface font-[Geist] flex items-center gap-sm">
                <span className="material-symbols-outlined text-primary">router</span>
                Collector Fleet Telemetry
              </h2>
              <span className="text-xs font-medium bg-surface-variant text-on-surface-variant px-sm py-1 rounded-full uppercase tracking-wider">
                Adaptive Scheduler Active
              </span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-surface-variant/30 text-on-surface-variant text-xs uppercase tracking-wider font-medium font-[Geist]">
                    <th className="p-md pl-lg font-medium">Collector</th>
                    <th className="p-md font-medium text-center">Health</th>
                    <th className="p-md font-medium text-right">Score</th>
                    <th className="p-md font-medium text-right">Yield</th>
                    <th className="p-md font-medium text-right">Interval</th>
                    <th className="p-md font-medium text-center">Trend</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/50 text-sm">
                  {collectors.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="p-xl text-center text-on-surface-variant">
                        No collectors deployed yet.
                      </td>
                    </tr>
                  ) : collectors.map((c) => (
                    <tr key={c.collector} className="hover:bg-surface-variant/20 transition-colors">
                      <td className="p-md pl-lg">
                        <div className="flex items-center gap-sm">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(c.status)}`} title={c.status}></div>
                          <div>
                            <p className="font-bold text-on-surface">{c.collector}</p>
                            <p className="text-xs text-on-surface-variant uppercase tracking-wider">{c.ats_type}</p>
                          </div>
                        </div>
                      </td>
                      <td className="p-md">
                        <div className="flex justify-center">
                          <span className={`px-sm py-1 rounded-full text-xs font-bold border ${getTierColor(c.tier)}`}>
                            {c.tier}
                          </span>
                        </div>
                      </td>
                      <td className="p-md text-right font-medium">
                        <div className="flex flex-col items-end">
                          <span className="text-on-surface">{c.score?.toFixed(1) || '0.0'}</span>
                          <span className="text-xs text-on-surface-variant">S: {c.stability?.toFixed(1) || '0'}</span>
                        </div>
                      </td>
                      <td className="p-md text-right">
                        <div className="flex flex-col items-end">
                          <span className="text-on-surface font-medium">{c.jobs_today || 0} today</span>
                          <span className="text-xs text-on-surface-variant">{c.active_jobs || 0} active</span>
                        </div>
                      </td>
                      <td className="p-md text-right">
                        <span className="font-[Geist] font-medium text-primary">
                          {c.adaptive_interval_hours ? `${c.adaptive_interval_hours.toFixed(1)}h` : '-'}
                        </span>
                      </td>
                      <td className="p-md">
                        <div className="flex justify-center">
                          {getTrendIcon(c.trend)}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: Alerts & Live Events */}
        <div className="space-y-lg">
          <div className="bg-surface-container rounded-3xl border border-outline-variant shadow-sm overflow-hidden">
            <div className="p-lg border-b border-outline-variant bg-surface/50 flex justify-between items-center">
              <h2 className="text-xl font-bold text-on-surface font-[Geist] flex items-center gap-sm">
                <span className="material-symbols-outlined text-error">crisis_alert</span>
                System Alerts
              </h2>
              {alerts.length > 0 && (
                <span className="bg-error text-on-error text-xs font-bold px-2 py-1 rounded-full">
                  {alerts.length}
                </span>
              )}
            </div>
            
            <div className="p-md space-y-sm max-h-[500px] overflow-y-auto custom-scrollbar">
              {alerts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-xl text-on-surface-variant opacity-70">
                  <span className="material-symbols-outlined text-4xl mb-sm">check_circle</span>
                  <p className="font-medium">All systems nominal.</p>
                </div>
              ) : (
                alerts.map((alert) => (
                  <div key={alert.id} className="bg-surface rounded-xl p-md border border-error/20 flex gap-md items-start shadow-sm">
                    <span className="material-symbols-outlined text-error mt-1">
                      {alert.severity === 'CRITICAL' ? 'gpp_bad' : 'warning'}
                    </span>
                    <div>
                      <div className="flex justify-between items-start gap-sm">
                        <p className="text-sm font-bold text-on-surface">{alert.collector}</p>
                        <span className="text-[10px] uppercase font-bold text-on-surface-variant/70 tracking-wider">
                          {new Date(alert.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-on-surface-variant mt-1">{alert.message}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
