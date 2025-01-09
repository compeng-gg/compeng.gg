import { Lab } from "@/app/[courseSlug]/page";
import { Card } from "primereact/card";


export interface StudentAssignmentTabProps {
    labs: Lab[];
}

export default function StudentAssignmentTab(props: StudentAssignmentTabProps){

    const {labs} = props;
    console.log(JSON.stringify(labs, null, 2));
    return (
        <div style={{display: "flex", gap: "10px", width: "100%", flexDirection: "column"}}>
            <span></span>
            {labs.map((assignment) => (
            <Card
            key={assignment.slug}
            title={assignment.name}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
            subTitle={`Due: ${new Date(assignment.due_date)}`}
            >
            <p style={{marginTop: "-10px"}}>Current Grade: {assignment.grade}</p>

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
                        <span className="text-red-600 font-semibold">{task.status}</span>
                    ) : (
                        task.status
                    )}
                    </p>
                    {task.grade && (
                    <p>
                        <strong>Grade:</strong> {task.grade}
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
                        <p>
                            <strong>Duration:</strong> {test.duration.toFixed(2)}s
                        </p>
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
            </Card>
        ))}
      </div>
    )

}