from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static
from textual.binding import Binding
from typing import List


class SessionsScreen(Static):
    """Screen for managing sessions."""

    BINDINGS = [
        Binding("n", "new_session", "New Session"),
        Binding("d", "delete_session", "Delete"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.sessions: List[dict] = []
        self.selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("📁 Sessions", classes="section-title")
        yield Static("Arrow keys: Navigate | Enter: Switch | n: New | d: Delete | r: Refresh", classes="hint-bar")
        yield Static("No sessions found.", id="session-list")

    def on_mount(self) -> None:
        self.refresh_sessions()

    def action_refresh(self) -> None:
        self.refresh_sessions()

    def refresh_sessions(self) -> None:
        from services.sessions import session_manager

        sessions = session_manager.list_sessions()
        self.sessions = [
            {
                "id": s.id,
                "created": s.created.strftime("%Y-%m-%d %H:%M"),
                "messages": s.message_count,
                "last_message": s.last_message,
                "path": str(s.path)
            }
            for s in sessions
        ]
        self.selected_index = 0
        self.update_session_list()

    def update_session_list(self) -> None:
        list_widget = self.query_one("#session-list", Static)

        if not self.sessions:
            list_widget.update("No sessions found. Press 'n' to create one.")
            return

        lines = []
        for i, session in enumerate(self.sessions):
            marker = ">" if i == self.selected_index else " "
            lines.append(f"{marker} {session['id'][:25]}... | {session['created']} | {session['messages']} msgs")
            lines.append(f"   {session['last_message'][:60]}")
            lines.append("")

        list_widget.update("\n".join(lines))

    def action_new_session(self) -> None:
        from services.claw_cli import claw_cli
        claw_cli.run_interactive()

    def action_delete_session(self) -> None:
        if not self.sessions or self.selected_index >= len(self.sessions):
            return

        session = self.sessions[self.selected_index]
        from services.sessions import session_manager

        if session_manager.delete_session(session["id"]):
            self.refresh_sessions()

    def on_key(self, event) -> None:
        """Handle navigation keys."""
        if event.key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_session_list()
        elif event.key == "down":
            if self.selected_index < len(self.sessions) - 1:
                self.selected_index += 1
                self.update_session_list()
        elif event.key == "enter":
            if self.sessions:
                session = self.sessions[self.selected_index]
                from services.claw_cli import claw_cli
                claw_cli.run_interactive("--resume", session["path"])