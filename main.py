#!/usr/bin/env python3
"""
Atlas AI Assistant - Main Entry Point

This file serves as a compatibility layer for scripts that still use the
old entry point. It simply imports and runs the main function from the
atlas package.

For new development, use `python -m atlas.main` directly.
"""

if __name__ == "__main__":
    from atlas.main import main

    main()
