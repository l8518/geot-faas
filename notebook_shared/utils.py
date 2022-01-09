import os
import numpy as np
import matplotlib.pyplot as plt

PLOT_FOLDER = "plots"
SIZES = {
            "tiny" : '-0.01',
            "small" : '-0.1',
            "full" : ''
        }

def get_dataset_path(DATASET_NAME, FSIZE, DATA_FOLDER='data'):
    full_filename = f"{DATASET_NAME}{SIZES[FSIZE]}.parquet"
    return os.path.join(DATA_FOLDER, full_filename)

def plot(name_or_name_components, **kwdata):

    if (type(name_or_name_components) is list):
        name = name_or_name_components[-1]
        folder = os.path.join(PLOT_FOLDER, *(name_or_name_components[:-1]))
    else:
        name = name_or_name_components
        folder = PLOT_FOLDER
    if not os.path.isdir(folder):
       os.makedirs(folder)
    plt.savefig(os.path.join(folder, f"{name}.pdf"))
    plt.show()
    plt.close()
    for key in kwdata:
        data = kwdata[key]
        str_resp = str(data)
        with open(os.path.join(folder, f"{name}_{key}.txt"), 'w') as f:
            f.write(str_resp)
            print(key, "\n", str_resp)

def cov(x):
    return np.std(x, ddof=1) / np.mean(x)

def boxplot(ax, df, ytitle, tickf, rot=0, sharex=False, showfliers=False):
    fig = ax.get_figure()
    gs = ax.get_subplotspec()
    ax.remove()
    ax = fig.add_subplot(gs)

    df.boxplot(subplots=False, ax=ax, showfliers=showfliers, sharex=sharex)

    if (sharex):
        ax.set_xticklabels([])
    else:
        labels = []
        for tick in ax.get_xticklabels():
            labels.append(tickf(tick))
        ax.set_xticklabels(labels)
        plt.setp(ax.get_xticklabels(), rotation=rot)

    ax.set_ylabel(ytitle)
    
    return ax

def tick_get_1st(x):
    return x.get_text()[1:].split(',')[0]
