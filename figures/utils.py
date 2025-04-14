import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os


def setup_style():
    """Setup the common style elements for all plots

    Configures the global matplotlib style settings to ensure consistent appearance across
    all plots. This includes setting up a white grid style, selecting a colorblind-friendly
    palette, and configuring font sizes for various plot elements.

    Returns:
        list: A color palette containing colors suitable for colorblind viewers, where:
              - First color (index 0) is used for C implementation data
              - Second color (index 1) is used for Rust implementation data
              - Third color (index 2) is used for Python implementation data
    """
    sns.set(style="whitegrid", font_scale=1.5)
    color_palette = sns.color_palette("colorblind", 3)  # Get 3 colors for C, Rust, Python

    # Increase font sizes significantly
    plt.rc("font", size=16)  # Default font size
    plt.rc("axes", titlesize=18)  # Plot title size
    plt.rc("axes", labelsize=16)  # Axis label size
    plt.rc("xtick", labelsize=14)  # X-axis tick label size
    plt.rc("ytick", labelsize=14)  # Y-axis tick label size
    plt.rc("legend", fontsize=14)  # Legend font size

    return color_palette


def style_plot(ax, title, df, x_rotation=45):
    """Apply common styling to a plot

    Applies a consistent style to the provided matplotlib axis. This includes:
    - Setting up logarithmic x-axis scaling with base 2
    - Configuring x-axis ticks and labels to show message sizes in human-readable format
    - Formatting y-axis to use appropriate number formatting (regular or scientific)
    - Adding bold labels and gridlines
    - Configuring legend appearance and position
    - Adjusting plot margins and frame visibility

    Args:
        ax (matplotlib.axes.Axes): The axis to style
        title (str): The plot title (currently unused)
        df (pandas.DataFrame): The data frame containing the plot data (used for x-axis range)
        x_rotation (int): Rotation angle for x-axis labels, default is 45 degrees
    """
    ax.grid(True, which="both", linestyle="--", alpha=0.7)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Message Size (bytes)", fontsize=14, fontweight="bold")

    # Set x-ticks and labels in KB/MB format
    size_ticks = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512] + [
        1024,
        2048,
        4096,
        8192,
        16384,
        32768,
        65536,
        131072,
        262144,
        524288,
        1048576,
    ]
    size_labels = [
        "1",
        "2",
        "4",
        "8",
        "16",
        "32",
        "64",
        "128",
        "256",
        "512",
        "1K",
        "2K",
        "4K",
        "8K",
        "16K",
        "32K",
        "64K",
        "128K",
        "256K",
        "512K",
        "1MB",
    ]

    ax.set_xticks(size_ticks)
    ax.set_xticklabels(size_labels, rotation=x_rotation, fontweight="bold", ha="right")

    # Format y-axis based on current scale
    current_scale = ax.get_yscale()
    
    if current_scale == 'log':
        # For log scale, format ticks as powers of 10
        ax.yaxis.set_major_formatter(plt.ScalarFormatter())
        ax.yaxis.get_major_formatter().set_scientific(False)
        
        # Get current y-axis limits and extend them
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, 10 ** (np.ceil(np.log10(ymax))))

        # Make y-axis labels bold with power notation
        yticks = ax.get_yticks()
        from matplotlib.ticker import FixedLocator
        ax.yaxis.set_major_locator(FixedLocator(yticks))
        ax.set_yticklabels(
            [
                f"$\mathbf{{10^{{{int(np.log10(tick))}}}}}$" if tick > 0 else "0"
                for tick in yticks
            ]
        )
    else:
        # For linear scale, use regular bold labels
        ax.yaxis.set_major_formatter(plt.ScalarFormatter())
        ax.yaxis.get_major_formatter().set_scientific(False)
        yticks = ax.get_yticks()
        ax.set_yticklabels([f"${{\mathbf{{{tick:.0f}}}}}$" if tick % 1 == 0 else f"${{\mathbf{{{tick:.2f}}}}}$" 
                           for tick in yticks], fontweight="bold")

    # Style improvements with bold legend
    ax.legend(
        frameon=True,
        fontsize=14,
        loc="upper left",
        bbox_to_anchor=(0.02, 0.98),
        prop={"weight": "bold"},
    )

    # Style the grid with different appearances for major/minor gridlines
    ax.grid(True, which="major", color="gray", linestyle="-", alpha=0.15)
    ax.grid(True, which="minor", color="gray", linestyle=":", alpha=0.1)

    # Make the plot more compact
    ax.margins(x=0.02)  # Reduce horizontal margins

    # Adjust tick parameters
    ax.tick_params(axis="both", which="major", labelsize=14, pad=8)

    # Make the frame more visible
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(True)
    
    # Adjust bottom margin to accommodate rotated labels
    plt.tight_layout()


def read_data(filename, directory):
    """Read data from a CSV file containing benchmark results

    Attempts to read data from a specific CSV file in either intranode or internode directories.
    Prints the available columns in the CSV for debugging purposes.

    Args:
        filename (str): Name of the CSV file to read
        directory (str): Directory containing the file ('intranode' or 'internode')

    Returns:
        pandas.DataFrame: The loaded data frame if successful, None if an error occurs
    """
    try:
        filepath = os.path.join("data", directory, filename)
        df = pd.read_csv(filepath)
        print(f"Columns in {filepath}:", df.columns.tolist())
        return df
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None


def create_plot(figsize=(10, 4), dpi=300):
    """Create a new figure and axis with common settings

    Creates a new matplotlib figure and axis with specified dimensions and resolution.
    Used as a starting point for all plots in the benchmark visualization.

    Args:
        figsize (tuple): Figure dimensions (width, height) in inches, defaults to (10, 4)
        dpi (int): Dots per inch for the figure, defaults to 300 for high resolution

    Returns:
        tuple: (matplotlib.figure.Figure, matplotlib.axes.Axes) The created figure and axes objects
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    return fig, ax


def save_plot(fig, filename, category, dpi=300):
    """Save the plot with common settings

    Saves the provided matplotlib figure to a PDF file in a category-specific subdirectory.
    Creates the directory structure if it doesn't exist.

    Args:
        fig (matplotlib.figure.Figure): The figure to save
        filename (str): Name of the output file
        category (str): Category subdirectory (e.g., 'get', 'put', 'sync')
        dpi (int): Dots per inch for the saved figure, defaults to 300
    """
    category_dir = os.path.join("figures", category)
    os.makedirs(category_dir, exist_ok=True)
    filepath = os.path.join(category_dir, filename)
    fig.savefig(filepath, format="pdf", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
