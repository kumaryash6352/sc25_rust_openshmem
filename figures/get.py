from utils import read_data, create_plot, style_plot, save_plot


def generate_latency_plot(color_palette, filename, directory, output_prefix):
    """Generate latency plot for get operations with logarithmic scale

    Creates a plot comparing latency between C, Rust, and Python implementations of shmem_get operations
    using logarithmic y-axis scaling for better visualization of performance differences.

    Args:
        color_palette (list): List of colors for the plot, expects at least 3 colors:
                            - color_palette[0] for C implementation
                            - color_palette[1] for Rust implementation
                            - color_palette[2] for Python implementation
        filename (str): Name of the CSV file to read data from
        directory (str): Directory containing the data ('intranode' or 'internode')
        output_prefix (str): Prefix for the output filename, either "local" for same-node
                           measurements or "net" for network measurements

    Returns:
        None. The plot is saved to disk as a PDF file.
    """
    # Read data
    df = read_data(filename, directory)
    if df is None:
        return

    # Create the plot
    fig, ax = create_plot()

    # Plot C implementation with circle markers
    ax.plot(
        df["Msg Size (b)"],
        df["C (raw, us)"],
        "o-",
        color=color_palette[0],
        label="C",
        linewidth=3,
        markersize=8,
        markeredgewidth=2,
    )

    # Plot RS implementation with x markers
    ax.plot(
        df["Msg Size (b)"],
        df["RS (raw, us)"],
        "x-",
        color=color_palette[1],
        label="RS",
        linewidth=3,
        markersize=8,
        markeredgewidth=2,
    )
    
    # Plot Python implementation with square markers
    ax.plot(
        df["Msg Size (b)"],
        df["Py (raw, us)"],
        "s-",
        color=color_palette[2],
        label="Py",
        linewidth=3,
        markersize=8,
        markeredgewidth=2,
    )

    # Set y-axis to logarithmic scale
    ax.set_yscale("log")
    ax.set_ylabel("Latency (μs)", fontsize=14, fontweight="bold", labelpad=15)
    
    # Style the plot with increased x-axis label rotation to prevent overlap
    style_plot(ax, "shmem_get Latency", df, x_rotation=30)

    # Save the plot
    save_plot(fig, f"get_{output_prefix}_latency.pdf", "get")


def generate_bandwidth_plot(color_palette, filename, directory, output_prefix):
    """Generate bandwidth plot for get operations with logarithmic scale

    Creates a plot comparing bandwidth between C, Rust, and Python implementations of shmem_get operations
    using logarithmic y-axis scaling for better visualization of performance differences.

    Args:
        color_palette (list): List of colors for the plot, expects at least 3 colors:
                            - color_palette[0] for C implementation
                            - color_palette[1] for Rust implementation
                            - color_palette[2] for Python implementation
        filename (str): Name of the CSV file to read data from
        directory (str): Directory containing the data ('intranode' or 'internode')
        output_prefix (str): Prefix for the output filename, either "local" for same-node
                           measurements or "net" for network measurements

    Returns:
        None. The plot is saved to disk as a PDF file.
    """
    # Read data
    df = read_data(filename, directory)
    if df is None:
        return
        
    # Calculate bandwidth metrics if they are not already in the CSV
    if "C MiBPS" not in df.columns:
        # Calculate bandwidth in MiB/s: (size in bytes) / (latency in μs) * conversion factor
        # size / (latency * 10^-6) / (2^20) = size / latency * 10^6 / 2^20
        df["C MiBPS"] = df["Msg Size (b)"] / df["C (raw, us)"] * 0.95367431640625
        df["RS MiBPS"] = df["Msg Size (b)"] / df["RS (raw, us)"] * 0.95367431640625
        df["Py MiBPS"] = df["Msg Size (b)"] / df["Py (raw, us)"] * 0.95367431640625

    # Create the plot
    fig, ax = create_plot()

    # Plot C implementation with circle markers
    ax.plot(
        df["Msg Size (b)"],
        df["C MiBPS"],
        "o-",
        color=color_palette[0],
        label="C",
        linewidth=3,
        markersize=8,
        markeredgewidth=2,
    )

    # Plot RS implementation with x markers
    ax.plot(
        df["Msg Size (b)"],
        df["RS MiBPS"],
        "x-",
        color=color_palette[1],
        label="RS",
        linewidth=3,
        markersize=8,
        markeredgewidth=2,
    )
    
    # Plot Python implementation with square markers
    ax.plot(
        df["Msg Size (b)"],
        df["Py MiBPS"],
        "s-",
        color=color_palette[2],
        label="Py",
        linewidth=3,
        markersize=8,
        markeredgewidth=2,
    )

    # Set y-axis to logarithmic scale
    ax.set_yscale("log")
    ax.set_ylabel("Bandwidth (MiB/s)", fontsize=14, fontweight="bold", labelpad=15)
    
    # Style the plot with increased x-axis label rotation to prevent overlap
    style_plot(ax, "shmem_get Bandwidth", df, x_rotation=30)

    # Save the plot
    save_plot(fig, f"get_{output_prefix}_bandwidth.pdf", "get")


def generate_plots(color_palette):
    """Generate all get-related plots

    Creates a complete set of plots comparing C, Rust, and Python implementations of shmem_get operations.
    Generates both latency and bandwidth plots for:
    - Local (same node) operations
    - Network (across nodes) operations

    The plots are saved in the 'figures/get' directory with appropriate filenames:
    - get_local_latency.pdf
    - get_local_bandwidth.pdf
    - get_net_latency.pdf
    - get_net_bandwidth.pdf

    Args:
        color_palette (list): List of colors for the plots, expects at least 3 colors:
                            - color_palette[0] for C implementation
                            - color_palette[1] for Rust implementation
                            - color_palette[2] for Python implementation

    Returns:
        None. All plots are saved to disk as PDF files.
    """
    # Generate local plots (intranode)
    generate_latency_plot(color_palette, "bw_shmem_get.csv", "intranode", "local")
    generate_bandwidth_plot(color_palette, "bw_shmem_get.csv", "intranode", "local")

    # Generate network plots (internode)
    generate_latency_plot(color_palette, "bw_shmem_get.csv", "internode", "net")
    generate_bandwidth_plot(color_palette, "bw_shmem_get.csv", "internode", "net")
