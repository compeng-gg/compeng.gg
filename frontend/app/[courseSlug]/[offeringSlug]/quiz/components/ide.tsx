import dynamic from 'next/dynamic';
import { useContext, useEffect, useState } from 'react';
import ace from 'ace-builds/src-noconflict/ace';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/ext-language_tools';
import Head from 'next/head';
import { CodeQuestionProps, CodeState, ProgrammingLanguages } from '../question-models';
import { Button } from 'primereact/button';
import { fetchApi, jwtObtainPairEndpoint, apiUrl} from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import TestRun, { RawToTestRunProps, TestRunHeader, TestRunProps } from './test-run';
import { Accordion, AccordionTab } from 'primereact/accordion';

/*
Note: To enable a new programming language, add it to the enum in the backend, ProgrammingLanguages on frontend
, then map it to the corresponding Ace mode in ProgrammingLanguageToMode and finally add the mode to the
configs and imports below. Follow c_cpp and python as examples.

*/

// Set base path for other Ace dependencies
ace.config.set('basePath', '/ace');

// Set custom URLs for specific modules if needed
ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
ace.config.setModuleUrl('ace/mode/python', '/ace/mode-python.js');
ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');

export interface IdeProps {
    language: ProgrammingLanguages;
    value: string;
    isMutable: boolean;
    state: CodeState;
    onChange: (value: string) => void;
}

export default function Ide(props: IdeProps) {

    const [loaded, setLoaded] = useState<boolean>(false);
    useEffect(() => {
        ace.config.setModuleUrl('ace/mode/c_cpp', '/ace/mode-c_cpp.js');
        ace.config.setModuleUrl('ace/mode/python', '/ace/mode-python.js');
        ace.config.setModuleUrl('ace/theme/monokai', '/ace/theme-monokai.js');
        ace.config.setModuleUrl('ace/ext/language_tools', '/ace/ext-language_tools.js');
    
        // Require autocomplete-related modules
        ace.require('ace/ext/language_tools');
        ace.require('ace/mode/c_cpp');
        ace.require('ace/mode/python');
        ace.require('ace/theme/monokai');
    
        setLoaded(true);
        
      }, []);
    

      return (
        <div>
            {loaded && <AceEditor
                mode={ProgrammingLanguageToMode(props.language)}
                theme="monokai"
                name="my_ace_editor"
                value={props.value}
                onChange={props.isMutable ? props.state.setValue : () => {}} 
                fontSize={14}
                showPrintMargin={false}
                showGutter={true}
                highlightActiveLine={true}
                style={{ width: '100%', height: '400px' }}
                readOnly={!props.isMutable} 
                setOptions={{
                  enableBasicAutocompletion: props.isMutable,
                  enableLiveAutocompletion: props.isMutable,
                  enableSnippets: props.isMutable,
                }}
              />}
        </div>
      )


}

export function ProgrammingLanguageToMode(language: ProgrammingLanguages): string {
    switch(language){
        case "C":
        case "C_PP":
            return "c_cpp";
        case "PYTHON":
            return "python";
    }
}
