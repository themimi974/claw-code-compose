from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.binding import Binding


class ChatScreen(Static):
    """Screen for launching interactive chat."""

    BINDINGS = [
        Binding("enter", "start_chat", "Start Chat"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("💬 Chat", classes="section-title"),
            Static("", classes="spacer"),
            Static("Press [b]Enter[/b] to start an interactive Claw Code session", classes="chat-instruction"),
            Static("", classes="spacer"),
            Static("This will launch the CLI in interactive mode.", classes="help-text"),
            Static("Type /help in CLI for available commands.", classes="help-text"),
            id="chat-container"
        )

    def on_mount(self) -> None:
        pass

    def action_start_chat(self) -> None:
        """Launch interactive chat session."""
        from services.claw_cli import claw_cli

        # Get current session if exists
        from services.sessions import session_manager
        session = session_manager.get_current_session()

        if session:
            self.notify("Starting chat with current session...")
            claw_cli.run_interactive("--resume", str(session.path))
        else:
            self.notify("Starting new chat session...")
            claw_cli.run_interactive()