import { Accordion, AccordionTab } from 'primereact/accordion';
import { RawToTestResult, TestResult, TestResultDisplay, TestResultHeader } from './test-result';
import { Badge } from 'primereact/badge';


export enum TestRunStatus {
    SUCCESS = 'SUCCESS',
    FAILURE = 'FAILURE',
}

export interface TestRunProps {
    testResults: TestResult[];
    numPassed: number;
    numFailed: number;
    stderr: string | undefined;
    status: TestRunStatus;
    time: Date;
}

export function TestRunHeader(props: TestRunProps){
    const {numPassed, numFailed, status, time} = props;

    const headerBadges = () => {
        if(status === TestRunStatus.SUCCESS){
            return (<div style={{gap: '5px', display: 'flex'}}>
                <Badge value={numPassed} className="ml-auto" severity={'success'}/>
                <Badge value={numFailed} className="ml-auto" severity={'danger'}/>
            </div>);
        } else if(status === TestRunStatus.FAILURE){
            return (
                <Badge value={'Failed'} severity={'danger'}/>
            );
        }
    };

    return (
        <span style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span>{time.toLocaleTimeString()}</span>
            {headerBadges()}
        </span>
    );
}

export default function TestRun(props: TestRunProps){
    //This function displays the results of a test run
    const {testResults, numPassed, numFailed, stderr, status, time} = props;



    if(props.status == TestRunStatus.SUCCESS){
        return (
            <Accordion>
                {testResults.map((test, index) => (
                    <AccordionTab header={TestResultHeader({test, index})} key={index}>
                        <TestResultDisplay {...test}/>
                    </AccordionTab>
                ))}
            </Accordion>
        );
    } else {
        return (
            <div>
                <div>Error:</div>
                <div style={{ backgroundColor: 'rgba(255, 0, 0, 0.2)', color: 'black', padding: '10px', whiteSpace: 'pre-wrap', fontFamily: 'monospace', border: '1px solid black', borderRadius: '5px' }}>
                    {stderr?.split('\n').map((line, index) => (
                        <div key={index}>{line}</div>
                    ))}
                </div>
            </div>
        );
    }
}


export function RawToTestRunProps(raw: string) : TestRunProps{
    const parsed = JSON.parse(raw);
    console.log(parsed);
    if(parsed.status == TestRunStatus.SUCCESS){
        return {
            testResults: parsed.tests.map((test: any) => RawToTestResult(JSON.stringify(test))),
            numPassed: parsed.num_passed,
            numFailed: parsed.num_failed,
            stderr: parsed.stderr ?? undefined,
            status: TestRunStatus.SUCCESS,
            time: new Date(),
        } as TestRunProps;
    } else {
        return {
            status: TestRunStatus.FAILURE,
            time: new Date(),
            numPassed: 0,
            numFailed: 0,
            stderr: parsed.stderr,
            testResults: [],
        };
    }
}