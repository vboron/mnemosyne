import subprocess


def get_cd_toc():
    result = subprocess.run(
        ["cdparanoia", "-Q"],
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    if "Table of contents" not in output:
        raise RuntimeError("No readable audio CD found.")

    return output