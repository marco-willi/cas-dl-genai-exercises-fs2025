"""Visualization Functions."""
import math
from textwrap import wrap

import numpy as np
import torch
from matplotlib import pyplot as plt
from PIL import Image
from torchvision.transforms.v2 import functional as TF


def plot_collage(
    images: list[torch.Tensor | Image.Image],
    captions: list[str] | None = None,
    row_labels: list[str] | None = None,
    col_labels: list[str] | None = None,
    col_labels_position: str = "top",  # 'top' or 'bottom'
    nrows: int | None = None,
    ncols: int | None = None,
    caption_width: int | None = 30,
    caption_font_size: int = 10,
    global_normalize: bool = False,
    figsize: tuple[int, int] | None = None,
    title: str | None = None,
    axes_iteration_order: str = "C",  # 'C' for C-style (row-major), 'F' for Fortran-style (column-major)
):
    """Plot a collage of images with optional captions and row labels in a grid of specified rows and columns."""

    num_images = len(images)

    # If nrows and ncols are not specified, create a square grid
    if nrows is None or ncols is None:
        nrows = ncols = math.ceil(math.sqrt(num_images))

    total_cells = nrows * ncols

    # Convert tensors to PIL images if needed
    pil_images = [TF.to_pil_image(img) if isinstance(img, torch.Tensor) else img for img in images]

    if global_normalize:
        # Find global min and max across all PIL images for normalization
        all_images = np.concatenate([np.array(img).flatten() for img in pil_images])
        vmin, vmax = all_images.min(), all_images.max()
    else:
        vmin, vmax = 0.0, 255.0

    if figsize is None:
        figsize = (ncols * 2, nrows * 2)

    # Create the figure for the collage
    fig, axes = plt.subplots(
        figsize=figsize,
        nrows=nrows,
        ncols=ncols,
    )

    if title:
        plt.suptitle(title, fontsize=20)

    # Flatten axes for easier iteration
    axes1d = axes.flatten(order=axes_iteration_order)

    for i, ax in enumerate(axes1d):
        if i < num_images:
            ax.imshow(np.array(pil_images[i]), vmin=vmin, vmax=vmax)

    # Set Captions
    if captions is not None:
        for i, ax in enumerate(axes1d):
            if i < len(captions):
                caption = captions[i]
                if caption_width is not None:
                    caption = "\n".join(wrap(caption, caption_width))
                if col_labels_position == "top":
                    ax.set_title(captions[i], fontsize=caption_font_size)
                elif col_labels_position == "bottom":
                    ax.set_xlabel(captions[i], fontsize=caption_font_size)

    # Format axes
    for i, ax in enumerate(axes1d):
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        ax.yaxis.set_ticks([])
        ax.xaxis.set_ticks([])
        if i >= num_images:
            ax.axis("off")

    # Add column labels at the top
    if col_labels is not None:
        for col_idx, label in enumerate(col_labels):
            if col_idx < ncols:
                axes[0, col_idx].set_title(label, fontsize=12, pad=20)

    # Add row labels at the start of each row
    if row_labels is not None:
        for row_idx, label in enumerate(row_labels):
            if row_idx < nrows:
                axes[row_idx, 0].set_ylabel(label, rotation=90, size="large", labelpad=20)

    return fig, axes
