import Link from 'next/link';
import React from 'react';

interface Offering {
  slug: string;
  name: string;
}

const offerings: Offering[] = [
  { slug: 'course1', name: 'Course 1' },
  { slug: 'course2', name: 'Course 2' },
];

function Courses() {
  return (
    <>
      <h2 className="text-2xl font-bold mb-4">Courses</h2>
      <ul>
        {offerings.map((offering, i) => (
          <li key={i}>
            <Link href={`/${offering.slug}/`} className="text-blue-500 hover:underline">
              {offering.name}
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}

export default Courses;
