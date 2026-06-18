import React from 'react';

export const ImageFallback: React.FC = () => {
    return (
        <div className="w-full h-48 flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-800 text-gray-400 p-4 select-none border border-dashed border-gray-300 dark:border-gray-600 rounded-md">
            <svg 
                className="w-12 h-12 mb-3 text-gray-400 dark:text-gray-500" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24" 
                xmlns="http://www.w3.org/2000/svg"
            >
                <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={1.5} 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
                />
            </svg>
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                Image Preview Unavailable
            </span>
            <span className="text-xs text-gray-400 dark:text-gray-500 mt-1 text-center">
                The visual content could not be loaded.
            </span>
        </div>
    );
};
