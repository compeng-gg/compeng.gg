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

type AssignmentFormProps = {
  courseSlug: string;
  semesterSlug: string;
  onClose: () => void;
  refreshData: () => void;
};

function AssignmentForm({ courseSlug, semesterSlug, onClose, refreshData }: AssignmentFormProps) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  const [slug, setSlug] = useState('');
  const [name, setName] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [files, setFiles] = useState<string[]>(['']);
  const [publicTotal, setPublicTotal] = useState('');
  const [privateTotal, setPrivateTotal] = useState('');

  const handleFileChange = (index: number, value: string) => {
    const updatedFiles = [...files];
    updatedFiles[index] = value;
    setFiles(updatedFiles);
  };

  const addFileField = () => setFiles([...files, '']);
  const removeFileField = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, 'create-assignment/', 'POST', {
        course_slug: courseSlug,
        semester_slug: semesterSlug,
        slug,
        name,
        due_date: dueDate,
        files,
        public_total: parseFloat(publicTotal),
        private_total: parseFloat(privateTotal),
      });
      if (response.ok) {
        alert(`Created assignment "${name}" for ${courseSlug} (${semesterSlug})`);
        await refreshData();
        onClose();
      }
      else {
        alert('Bad request');
      }
    } catch (error) {
      console.error('Error creating assignment:', error);
    }
  };

  return (
    <div className="p-4 border rounded text-black bg-gray-50 mt-4">
      <h4 className="font-bold mb-2">Add Assignment</h4>
      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          className="border p-1 w-full"
          placeholder="Slug"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          required
        />
        <input
          className="border p-1 w-full"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          className="border p-1 w-full"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          required
        />

        <div>
          <label className="block font-medium">Files</label>
          {files.map((file, i) => (
            <div key={i} className="flex space-x-2 mb-1">
              <input
                className="border p-1 flex-1"
                placeholder="File path"
                value={file}
                onChange={(e) => handleFileChange(i, e.target.value)}
                required
              />
              {files.length > 1 && (
                <button
                  type="button"
                  className="text-red-500"
                  onClick={() => removeFileField(i)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            className="text-blue-600 mt-1"
            onClick={addFileField}
          >
            + Add path
          </button>
        </div>

        <input
          className="border p-1 w-full"
          placeholder="Public test case total"
          value={publicTotal}
          onChange={(e) => setPublicTotal(e.target.value)}
          required
        />
        <input
          className="border p-1 w-full"
          placeholder="Private test case total"
          value={privateTotal}
          onChange={(e) => setPrivateTotal(e.target.value)}
          required
        />

        <div className="flex space-x-2">
          <button type="submit" className="bg-blue-500 text-white px-3 py-1 rounded">
            Create
          </button>
          <button
            type="button"
            className="bg-gray-300 px-3 py-1 rounded"
            onClick={onClose}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

function Staff() {
  const params = useParams<{ course_slug: string }>();
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [data, setData] = useState<any>({});

  const [openAssignmentForm, setOpenAssignmentForm] = useState<{
    course: string;
    semester: string;
  } | null>(null);

  const fetchLabs = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/staff/`, "GET");
      const data = await response.json();
      setData(data);
    } catch (error) {
      console.error('Error fetching labs:', error);
    }
  }

  useEffect(() => {
    /*
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/staff/`, "GET");
        const data = await response.json();
        setData(data);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }*/

    fetchLabs();
  }, [params.course_slug, jwt, setAndStoreJwt]);

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
        <H2>Assignments</H2>

            <table key="table" className="table-auto">
              <thead className="bg-slate-300 dark:bg-slate-700">
                <tr>
                  <th className="text-left border border-slate-500 p-2 text-sm">Name</th>
                  <th className="text-left border border-slate-500 p-2 text-sm">Due Date</th>
                </tr>
              </thead>
              <tbody>
                {data.assignments.map((assignment: any, index: any) => (
                  <tr key={index}>
                    <td className="text-left border border-slate-500 p-2 text-sm" >
                      <Link href={`/${params.course_slug}/staff/${assignment.slug}/`} className="text-blue-500 hover:underline">{ assignment.name }</Link>
                    </td>
                    <td className="text-left border border-slate-500 p-2 text-sm" >{`${new Date(assignment.due_date)}`}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <button
              className="text-blue-600 hover:underline ml-2"
              onClick={() =>
                setOpenAssignmentForm({
                  course: data.course_slug,
                  semester: data.semester_slug,
                })
              }
            >
              + Add Assignment
            </button>
          {openAssignmentForm && (
            <AssignmentForm
              courseSlug={openAssignmentForm.course}
              semesterSlug={openAssignmentForm.semester}
              onClose={() => setOpenAssignmentForm(null)}
              refreshData={fetchLabs}
            />
          )}
      </Main>
    </>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <Staff />
    </LoginRequired>
  );
}
