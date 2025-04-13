from utils import read_data, create_plot, style_plot, save_plot
import numpy as np


def generate_sync_plot(color_palette, filename, directory, output_prefix):
    """Generate sync operations comparison plots with different y-axis ranges

    Creates bar plots comparing the performance of synchronization operations between
    C, Rust, and Python implementations. The C implementation is used as a baseline (100%) and
    the Rust and Python implementations' performance is shown as a percentage relative to C.

    Generates two versions of each plot:
    1. With a standard y-axis range (0-150%)
    2. With an extended y-axis range to show all data points

    The plots include:
    - Grouped bars for each sync operation (C vs Rust vs Python)
    - Percentage labels on top of each bar
    - Grid lines for easier comparison
    - Bold labels and legend

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

    # Generate standard scale plot (fixed at 0-150%)
    generate_sync_plot_with_scale(color_palette, df, output_prefix, scale_type="standard")
    
    # Generate extended scale plot (adapts to data)
    generate_sync_plot_with_scale(color_palette, df, output_prefix, scale_type="extended")


def generate_sync_plot_with_scale(color_palette, df, output_prefix, scale_type):
    """Helper function to generate sync plot with specified y-axis scale

    Args:
        color_palette (list): List of colors for the plot
        df (pandas.DataFrame): DataFrame containing the data
        output_prefix (str): Prefix for the output filename
        scale_type (str): Y-axis scale type, either "standard" or "extended"
    """
    # Create the plot with wider figure for better visibility
    fig, ax = create_plot(figsize=(12, 6))

    # Set up bar positions with proper spacing
    routines = df["Routine"].values
    x = np.arange(len(routines))
    width = 0.25  # Width of bars for 3 implementations

    # Create bars for C implementation (baseline)
    ax.bar(
        x - width,
        [100] * len(routines),
        width,
        label="C (baseline)",
        color=color_palette[0],
        alpha=0.9,
    )

    # Create bars for Rust implementation (as percentage of C)
    ax.bar(
        x,
        df["RS (normalized)"].values * 100,
        width,
        label="RS (% of C)",
        color=color_palette[1],
        alpha=0.9,
    )
    
    # Create bars for Python implementation (as percentage of C)
    ax.bar(
        x + width,
        df["Py (normalized)"].values * 100,
        width,
        label="Py (% of C)",
        color=color_palette[2],
        alpha=0.9,
    )

    # Customize the plot appearance
    ax.set_ylabel("Percentage (%)", fontsize=14, fontweight="bold", labelpad=15)

    # Set x-axis ticks and labels
    ax.set_xticks(x)
    ax.set_xticklabels(routines, rotation=0, fontweight="bold", ha="center")

    # Add percentage labels on top of each bar
    for i in x:
        # Label for C baseline (always 100%)
        ax.text(
            i - width,
            100,
            "100.00%",
            ha="center",
            va="bottom",
            color=color_palette[0],
            fontweight="bold",
        )
        # Label for Rust implementation (calculated percentage)
        rs_val = f"{df['RS (normalized)'].values[i] * 100:.2f}%"
        ax.text(
            i,
            df["RS (normalized)"].values[i] * 100,
            rs_val,
            ha="center",
            va="bottom",
            color=color_palette[1],
            fontweight="bold",
        )
        # Label for Python implementation (calculated percentage)
        py_val = f"{df['Py (normalized)'].values[i] * 100:.2f}%"
        ax.text(
            i + width,
            df["Py (normalized)"].values[i] * 100,
            py_val,
            ha="center",
            va="bottom",
            color=color_palette[2],
            fontweight="bold",
        )

    # Set y-axis range based on scale type
    if scale_type == "standard":
        # Fixed range of 0-150% for standard scale
        y_max = 150
    else:  # extended scale
        # Calculate y-axis upper limit based on maximum value
        # Add 20% margin above the maximum value
        max_value = max(df["Py (normalized)"].max(), df["RS (normalized)"].max()) * 100
        y_max = max(150, max_value * 1.2)  # At least 150%
    
    # Configure y-axis range and tick labels
    ax.set_ylim(0, y_max)
    ax.set_yticks(np.arange(0, y_max + 1, 25))
    ax.set_yticklabels([f"{x:.2f}%" for x in np.arange(0, y_max + 1, 25)], fontweight="bold")

    # Add horizontal grid lines and legend
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(frameon=True, fontsize=14, loc="upper right", prop={"weight": "bold"})

    # Save the plot to the appropriate directory
    scale_suffix = "_standard" if scale_type == "standard" else "_extended"
    save_plot(fig, f"sync_{output_prefix}{scale_suffix}.pdf", "sync")


def generate_plots(color_palette):
    """Generate all sync-related plots

    Creates comparison plots for synchronization operations between C, Rust, and Python
    implementations for both local (same node) and network scenarios.

    For each scenario, two versions of the plot are generated:
    1. With a standard y-axis range (0-150%)
    2. With an extended y-axis range to show all data points

    The generated plots are saved as:
    - figures/sync/sync_local_standard.pdf / sync_local_extended.pdf
    - figures/sync/sync_net_standard.pdf / sync_net_extended.pdf

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
