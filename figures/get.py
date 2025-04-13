from utils import read_data, create_plot, style_plot, save_plot


def generate_latency_plot(color_palette, filename, directory, output_prefix):
    """Generate latency plots for get operations with both linear and log scales

    Creates plots comparing latency between C, Rust, and Python implementations of shmem_get operations.
    Generates two versions of each plot:
    1. With linear y-axis scaling
    2. With logarithmic y-axis scaling

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
        None. The plots are saved to disk as PDF files.
    """
    # Read data
    df = read_data(filename, directory)
    if df is None:
        return

    # Generate linear scale plot
    generate_latency_plot_with_scale(color_palette, df, output_prefix, scale="linear")
    
    # Generate log scale plot
    generate_latency_plot_with_scale(color_palette, df, output_prefix, scale="log")


def generate_latency_plot_with_scale(color_palette, df, output_prefix, scale):
    """Helper function to generate latency plot with specified y-axis scale

    Args:
        color_palette (list): List of colors for the plot
        df (pandas.DataFrame): DataFrame containing the data
        output_prefix (str): Prefix for the output filename
        scale (str): Y-axis scale, either "linear" or "log"
    """
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

    # Set y-axis scale
    ax.set_yscale(scale)
    ax.set_ylabel("Latency (μs)", fontsize=14, fontweight="bold", labelpad=15)
    style_plot(ax, "shmem_get Latency", df)

    # Save the plot with scale indicator in filename
    scale_suffix = "_log" if scale == "log" else "_linear"
    save_plot(fig, f"get_{output_prefix}_latency{scale_suffix}.pdf", "get")


def generate_bandwidth_plot(color_palette, filename, directory, output_prefix):
    """Generate bandwidth plots for get operations with both linear and log scales

    Creates plots comparing bandwidth between C, Rust, and Python implementations of shmem_get operations.
    Generates two versions of each plot:
    1. With linear y-axis scaling
    2. With logarithmic y-axis scaling

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
        None. The plots are saved to disk as PDF files.
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

    # Generate linear scale plot
    generate_bandwidth_plot_with_scale(color_palette, df, output_prefix, scale="linear")
    
    # Generate log scale plot
    generate_bandwidth_plot_with_scale(color_palette, df, output_prefix, scale="log")


def generate_bandwidth_plot_with_scale(color_palette, df, output_prefix, scale):
    """Helper function to generate bandwidth plot with specified y-axis scale

    Args:
        color_palette (list): List of colors for the plot
        df (pandas.DataFrame): DataFrame containing the data
        output_prefix (str): Prefix for the output filename
        scale (str): Y-axis scale, either "linear" or "log"
    """
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

    # Set y-axis scale
    ax.set_yscale(scale)
    ax.set_ylabel("Bandwidth (MiB/s)", fontsize=14, fontweight="bold", labelpad=15)
    style_plot(ax, "shmem_get Bandwidth", df)

    # Save the plot with scale indicator in filename
    scale_suffix = "_log" if scale == "log" else "_linear"
    save_plot(fig, f"get_{output_prefix}_bandwidth{scale_suffix}.pdf", "get")


def generate_plots(color_palette):
    """Generate all get-related plots

    Creates a complete set of plots comparing C, Rust, and Python implementations of shmem_get operations.
    Generates both latency and bandwidth plots for:
    - Local (same node) operations
    - Network (across nodes) operations
    
    For each plot, both linear and logarithmic y-axis scales are generated.

    The plots are saved in the 'figures/get' directory with appropriate filenames:
    - get_local_latency_linear.pdf / get_local_latency_log.pdf
    - get_local_bandwidth_linear.pdf / get_local_bandwidth_log.pdf
    - get_net_latency_linear.pdf / get_net_latency_log.pdf
    - get_net_bandwidth_linear.pdf / get_net_bandwidth_log.pdf

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
