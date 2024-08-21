import React from 'react';

interface MainProps {
  children: React.ReactNode;
  className?: string; 
}

const Main: React.FC<MainProps> = ({ children, className = '' }) => {
  return (
    <main className={`p-12 space-y-4 ${className}`}>
      {children}
    </main>
  );
};

export default Main;
