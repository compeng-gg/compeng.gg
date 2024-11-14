import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import ace from 'ace-builds/src-noconflict/ace';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/ext-language_tools';
import Head from 'next/head';

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');

interface CodeEditorProps {
  value: string;
  onChange: (newValue: string) => void;
}

export default function CodeEditor({ value, onChange }: CodeEditorProps) {
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
    <>
      {loaded && (
        <AceEditor
          mode="c_cpp"
          theme="monokai"
          name="my_ace_editor"
          value={value}
          onChange={onChange}
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
