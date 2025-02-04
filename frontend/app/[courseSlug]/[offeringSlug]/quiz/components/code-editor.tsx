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

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');

enum TestRunStatus {
  NOT_RUN = "Idle",
  ERROR = "Error",
  RUNNING = "Running",
  COMPLETE = "Complete"
}

export default function CodeEditor(props: CodeState) {
  const [loaded, setLoaded] = useState<boolean>(false);
  const [socket, setSocket] = useState<WebSocket | undefined>(undefined);
  const [message, setMessage] = useState<string>("");
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [testStatus, setTestStatus] = useState<TestRunStatus>(TestRunStatus.NOT_RUN);
  const [testRuns, setTestRuns] = useState<TestRunProps[]>([]);

  useEffect(() => {
    ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
    ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
    ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');
    
    // Require autocomplete-related modules
    ace.require('ace/ext/language_tools');
    ace.require('ace/mode/c_cpp');
    ace.require('ace/theme/monokai');

    setLoaded(true);
    
  }, []);

  useEffect(() => {
    // Create a WebSocket connection
    const ws = new WebSocket(apiUrl+`ws/${props.courseSlug}/quiz/${props.quizSlug}/run_code/${props.id}/?token=${jwt.access}`);
    setSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connection opened.');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTestStatus(TestRunStatus.COMPLETE);
      console.log('Message from server:', data);
      setMessage(JSON.stringify(data, null, 2));
      const newResult: TestRunProps = RawToTestRunProps(JSON.stringify(data));
      setTestRuns((testRuns) => [...testRuns, newResult]);

    };

    ws.onclose = () => {
      console.log('WebSocket connection closed.');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Cleanup the WebSocket connection
    return () => {
      ws.close();
    };
  }, []);

  async function runTests() {
    if(socket){
      setTestStatus(TestRunStatus.RUNNING)
      socket.send(JSON.stringify({solution: props.state.value, questionId: props.id}));
    }
  }

  return (
    <>
      {loaded && (
        <AceEditor
          mode="c_cpp"
          theme="monokai"
          name="my_ace_editor"
          value={props.value}
          onChange={props.setValue}
          fontSize={14}
          showPrintMargin={false}
          showGutter={true}
          highlightActiveLine={true}
          style={{ width: '100%', height: '400px' }}
          // Enable autocomplete features
          setOptions={{
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true,
            enableSnippets: true,
          }}
        />
      )}
      <Accordion>
        {testRuns.map((testRun: TestRunProps, index) => (
          <AccordionTab header={TestRunHeader(testRun)} key={index}>
            <TestRun {...testRun} />
          </AccordionTab>
        ))}
      </Accordion>
      {props.isMutable ? (
        <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse" }}>
          <span></span>
          <Button label="Run Tests" size="small" onClick={runTests}/>
        </div>
      ) : null}
    </div>
  );
}

