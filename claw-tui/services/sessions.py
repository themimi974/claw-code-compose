import json
import os
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Session:
    """Represents a Claw Code session."""
    id: str
    created: datetime
    message_count: int
    last_message: str
    path: Path


class SessionManager:
    """Manages Claw Code sessions."""

    def __init__(self):
        self.claw_dir = Path.home() / ".claw"
        self.sessions_dir = self.claw_dir / "sessions"
        self._workspace_fingerprint = None

    @property
    def workspace_fingerprint(self) -> str:
        """Get workspace fingerprint (derived from current working directory)."""
        if self._workspace_fingerprint is None:
            cwd = str(Path.cwd())
            self._workspace_fingerprint = hashlib.md5(cwd.encode()).hexdigest()[:12]
        return self._workspace_fingerprint

    def get_sessions_dir(self) -> Path:
        """Get the sessions directory for current workspace."""
        return self.sessions_dir / self.workspace_fingerprint

    def _parse_timestamp(self, filepath: Path) -> datetime:
        """Extract timestamp from session filename."""
        # Format: session-1778866214744-0.jsonl
        try:
            basename = filepath.stem  # session-1778866214744-0
            parts = basename.split("-")
            if len(parts) >= 2:
                timestamp = int(parts[1])
                return datetime.fromtimestamp(timestamp / 1000)
        except (ValueError, IndexError):
            pass
        # Fallback to file modification time
        return datetime.fromtimestamp(filepath.stat().st_mtime)

    def list_sessions(self) -> List[Session]:
        """List all sessions in the current workspace."""
        sessions_dir = self.get_sessions_dir()

        if not sessions_dir.exists():
            return []

        sessions = []
        for filepath in sessions_dir.glob("*.jsonl"):
            try:
                # Count messages and get last message
                message_count = 0
                last_message = ""

                with open(filepath) as f:
                    lines = f.readlines()
                    message_count = len(lines)
                    if lines:
                        try:
                            last_obj = json.loads(lines[-1])
                            # Try to get content from different possible fields
                            last_message = last_obj.get("content", "") or last_obj.get("message", "")
                            if isinstance(last_message, list):
                                # Handle array content (e.g., tool results)
                                last_message = str(last_message[0]) if last_message else ""
                        except json.JSONDecodeError:
                            pass

                # Truncate last message
                last_message = last_message[:80].replace("\n", " ")

                sessions.append(Session(
                    id=filepath.stem,
                    created=self._parse_timestamp(filepath),
                    message_count=message_count,
                    last_message=last_message if last_message else "[Empty session]",
                    path=filepath
                ))
            except Exception:
                continue

        # Sort by creation date, newest first
        sessions.sort(key=lambda s: s.created, reverse=True)
        return sessions

    def get_current_session(self) -> Optional[Session]:
        """Get the most recent session."""
        sessions = self.list_sessions()
        return sessions[0] if sessions else None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        sessions_dir = self.get_sessions_dir()
        filepath = sessions_dir / f"{session_id}.jsonl"

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def create_new_session_path(self) -> Path:
        """Get path for a new session file."""
        sessions_dir = self.get_sessions_dir()
        sessions_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(datetime.now().timestamp() * 1000)
        return sessions_dir / f"session-{timestamp}-0.jsonl"


session_manager = SessionManager()