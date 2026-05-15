from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static
from textual.binding import Binding
from typing import List


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
        yield Container(
            Static("🛡️ Permissions", classes="section-title"),
            Static("↑↓ Navigate | Enter: Switch | r: Refresh", classes="hint-bar"),
            VerticalScroll(id="permission-list"),
            id="permissions-container"
        )

    def on_mount(self) -> None:
        self.update_permission_list()

    def action_refresh(self) -> None:
        self.update_permission_list()

    def update_permission_list(self) -> None:
        list_container = self.query_one("#permission-list", VerticalScroll)
        for child in list_container.children:
            child.remove()

        # Add warning header if danger-full-access is current
        if self.current_permission == "danger-full-access":
            list_container.mount(
                Static("⚠️  Current: danger-full-access", classes="warning-text")
            )
            list_container.mount(Static(""))

        for i, (mode, description) in enumerate(self.PERMISSION_MODES):
            is_current = mode == self.current_permission
            classes = "permission-item selected" if is_current else "permission-item"
            marker = "●" if is_current else "○"

            if mode.startswith("danger"):
                classes += " danger"

            list_container.mount(
                Static(f"{marker} [b]{mode}[/b]\n   {description}", classes=classes)
            )

    def action_switch_permission(self) -> None:
        """Switch to selected permission mode."""
        if self.selected_index >= len(self.PERMISSION_MODES):
            return

        new_permission = self.PERMISSION_MODES[self.selected_index][0]

        if new_permission == "danger-full-access":
            self.notify("⚠️ Switching to danger-full-access mode!", severity="warning")

        from services.claw_cli import claw_cli
        success, msg = claw_cli.switch_permission(new_permission)

        if success:
            self.current_permission = new_permission
            self.notify(f"Switched to: {new_permission}")
            self.update_permission_list()
        else:
            self.notify(f"Failed: {msg}", severity="error")