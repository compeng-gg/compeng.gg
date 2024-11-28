import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/components/navbar';
import Table from '@/app/ui/table';
import Link from 'next/link';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import { TabMenu } from 'primereact/tabmenu';
import StudentView from '../studentView/student-view';
import { Card } from 'primereact/card';
import StaffView from '../staffView/staff-view';
import { Console } from 'console';

export interface Lab {
  name: string;
  slug: string;
  due_date: Date;
  grade: number;
  tasks: any;
}

const taskFields: [string, string][] = [
  ['id', 'ID'],
  ['speedup', 'Speedup'],
]

// Role mapping based on Kind enum
const ROLE_MAP: Record<number, string> = {
  1: 'INSTRUCTOR',
  2: 'TA',
  3: 'STUDENT',
  4: 'AUDIT',
};


function Course({ params }: { params: { slug: string } }) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [name, setName] = useState();
  const [labs, setLabs] = useState([] as Lab[]);
  const [role, setRole] = useState<string | null>(null); // State to store user role
  const [loadingRole, setLoadingRole] = useState<boolean>(true); // State to track role loading

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.slug}/`, 'GET');
        const data = await response.json();
        setName(data.name);
        setLabs(data.assignments);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    async function fetchUserRole() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `offering/role/${params.slug}/`, 'GET');
        const data = await response.json();
        const roleString = ROLE_MAP[data.role]; // Map the integer role to a string
        setRole(roleString); // Save the role as a string
      } catch (error) {
        console.error('Error fetching user role:', error);
        setRole(null); // Reset role on error
      } finally {
        setLoadingRole(false); // Stop loading spinner for role
      }
    }

    fetchLabs();
    fetchUserRole();
  }, [params.slug, jwt, setAndStoreJwt]);

  console.log(params.slug);
  if (!name || loadingRole) {
    return (
      <>
        <Navbar />
        <Main>
          <></>
        </Main>
      </>
    );
  }

  if (!role) {
    return (
      <>
        <Navbar />
        <div>Error: Unable to determine your role. Please contact support.</div>
      </>
    );
  }

  const items = [
    { label: 'Assignments', icon: 'pi pi-list-check'},
    { label: 'Exercises', icons: 'pi pi-pencil'},

  ]

  //Temp value

  // const role = "Student";

  return (
    <>
      <Navbar />
      <Card>
        {role === 'STUDENT' ? (
          <StudentView courseName={name} labs={labs} courseSlug={params.slug} />
        ) : role === 'INSTRUCTOR' || role === 'TA' ? (
          <StaffView courseName={name} labs={labs} courseSlug={params.slug}/>
        ) : (
          <div>Unknown role: {role}</div>
        )}
      </Card>
    </>
  );

  // return (
  //   <>
  //     <Navbar />
  //     <Main>
  //       <H1>{name}</H1>

  //       {labs.map((assignment) => (
  //         <div
  //           key={assignment.slug}
  //           className="bg-gray-100 dark:bg-gray-900 shadow-md rounded-lg p-6 mb-6"
  //         >
  //           <h2 className="text-2xl font-semibold mb-2">{assignment.name}</h2>
  //           <p>
  //             Due: {`${new Date(assignment.due_date)}`}
  //           </p>
  //           <p>Current Grade: {assignment.grade}</p>

  //           {assignment.tasks && assignment.tasks.length > 0 && (
  //           <div className="border-t border-gray-500 pt-4 mt-4">
  //             <h3 className="text-xl font-semibold mb-3">Pushes:</h3>
  //             {assignment.tasks.map((task: any) => (
  //               <div
  //                 key={task.id}
  //                 className="bg-gray-200 dark:bg-gray-800 rounded-lg p-4 mb-4 shadow"
  //               >
  //                 <p>
  //                   <strong>Status:</strong>{' '}
  //                   {task.status === 'Success' ? (
  //                     <span className="text-green-600 font-semibold">{task.status}</span>
  //                   ) : task.status === 'Failure' ? (
  //                     <span className="text-red-600 font-semibold">{task.status}</span>
  //                   ) : (
  //                     task.status
  //                   )}
  //                 </p>
  //                 {task.grade && (
  //                   <p>
  //                     <strong>Grade:</strong> {task.grade}
  //                   </p>
  //                 )}
  //                 <p>
  //                   <strong>Repo:</strong>{' '}
  //                   <a
  //                     href={`https://github.com/compeng-gg/${task.repo}`}
  //                     className="text-blue-500 hover:underline"
  //                     target="_blank"
  //                     rel="noopener noreferrer"
  //                   >
  //                     {task.repo}
  //                   </a>
  //                 </p>
  //                 <p>
  //                   <strong>Commit:</strong> {task.commit}
  //                 </p>
  //                 <p>
  //                   <strong>Received:</strong>{' '}
  //                   {`${new Date(task.received)}`}
  //                 </p>

  //                 {task.result && task.result.tests &&
  //                 <div className="border-t border-gray-500 mt-4 pt-2">
  //                   <h4 className="font-semibold mb-2">Test Results:</h4>
  //                   {task.result.tests.map((test:any, index:any) => (
  //                     <div
  //                       key={index}
  //                       className="bg-white dark:bg-black p-3 rounded-lg shadow-sm mb-2"
  //                     >
  //                       <p>
  //                         <strong>Test:</strong> {test.name}
  //                       </p>
  //                       <p>
  //                         <strong>Weight:</strong> {test.weight}
  //                       </p>
  //                       <p>
  //                         <strong>Result:</strong>{' '}
  //                         <span
  //                           className={
  //                             test.result === 'OK'
  //                               ? 'text-green-600 font-semibold'
  //                               : 'text-red-600 font-semibold'
  //                           }
  //                         >
  //                           {test.result}
  //                         </span>
  //                       </p>
  //                       <p>
  //                         <strong>Duration:</strong> {test.duration.toFixed(2)}s
  //                       </p>
  //                       {test.stderr && (
  //                         <div className="bg-red-100 font-xs text-red-600 p-3 rounded mt-2">
  //                           <p className="mb-2"><strong>Standard Error</strong></p>
  //                           <pre className="text-sm">{test.stderr}</pre>
  //                         </div>
  //                       )}
  //                     </div>
  //                   ))}
  //                 </div>
  //                 }
  //               </div>
  //             ))}
  //           </div>
  //           )}
  //         </div>
  //       ))}
  //     </Main>
  //   </>
  // );
}

export default Assignment;
