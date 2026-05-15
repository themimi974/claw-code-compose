#!/usr/bin/env python3
"""
Claw Code TUI - Entry Point

Usage:
    python3 main.py          # Launch TUI
    python3 main.py --cli    # Launch raw CLI instead
    python3 main.py --help   # Show help
"""

import sys
import os


def main():
    """Main entry point."""
    # Check for --cli flag to bypass TUI
    if "--cli" in sys.argv or "--raw" in sys.argv:
        print("Launching raw Claw Code CLI...")
        os.execvp("/usr/local/bin/claw", ["/usr/local/bin/claw"] + sys.argv[1:])

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("\nKeyboard shortcuts in TUI:")
        print("  1-6      Switch tabs")
        print("  Arrow keys Navigate lists")
        print("  Enter    Select/Switch")
        print("  n        New session")
        print("  d        Delete session")
        print("  r        Refresh")
        print("  q        Quit to CLI")
        print("  Ctrl+C   Exit entirely")
        sys.exit(0)

    # Add current directory to path for imports
    tui_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, tui_dir)

    # Import and run TUI
    from app import run_tui
    run_tui()


if __name__ == "__main__":
    main()