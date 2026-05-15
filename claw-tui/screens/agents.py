from textual.app import ComposeResult
from textual.widgets import Static
from textual.binding import Binding
from typing import List


class AgentsScreen(Static):
    """Screen for managing agents."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.agents: List[str] = []
        self.current_agent: str = "default"
        self.selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("🤖 Agents", classes="section-title")
        yield Static("Arrow keys: Navigate | Enter: Switch | r: Refresh", classes="hint-bar")
        yield Static("No agents configured.", id="agent-list")

    def on_mount(self) -> None:
        self.refresh_agents()

    def action_refresh(self) -> None:
        self.refresh_agents()

    def refresh_agents(self) -> None:
        from services.config import config_manager

        workspace_config = config_manager.get_workspace_config()
        model = workspace_config.get("model", "claude-sonnet-4-20250514")
        self.agents = [model]
        self.current_agent = model
        self.update_agent_list()

    def update_agent_list(self) -> None:
        list_widget = self.query_one("#agent-list", Static)

        if not self.agents:
            list_widget.update("No agents configured.")
            return

        lines = []
        for i, agent in enumerate(self.agents):
            marker = ">" if i == self.selected_index else " "
            current = " (current)" if agent == self.current_agent else ""
            lines.append(f"{marker} {agent}{current}")

        list_widget.update("\n".join(lines))

    def on_key(self, event) -> None:
        if event.key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_agent_list()
        elif event.key == "down":
            if self.selected_index < len(self.agents) - 1:
                self.selected_index += 1
                self.update_agent_list()