import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seaborn.categorical import _ViolinPlotter

from . import utils


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seaborn.categorical import _ViolinPlotter

# from . import utils


class CustomViolinPlotter(_ViolinPlotter):
    
    
    
    def __init__(self, x, y, hue, data, order, hue_order,
                 bw, cut, scale, scale_hue, gridsize,
                 width, inner, split, dodge, orient, linewidth,
                 color, palette, saturation, customlineswidth = 4):
        
        if (customlineswidth is None):
                customlineswidth = 4

        color = 'b'
        self.customlineswidth = customlineswidth
        
        super().__init__(x, y, hue, data, order, hue_order,
                         bw, cut, scale, scale_hue, gridsize,
                         width, inner, split, dodge, orient, linewidth,
                         color, palette, saturation)
    
    def draw_box_lines(self, ax, data, support, density, center):
        defaultlinewidth = self.linewidth
        
        self.linewidth = self.customlineswidth
        
        # include code from super().draw_box_lines(ax, data, support, density, center)
        # to improve custom plotting
        q25, q50, q75 = np.percentile(data, [25, 50, 75])
        iqr = (q75 - q25)
        whisker_lim = 1.5 * iqr
        h1 = np.min(data[data >= (q25 - whisker_lim)])
        h2 = np.max(data[data <= (q75 + whisker_lim)])

        # Draw a boxplot using lines
        if self.orient == "v":
            ax.plot([center, center], [h1, h2],
                    linewidth=self.linewidth,
                    color=self.gray, alpha=1, solid_capstyle='butt')            
            ax.plot([center, center], [q25, q75],
                    linewidth=self.linewidth * 3,
                    color=self.gray, alpha=0.8, solid_capstyle='butt')
            ax.plot([center - 0.1, center + 0.1], [q50, q50],
                zorder=3,
                linewidth=self.linewidth,
                alpha=0.8,
                color='lightgray')   
            # Improved Whiskers:
            # min
            ax.plot([center - 0.1, center + 0.1], [h2, h2],
                    linewidth=self.linewidth,
                    color=self.gray, alpha=1, solid_capstyle='butt')
            
            # max
            ax.plot([center - 0.1, center + 0.1], [h1, h1],
                    linewidth=self.linewidth,
                    color=self.gray, alpha=1, solid_capstyle='butt')
        else:
            ax.plot([h1, h2], [center, center],
                    linewidth=self.linewidth,
                    color=self.gray)
            ax.plot([q25, q75], [center, center],
                    linewidth=self.linewidth * 3,
                    color=self.gray)
            ax.plot([center - 0.1, center + 0.1], [q50, q50],
                zorder=3,
                linewidth=self.linewidth,
                alpha=0.8,
                color='lightgray')     
        
        
        # Plot mean line into violinplot
        mean = np.mean(data)
        ax.scatter(center, mean, alpha=1, s=80, c='red', zorder=5, marker=(5, 2))

        #ax.plot([center - 0.1, center + 0.1], [mean, mean],
        #        linewidth=2,
        #        alpha=0.8,
        #        color='orangered', zorder = 5)
        
        self.linewidth = defaultlinewidth


def violinplot(
    *,
    x=None, y=None,
    hue=None, data=None,
    order=None, hue_order=None,
    bw="scott", cut=2, scale="area", scale_hue=True, gridsize=100,
    width=.8, inner="box", split=False, dodge=True, orient=None,
    linewidth=None, color=None, palette=None, saturation=.75,
    ax=None, customlineswidth = None, **kwargs,
):
    plotter = CustomViolinPlotter(x, y, hue, data, order, hue_order,
                                  bw, cut, scale, scale_hue, gridsize,
                                  width, inner, split, dodge, orient, linewidth,
                                  color, palette, saturation, customlineswidth)

    if ax is None:
        ax = plt.gca()

    plotter.plot(ax)
    return ax
