import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seaborn.categorical import _ViolinPlotter

from . import utils


class CustomViolinPlotter(_ViolinPlotter):

    def __init__(self, x, y, hue, data, order, hue_order,
                 bw, cut, scale, scale_hue, gridsize,
                 width, inner, split, dodge, orient, linewidth,
                 color, palette, saturation):
        super().__init__(x, y, hue, data, order, hue_order,
                         bw, cut, scale, scale_hue, gridsize,
                         width, inner, split, dodge, orient, linewidth,
                         color, palette, saturation)

    def draw_box_lines(self, ax, data, support, density, center):
        tmp = self.linewidth
        self.linewidth = 4
        super().draw_box_lines(ax, data, support, density, center)

        # Add mean
        mean = np.mean(data)
        ax.plot([center - 0.1, center + 0.1], [mean, mean],
                linewidth=2,
                alpha=0.5,
                color='red', zorder = 5)
        # ax.scatter(center, mean, zorder=3, alpha=0.5, color="red", edgecolor=self.gray, s=np.square(self.linewidth * 2))

        self.linewidth = tmp


def violinplot(
    *,
    x=None, y=None,
    hue=None, data=None,
    order=None, hue_order=None,
    bw="scott", cut=2, scale="area", scale_hue=True, gridsize=100,
    width=.8, inner="box", split=False, dodge=True, orient=None,
    linewidth=None, color=None, palette=None, saturation=.75,
    ax=None, **kwargs,
):
    plotter = CustomViolinPlotter(x, y, hue, data, order, hue_order,
                                  bw, cut, scale, scale_hue, gridsize,
                                  width, inner, split, dodge, orient, linewidth,
                                  color, palette, saturation)

    if ax is None:
        ax = plt.gca()

    plotter.plot(ax)
    return ax

# Custom Violin Plots
def vioplot(pdf, axes, col, **kwargs):
    tmp = pd.DataFrame(pdf.to_dict()) #TODO: Improve?
    ax = violinplot(**kwargs, x="region", y=col, data=tmp, ax=axes,
                    inner='box', linewidth=0, rot=45)
    return ax
