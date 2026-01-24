"""
Visualization utilities for architecture diagrams and reports.
"""

from typing import Optional


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def generate_ascii_diagram(
    channels: list[str],
    hosting: str,
    llm: str,
    database: str = "SQLite",
) -> str:
    """
    Generate ASCII architecture diagram.

    Args:
        channels: List of channel names
        hosting: Hosting provider name
        llm: LLM model name
        database: Database name

    Returns:
        ASCII diagram as string
    """
    # Truncate channel list if too long
    if len(channels) > 3:
        channels_display = ", ".join(channels[:3]) + "..."
    else:
        channels_display = ", ".join(channels)

    diagram = f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHATBOT ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────────┐                                                         │
│    │  CUSTOMERS   │                                                         │
│    └──────┬───────┘                                                         │
│           │                                                                 │
│           ▼                                                                 │
│    ┌──────────────────────────────────────────────────┐                     │
│    │              CHANNEL APIs                        │                     │
│    │  {channels_display:^46}  │                     │
│    └──────────────────────────┬───────────────────────┘                     │
│                               │                                             │
│                               ▼                                             │
│    ┌──────────────────────────────────────────────────┐                     │
│    │           WEBHOOK SERVER ({hosting:^20})       │                     │
│    │                                                  │                     │
│    │  ┌────────────────────────────────────────────┐  │                     │
│    │  │              n8n Orchestrator              │  │                     │
│    │  │           (Free, Self-Hosted)              │  │                     │
│    │  └─────────────────┬──────────────────────────┘  │                     │
│    │                    │                             │                     │
│    │     ┌──────────────┼──────────────┐              │                     │
│    │     │              │              │              │                     │
│    │     ▼              ▼              ▼              │                     │
│    │  ┌──────┐    ┌──────────┐   ┌──────────┐         │                     │
│    │  │ {llm[:6]:^6} │    │  Python  │   │ {database:^8} │         │                     │
│    │  │  LLM │    │ Backend  │   │    DB    │         │                     │
│    │  └──────┘    └──────────┘   └──────────┘         │                     │
│    │                                                  │                     │
│    └──────────────────────────────────────────────────┘                     │
│                               │                                             │
│                               ▼                                             │
│    ┌──────────────────────────────────────────────────┐                     │
│    │                   RESPONSE                       │                     │
│    │              → Customer Device                   │                     │
│    └──────────────────────────────────────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""
    return diagram


def generate_cost_chart(
    costs: list[tuple[str, float]],
    title: str = "Monthly Cost Breakdown",
    max_width: int = 40,
) -> str:
    """
    Generate ASCII bar chart for costs.

    Args:
        costs: List of (label, amount) tuples
        title: Chart title
        max_width: Maximum bar width in characters

    Returns:
        ASCII chart as string
    """
    if not costs:
        return "No costs to display."

    # Filter out zero costs for display
    nonzero_costs = [(label, amount) for label, amount in costs if amount > 0]
    if not nonzero_costs:
        nonzero_costs = costs[:3]  # Show at least first 3

    max_amount = max(amount for _, amount in nonzero_costs) if nonzero_costs else 1
    max_label_len = max(len(label) for label, _ in nonzero_costs)

    lines = [
        f"╔{'═' * (max_label_len + max_width + 15)}╗",
        f"║ {title:^{max_label_len + max_width + 13}} ║",
        f"╠{'═' * (max_label_len + max_width + 15)}╣",
    ]

    for label, amount in nonzero_costs:
        bar_length = int((amount / max_amount) * max_width) if max_amount > 0 else 0
        bar = "█" * bar_length
        lines.append(
            f"║ {label:<{max_label_len}} │{bar:<{max_width}}│ ${amount:>7.2f} ║"
        )

    # Total
    total = sum(amount for _, amount in costs)
    lines.extend([
        f"╠{'═' * (max_label_len + max_width + 15)}╣",
        f"║ {'TOTAL':<{max_label_len}} │{' ' * max_width}│ ${total:>7.2f} ║",
        f"╚{'═' * (max_label_len + max_width + 15)}╝",
    ])

    return "\n".join(lines)


def generate_timeline_chart(
    phases: list[tuple[str, int]],
    title: str = "Implementation Timeline",
) -> str:
    """
    Generate ASCII timeline/Gantt chart.

    Args:
        phases: List of (phase_name, duration_weeks) tuples
        title: Chart title

    Returns:
        ASCII timeline chart
    """
    if not phases:
        return "No phases to display."

    total_weeks = sum(weeks for _, weeks in phases)
    max_name_len = max(len(name) for name, _ in phases)

    lines = [
        title,
        "=" * (max_name_len + total_weeks * 3 + 10),
        "",
        " " * (max_name_len + 2) + "".join(f"W{i+1:<2}" for i in range(total_weeks)),
        " " * (max_name_len + 2) + "─" * (total_weeks * 3),
    ]

    current_week = 0
    for name, weeks in phases:
        bar = " " * (current_week * 3) + "█" * (weeks * 3)
        bar = bar.ljust(total_weeks * 3)
        lines.append(f"{name:<{max_name_len}} │{bar}│")
        current_week += weeks

    lines.append(" " * (max_name_len + 2) + "─" * (total_weeks * 3))

    return "\n".join(lines)


def generate_comparison_table(
    data: dict[str, dict],
    columns: list[str],
    title: str = "Comparison",
) -> str:
    """
    Generate ASCII comparison table.

    Args:
        data: Dict of {row_name: {column: value}}
        columns: List of column names to display
        title: Table title

    Returns:
        ASCII table
    """
    if not data:
        return "No data to display."

    # Calculate column widths
    row_names = list(data.keys())
    max_row_name = max(len(name) for name in row_names)

    col_widths = {}
    for col in columns:
        values = [str(data[row].get(col, "")) for row in row_names]
        col_widths[col] = max(len(col), max(len(v) for v in values))

    # Build table
    total_width = max_row_name + sum(col_widths.values()) + len(columns) * 3 + 4

    lines = [
        "┌" + "─" * (total_width - 2) + "┐",
        "│" + title.center(total_width - 2) + "│",
        "├" + "─" * (total_width - 2) + "┤",
    ]

    # Header row
    header = "│ " + " " * max_row_name + " │"
    for col in columns:
        header += f" {col:^{col_widths[col]}} │"
    lines.append(header)

    # Separator
    sep = "├─" + "─" * max_row_name + "─┼"
    for col in columns:
        sep += "─" * (col_widths[col] + 2) + "┼"
    lines.append(sep[:-1] + "┤")

    # Data rows
    for row_name in row_names:
        row = f"│ {row_name:<{max_row_name}} │"
        for col in columns:
            value = str(data[row_name].get(col, ""))
            row += f" {value:>{col_widths[col]}} │"
        lines.append(row)

    lines.append("└" + "─" * (total_width - 2) + "┘")

    return "\n".join(lines)
