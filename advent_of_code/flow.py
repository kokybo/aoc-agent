from dotenv import load_dotenv

load_dotenv()

import argparse
import os
import controlflow as cf
from pydantic import BaseModel
import json

from advent_of_code import agents
from advent_of_code.tools import execute_python_subprocess


class AcceptanceStatus(BaseModel):
    """
    This class provides a mechanism to indicate if a solution passes acceptance testing.
    If a solution fails acceptance testing then the error can be detailed as well
    """

    passed: bool
    error: str = ""
    reason: str = ""


@cf.flow()
def solve_problem(problem: str, max_iter: int = 3) -> str:
    solution_context = {"problem": problem}
    task_plan = cf.run(
        "Develop a list of tasks that need to be accomplished in order to solve the problem",
        agents=[agents.PLANNER],
        context=solution_context,
        result_type=list[str],
    )

    solution_context["task_plan"] = task_plan

    solution_context["expected_output"] = cf.run(
        "Please identify the value that should be outputted by the program in problem statement",
        instructions="""
        Only return the expected output value and nothing else
        """,
        context=solution_context,
    )

    code = cf.run(
        "Write code to implement the tasks required to solve the problem",
        instructions="""
        Solutions should be designed to complete within 5 minutes.
        Only return the code that you wrote, no other information or commentary.
        Please include the inputs as a string literal in the puzzle.
        """,
        agents=[agents.PROGRAMMER],
        context=solution_context,
        result_type=str,
    )

    solution_context["code"] = code

    solved = False
    iterations = 0
    while not solved and iterations < max_iter:
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
            context=solution_context,
            result_type=AcceptanceStatus,
        )

        result = execute_python_subprocess(solution_context["code"])
        if result["exit_code"] != 0:
            accepted.passed = False

        # accepted = AcceptanceStatus(passed="1928" in result['stdout'].strip() , error="", reason="Returned Correct Result")
        solution_context["test_output"] = result

        if not accepted.passed:
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
                context=solution_context,
            )

            solution_context["code"] = new_code
            iterations += 1
        else:
            solved = True
            print(accepted.reason)

    with open("debug.json", "w") as f:
        solution_context["iterations"] = iterations
        json.dump(solution_context, f, indent=2)

    return solution_context["code"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "problem_statement",
        type=str,
        help="Path to a file containing the problem to solve",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="solution.py",
        type=str,
        help="File to output the solution into",
    )

    args = parser.parse_args()
    with open(args.problem_statement) as f:
        problem = f.read()

    code = solve_problem(problem)

    with open(args.output, "w") as f:
        f.write(code)
