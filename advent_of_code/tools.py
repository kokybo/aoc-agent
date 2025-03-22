import sys
import io
import traceback
import tempfile
import subprocess
import os

from concurrent.futures import ThreadPoolExecutor


def run_in_process(code: str):
    exec(code)  # Execute the generated code


def execute_python_subprocess(code: str):
    _, file = tempfile.mkstemp()

    with open(file, "w") as f:
        f.write(code)

    try:
        result = subprocess.run(
            ["python", file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=60.0,
        )
    except Exception:
        os.remove(file)
        return {
            "stdout": "",
            "stderr": "process timed out after 60 seconds",
            "exit_code": 1,
        }

    os.remove(file)

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }


def execute_python(code: str) -> str:
    """
    Executes the code that is passed in and then captures the content of standard out and returns it.
    """
    output = io.StringIO()
    sys.stdout = output  # Redirect standard output

    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(run_in_process, code)
        try:
            future.result(timeout=60.0)
        except TimeoutError:
            pool.shutdown(wait=False)
            sys.stdout = sys.__stdout__
            raise TimeoutError("Process did not finish for 60 seconds.")
        except Exception:
            error = traceback.format_exc()
            sys.stdout = sys.__stdout__
            return error

    sys.stdout = sys.__stdout__
    captured_output = output.getvalue()
    output.close()
    return captured_output
