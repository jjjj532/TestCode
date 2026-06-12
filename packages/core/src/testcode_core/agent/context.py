import os
import sys
import platform
from datetime import datetime


class SystemContext:
    def collect(self) -> str:
        lines = [
            f"Platform: {sys.platform}",
            f"OS: {platform.platform()}",
            f"Python: {sys.version}",
            f"CWD: {os.getcwd()}",
            f"Shell: {os.environ.get('SHELL', 'unknown')}",
            f"Time: {datetime.now().isoformat()}",
        ]
        try:
            import subprocess
            result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                repo_path = result.stdout.strip()
                lines.append(f"Git repo: {repo_path}")
                lines.append(f"Project: {os.path.basename(repo_path)}")
        except Exception:
            pass
        return "\n".join(lines)
