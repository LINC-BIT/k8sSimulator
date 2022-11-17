import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def auto_label(rects):
    for rect in rects:
        height = rect.get_height()
        #plt.text(rect.get_x() + rect.get_width() / 2. - 0.15, 1.01 * height, str(int(height)), fontsize=4)
        plt.text(rect.get_x() + rect.get_width() / 2 - 0.05, 1.01 * height, str(int(height)), fontsize=6)


def draw_jct_avg(data_frame: pd.DataFrame,
                 algorithm_names,
                 title: str = None,
                 x_label: str = None,
                 y_label: str = None):
    means = []
    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        mean = df['mean(jct)'].mean()
        means.append(mean)

    x = algorithm_names
    y = means

    plt.xticks(np.arange(len(x)), x, rotation=-270)
    plt.tick_params(labelsize=6)
    a = plt.bar(np.arange(len(x)), y)
    auto_label(a)
    plt.ylim((0, max(means)+20))

    plt.title(title, fontsize=8)
    plt.xlabel(x_label, fontsize=8)
    plt.ylabel(y_label, fontsize=8)
    plt.grid(True)
    #plt.show()
