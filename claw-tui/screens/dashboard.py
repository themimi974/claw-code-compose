from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static


class DashboardScreen(Static):
    """Dashboard showing current session status."""

    def compose(self) -> ComposeResult:
        yield Static("📊 Dashboard", classes="section-title")
        yield Static("", id="status-info")
        yield Static("", id="session-info")
        yield Static("", id="permission-info")

    def on_mount(self) -> None:
        self.update_dashboard()

    def update_dashboard(self) -> None:
        from services.config import config_manager
        from services.sessions import session_manager

        session = session_manager.get_current_session()
        workspace_config = config_manager.get_workspace_config()

        status_lines = []
        status_lines.append(f"Model: {workspace_config.get('model', 'unknown')}")
        status_lines.append(f"Sandbox: {'Enabled' if config_manager.get_sandbox_enabled() else 'Disabled'}")

        if session:
            session_lines = []
            session_lines.append(f"Session: {session.id[:30]}...")
            session_lines.append(f"Created: {session.created.strftime('%Y-%m-%d %H:%M')}")
            session_lines.append(f"Messages: {session.message_count}")
        else:
            session_lines = ["No active session"]

        perm_lines = ["Permissions: danger-full-access"]

        self.query_one("#status-info", Static).update("\n".join(status_lines))
        self.query_one("#session-info", Static).update("\n".join(session_lines))
        self.query_one("#permission-info", Static).update("\n".join(perm_lines))