import React from 'react';

interface H2Props {
  children: React.ReactNode;
  className?: string; 
}

const H2: React.FC<H2Props> = ({ children, className = '' }) => {
  return (
    <h2 className={`font-semibold text-3xl ${className}`}>
      {children}
    </h2>
  );
};

export default H2;
