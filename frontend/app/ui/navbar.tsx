'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import LogoutButton from '@/app/ui/logout-button';

export default function Navbar() {
  // const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  // const dropdownTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  // const dropdownRef = useRef<HTMLDivElement>(null);  

  // const toggleDropdown = () => {
  //   setIsDropdownOpen((prevState) => !prevState); //chnage state, toggle
  // };

  // const openDropdown = () => {
  //   if (dropdownTimeoutRef.current) {
  //     clearTimeout(dropdownTimeoutRef.current); //c
  //     dropdownTimeoutRef.current = null;
  //   }
  //   setIsDropdownOpen(true);
  // };

  // const closeDropdown = () => {
  //   dropdownTimeoutRef.current = setTimeout(() => {
  //     setIsDropdownOpen(false);
  //   }, 300);
  // };

  // const handleMouseEnter = () => {
  //   if (dropdownTimeoutRef.current) {
  //     clearTimeout(dropdownTimeoutRef.current);
  //     dropdownTimeoutRef.current = null;
  //   }
  //   openDropdown();
  // };

  // const handleMouseLeave = () => {
  //   closeDropdown();
  // };

  // useEffect(() => {
  //   function handleClickOutside(event: MouseEvent) {
  //     if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
  //       setIsDropdownOpen(false);
  //     }
  //   }

  //   document.addEventListener('mousedown', handleClickOutside);

  //   return () => {
  //     document.removeEventListener('mousedown', handleClickOutside);
  //   };
  // }, []);

  return (
    <nav className="flex items-center justify-between flex-wrap bg-zinc-900 transition-colors duration-200 ease-in-out p-2 relative hover:bg-zinc-800">
      <div className="items-center flex-shrink-0 text-white mr-6 transition transform active:scale-95">
        <Link href="/" className="font-black text-xl tracking-tight">CompEng.gg</Link>
      </div>

      <div className="relative ml-auto">
        <button 
          className="flex items-center justify-center w-8 h-8 rounded-full border border-zinc-800 text-zinc-200 hover:text-white hover:border-white transition transform active:scale-95"
          // onClick={toggleDropdown}
          // onMouseEnter={handleMouseEnter}
          // onMouseLeave={handleMouseLeave}
        >
          <svg className="fill-current h-5 w-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <title>Profile</title>
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-3.31 0-6 2.69-6 6v1h12v-1c0-3.31-2.69-6-6-6z"/>
          </svg>
        </button>
        {/* {isDropdownOpen &&  */
        (
          <div 
            //ref={dropdownRef} 
            className="absolute right-0 mt-2 w-48 bg-zinc-800 rounded-lg shadow-lg flex flex-col items-center transition transform active:scale-95">
            <Link href="/settings/" className="w-full px-4 py-2 text-zinc-100 text-center hover:bg-zinc-700 transition transform active:scale-95">
              Settings
            </Link>
            <LogoutButton />
          </div>
        )}
      </div>
    </nav>
  );
}
