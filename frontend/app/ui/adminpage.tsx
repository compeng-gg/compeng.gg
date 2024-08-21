import React, { useState } from 'react';
import { useRouter } from 'next/router';

interface ProgressTrackerProps {
  testcasespassed: number; 
  totaltestcases: number;
  title: string;
  date: Date;
}

function AdminPage() {
  const [testcasesPassed, setTestcasesPassed] = useState<number>(0);
  const [totalTestcases, setTotalTestcases] = useState<number>(100);
  const [title, setTitle] = useState<string>('Lab');
  const [date, setDate] = useState<Date>(new Date(2003, 11, 4));
  const router = useRouter();

  const handleSave = () => {
    console.log({ testcasesPassed, totalTestcases, title, date });
    router.push('/');
  };

  return (
    <div className="p-4 bg-gray-800 min-h-screen text-white">
      <h1 className="text-3xl font-bold mb-4">Update Progress Tracker</h1>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold">Test Cases Passed:</label>
          <input
            type="number"
            value={testcasesPassed}
            onChange={(e) => setTestcasesPassed(Number(e.target.value))}
            className="px-2 py-1 rounded bg-gray-700"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold">Total Test Cases:</label>
          <input
            type="number"
            value={totalTestcases}
            onChange={(e) => setTotalTestcases(Number(e.target.value))}
            className="px-2 py-1 rounded bg-gray-700"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold">Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="px-2 py-1 rounded bg-gray-700"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold">Date:</label>
          <input
            type="date"
            value={date.toISOString().split('T')[0]} // Format to YYYY-MM-DD
            onChange={(e) => setDate(new Date(e.target.value))}
            className="px-2 py-1 rounded bg-gray-700"
          />
        </div>
        <button
          onClick={handleSave}
          className="bg-blue-500 px-4 py-2 rounded text-white hover:bg-blue-600"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
}

export default AdminPage;
