import React from 'react';

interface PageLoaderProps {
  message?: string;
}

const PageLoader: React.FC<PageLoaderProps> = ({ message = 'सुरक्षित डैशबोर्ड लोड हो रहा है…' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center text-slate-300">
      <div className="w-12 h-12 border-4 border-[#8BF5E6]/40 border-t-[#8BF5E6] rounded-full animate-spin" aria-label="Loading" />
      <p className="text-sm font-hindi">{message}</p>
    </div>
  );
};

export default PageLoader;
