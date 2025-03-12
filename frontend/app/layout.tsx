import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

import JwtProvider from '@/app/lib/jwt-provider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: {
        template: '%s - CompEng.gg',
        default: 'CompEng.gg',
    },
    description: 'A site to learn coding.',
};

export default function RootLayout({
    children,
}: Readonly<{
  children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <JwtProvider>{children}</JwtProvider>
            </body>
        </html>
    );
}
