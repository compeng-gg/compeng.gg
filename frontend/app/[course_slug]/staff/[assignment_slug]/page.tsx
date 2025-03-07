'use client';

import { useEffect, useState, useContext, Fragment } from 'react';
import { useParams } from 'next/navigation';

import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import H3 from '@/app/ui/h3';
import Link from 'next/link';

import LoginRequired from '@/app/lib/login-required';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

function StaffAssignment() {
  const params = useParams<{ course_slug: string, assignment_slug: string }>();
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [data, setData] = useState<any>({});
  const [loading, setLoading] = useState<string | null>(null); // To track which student's button is loading
  const [daysInput, setDaysInput] = useState<{ [key: string]: number }>({}); // Tracks input for each student
  const [isToggling, setIsToggling] = useState(false);

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/staff/${params.assignment_slug}/`, "GET");
        const data = await response.json();
        setData(data);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    fetchLabs();
  }, [params.course_slug, jwt, setAndStoreJwt]);

  const handleTogglePrivateRelease = async () => {
    try {
      setIsToggling(true);
      const newStatus = !data.is_private_released;
      const response = await fetchApi(
        jwt,
        setAndStoreJwt,
        `courses/${params.course_slug}/staff/${params.assignment_slug}/private-release/`,
        'POST',
        { is_private_released: newStatus }
      );
      if (response.ok) {
        setData((prevData: any) => ({
          ...prevData,
          is_private_released: newStatus,
        }));
        alert(`Private release status updated to ${newStatus ? 'true' : 'false'}.`);
      } else {
        console.error('Failed to toggle private release:', await response.text());
        alert('Failed to toggle private release status.');
      }
    } catch (error) {
      console.error('Error toggling private release:', error);
      alert('An error occurred while toggling private release.');
    } finally {
      setIsToggling(false);
    }
  };

  const handleAccommodation = async (username: string) => {
    const days = daysInput[username] ?? (data.students.find((s: any) => s.username === username)?.accommodation ?? 0);

    if (days < 0) {
      alert('Please enter a valid number of days.');
      return;
    }
  
    try {
      setLoading(username); // Indicate which button is loading
      const postData = { username, days };
      const response = await fetchApi(
        jwt,
        setAndStoreJwt,
        `courses/${params.course_slug}/staff/${params.assignment_slug}/accommodation/`,
        'POST',
        postData
      );
      if (response.ok) {
        const updatedStudent = await response.json();
        setData((prevData: any) => ({
          ...prevData,
          students: prevData.students.map((student: any) =>
            student.username === username ? { ...student, ...updatedStudent } : student
          ),
        }));
        alert(`Accommodation granted for ${username} for ${days} days.`);
      } else {
        console.error('Failed to update accommodation:', await response.text());
        alert('Failed to grant accommodation.');
      }
    } catch (error) {
      console.error('Error during accommodation POST:', error);
      alert('An error occurred.');
    } finally {
      setLoading(null); // Reset loading state
    }
  };

  const handleInputChange = (username: string, value: string) => {
    const parsedValue = parseInt(value, 10);
    setDaysInput((prev) => ({
      ...prev,
      [username]: isNaN(parsedValue) ? 0 : parsedValue,
    }));
  };


  if (Object.keys(data).length === 0) {
    return (
      <>
        <Navbar />
        <Main>
          <></>
        </Main>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Main>
        <H1>{ data.offering} Staff</H1>
        <H2>{ data.name }</H2>
        <p>Students with submissions: { data.students_with_submissions_count }/{ data.students_count }</p>
        <p>Private released: {data.is_private_released ? 'true' : 'false'}
          <button
            className={`px-4 py-2 rounded ${
              data.is_private_released
                ? 'bg-green-500 hover:bg-red-600 text-white text-sm'
                : 'bg-red-500 hover:bg-greeb-600 text-white text-sm'
            }`}
            onClick={handleTogglePrivateRelease}
            disabled={isToggling}
          >
            {isToggling
              ? 'Processing...'
              : data.is_private_released
              ? 'Revoke'
              : 'Release'}
          </button>
        </p>

        <table key="table" className="table-auto">
          <thead className="bg-slate-300 dark:bg-slate-700">
            <tr>
              <th className="text-left border border-slate-500 p-2 text-sm">Username</th>
              <th className="text-left border border-slate-500 p-2 text-sm">Repository</th>
              <th className="text-left border border-slate-500 p-2 text-center text-sm">Overall Grade</th>
              <th className="text-left border border-slate-500 p-2 text-center text-sm">Submissions</th>
              <th className="text-left border border-slate-500 p-2 text-center text-sm">Late Submissions</th>
              <th className="text-left border border-slate-500 p-2 text-sm">Accommodation</th>
            </tr>
          </thead>
          <tbody>
          {data.students.map((student: any, rowIndex: any) => {
            const currentDays = daysInput[student.username] ?? student.accommodation ?? 0;
            const isGreen = currentDays > 0;

            return (
            <tr key={rowIndex}>
              <td className="text-left border border-slate-500 p-2 text-sm" >
                <Link href={`/${params.course_slug}/staff/${params.assignment_slug}/${student.username}/`} className="text-blue-500 hover:underline">
                  {student.username}
                </Link>
              </td>
              <td className="text-left border border-slate-500 p-2 text-sm" >
                  {student.repository_name === "" ? (
                  <span className="text-red-500">Missing</span>
                  ) : (
                  <Link href={`${student.repository_url}`} className="text-blue-500 hover:underline">{ student.repository_name }</Link>
                  )}
              </td>
              <td className="text-left border border-slate-500 p-2 text-center text-sm" >
                {student.overall_grade}
                  {student.graded_commit_url !== "" && (
                    <>
                      {' '}<Link href={`${student.graded_commit_url}`} className="text-blue-500 hover:underline">Commit</Link>
                    </>
                  )}
              </td>
              <td className="text-left border border-slate-500 p-2 text-center text-sm" >{student.submissions}</td>
              <td className="text-left border border-slate-500 p-2 text-center text-sm" >{student.late_submissions}</td>
              <td className="text-left border border-slate-500 p-2 text-sm">
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        className={`border border-gray-300 dark:border-gray-600 p-1 rounded w-16 bg-white dark:bg-gray-800 ${
                          isGreen ? 'text-green-500' : 'text-gray-900 dark:text-gray-200'
                        }`}
                        value={currentDays}
                        onChange={(e) => handleInputChange(student.username, e.target.value)}
                      />
                      <button
                        className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600 disabled:bg-gray-400 dark:disabled:bg-gray-600"
                        onClick={() => handleAccommodation(student.username)}
                        disabled={loading === student.username}
                      >
                        {loading === student.username ? 'Processing...' : 'Grant'}
                      </button>
                    </div>
                  </td>
            </tr>
          )})}
          </tbody>
        </table>
      </Main>
    </>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <StaffAssignment />
    </LoginRequired>
  );
}
