import React from 'react';

export const Alert = ({ type = 'error', message, action }) => {
  const styles = {
    error: 'bg-error/10 border-error/20 text-error',
    success: 'bg-success/10 border-success/20 text-success',
    info: 'bg-info/10 border-info/20 text-info',
    warning: 'bg-warning/10 border-warning/20 text-warning',
  };
  
  const icons = {
    error: 'error',
    success: 'check_circle',
    info: 'info',
    warning: 'warning',
  };

  return (
    <div className={`mb-4 p-3 border rounded-lg flex items-start gap-3 animate-fade-in-up ${styles[type]}`}>
      <span className="material-symbols-outlined text-[20px] shrink-0 mt-0.5">{icons[type]}</span>
      <div className="flex-1">
        <p className="text-sm font-medium leading-relaxed">{message}</p>
        {action && <div className="mt-2">{action}</div>}
      </div>
    </div>
  );
};
