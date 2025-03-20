from dotenv import load_dotenv
load_dotenv
import argparse
import os
import controlflow as cf
from pydantic import BaseModel

from advent_of_code.solver import agents


class Feedback(BaseModel):
    was_successful: bool
    run_details: str


@cf.flow(default_agent=agents.PLANNER)
def solve_problem(problem_statement: str, output_file: str) -> str:
    code = cf.run(
        "Plan, develop, test, and verify a solution to this programming problem",
        instructions="\n".join(
            (
                "Code should be written in the form of a Python script",
                "Code should provide mechanisms for reading input files",
                "Return just the code that was developed for this problem",
                "Only Code should be produced. No Markdown, and no notes explaining the code",
                "If an error occurs during testing attempt to identify the cause of the error and correct it",
            )
        ),
        agents=[
            agents.PROGRAMMER,
            agents.TESTER,
            agents.PLANNER,
            # agents.INPUT_PARSER,
            agents.CODE_OPTIMIZER,
            agents.DEBUGGER,
        ],
        result_type=str,
        context={"problem": problem_statement},
        completion_agents=[agents.TESTER],
        turn_strategy=cf.orchestration.turn_strategies.Moderated(
            moderator=agents.PLANNER
        ),
        interactive=True,
    )

    # TODO: Add a step to extract the input format and parse it
    parser_code = cf.run(
        "Identify the input format specified in the problem and develop code to parse the input into the format required by the solution code",
        instructions="""
        Extract the sample input from the problem statement.
        Identify the Input format expected by the solution code.
        Write code to transform the input from the problem statement into the format expected by the solution code.
        Test the code to verify correctness
        """,
        agents=[
            agents.PROGRAMMER,
            agents.TESTER,
            agents.PLANNER,
            # agents.INPUT_PARSER,
            agents.CODE_OPTIMIZER,
            agents.DEBUGGER,
        ],
        result_type=str,
        context={"problem": problem_statement, "solution_code": code},
        completion_agents=[agents.TESTER],
        turn_strategy=cf.orchestration.turn_strategies.Popcorn(),
    )

    output = cf.run(
        "Combine the parser code and the solution code into a single unit.",
        instructions="""
        Output only the combined code and nothing else.
        """,
        agents=[
            agents.PROGRAMMER,
            agents.TESTER,
            agents.PLANNER,
            # agents.INPUT_PARSER,
            agents.CODE_OPTIMIZER,
            agents.DEBUGGER,
        ],
        result_type=str,
        context={
            "problem": problem_statement,
            "solution_code": code,
            "parser_code": parser_code,
        },
        completion_agents=[agents.TESTER],
        turn_strategy=cf.orchestration.turn_strategies.Popcorn(),
    )

    with open(output_file, "w") as f:
        f.write(output)

    feedback = cf.run(
        "Have the user run the program and then provide feedback about it's success",
        instructions="""
        Instruct the user to run the program.
        Ask the user to provide feedback on the programs performance
        Indicate if the run was successful and what other information the user provided
        """,
        result_type=Feedback,
        interactive=True,
    )

    if feedback.was_successful:
        return
    else:
        pass


def main():
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

    code = solve_problem(problem, args.output)


if __name__ == "__main__":
    main()
