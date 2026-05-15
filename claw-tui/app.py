#!/usr/bin/env python3
"""Claw Code TUI - Main application."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, TabbedContent, Tab
from textual.binding import Binding

from screens.dashboard import DashboardScreen
from screens.sessions import SessionsScreen
from screens.agents import AgentsScreen
from screens.permissions import PermissionsScreen
from screens.commands import CommandsScreen
from screens.chat import ChatScreen


class ClawTUI(App):
    """Claw Code Terminal User Interface."""

    CSS = """
    Screen {
        background: $surface;
    }

    .section-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding: 1;
    }

    .hint-bar {
        text-align: center;
        color: $text-secondary;
        padding: 0 1;
    }

    .spacer {
        height: 1;
    }

    .session-item, .agent-item, .permission-item, .command-item {
        padding: 1 2;
        border: solid $primary;
    }

    .session-item.selected, .agent-item.selected, .permission-item.selected, .command-item.selected {
        background: $primary;
        border: solid $accent;
    }

    .empty-message {
        text-align: center;
        color: $text-secondary;
        padding: 2;
    }

    .warning-text {
        color: $warning;
        text-style: bold;
    }

    .permission-item.danger {
        color: $error;
    }

    .chat-instruction {
        text-align: center;
        color: $text;
        padding: 2;
    }

    .help-text {
        text-align: center;
        color: $text-secondary;
        padding: 0 2;
    }

    #header {
        dock: top;
        height: 3;
        background: $primary;
        align: center middle;
    }

    #footer {
        dock: bottom;
        height: 1;
        background: $primary;
        content-align: center middle;
    }

    TabbedContent Tab {
        background: $surface;
    }

    TabbedContent Tab.active {
        background: $primary;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit to CLI"),
        Binding("ctrl+c", "exit", "Exit"),
        Binding("1", "switch_tab('dashboard')", "Dashboard"),
        Binding("2", "switch_tab('sessions')", "Sessions"),
        Binding("3", "switch_tab('agents')", "Agents"),
        Binding("4", "switch_tab('permissions')", "Permissions"),
        Binding("5", "switch_tab('commands')", "Commands"),
        Binding("6", "switch_tab('chat')", "Chat"),
    ]

    def compose(self) -> ComposeResult:
        # Header
        yield Container(
            Static("🦔 Claw Code TUI", classes="header-title"),
            Static("│ q: Quit │ 1-6: Switch Tabs", classes="header-hint"),
            id="header"
        )

        # Tabbed content
        with TabbedContent():
            with Tab("Dashboard", id="tab-dashboard"):
                yield DashboardScreen()
            with Tab("Sessions", id="tab-sessions"):
                yield SessionsScreen()
            with Tab("Agents", id="tab-agents"):
                yield AgentsScreen()
            with Tab("Permissions", id="tab-permissions"):
                yield PermissionsScreen()
            with Tab("Commands", id="tab-commands"):
                yield CommandsScreen()
            with Tab("Chat", id="tab-chat"):
                yield ChatScreen()

        # Footer
        yield Container(
            Static("Arrow keys: Navigate │ Enter: Select │ n: New │ d: Delete │ r: Refresh", classes="footer-hint"),
            id="footer"
        )

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to a specific tab."""
        self.query_one(TabbedContent).active = tab_id.replace("tab-", "")

    def action_quit(self) -> None:
        """Quit to raw CLI."""
        self.exit()
        from services.claw_cli import claw_cli
        claw_cli.run_interactive()

    def action_exit(self) -> None:
        """Exit entirely."""
        self.exit()


def run_tui():
    """Run the TUI application."""
    app = ClawTUI()
    app.run()


if __name__ == "__main__":
    run_tui()