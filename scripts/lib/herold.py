import subprocess
import tempfile


def convert(html: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w+t",
        encoding="UTF-8",
    ) as tmp_file:
        result = subprocess.run(
            ["herold", "-o", tmp_file.name, "-p", "config/herold.conf"],
            capture_output=True,
            input=html,
            text=True,
            encoding="UTF-8",
            check=True,
        )

        if "herold Version" in result.stdout:
            msg = "Convertation from html to xml failed: "
            raise RuntimeError(msg, result.stderr)

        return tmp_file.read()

    return None
