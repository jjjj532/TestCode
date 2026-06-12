"""PyInstaller entry point for TestCode CLI."""
import sys
from testcode_cli.main import app


def main():
    app()


if __name__ == "__main__":
    main()
