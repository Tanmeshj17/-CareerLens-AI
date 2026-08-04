import React from 'react';

export const Input = React.forwardRef(({ 
  label,
  error,
  helperText,
  id,
  className = '',
  ...props 
}, ref) => {
  const inputId = id || Math.random().toString(36).substring(2, 9);
  
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-on-surface mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          ref={ref}
          id={inputId}
          className={`block w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:cursor-not-allowed disabled:bg-surface-container-low transition-colors
            ${error 
              ? 'border-error text-error placeholder:text-error/60 focus:border-error focus:ring-error/20' 
              : 'border-outline-variant text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-primary/20'
            }`}
          {...props}
        />
      </div>
      {(error || helperText) && (
        <p className={`mt-1.5 text-xs font-medium ${error ? 'text-error' : 'text-on-surface-variant'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';
