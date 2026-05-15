from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Label


class DashboardScreen(Static):
    """Dashboard showing current session status."""

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Container(
                Static("📊 Dashboard", classes="section-title"),
                Static("", id="status-info"),
                Static("", id="session-info"),
                Static("", id="model-info"),
                Static("", id="agent-info"),
                Static("", id="permission-info"),
            )
        )

    def on_mount(self) -> None:
        self.update_dashboard()

    def update_dashboard(self) -> None:
        from services.config import config_manager
        from services.sessions import session_manager

        # Get current session
        session = session_manager.get_current_session()

        # Get config
        settings = config_manager.get_settings()
        workspace_config = config_manager.get_workspace_config()

        # Build status display
        status_lines = []
        status_lines.append(f"🎯 Model: {workspace_config.get('model', 'unknown')}")
        status_lines.append(f"🔧 Agent: {config_manager.get_system_prompt()[:30]}...")
        status_lines.append(f"🛡️  Sandbox: {'Enabled' if config_manager.get_sandbox_enabled() else 'Disabled'}")

        # Session info
        if session:
            session_lines = []
            session_lines.append(f"📁 Session: {session.id[:25]}...")
            session_lines.append(f"   Created: {session.created.strftime('%Y-%m-%d %H:%M')}")
            session_lines.append(f"   Messages: {session.message_count}")
        else:
            session_lines = ["📁 No active session"]

        # Permission level - would need to query, default to danger-full-access as that's default
        perm_lines = ["🔐 Permissions: danger-full-access (default)"]

        # Update widgets
        self.query_one("#status-info", Static).update("\n".join(status_lines))
        self.query_one("#session-info", Static).update("\n".join(session_lines))
        self.query_one("#model-info", Static).update("")
        self.query_one("#agent-info", Static).update("")
        self.query_one("#permission-info", Static).update("\n".join(perm_lines))