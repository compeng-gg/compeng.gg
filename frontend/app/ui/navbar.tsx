'use client';

import Link from 'next/link';
import LogoutButton from '@/app/ui/logout-button';

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between flex-wrap bg-zinc-900 p-2">
      <div className="flex items-center flex-shrink-0 text-white mr-6">
        <Link href="/" className="font-black text-xl tracking-tight">CompEng.gg</Link>
      </div>
      <div className="block lg:hidden">
        <button className="flex items-center px-3 py-2 border rounded text-zinc-200 border-zinc-800 hover:text-white hover:border-white">
          <svg className="fill-current h-3 w-3" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><title>Menu</title><path d="M0 3h20v2H0V3zm0 6h20v2H0V9zm0 6h20v2H0v-2z"/></svg>
        </button>
      </div>
      <div className="w-full block flex-grow lg:flex lg:items-center lg:w-auto">
        <div className="text-sm lg:flex-grow">
          <Link href="/settings/" className="block mt-4 lg:inline-block lg:mt-0 text-zinc-100 hover:text-white mr-4">
            Settings
          </Link>
        </div>
        <div>
          <LogoutButton />
        </div>
      </div>
    </nav>
  );
}
