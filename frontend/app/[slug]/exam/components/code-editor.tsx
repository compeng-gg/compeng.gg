import dynamic from 'next/dynamic';
import { useContext, useEffect, useState } from 'react';
import ace from 'ace-builds/src-noconflict/ace';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/ext-language_tools';
import Head from 'next/head';
import { CodeQuestionProps, CodeState } from '../question-models';
import { Button } from 'primereact/button';
import { fetchApi, jwtObtainPairEndpoint } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');


export default function CodeEditor({props, save} : {props: CodeQuestionProps, save: (newValue: any) => void}) {
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

  return (
    <div style={{ display: "flex", "flexDirection": "column", gap: "10px" }}>
      {loaded && (
        <AceEditor
          mode="c_cpp"
          theme="monokai"
          name="my_ace_editor"
          value={props.state.value}
          onChange={props.state.setValue}
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
      {props.isMutable ? (
        <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse" }}>
          <span></span>
          <Button label="Submit" size="small" />
        </div>
      ) : null}
    </div>
  );
}
