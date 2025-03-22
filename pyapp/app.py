from typing import Any
from dotenv import load_dotenv

from pyapp.tools import execute_python_subprocess
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import controlflow as cf
from pyapp.models import AcceptanceStatus, CodeExecuteRequest, CodeExecuteResponse, DebugCodeRequest, TaskPlanRequest, TestCodeRequest
import pyapp.agents as agents

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains (use cautiously in production)
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/generate_task_plan", response_model=list[str])
def create_task_plan(context: TaskPlanRequest):
    with cf.Flow():
        task_plan = cf.run(
            "Develop a list of tasks that need to be accomplished in order to solve the problem",
            agents=[agents.PLANNER],
            context=context.model_dump(),
            result_type=list[str],
        )

    return task_plan

@app.post("/extract_solution", response_model=dict[str, str])
def extract_solution(context: TaskPlanRequest):
    with cf.Flow():
        target_value = cf.run(
        "Please identify the value that should be outputted by the program in problem statement",
        instructions="""
        Only return the expected output value and nothing else
        """,
        context=context.model_dump(),
        result_type=str
    )
        
    return {"solution": target_value}

@app.post("/generate_code", response_model=dict[str, str])
def extract_solution(context: TaskPlanRequest):
    with cf.Flow():
        code = cf.run(
            "Write code to implement the tasks required to solve the problem",
            instructions="""
            Solutions should be designed to complete within 5 minutes.
            Only return the code that you wrote, no other information or commentary.
            Please include the inputs as a string literal in the puzzle.
            """,
            agents=[agents.PROGRAMMER],
            context=context.model_dump(),
            result_type=str,
        )
        
    return {"code": code}

@app.post("/test_solution", response_model=AcceptanceStatus)
def test_solution(context: TestCodeRequest):
    accepted = cf.run(
        "Test the code and verify that it meets the criteria defined in the problem",
        instructions="""
        Verify the solution code for correctness and efficiency.
        Report any errors encountered to allow for debugging.
        Before running any code please verify that the solution is likely to complete in a timely manner.
        If you accept the solution please indicate your reason for accepting the solution as correct.
        Ensure that the standard output from running the solution contains the expected result from the problem statement.
        """,
        agents=[agents.TESTER],
        context=context.model_dump(),
        result_type=AcceptanceStatus,
    )

    return accepted

@app.post("/debug_solution", response_model=dict[str, str])
def debug_solution(context: DebugCodeRequest):
    new_code = cf.run(
        "Debug the code and correct any errors preventing it from solving the problem",
        instructions="""
        Output only the new code once you have finished debugging.
        You may request help from the user if more information is required in your debugging.
        Identify and correct any logic bugs that you encounter in the code
        """,
        agents=[agents.DEBUGGER, agents.PROGRAMMER, agents.CODE_OPTIMIZER],
        result_type=str,
        turn_strategy=cf.orchestration.turn_strategies.Popcorn(),
        interactive=True,
        context=context.model_dump(),
    )

    return {"code":new_code}


@app.post("/execute", response_model=CodeExecuteResponse)
def execute_code(solution: CodeExecuteRequest):
    return execute_python_subprocess(solution.code)


def main():
    import uvicorn
    uvicorn.run(app)

if __name__ == "__main__":
    main()