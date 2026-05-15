from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Button
from textual.widget import Widget
from textual.binding import Binding
from textual import work
from typing import List, Optional


class SessionListItem(Widget):
    """A single session in the list."""

    def __init__(self, session_data: dict, is_selected: bool = False):
        super().__init__()
        self.session_data = session_data
        self.is_selected = is_selected

    def compose(self) -> ComposeResult:
        classes = "session-item selected" if self.is_selected else "session-item"
        yield Static(
            f"{self.session_data['id'][:25]}... | {self.session_data['created']} | {self.session_data['messages']} msgs\n  {self.session_data['last_message']}",
            classes=classes
        )


class SessionsScreen(Static):
    """Screen for managing sessions."""

    BINDINGS = [
        Binding("n", "new_session", "New Session"),
        Binding("d", "delete_session", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "switch_session", "Switch"),
    ]

    def __init__(self):
        super().__init__()
        self.sessions: List[dict] = []
        self.selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Container(
            Static("📁 Sessions", classes="section-title"),
            Static("↑↓ Navigate | Enter: Switch | n: New | d: Delete | r: Refresh", classes="hint-bar"),
            VerticalScroll(id="session-list"),
            id="sessions-container"
        )

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
        list_container = self.query_one("#session-list", VerticalScroll)
        list_container.remove_all()

        if not self.sessions:
            list_container.mount(Static("No sessions found. Press 'n' to create one.", classes="empty-message"))
            return

        for i, session in enumerate(self.sessions):
            classes = "session-item"
            if i == self.selected_index:
                classes += " selected"
            list_container.mount(
                Static(
                    f"[b]{session['id'][:20]}...[/b] | {session['created']} | {session['messages']} msgs\n  Last: {session['last_message'][:60]}",
                    classes=classes
                )
            )

    def action_new_session(self) -> None:
        """Create a new session and switch to chat."""
        self.notify("New session created. Switching to chat...")
        # The actual session creation happens when user starts chatting
        from services.claw_cli import claw_cli
        claw_cli.run_interactive()

    def action_delete_session(self) -> None:
        """Delete selected session."""
        if not self.sessions or self.selected_index >= len(self.sessions):
            return

        session = self.sessions[self.selected_index]
        from services.sessions import session_manager

        if session_manager.delete_session(session["id"]):
            self.notify(f"Deleted session: {session['id']}")
            self.refresh_sessions()
        else:
            self.notify("Failed to delete session", severity="error")

    def action_switch_session(self) -> None:
        """Switch to selected session and start chat."""
        if not self.sessions or self.selected_index >= len(self.sessions):
            return

        session = self.sessions[self.selected_index]
        self.notify(f"Switching to session: {session['id'][:20]}...")

        from services.claw_cli import claw_cli
        claw_cli.run_interactive("--resume", session["path"])

    def handle_key(self, event) -> bool:
        """Handle navigation keys."""
        if event.key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_session_list()
            return True
        elif event.key == "down":
            if self.selected_index < len(self.sessions) - 1:
                self.selected_index += 1
                self.update_session_list()
            return True
        return False