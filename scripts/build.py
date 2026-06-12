#!/usr/bin/env python3
"""Build TestCode standalone executable with PyInstaller.

Usage:
    python scripts/build.py                    # Build for current platform
    python scripts/build.py --onefile          # Single executable file
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build TestCode executable")
    parser.add_argument("--onefile", action="store_true", help="Build single executable")
    parser.add_argument("--name", default="testcode", help="Output executable name")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    spec = root / "scripts" / "build.spec"
    launcher = root / "scripts" / "launcher.py"

    cmd = ["pyinstaller"]
    if args.onefile:
        cmd.append("--onefile")
    cmd.extend([
        "--clean",
        "--name", args.name,
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build"),
        "--specpath", str(root / "scripts"),
        "--add-data", f"{root / 'pyproject.toml'}:.",
        # Hidden imports for all packages
    ])
    cmd.append(str(launcher))

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=root)
    if result.returncode != 0:
        print("Build failed!", file=sys.stderr)
        sys.exit(1)

    print(f"Build complete! Executable in: {root / 'dist'}")


if __name__ == "__main__":
    main()
