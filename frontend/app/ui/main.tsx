import React from 'react';

interface MainProps {
  children: React.ReactNode;
  className?: string; 
}

const Main: React.FC<MainProps> = ({ children, className = '' }) => {
  return (
    <main className={`container mx-auto p-4 space-y-4 ${className}`}>
      {children}
    </main>
  );
};

export default Main;
