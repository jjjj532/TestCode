import asyncio


async def bash(command: str, timeout: int = 120) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = stdout.decode(errors="replace") + stderr.decode(errors="replace")
        return output.strip() or "(no output)"
    except asyncio.TimeoutError:
        raise TimeoutError(f"Command timed out after {timeout}s")
