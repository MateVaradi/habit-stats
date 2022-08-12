import numpy as np
import matplotlib.pyplot as plt
import july
from july.utils import date_range
import seaborn as sns
import pandas as pd

from habitstats.aesthetics import get_binary_cmap, get_linear_cmap


def heatmap_per_habit(data, habit, color, title=None):
    # Prepare data
    dates = date_range(data.date.min(), data.date.max())
    habit_array = np.array(
        [1 if d in data.loc[data.habit == habit, "date"].values else 0 for d in dates]
    )
    # Create plot
    ax = july.heatmap(
        dates,
        habit_array,
        title=title,
        cmap=get_binary_cmap(color),
        fontfamily="sans-serif",
        fontsize=12,
    )
    return ax


def get_grid(data, by="week"):
    if by == "week":
        grid_df = (
            data.groupby(["week", "habit"])["month"]
            .count()
            .reset_index()
            .rename(columns={"month": "count"})
            .pivot(index="week", columns="habit", values="count")
        )
        grid_df = grid_df.reindex(range(0, 53), axis=0)
    elif by == "month":
        grid_df = (
            data.groupby(["month", "habit"])["week"]
            .count()
            .reset_index()
            .rename(columns={"week": "count"})
            .pivot(index="month", columns="habit", values="count")
        )
        grid_df = grid_df.reindex(range(1, 13), axis=0)
    return grid_df


def heatmap_all_habits(
    data,
    by="week",
    colors=None,
    labels=False,
    label_format="{:0.0f}",
    title=None,
):
    # Prepare data for plot
    grid_df = get_grid(data, by)
    habits = grid_df.columns
    p = len(habits)
    vmax = 7 if by == "week" else 31

    # Prepare aesthetics
    fontsize = 8 if by == "week" else 12
    if colors is None:
        pal = sns.color_palette("Set3", n_colors=p)
        color_list = pal.as_hex()
        colors = dict(zip(habits, color_list))

    # Create plot
    fig, axes = plt.subplots(p, 1, figsize=(12, 5), dpi=100)
    for habit, ax in zip(habits, axes):
        cal = grid_df[habit].values.reshape(1, -1)
        cal = np.nan_to_num(cal)
        n = cal.shape[1]

        pc = ax.pcolormesh(
            cal,
            edgecolors="white",
            linewidth=0.25,
            cmap=get_linear_cmap(colors[habit], n_colors=vmax),
            vmin=0,
        )
        ax.invert_yaxis()
        ax.set_frame_on(False)
        ax.set_xticks([])
        ax.set_yticks([0.5])
        ax.set_yticklabels(labels=habit, fontsize=fontsize)
        ax.set_xticklabels([])
        if labels:
            for (i, j), z in np.ndenumerate(cal):
                if np.isfinite(z) and z > 0:
                    ax.text(
                        j + 0.5,
                        i + 0.5,
                        label_format.format(z),
                        ha="center",
                        va="center",
                        fontsize=fontsize - 3,
                    )

    axes[-1].set_xticks(list(np.array(range(0, n)) + 0.5))
    axes[-1].set_xticklabels(labels=list(range(1, n + 1)), fontsize=fontsize)
    axes[-1].set_xlabel(by.capitalize())
    axes[int(p / 2)].set_ylabel("Habit")
    plt.subplots_adjust(hspace=0.05)
    if title:
        axes[0].set_title(title)


def stacked_barplot(
    data,
    x,
    y,
    hue,
    orient="v",
    ax=None,
    color=None,
    labels=False,
    label_color="black",
    label_format="{:.1f}",
    label_fontsize=8,
    **kwargs
):
    """
    Seaborn syntax stacked barplot
    Parameters
    ----------
    data : pd.DataFrame
        Dataset for plotting (in long format).
    x : str
        variable on the x axis.
    y : str
        Variable on the y axis.
    hue :
        Variable used to fill the bars.
    orient : “v” | “h”, optional
        Orientation of the plot (vertical or horizontal).
    ax : matplotlib axes object, optional
        An axes of the current figure.
    color : str, array-like, or dict, optional
            The color for each of the DataFrame's columns. Possible values are:
            - A single color string referred to by name, RGB or RGBA code,
                for instance 'red' or '#a98d19'.
            - A sequence of color strings referred to by name, RGB or RGBA
                code, which will be used for each column recursively. For
                instance ['green','yellow'] each column's %(kind)s will be filled in
                green or yellow, alternatively. If there is only a single column to
                be plotted, then only the first color from the color list will be
                used.
            - A dict of the form {column name : color}, so that each column will be
                colored accordingly. For example, if your columns are called `a` and
                `b`, then passing {'a': 'green', 'b': 'red'} will color %(kind)ss for
                column `a` in green and %(kind)ss for column `b` in red.
    labels: boolean, optional
        Whether to annotate the barcharts with value labels.
    label_color: str, optional
        Color of labels
    label_fontsize: int, optional
        Font size used in label
    label_format: str, optional
        formatting type of bars' labels
    **kwargs
            Additional keyword arguments are documented in
            :meth:`DataFrame.plot`.
    Examples
    --------
    >>> df = sns.load_dataset("tips")
    >>> plot_data = df.groupby(["day","time"])["total_bill"].sum().reset_index()
    >>> stacked_barplot(data=plot_data, x="day", y="total_bill", hue="time")
    """
    data_pivot = data.pivot_table(values=y, index=x, columns=hue, fill_value=0)
    if ax is None:
        ax = plt.gca()

    if color:
        kwargs["color"] = color

    if orient == "h":
        data_pivot.plot.barh(ax=ax, stacked=True, **kwargs)
        ax.set_xlabel(y)
    else:
        data_pivot.plot.bar(ax=ax, stacked=True, **kwargs)
        ax.set_ylabel(y)

    if labels:
        threshold = ax.get_ylim()[1] / 20
        for p_nr in range(len(ax.patches)):  # p_nr = 1
            p = ax.patches[p_nr]
            width, height = p.get_width(), p.get_height()
            x, y = p.get_xy()

            if height > threshold:
                ax.text(
                    x + width / 2,
                    y + height / 2,
                    label_format.format(height),
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=label_fontsize,
                    color=label_color,
                )

    return ax


def barchart_all_habits(data, by="week", labels=True, color_dict=None, title=None):
    # Prepare data
    val_col = "month" if by == "week" else "week"
    plot_df = (
        data.groupby([by, "habit"])[val_col]
        .count()
        .reset_index()
        .rename(columns={val_col: "count"})
    )

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
    stacked_barplot(
        plot_df,
        x=by,
        y="count",
        hue="habit",
        color=color_dict,
        labels=True,
        label_format="{:.0f}",
        ax=ax,
    )
    # Setting labels and ticks
    ax.set_ylabel("")
    ax.set_xlabel(by.capitalize())
    if by == "week":
        ax.set_xticks([1] + list(range(4, 53, 4)))
        ax.set_xticklabels(labels=[1] + list(range(4, 53, 4)), rotation=0, fontsize=8)
    else:
        ax.set_xticklabels(labels=range(1, 13, 1), rotation=0, fontsize=12)
    # Other aesthetics
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    ax.set_ylim(0, data.groupby(by)[val_col].count().max() * 1.1)
    ax.set_title(title)
