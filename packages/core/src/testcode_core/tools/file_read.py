import os


async def file_read(path: str, offset: int = 0, limit: int = 2000) -> str:
    if not os.path.exists(path):
        return f"Error: file not found: {path}"
    try:
        with open(path, "r") as f:
            if offset > 0:
                for _ in range(offset):
                    f.readline()
            lines = []
            for _ in range(limit):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
        return "".join(lines) or "(empty file)"
    except Exception as e:
        return f"Error reading file: {e}"
