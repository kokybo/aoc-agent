from pydantic import BaseModel

class TaskPlanRequest(BaseModel):
    problem: str

class GenerateCodeRequest(BaseModel):
    problem: str
    expected_output: str

class TestCodeRequest(BaseModel):
    problem: str
    expected_output: str
    code: str

class AcceptanceStatus(BaseModel):
    """
    This class provides a mechanism to indicate if a solution passes acceptance testing.
    If a solution fails acceptance testing then the error can be detailed as well
    """

    passed: bool
    error: str = ""
    reason: str = ""

class DebugCodeRequest(BaseModel):
    problem: str
    expected_output: str
    code: str
    test_results: AcceptanceStatus

class CodeExecuteRequest(BaseModel):
    code: str

class CodeExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int