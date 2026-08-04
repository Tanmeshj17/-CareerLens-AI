import React from 'react';
import { Button } from './Button';

export const EmptyState = ({ 
  icon = 'folder_open', 
  title = 'No Data Found', 
  description = 'There is currently no data to display.', 
  actionLabel, 
  onAction,
  className = ''
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-outline-variant border-dashed ${className}`}>
      <div className="w-16 h-16 bg-surface-container-high rounded-full flex items-center justify-center mb-4">
        <span className="material-symbols-outlined text-[32px] text-on-surface-variant">
          {icon}
        </span>
      </div>
      <h3 className="text-xl font-semibold text-on-surface mb-2">{title}</h3>
      <p className="text-sm text-on-surface-variant max-w-sm mb-6">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
