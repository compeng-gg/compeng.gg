'use client';

import { useContext, useEffect, useState } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';

import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import H3 from '@/app/ui/h3';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Table from '@/app/ui/table';

const userFields: [string, string][] = [
  ['id', 'ID'],
  ['username', 'Username'],
  ['email', 'Email'],
  ['first_name', 'First Name'],
  ['last_name', 'Last Name'],
  ['discord', 'Discord'],
  ['github', 'GitHub'],
]

function AdminPage() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [users, setUsers] = useState<any[]>([]);
  const [semesters, setSemesters] = useState<any[]>([]);
  const [openSemesters, setOpenSemesters] = useState<Record<string, boolean>>({});

  const fetchData = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, "users/", "GET");
      const data = await response.json();
      const transformedData = data.map((item: any) => {
        const newItem: any = {
          id: item.id,
          username: item.username,
          email: item.email,
          first_name: item.first_name,
          last_name: item.last_name,
        };
        item.social_auth.forEach((auth: any) => {
          newItem[auth.provider] = auth.uid;
        });
        return newItem;
      });
      setUsers(transformedData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchSemesters = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, 'semesters/', 'GET');
      const data = await response.json();
      setSemesters(data);
    } catch (error) {
      console.error('Error fetching semesters:', error);
    }
  };

  useEffect(() => {
    fetchData();
    fetchSemesters();
  }, []);

  const handleCourseClick = async (course_slug: string, semester_slug: string) => {
    try {
      const instructor = prompt('Enter instructor UTORid:');
      if (!instructor) return;
      const response = await fetchApi(jwt, setAndStoreJwt, 'create-offering/', 'POST', {
        course_slug: course_slug,
        semester_slug: semester_slug,
        instructor: instructor,
      });
      if (response.ok) {
        alert(`Added offering: ${course_slug} (${semester_slug})`);
      }
      else {
        alert(`Bad request.`);
      }
    } catch (error) {
      console.error('Error adding offering:', error);
    }
  };

  const toggleSemester = (slug: string) => {
    setOpenSemesters((prev) => ({
      ...prev,
      [slug]: !prev[slug],
    }));
  };

  return (
    <>
      <Navbar />
      <Main>
        <H1>Admin</H1>
        <H2>Create Offerings</H2>
        {semesters.map((semester) => {
          const isOpen = openSemesters[semester.slug] ?? false;
          return (
            <div key={semester.slug} className="mb-4">
              <h3
                onClick={() => toggleSemester(semester.slug)}
                className="cursor-pointer hover:underline"
              >
                {semester.name} {isOpen ? '▲' : '▼'}
              </h3>
              {isOpen && (
                <ul className="list-disc list-inside pl-2">
                  {semester.courses.map((course: any) => (
                    <li key={course.slug}>
                      <button
                        className="text-blue-600 hover:underline"
                        onClick={() =>
                          handleCourseClick(course.slug, semester.slug)
                        }
                      >
                        {course.name}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
        <H2>Users</H2>
        <Table fields={userFields} data={users} />
      </Main>
    </>
  );

}

export default function Page() {
  return (
    <LoginRequired>
      <AdminPage />
    </LoginRequired>
  );
}
