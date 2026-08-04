import React from 'react';

export const Card = ({ children, className = '', onClick, hoverable = false, ...props }) => {
  return (
    <div 
      className={`bg-white rounded-xl border border-outline-variant overflow-hidden 
        ${hoverable || onClick ? 'transition-all hover:shadow-md hover:border-primary/40 cursor-pointer' : 'shadow-sm'} 
        ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-outline-variant/30 ${className}`}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold text-on-surface m-0 ${className}`}>
    {children}
  </h3>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`px-6 py-4 bg-surface-container-low border-t border-outline-variant/30 flex items-center ${className}`}>
    {children}
  </div>
);
