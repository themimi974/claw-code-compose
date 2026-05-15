from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
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
        yield Container(
            Static("🤖 Agents", classes="section-title"),
            Static("↑↓ Navigate | Enter: Switch | r: Refresh", classes="hint-bar"),
            VerticalScroll(id="agent-list"),
            id="agents-container"
        )

    def on_mount(self) -> None:
        self.refresh_agents()

    def action_refresh(self) -> None:
        self.refresh_agents()

    def refresh_agents(self) -> None:
        from services.config import config_manager

        # Get agents from config - in real implementation, this would query the CLI
        workspace_config = config_manager.get_workspace_config()
        model = workspace_config.get("model", "claude-sonnet-4-20250514")

        # For now, show the model as the agent
        self.agents = [model]
        self.current_agent = model

        self.update_agent_list()

    def update_agent_list(self) -> None:
        list_container = self.query_one("#agent-list", VerticalScroll)
        for child in list_container.children:
            child.remove()

        if not self.agents:
            list_container.mount(Static("No agents configured.", classes="empty-message"))
            return

        for i, agent in enumerate(self.agents):
            is_current = agent == self.current_agent
            classes = "agent-item selected" if is_current else "agent-item"
            marker = "●" if is_current else "○"
            list_container.mount(
                Static(f"{marker} {agent}", classes=classes)
            )

    def action_switch_agent(self) -> None:
        """Switch to selected agent."""
        if not self.agents or self.selected_index >= len(self.agents):
            return

        # In implementation, this would call claw CLI to switch agent
        self.notify(f"Switching to agent: {self.agents[self.selected_index]}")