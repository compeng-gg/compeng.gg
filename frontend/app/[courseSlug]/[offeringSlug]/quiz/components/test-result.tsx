

/*
Success example:
{"status": "SUCCESS",
"tests": [
{ "kind": "public", "result": "OK", "actual_result": 0, "expected_result": 0 },
 { "kind": "public", "result": "OK", "actual_result": 4, "expected_result": 4 },
  { "kind": "private", "result": "OK" }, { "kind": "private", "result": "OK" } ], "stderr": null, "num_passed": 3, "num_failed": 0 }



*/

import { Badge } from "primereact/badge";
import { IconField } from "primereact/iconfield";

enum TestCaseType {
    PUBLIC = "public",
    PRIVATE = "private",
};


export interface TestResult {
    kind: TestCaseType,
    isOk: boolean,
    actualResult: string,
    expectedResult: string,
}

export function TestResultHeader({test, index} : {test : TestResult, index: number}) {
    return (
        <span style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
            <span>{`Test ${index}`}</span>
            <Badge value={test.isOk ? "Passed" : "Failed"} severity={test.isOk ? "success" : "danger"}/>
        </span>
    )
}

export function TestResultDisplay(test: TestResult) {
    if(test.kind == TestCaseType.PUBLIC){
        return (
            <div>
                <div>Actual Result: {test.actualResult}</div>
                <div>Expected Result: {test.expectedResult}</div>
            </div>
        )
    } else {
        return (
            <div>
                Private
            </div>
        )
    }
}

export function RawToTestResult(raw: string): TestResult {
    const parsed = JSON.parse(raw);

    return {
        kind: parsed.kind as TestCaseType,
        isOk: parsed.result === "OK",
        actualResult: parsed.actual_result,
        expectedResult: parsed.expected_result,
    } as TestResult;
}