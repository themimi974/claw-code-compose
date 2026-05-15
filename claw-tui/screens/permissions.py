from textual.app import ComposeResult
from textual.widgets import Static
from textual.binding import Binding


class PermissionsScreen(Static):
    """Screen for managing permission modes."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
    ]

    PERMISSION_MODES = [
        ("read-only", "Read-only access - can read files but cannot modify"),
        ("workspace-write", "Workspace write - can read and write files in workspace"),
        ("danger-full-access", "Danger: Full access - can execute any command"),
    ]

    def __init__(self):
        super().__init__()
        self.current_permission = "danger-full-access"
        self.selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("🛡️ Permissions", classes="section-title")
        yield Static("Arrow keys: Navigate | Enter: Switch | r: Refresh", classes="hint-bar")
        yield Static("", id="permission-list")

    def on_mount(self) -> None:
        self.update_permission_list()

    def action_refresh(self) -> None:
        self.update_permission_list()

    def update_permission_list(self) -> None:
        list_widget = self.query_one("#permission-list", Static)

        lines = []
        if self.current_permission == "danger-full-access":
            lines.append("⚠️  Current: danger-full-access")
            lines.append("")

        for i, (mode, description) in enumerate(self.PERMISSION_MODES):
            marker = ">" if i == self.selected_index else " "
            lines.append(f"{marker} {mode}")
            lines.append(f"   {description}")
            lines.append("")

        list_widget.update("\n".join(lines))

    def on_key(self, event) -> None:
        if event.key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_permission_list()
        elif event.key == "down":
            if self.selected_index < len(self.PERMISSION_MODES) - 1:
                self.selected_index += 1
                self.update_permission_list()
        elif event.key == "enter":
            new_permission = self.PERMISSION_MODES[self.selected_index][0]
            from services.claw_cli import claw_cli
            success, msg = claw_cli.switch_permission(new_permission)
            if success:
                self.current_permission = new_permission
            self.update_permission_list()