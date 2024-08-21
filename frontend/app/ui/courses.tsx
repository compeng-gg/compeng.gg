import Link from 'next/link';
import React from 'react';
import { useState } from 'react';
import ProgressTracker from './progress';
import { stringify } from 'querystring';

interface Offering {
  slug: string;
  name: string;
}

const offerings: Offering[] = [
  { slug: 'course1', name: 'APS105' },
  { slug: 'course2', name: 'ECE344' },
];

function Courses() {
  const [clickedIndex, setClickedIndex] = useState<number | null>(null);

  const handleClick = (index: number) => {
    setClickedIndex(index);
  };

  const dueDate = new Date(2003, 11, 4); //random date added

  return (
    <>
      <h2 className="text-3xl font-bold mb-4">Courses</h2>
     
      {offerings.length > 0 ? (
        offerings.map((offering, i) => (
          <div
            key={i}
            className={`p-4 mb-4 bg-zinc-900 border border-gray-600 rounded-xl transition-colors duration-300 ease-in-out p-2 relative hover:bg-zinc-800 ${clickedIndex === i ? 'scale-95' : 'scale-100'}`}
            onClick={() => handleClick(i)}
          >
            <Link href={`/${offering.slug}/`} className="text-blue-500 hover:underline">
              <p className="text-2xl mb-1 text-blue-500 font-bold">{offering.name}</p>
            </Link>
            <ProgressTracker
              testcasespassed={40}
              totaltestcases={100}
              title="Lab"
              date={dueDate} 
            />
            <div className="flex justify-between items-center">
              <p className="text-sm font-semibold text-gray-100 mb-1">Lab Due:</p>
              <p className="text-sm font-semibold text-gray-100 mb-1">
                {dueDate.toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit'
                })}
              </p>
            </div>
          </div>
        ))
      ) : (
        <p className="text-gray-500">No current courses</p>
      )}
    </>
  );
}

export default Courses;