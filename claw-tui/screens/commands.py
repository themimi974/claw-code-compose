from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Grid
from textual.widgets import Static, Button
from textual.binding import Binding
from typing import List, Tuple


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
        CommandItem("/version", "Show CLI version"),
        CommandItem("/doctor", "Diagnose setup issues"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Container(
            Static("⚡ Commands", classes="section-title"),
            Static("↑↓←→ Navigate | Enter: Execute", classes="hint-bar"),
            VerticalScroll(id="command-list"),
            id="commands-container"
        )

    def on_mount(self) -> None:
        self.update_command_list()

    def action_refresh(self) -> None:
        self.update_command_list()

    def update_command_list(self) -> None:
        list_container = self.query_one("#command-list", VerticalScroll)
        list_container.remove_all()

        # Build a grid-like display
        for i, cmd in enumerate(self.COMMANDS):
            is_selected = i == self.selected_index
            classes = "command-item selected" if is_selected else "command-item"
            list_container.mount(
                Static(f"[b]{cmd.command:<20}[/b] - {cmd.description}", classes=classes)
            )

    def action_execute_command(self) -> None:
        """Execute the selected command."""
        if self.selected_index >= len(self.COMMANDS):
            return

        cmd = self.COMMANDS[self.selected_index]
        self.notify(f"Executing: {cmd.command}...")

        from services.claw_cli import claw_cli

        # Parse command - remove leading slash
        args = cmd.command[1:].split()
        code, stdout, stderr = claw_cli.run(*args)

        # Show output
        output = stdout if stdout else stderr
        if not output:
            output = "(no output)"

        # Display result (in a real implementation, would show in a modal)
        self.notify(f"Done: {code == 0}")