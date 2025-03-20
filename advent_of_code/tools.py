import sys
import io
import time

from concurrent.futures import ProcessPoolExecutor


def run_in_process(code: str):
    exec(code)  # Execute the generated code


def execute_python(code: str) -> str:
    """
    Executes the code that is passed in and then captures the content of standard out and returns it.
    """
    output = io.StringIO()
    sys.stdout = output  # Redirect standard output

    with ProcessPoolExecutor(1) as pool:
        future = pool.submit(run_in_process, code)
        start = time.time()

        while not future.done() and time.time() - start < 60.0:
            time.sleep(2)

        if not future.done():
            pool.shutdown(wait=False)
            sys.stdout = sys.__stdout__
            raise TimeoutError("Process did not finish for 60 seconds.")

    sys.stdout = sys.__stdout__
    captured_output = output.getvalue()
    output.close()
    return captured_output
