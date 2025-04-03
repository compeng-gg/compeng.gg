

/*
Success example:
{"status": "SUCCESS",
"tests": [
{ "kind": "public", "result": "OK", "actual_result": 0, "expected_result": 0 },
 { "kind": "public", "result": "OK", "actual_result": 4, "expected_result": 4 },
  { "kind": "private", "result": "OK" }, { "kind": "private", "result": "OK" } ], "stderr": null, "num_passed": 3, "num_failed": 0 }



*/

import { Badge } from 'primereact/badge';
import { IconField } from 'primereact/iconfield';

enum TestCaseType {
    PUBLIC = 'public',
    PRIVATE = 'private',
};


export interface TestResult {
    kind: TestCaseType,
    result: string,
    actual_result: string,
    expected_result: string,
}

export function TestResultHeader({test, index} : {test : TestResult, index: number}) {
    return (
        <span style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span>{`Test ${index}`}</span>
            <Badge value={test.result == 'OK' ? 'Passed' : 'Failed'} severity={test.result == 'OK' ? 'success' : 'danger'}/>
        </span>
    );
}

export function TestResultDisplay(test: TestResult) {
    if(test.kind == TestCaseType.PUBLIC){
        return (
            <div>
                <div>Actual Result: {test.actual_result}</div>
                <div>Expected Result: {test.expected_result}</div>
            </div>
        );
    } else {
        return (
            <div>
                Private
            </div>
        );
    }
}

export function RawToTestResult(raw: string): TestResult {
    const parsed = JSON.parse(raw);

    return {
        kind: parsed.kind as TestCaseType,
        result: parsed.result,
        actual_result: parsed.actual_result,
        expected_result: parsed.expected_result,
    } as TestResult;
}