import React from 'react';

export const Button = React.forwardRef(({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  isLoading = false,
  disabled,
  ...props 
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-primary text-on-primary hover:bg-primary/90 focus:ring-primary shadow-sm',
    secondary: 'bg-surface text-on-surface border border-outline-variant hover:bg-surface-container focus:ring-primary shadow-sm',
    danger: 'bg-error text-on-error hover:bg-error/90 focus:ring-error shadow-sm',
    ghost: 'bg-transparent text-on-surface hover:bg-surface-container focus:ring-primary',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      ref={ref}
      disabled={disabled || isLoading}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {isLoading && (
        <span className="material-symbols-outlined animate-spin mr-2 text-[18px]">
          progress_activity
        </span>
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';
