import React from 'react';

export const Badge = ({ 
  children, 
  variant = 'default',
  icon = null,
  className = '',
  ...props 
}) => {
  const variants = {
    default: 'bg-surface-container text-on-surface-variant border-outline-variant',
    primary: 'bg-primary/10 text-primary border-primary/20',
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    error: 'bg-error/10 text-error border-error/20',
    info: 'bg-info/10 text-info border-info/20',
  };

  return (
    <span 
      className={`inline-flex items-center gap-[3px] px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${variants[variant]} ${className}`}
      {...props}
    >
      {icon && (
        <span className="material-symbols-outlined text-[11px]">{icon}</span>
      )}
      {children}
    </span>
  );
};
