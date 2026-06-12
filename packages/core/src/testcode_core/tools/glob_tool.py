import glob as glob_module


async def glob_tool(pattern: str, path: str | None = None) -> str:
    try:
        search_path = f"{path}/{pattern}" if path else pattern
        matches = sorted(glob_module.glob(search_path))
        if not matches:
            return "(no matches)"
        return "\n".join(matches)
    except Exception as e:
        return f"Error during glob: {e}"
