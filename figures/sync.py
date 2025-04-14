from utils import read_data, create_plot, style_plot, save_plot
import numpy as np
import matplotlib.pyplot as plt


def generate_sync_plot(color_palette, filename, directory, output_prefix):
    """Generate sync operations comparison plots with logarithmic scale

    Creates bar plots comparing the performance of synchronization operations between
    C, Rust, and Python implementations. The C implementation is used as a baseline (100%) and
    the Rust and Python implementations' performance is shown as a percentage relative to C.

    The plots include:
    - Grouped bars for each sync operation (C vs Rust vs Python)
    - Percentage labels on top of each bar
    - Grid lines for easier comparison
    - Bold labels and legend
    - Logarithmic y-axis scale to better handle extreme values

    Args:
        color_palette (list): List of colors for the plot, expects at least 3 colors:
                            - color_palette[0] for C implementation
                            - color_palette[1] for Rust implementation
                            - color_palette[2] for Python implementation
        filename (str): Name of the CSV file containing the sync operation data
        directory (str): Directory containing the data ('intranode' or 'internode')
        output_prefix (str): Prefix for the output filename:
                           - "local" for same-node measurements
                           - "net" for network measurements

    Returns:
        None. The plots are saved to disk as PDF files in the figures/sync directory.
    """
    # Read data from CSV file
    df = read_data(filename, directory)
    if df is None:
        return

    # Generate logarithmic scale plot
    generate_sync_plot_log_scale(color_palette, df, output_prefix)


def generate_sync_plot_log_scale(color_palette, df, output_prefix):
    """Generate sync plot with logarithmic y-axis scale

    Args:
        color_palette (list): List of colors for the plot
        df (pandas.DataFrame): DataFrame containing the data
        output_prefix (str): Prefix for the output filename
    """
    # Create the plot with wider figure for better visibility
    fig, ax = create_plot(figsize=(12, 6))

    # Set up bar positions with proper spacing
    routines = df["Routine"].values
    x = np.arange(len(routines))
    width = 0.25  # Width of bars for 3 implementations

    # Define simplified labels for the x-axis
    simplified_labels = []
    for routine in routines:
        # Remove "shmem_" prefix and extract the core operation name
        if routine.startswith("shmem_"):
            label = routine[6:]  # Remove "shmem_" prefix
        else:
            label = routine
            
        # Special case for atomic_compare_swap - rename to atomic_cswap
        if label == "atomic_compare_swap":
            label = "atomic_cswap"
            
        simplified_labels.append(label)

    # Create bars for C implementation (baseline)
    c_bars = ax.bar(
        x - width,
        [100] * len(routines),
        width,
        label="C (baseline)",
        color=color_palette[0],
        alpha=0.9,
    )

    # Create bars for Rust implementation (as percentage of C)
    rs_values = df["RS (normalized)"].values * 100
    rs_bars = ax.bar(
        x,
        rs_values,
        width,
        label="RS (% of C)",
        color=color_palette[1],
        alpha=0.9,
    )
    
    # Create bars for Python implementation (as percentage of C)
    py_values = df["Py (normalized)"].values * 100
    py_bars = ax.bar(
        x + width,
        py_values,
        width,
        label="Py (% of C)",
        color=color_palette[2],
        alpha=0.9,
    )

    # Customize the plot appearance
    ax.set_ylabel("Percentage (%)", fontsize=14, fontweight="bold", labelpad=15)

    # Set x-axis ticks and labels with rotation to prevent overlap
    ax.set_xticks(x)
    ax.set_xticklabels(simplified_labels, rotation=30, fontweight="bold", ha="right")

    # Set logarithmic scale for y-axis
    ax.set_yscale('log')
    # Ensure the bottom of the scale is at or slightly below 100%
    ax.set_ylim(bottom=50)
    
    # For log scale, customize tick labels
    yticks = ax.get_yticks()
    ax.set_yticklabels([f"{y:.0f}%" for y in yticks], fontweight="bold")
    
    # Add percentage labels with adjusted position for log scale
    add_percentage_labels_log(ax, x, width, df, color_palette, c_bars, rs_bars, py_bars)

    # Add horizontal grid lines and legend in the top left
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(frameon=True, fontsize=14, loc="upper left", prop={"weight": "bold"})

    # Save the plot to the appropriate directory
    save_plot(fig, f"sync_{output_prefix}.pdf", "sync")


def add_percentage_labels_log(ax, x, width, df, color_palette, c_bars, rs_bars, py_bars):
    """Add percentage labels on top of each bar for logarithmic scale

    Args:
        ax (matplotlib.axes.Axes): The axis to add labels to
        x (numpy.ndarray): X positions for the bars
        width (float): Width of each bar
        df (pandas.DataFrame): DataFrame containing the data
        color_palette (list): List of colors for the plot
        c_bars (matplotlib.container.BarContainer): C implementation bars
        rs_bars (matplotlib.container.BarContainer): Rust implementation bars
        py_bars (matplotlib.container.BarContainer): Python implementation bars
    """
    for i in range(len(x)):
        # Label for C baseline (always 100%)
        ax.text(
            x[i] - width,
            110,  # Place slightly above the bar in log scale
            "100.00%",
            ha="center",
            va="bottom",
            color=color_palette[0],
            fontweight="bold",
        )
        
        # Label for Rust implementation (calculated percentage)
        rs_val = df["RS (normalized)"].values[i] * 100
        rs_txt = f"{rs_val:.2f}%"
        ax.text(
            x[i],
            rs_val * 1.1,  # Place slightly above the bar
            rs_txt,
            ha="center",
            va="bottom",
            color=color_palette[1],
            fontweight="bold",
        )
        
        # Label for Python implementation (calculated percentage)
        py_val = df["Py (normalized)"].values[i] * 100
        py_txt = f"{py_val:.2f}%"
        ax.text(
            x[i] + width,
            py_val * 1.1,  # Place slightly above the bar
            py_txt,
            ha="center",
            va="bottom",
            color=color_palette[2],
            fontweight="bold",
        )


def generate_plots(color_palette):
    """Generate all sync-related plots

    Creates comparison plots for synchronization operations between C, Rust, and Python
    implementations for both local (same node) and network scenarios.

    The generated plots are saved as:
    - figures/sync/sync_local.pdf - Log-scale comparison for same-node operations
    - figures/sync/sync_net.pdf - Log-scale comparison for network operations

    Args:
        color_palette (list): List of colors for the plots, expects at least 3 colors:
                            - color_palette[0] for C implementation
                            - color_palette[1] for Rust implementation
                            - color_palette[2] for Python implementation

    Returns:
        None. All plots are saved to disk as PDF files.
    """
    # Generate plot for same-node measurements (intranode)
    generate_sync_plot(color_palette, "latency.csv", "intranode", "local")

    # Generate plot for network measurements (internode)
    generate_sync_plot(color_palette, "latency.csv", "internode", "net")
