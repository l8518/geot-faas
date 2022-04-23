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
        whisker_lim = 1.5 * (q75 - q25)
        h1 = np.min(data[data >= (q25 - whisker_lim)])
        h2 = np.max(data[data <= (q75 + whisker_lim)])

        # Draw a boxplot using lines and a point
        if self.orient == "v":
            ax.plot([center, center], [h1, h2],
                    linewidth=self.linewidth,
                    color=self.gray, alpha=1, solid_capstyle='butt')            
            ax.plot([center, center], [q25, q75],
                    linewidth=self.linewidth * 3,
                    color=self.gray, alpha=0.8, solid_capstyle='butt')
            ax.scatter(center, q50,
                       zorder=3,
                       color="white",
                       edgecolor=self.gray,
                       s=np.square(self.linewidth * 3))
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
            ax.scatter(q50, center,
                       zorder=3,
                       color="red",
                       edgecolor=self.gray,
                       s=np.square(self.linewidth * 3))       
        
        
        # Plot mean line into violinplot
        mean = np.mean(data)
        ax.plot([center - 0.1, center + 0.1], [mean, mean],
                linewidth=2,
                alpha=0.5,
                color='red', zorder = 5)
        
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

# Custom Violin Plots
def vioplot(pdf, axes, col, **kwargs):
    tmp = pd.DataFrame(pdf.to_dict()) #TODO: Improve?
    ax = violinplot(**kwargs, x="region", y=col, data=tmp, ax=axes,
                    inner='box', linewidth=0, rot=45)
    return ax
