import React from 'react';
import 'primeicons/primeicons.css';
import 'primereact/resources/themes/lara-light-blue/theme.css';
import { PrimeReactProvider } from 'primereact/api';

//This component will import prime styling and ensure tailwind does not affect the components
export default function PrimeWrapper({children}: {
    children: React.ReactNode
}) {
    return (
        <div className="prime-container">
            {children}
        </div>
    );
}