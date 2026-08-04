import React from 'react';

export const Skeleton = ({ className = '', ...props }) => {
  return (
    <div
      className={`animate-pulse bg-surface-container-high rounded ${className}`}
      {...props}
    />
  );
};
