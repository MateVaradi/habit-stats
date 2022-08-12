from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import to_rgb as hex_to_rgb
from matplotlib.colors import to_hex as rgb_to_hex
import seaborn as sns
import numpy as np


def generate_color_dict(items):
    """
    Generate dictionary of colors from list of items.

    Parameters
    ----------
    items: list
        List of items to be colored consistently
    """

    n_colors = len(items)
    if n_colors == 5:
        # default colors I usually use
        colors = ["#FA8879", "#96C8DF", "#BCE4CF", "#F9E031", "#C3D3D1"]
    else:
        pal = sns.color_palette("Set3", n_colors=n_colors)
        colors = pal.as_hex()
    color_dict = dict(zip(items, colors))

    return color_dict


# Aesthetic settings
def get_binary_cmap(color1, color2="#DCDCDC"):
    """
    Creates binary colormap of two colors
    """
    bin_cmap = LinearSegmentedColormap.from_list("bin_cmap", [color1, color2], N=2)
    return bin_cmap


def make_opaque(color, opacity):
    """
    Converts color to a more opaque version.

    Parameters
    ----------
    color : string or tuple
        Color to be adjusted. If string it should be a hex code. If tuple it should be a length 3 tuple of RGB channels (absolute or relative).
    opacity: int or float
        Opacity level. If int, should be a percentage between 0 and 100. If float, should be between 0 and 1.

    Returns
    -------
    adjusted_color : string or tuple
        Adjusted color in same format as input

    Examples
    --------
    >>> make_opaque("#c3d3d1", opacity=0.5)
    >>> "#e1e9e8"
    """
    from matplotlib.colors import to_rgb as hex_to_rgb
    from matplotlib.colors import to_hex as rgb_to_hex

    # if hex convert to rgb
    if isinstance(color, str):
        input_type = "hex"
    elif len(color) == 3 and all(c <= 1 for c in color):
        input_type = "rgb_0_1"
    elif len(color) == 3 and all(c <= 255 for c in color):
        input_type = "rgb_0_255"
    else:
        raise ValueError(
            f"Color ({color}) not recognized. It should be a 7 digit string or a length 3 tuple of RGB codes"
        )

    if opacity >= 0 and opacity <= 1:
        opacity = opacity
    elif opacity >= 0 and opacity <= 100:
        opacity = opacity / 100
    else:
        raise ValueError(
            f"Opacity ({opacity}) should be a a value between 0 and 1 or a percentage."
        )

    # convert to array of 0-255 rgb values
    if input_type == "hex":
        rgb_array = np.array(hex_to_rgb(color)) * 255
    elif input_type == "rgb_0_1":
        rgb_array = np.array(color) * 255
    elif input_type == "rgb_0_255":
        rgb_array = np.array(color)

    # make adjustment
    adjusted_color = opacity * rgb_array + (1 - opacity) * 255

    # convert back to input format
    if input_type == "hex":
        adjusted_color = rgb_to_hex(adjusted_color / 255)
    elif input_type == "rgb_0_1":
        adjusted_color = adjusted_color / 255
    elif input_type == "rgb_0_255":
        adjusted_color = adjusted_color

    return adjusted_color


def get_linear_cmap(color, n_colors=7, color_for_zero=None):
    opacities = np.linspace(0.1, 1, n_colors)
    colors = [make_opaque(color, o) for o in opacities]
    if color_for_zero:
        colors = [color_for_zero] + colors
    else:
        colors = ["white"] + colors
    linear_cmap = LinearSegmentedColormap.from_list(
        "linear_cmap", colors, N=n_colors + 1
    )
    return linear_cmap
