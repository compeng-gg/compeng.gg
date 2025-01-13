import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import ace from 'ace-builds/src-noconflict/ace';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/ext-language_tools';
import Head from 'next/head';
import { CodeState } from '../question-models';

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');


export default function CodeEditor(props: CodeState) {
  const [loaded, setLoaded] = useState<boolean>(false);

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
    const localUrl = 'http://localhost:8000/'
    const ws = new WebSocket(localUrl+`api/ws/v0/${props.courseSlug}/quiz/${props.quizSlug}/run_code/${props.id}/?token=${jwt.access}`);
    setSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connection opened.');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTestStatus(TestRunStatus.COMPLETE);
      console.log('Message from server:', data);
      setMessage(JSON.stringify(data, null, 2));
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
    </>
  );
}
