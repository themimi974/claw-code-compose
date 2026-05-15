from textual.app import ComposeResult
from textual.widgets import Static
from textual.binding import Binding
from typing import List


class CommandItem:
    """Represents a command in the grid."""

    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description


class CommandsScreen(Static):
    """Screen for quick command launcher."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
    ]

    COMMANDS: List[CommandItem] = [
        CommandItem("/status", "Show session status"),
        CommandItem("/session list", "List all sessions"),
        CommandItem("/diff", "Show git diff"),
        CommandItem("/commit", "Generate & create commit"),
        CommandItem("/model", "Show/switch model"),
        CommandItem("/agents list", "List configured agents"),
        CommandItem("/skills list", "List available skills"),
        CommandItem("/config env", "Show environment config"),
        CommandItem("/history", "Show conversation history"),
        CommandItem("/stats", "Show workspace stats"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("⚡ Commands", classes="section-title")
        yield Static("Arrow keys: Navigate | Enter: Execute", classes="hint-bar")
        yield Static("", id="command-list")

    def on_mount(self) -> None:
        self.update_command_list()

    def action_refresh(self) -> None:
        self.update_command_list()

    def update_command_list(self) -> None:
        list_widget = self.query_one("#command-list", Static)

        lines = []
        for i, cmd in enumerate(self.COMMANDS):
            marker = ">" if i == self.selected_index else " "
            lines.append(f"{marker} {cmd.command:<20} - {cmd.description}")

        list_widget.update("\n".join(lines))

    def on_key(self, event) -> None:
        if event.key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_command_list()
        elif event.key == "down":
            if self.selected_index < len(self.COMMANDS) - 1:
                self.selected_index += 1
                self.update_command_list()
        elif event.key == "enter":
            cmd = self.COMMANDS[self.selected_index]
            from services.claw_cli import claw_cli
            args = cmd.command[1:].split()
            code, stdout, stderr = claw_cli.run(*args)