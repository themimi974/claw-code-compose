import subprocess
import os
from typing import Optional, Tuple


class ClawCLI:
    """Wrapper for Claw Code CLI operations."""

    def __init__(self):
        self.cli_path = "/usr/local/bin/claw"

    def is_available(self) -> bool:
        """Check if claw CLI is available."""
        return os.path.exists(self.cli_path)

    def run(self, *args: str, timeout: int = 30) -> Tuple[int, str, str]:
        """Run a claw command and return (returncode, stdout, stderr)."""
        cmd = [self.cli_path] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "Claw CLI not found"
        except Exception as e:
            return -1, "", str(e)

    def run_interactive(self, *args: str) -> None:
        """Run claw CLI interactively (replaces current process)."""
        cmd = [self.cli_path] + list(args)
        try:
            # Use os.execvp to replace current process with claw
            os.execvp(cmd[0], cmd)
        except Exception as e:
            print(f"Failed to run interactive claw: {e}")
            input("Press Enter to continue...")

    def get_version(self) -> str:
        """Get claw CLI version."""
        code, stdout, _ = self.run("--version")
        return stdout.strip() if code == 0 else "unknown"

    def get_status(self) -> str:
        """Get current status."""
        code, stdout, stderr = self.run("/status")
        return stdout if code == 0 else stderr

    def switch_session(self, session_path: str) -> None:
        """Switch to a session and run interactively."""
        self.run_interactive("--resume", session_path)

    def switch_model(self, model: str) -> Tuple[bool, str]:
        """Switch the current model."""
        code, stdout, stderr = self.run("/model", model)
        return code == 0, stdout + stderr

    def switch_permission(self, permission: str) -> Tuple[bool, str]:
        """Switch permission mode."""
        code, stdout, stderr = self.run("/permissions", permission)
        return code == 0, stdout + stderr


claw_cli = ClawCLI()