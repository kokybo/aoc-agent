import controlflow as cf

from advent_of_code.tools import execute_python_subprocess
from langchain_openai import ChatOpenAI

# MODEL = "openai/o1"
MODEL = ChatOpenAI(model="o3-mini")

PROGRAMMER = cf.Agent(
    name="Programmer",
    instructions="Write python scripts to solve complex programming problems.",
    description="Writes python code",
    model=MODEL
)

TESTER = cf.Agent(
    name="Software Tester",
    description="Tests software",
    instructions="\n".join(
        (
            "Run developers code and capute the output",
            "verify the outputs align with the stated problem",
            "Identify possible testing scenarios that can identify potential problems",
        )
    ),
    tools=[execute_python_subprocess],
    model=MODEL
)

PLANNER = cf.Agent(
    name="Task Planner",
    description="Identifies the tasks required to solve a problem",
    instructions="\n".join(
        (
            "Decompose a complex problem into simple tasks",
            "Identify functionality required to implement simple tasks"
        )
    ),
    model=MODEL
)

INPUT_PARSER = cf.Agent(
    name="Input Parser",
    description="Identifies the inputs and outputs of a problem",
    instructions="\n".join(
        (
            "Extract the inputs and outputs from a problem",
            "validate that code will correctly parse the inputs produce the required outputs",
        )
    ),
    model=MODEL
)

CODE_OPTIMIZER = cf.Agent(
    name="Software Optimizer",
    description="Optimizes written code to ensure performance",
    instructions="\n".join(
        (
            "Optimize code to ensure efficient run time",
            "Identify potential algorithms that can be applied to solve a problem",
            "Balance readability with the number of lines of code",
            "Where appropriate apply parallelism to improve software performance",
        )
    ),
    model=MODEL
)

DEBUGGER = cf.Agent(
    name="Debugger",
    description="Identifies Software Bugs",
    instructions="""
    Identify and remove software bugs in software.
    Preserve the intended functionality as much as possible
    """,
    model=MODEL
)

VALIDATOR = cf.Agent(
    name="Validator",
    description="Checks with the user to confirms that the software is valid",
    instructions="""
        Please chat with the user and confirm with them that the developed code is correct and valid.
        Accept any feedback that they give and incorporate it into the developed code.
        Ensure that the developed code has the required components for reading the input from a file.
    """,
    model=MODEL
)
