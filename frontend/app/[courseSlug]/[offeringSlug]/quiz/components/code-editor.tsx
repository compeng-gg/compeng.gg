import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import ace from 'ace-builds/src-noconflict/ace';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/ext-language_tools';
import Head from 'next/head';
import { CodeQuestionProps, CodeState } from '../question-models';
import { Button } from 'primereact/button';
import { fetchApi, jwtObtainPairEndpoint, apiUrl} from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import TestRun, { RawToTestRunProps, TestRunHeader, TestRunProps } from './test-run';
import { Accordion, AccordionTab } from 'primereact/accordion';
import Ide from './ide';

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');

enum TestRunStatus {
  NOT_RUN = 'Idle',
  ERROR = 'Error',
  RUNNING = 'Running',
  COMPLETE = 'Complete'
}

export default function CodeEditor({ props, includeTests }: { props: CodeQuestionProps, includeTests: boolean}) {
    const [loaded, setLoaded] = useState<boolean>(false);
    const [socket, setSocket] = useState<WebSocket | undefined>(undefined);
    const [message, setMessage] = useState<string>('');
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [testStatus, setTestStatus] = useState<TestRunStatus>(TestRunStatus.NOT_RUN);

    // ✅ Convert executions to TestRunProps format
    const [testRuns, setTestRuns] = useState<TestRunProps[]>(props.executions?.map(exec => ({
        testResults: exec.result?.tests ?? [],
        numPassed: exec.result?.tests?.filter(test => test.result === 'OK').length ?? 0,
        numFailed: exec.result?.tests?.filter(test => test.result !== 'OK').length ?? 0,
        stderr: exec.stderr ?? '',
        status: exec.status ?? 'ERROR',
        time: new Date() // No timestamp provided, so defaulting to now
    })) ?? []);

    useEffect(() => {
        ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
        ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
        ace.config.setModuleUrl('ace/ext-language_tools', '/ace/ext-language_tools.js');

        ace.require('ace/ext/language_tools');
        ace.require('ace/mode/c_cpp');
        ace.require('ace/theme/monokai');

        setLoaded(true);
    }, []);

    useEffect(() => {
        if (!props.isMutable) return;

        const ws = new WebSocket(apiUrl+`ws/${props.courseSlug}/quiz/${props.quizSlug}/run_code/${props.id}/?token=${jwt.access}`);
        setSocket(ws);

        ws.onopen = () => console.log('WebSocket connection opened.');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setTestStatus(TestRunStatus.COMPLETE);
            console.log('Message from server:', data);
            setMessage(JSON.stringify(data, null, 2));

            const newResult: TestRunProps = {
                testResults: data.tests ?? [],
                numPassed: data.tests?.filter(test => test.result === 'OK').length ?? 0,
                numFailed: data.tests?.filter(test => test.result !== 'OK').length ?? 0,
                stderr: data.stderr ?? '',
                status: data.status ?? 'ERROR',
                time: new Date()
            };

            setTestRuns((prevTestRuns) => [...prevTestRuns, newResult]);
        };

        ws.onclose = () => console.log('WebSocket connection closed.');
        ws.onerror = (error) => console.error('WebSocket error:', error);

        return () => ws.close();
    }, [props.isMutable, jwt.access, props.courseSlug, props.quizSlug, props.id]);

    async function runTests() {
        if (socket) {
            setTestStatus(TestRunStatus.RUNNING);
            socket.send(JSON.stringify({ solution: props.state.value, questionId: props.id }));
        }
    }

    return (
        <div style={{ display: 'flex', 'flexDirection': 'column', gap: '10px' }}>
            <Ide language={props.programmingLanguage} value={props.state.value} onChange={props.state.setValue} isMutable={props.isMutable} state={props.state} />
            <Accordion>
                {testRuns.map((testRun: TestRunProps, index) => (
                    <AccordionTab header={TestRunHeader(testRun)} key={index}>
                        <TestRun {...testRun} />
                    </AccordionTab>
                ))}
            </Accordion>

            {props.isMutable && (
                <div style={{ position: 'relative', display: 'flex', flexDirection: 'row-reverse' }}>
                    <span></span>
                    <Button label="Run Tests" size="small" onClick={runTests} />
                </div>
            )}
        </div>
    );
}
