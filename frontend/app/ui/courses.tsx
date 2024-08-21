import Link from 'next/link';
import React from 'react';
import { useState } from 'react';
import ProgressTracker from './progress';

interface Offering {
  slug: string;
  name: string;
}

const offerings: Offering[] = [
  { slug: 'course1', name: 'APS105' },
  { slug: 'course2', name: 'ECE344' },
];

//const done: 

function Courses() {
  const [clickedIndex, setClickedIndex] = useState<number | null>(null);

  const handleClick = (index: number) => {
    setClickedIndex(index);
  };

  return (
    <>
      <h2 className="text-3xl font-bold mb-4">Courses</h2>
     
      {offerings.length > 0 ? (
        offerings.map((offering, i) => (
          <div key={i} className={`p-4 mb-4 bg-zinc-900 border border-gray-600 rounded-xl transition-transform duration-300 ${clickedIndex === i ? 'scale-95' : 'scale-100'}`}
            onClick={() => handleClick(i)}>
            <Link href={`/${offering.slug}/`} className="text-blue-500 hover:underline">
              <p className="text-2xl mb-1 text-blue-500 font-bold">{offering.name}</p>
            </Link>
            <p className="text-sm">Lab Progress:</p>
            {<ProgressTracker progress={40} title={''}/>}
            <p className="text-sm">Lab Due: </p>
          </div>
        ))
      ) : (
        <p className="text-gray-500">No current courses</p>
      )}
    </>
  );
}


export default Courses;