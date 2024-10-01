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

function Course({ params }: { params: { slug: string } }) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [name, setName] = useState();
  const [labs, setLabs] = useState([] as Lab[]);

  useEffect(() => {
    async function fetchLabs() {
      try {
        //To do: include role in this API
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.slug}/`, "GET");
        const data = await response.json();
        setName(data.name);
        setLabs(data.assignments);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    fetchLabs();
  }, [params.slug, jwt, setAndStoreJwt]);

  if (!name) {
    return (
      <>
        <Navbar />
        <Main>
          <></>
        </Main>
      </>
    );
  }

  const items = [
    { label: 'Assignments', icon: 'pi pi-list-check'},
    { label: 'Exercises', icons: 'pi pi-pencil'},

  ]

  //Temp value
  const role = "Student";

  if(role == "Student"){
    return (
      <>
        <Navbar />
        <Card>
          <StudentView courseName={name} labs={labs} />
          </Card>
      </>
    )
  }


  return (
    <>
      <Navbar />
      <Main>
        <H1>{name}</H1>

        {labs.map((assignment) => (
          <div
            className="bg-gray-100 dark:bg-gray-900 shadow-md rounded-lg p-6 mb-6"
          >
            <H2>{assignment.name}</H2>
            <p className="mt-2">
              Due: {`${new Date(assignment.due_date)}`}
            </p>
            {"grade" in assignment && (
              <p>Highest Grade: {assignment.grade}</p>
            )}

            {"leaderboard" in assignment && (<>
              <div className="border-t border-gray-500 pt-4 mt-4">
                <h3 className="text-xl font-semibold mb-3">Leaderboard</h3>
                <Table fields={leaderboardFields} data={assignment.leaderboard} ></Table>
              </div>
            </>)}

            {assignment.tasks && assignment.tasks.length > 0 && (
            <div className="border-t border-gray-500 pt-4 mt-4">
              <h3 className="text-xl font-semibold mb-3">Pushes:</h3>
              {assignment.tasks.map((task: any) => (
                <div
                  key={task.id}
                  className="bg-gray-200 dark:bg-gray-800 rounded-lg p-4 mb-4 shadow"
                >
                  <p>
                    <strong>Status:</strong>{' '}
                    {task.status === 'Success' ? (
                      <span className="text-green-600 font-semibold">{task.status}</span>
                    ) : task.status === 'Failure' ? (
                      <>
                      <span className="text-red-600 font-semibold">{task.status}
                      {task.result && "error" in task.result && (
                        <>
                           {' '}
                          ({task.result.error})
                        </>
                      )}
                      </span>
                      </>
                    ) : (
                      task.status
                    )}
                  </p>
                  {"grade" in task && (
                    <p>
                      <strong>Grade:</strong> {task.grade}
                    </p>
                  )}
                  {"speedup" in task && (
                    <p>
                      <strong>Speedup:</strong> {task.speedup}
                    </p>
                  )}
                  <p>
                    <strong>Repo:</strong>{' '}
                    <a
                      href={`https://github.com/compeng-gg/${task.repo}`}
                      className="text-blue-500 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {task.repo}
                    </a>
                  </p>
                  <p>
                    <strong>Commit:</strong> {task.commit}
                  </p>
                  <p>
                    <strong>Received:</strong>{' '}
                    {`${new Date(task.received)}`}
                  </p>

                  {task.result && "thru" in task.result && "util" in task.result &&
                    <div className="border-t border-gray-500 mt-4 pt-2">
                      <p>
                        <strong>Throughput:</strong>{' '}
                        {task.result.thru}/40
                      </p>
                      <p>
                        <strong>Utilization:</strong>{' '}
                        {task.result.util}/60
                      </p>
                    </div>
                  }

                  {task.result && "stdout" in task.result && task.result.stdout && (
                    <div className="bg-blue-100 font-xs text-blue-600 p-3 rounded mt-2">
                      <p className="mb-2"><strong>Standard Output</strong></p>
                      <pre className="text-sm">{task.result.stdout}</pre>
                    </div>
                  )}
                  {task.result && "stderr" in task.result && task.result.stderr && (
                    <div className="bg-red-100 font-xs text-red-600 p-3 rounded mt-2">
                      <p className="mb-2"><strong>Standard Error</strong></p>
                      <pre className="text-sm">{task.result.stderr}</pre>
                    </div>
                  )}

                  {task.result && task.result.tests &&
                  <div className="border-t border-gray-500 mt-4 pt-2">
                    <h4 className="font-semibold mb-2">Test Results:</h4>
                    {task.result.tests.map((test:any, index:any) => (
                      <div
                        key={index}
                        className="bg-white dark:bg-black p-3 rounded-lg shadow-sm mb-2"
                      >
                        <p>
                          <strong>Test:</strong> {test.name}
                        </p>
                        <p>
                          <strong>Weight:</strong> {test.weight}
                        </p>
                        <p>
                          <strong>Result:</strong>{' '}
                          <span
                            className={
                              test.result === 'OK'
                                ? 'text-green-600 font-semibold'
                                : 'text-red-600 font-semibold'
                            }
                          >
                            {test.result}
                          </span>
                        </p>
                        {test.duration &&
                        (<p>
                          <strong>Duration:</strong> {test.duration.toFixed(2)}s
                        </p>)}
                        {test.stdout && (
                          <div className="bg-blue-100 font-xs text-blue-600 p-3 rounded mt-2">
                            <p className="mb-2"><strong>Standard Output</strong></p>
                            <pre className="text-sm">{test.stdout}</pre>
                          </div>
                        )}
                        {test.stderr && (
                          <div className="bg-red-100 font-xs text-red-600 p-3 rounded mt-2">
                            <p className="mb-2"><strong>Standard Error</strong></p>
                            <pre className="text-sm">{test.stderr}</pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                  }
                </div>
              ))}
            </div>
            )}
          </div>
        )
}

export default Assignment;
