"""
Printing utilities for rich console output.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Re-export for compatibility
__all__ = ["console", "Panel", "Table"]
