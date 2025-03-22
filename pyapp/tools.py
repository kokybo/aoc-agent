import os
import subprocess
import tempfile


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