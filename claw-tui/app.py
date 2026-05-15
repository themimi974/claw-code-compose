#!/usr/bin/env python3
"""Claw Code TUI - Main application."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Footer, Button
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

    .header-title {
        text-style: bold;
        color: $text;
        padding: 0 1;
    }

    .header-hint {
        color: $text-muted;
        padding: 0 1;
    }

    .footer-hint {
        color: $text-muted;
        padding: 0 1;
    }

    #header {
        dock: top;
        height: 3;
        background: $primary;
        align: center middle;
    }

    #nav-bar {
        dock: top;
        height: auto;
        background: $primary;
        content-align: center middle;
    }

    .nav-button {
        margin: 0 1;
        min-width: 12;
    }

    .nav-button.active {
        background: $accent;
        color: $text;
    }

    #footer {
        dock: bottom;
        height: 1;
        background: $primary;
        content-align: center middle;
    }

    #content-area {
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit to CLI"),
        Binding("ctrl+c", "exit", "Exit"),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Prev Tab"),
        Binding("1", "goto_tab('dashboard')", "Dashboard"),
        Binding("2", "goto_tab('sessions')", "Sessions"),
        Binding("3", "goto_tab('agents')", "Agents"),
        Binding("4", "goto_tab('permissions')", "Permissions"),
        Binding("5", "goto_tab('commands')", "Commands"),
        Binding("6", "goto_tab('chat')", "Chat"),
    ]

    current_tab = "dashboard"
    tabs = ["dashboard", "sessions", "agents", "permissions", "commands", "chat"]

    def compose(self) -> ComposeResult:
        # Header
        yield Container(
            Static("🦔 Claw Code TUI", classes="header-title"),
            Static("│ q: Quit │ 1-6: Switch Tabs", classes="header-hint"),
            id="header"
        )

        # Navigation bar with tab names
        with Horizontal(id="nav-bar"):
            yield Button("1.Dashboard", id="nav-dashboard", classes="nav-button")
            yield Button("2.Sessions", id="nav-sessions", classes="nav-button")
            yield Button("3.Agents", id="nav-agents", classes="nav-button")
            yield Button("4.Permissions", id="nav-permissions", classes="nav-button")
            yield Button("5.Commands", id="nav-commands", classes="nav-button")
            yield Button("6.Chat", id="nav-chat", classes="nav-button")

        # Content area - show based on current tab
        yield Container(id="content-area")

        # Footer
        yield Container(
            Static("Arrow keys: Navigate │ Enter: Select │ n: New │ d: Delete │ r: Refresh", classes="footer-hint"),
            id="footer"
        )

    def on_mount(self) -> None:
        self.show_tab("dashboard")
        self.update_nav_buttons()

    def show_tab(self, tab_name: str) -> None:
        """Show the specified tab."""
        self.current_tab = tab_name
        content = self.query_one("#content-area", Container)
        
        # Clear content properly
        content.remove_children()
        
        # Update nav button styles
        self.update_nav_buttons()
        
        # Show appropriate screen
        if tab_name == "dashboard":
            content.mount(DashboardScreen())
        elif tab_name == "sessions":
            content.mount(SessionsScreen())
        elif tab_name == "agents":
            content.mount(AgentsScreen())
        elif tab_name == "permissions":
            content.mount(PermissionsScreen())
        elif tab_name == "commands":
            content.mount(CommandsScreen())
        elif tab_name == "chat":
            content.mount(ChatScreen())

    def update_nav_buttons(self) -> None:
        """Update navigation button styles to show active tab."""
        for btn in self.query(".nav-button"):
            btn_id = btn.id
            if btn_id:
                tab_name = btn_id.replace("nav-", "")
                if tab_name == self.current_tab:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")

    def action_goto_tab(self, tab_name: str) -> None:
        """Go to a specific tab."""
        self.show_tab(tab_name)

    def action_next_tab(self) -> None:
        """Go to the next tab."""
        current_idx = self.tabs.index(self.current_tab)
        next_idx = (current_idx + 1) % len(self.tabs)
        self.show_tab(self.tabs[next_idx])

    def action_prev_tab(self) -> None:
        """Go to the previous tab."""
        current_idx = self.tabs.index(self.current_tab)
        prev_idx = (current_idx - 1) % len(self.tabs)
        self.show_tab(self.tabs[prev_idx])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for navigation."""
        button_id = event.button.id
        if button_id:
            tab_name = button_id.replace("nav-", "")
            self.show_tab(tab_name)
            self.update_nav_buttons()

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