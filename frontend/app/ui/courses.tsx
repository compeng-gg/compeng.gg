import Link from 'next/link';
import React from 'react';

interface Offering {
  slug: string;
  name: string;
}

const offerings: Offering[] = [
  { slug: 'course1', name: 'APS105' },
  { slug: 'course2', name: 'ECE344' },
];

function Courses() {
  return (
    <>
      <h2 className="text-3xl font-bold mb-4">Courses</h2>
      <div className="p-4 rounded-lg shadow-lg bg-zinc-900 w-full space-y-4">
        {offerings.length > 0 ? (
          offerings.map((offering, i) => (
            <div key={i} className="p-4 mb-4 bg-zinc-800 rounded-lg">
              <Link href={`/${offering.slug}/`} className="text-blue-500 hover:underline">
              <p className="text-2xl mb-1 text-blue-500 font-bold">{offering.name}</p>
              </Link>
              some info here 
            </div>
          ))
        ) : (
          <p className="text-gray-500">No current courses</p>
        )}
      </div>
    </>
  );
}

export default Courses;