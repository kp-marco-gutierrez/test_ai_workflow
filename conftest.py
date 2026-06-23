import subprocess
import sys


def pytest_configure(config):
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
        check=True,
    )
