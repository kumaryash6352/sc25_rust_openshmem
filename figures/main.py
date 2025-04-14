import get
import put
import sync
import shutil
import os
from utils import setup_style


def clean_figures_directory():
    """Remove and recreate the figures directory

    This function ensures a clean slate for generating new figures by:
    1. Removing the existing figures directory and all its contents
    2. Creating a fresh empty figures directory

    The removal is done safely with ignore_errors=True to handle cases where
    the directory doesn't exist or files are locked.
    """
    shutil.rmtree("figures", ignore_errors=True)
    os.makedirs("figures", exist_ok=True)


def main():
    """Main entry point for generating benchmark visualization plots

    This function orchestrates the entire plot generation process:
    1. Cleans up any existing figures to avoid mixing old and new plots
    2. Sets up consistent plotting styles and color schemes
    3. Generates all benchmark comparison plots:
       - get operations (latency and bandwidth)
       - put operations (latency and bandwidth)
       - sync operations (local and network comparisons)

    The plots compare performance between C, Rust, and Python implementations,
    using data from CSV files in the data directory. All generated plots are 
    saved as PDF files in category-specific subdirectories under ./figures/
    """
    # Clean up existing figures
    clean_figures_directory()

    # Setup the plotting style and get colorblind-friendly palette
    color_palette = setup_style()

    # Generate all benchmark comparison plots
    get.generate_plots(color_palette)  # Get operation comparisons
    put.generate_plots(color_palette)  # Put operation comparisons
    sync.generate_plots(color_palette)  # Sync operations comparisons


if __name__ == "__main__":
    main()
