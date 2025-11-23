import React from 'react';

interface PageWrapperProps {
  title?: string;
  children: React.ReactNode;
}

const PageWrapper: React.FC<PageWrapperProps> = ({ title, children }) => {
  return (
    <section className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl backdrop-blur-xl space-y-4">
      {title ? <h2 className="text-2xl font-bold text-white font-hindi">{title}</h2> : null}
      {children}
    </section>
  );
};

export default PageWrapper;
