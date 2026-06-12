import subprocess


async def grep_tool(pattern: str, path: str | None = None, include: str | None = None) -> str:
    try:
        cmd = ["rg", "-n"]
        if include:
            cmd.extend(["--glob", include])
        if path:
            cmd.extend([pattern, path])
        else:
            cmd.append(pattern)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout or result.stderr
        return output.strip() or "(no matches)"
    except FileNotFoundError:
        return "Error: ripgrep (rg) not found. Install with: brew install ripgrep"
    except Exception as e:
        return f"Error during grep: {e}"
