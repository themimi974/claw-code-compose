from textual.app import ComposeResult
from textual.widgets import Static
from textual.binding import Binding


class ChatScreen(Static):
    """Screen for launching interactive chat."""

    BINDINGS = [
        Binding("enter", "start_chat", "Start Chat"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("💬 Chat", classes="section-title")
        yield Static("")
        yield Static("Press [Enter] to start an interactive Claw Code session", classes="chat-instruction")
        yield Static("")
        yield Static("This will launch the CLI in interactive mode.", classes="help-text")
        yield Static("Type /help in CLI for available commands.", classes="help-text")

    def action_start_chat(self) -> None:
        from services.claw_cli import claw_cli
        from services.sessions import session_manager

        session = session_manager.get_current_session()

        if session:
            claw_cli.run_interactive("--resume", str(session.path))
        else:
            claw_cli.run_interactive()