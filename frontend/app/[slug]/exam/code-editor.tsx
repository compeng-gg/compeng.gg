import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import ace from 'ace-builds/src-noconflict/ace';
import AceEditor from "react-ace";
import Head from 'next/head';

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// // Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');


interface CodeEditorProps {
    value: string;
    onChange: (newValue: string) => void;
}

export default function CodeEditor({ value, onChange }: CodeEditorProps) {
    
    const [loaded, setLoaded] = useState<boolean>(false);
    useEffect(() => {
        ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
        ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
        ace.require(`ace/mode/c_cpp`);
        ace.require('ace/theme/monokai');

        setLoaded(true);
    }), []

    return (
        <>
            {loaded && <AceEditor
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
        />}
        </>

    );
}
