async def file_edit(path: str, old_string: str, new_string: str) -> str:
    try:
        with open(path, "r") as f:
            content = f.read()
        if old_string not in content:
            return f"Error: old_string not found in {path}"
        new_content = content.replace(old_string, new_string, 1)
        with open(path, "w") as f:
            f.write(new_content)
        return f"Edited {path}: replaced 1 occurrence"
    except Exception as e:
        return f"Error editing file: {e}"
