import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def draw_jct_box(data_frame: pd.DataFrame,
                 algorithm_names,
                 title: str = None,
                 x_label: str = None,
                 y_label: str = None):
    data = []
    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        data.append(df['Job Completed Time(s)'])

    plt.boxplot(data, notch=False, sym='o', vert=True, patch_artist=False, showmeans=True,
                showfliers=False,
                meanprops={'marker': 'o', 'markerfacecolor': 'magenta', 'markersize': 3},
                medianprops={'color': 'red', 'linewidth': 2})

    plt.xticks([x + 1 for x in range(len(data))], algorithm_names, rotation=-270)
    plt.tick_params(labelsize=6)
    #plt.yticks(fontsize=6)

    plt.title(title, fontsize=8)
    plt.xlabel(x_label, fontsize=8)
    plt.ylabel(y_label, fontsize=8)

    plt.ylim(ymin=0)
    plt.grid(True)
    #plt.show()

def draw_jct_box_modify(data_frame: pd.DataFrame,
                 algorithm_names,
                 title: str = None,
                 x_label: str = None,
                 y_label: str = None):
    data = []
    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        data.append(df['Job Completed Time(s)'])

    sns.boxplot(data=data)

    plt.xticks([x + 1 for x in range(len(data))], algorithm_names, rotation=-270, fontsize=3,font='Times New Roman')
    plt.yticks(fontsize=3,font='Times New Roman')

    plt.title(title, fontsize=3, font='Times New Roman')
    plt.xlabel(x_label, fontsize=3, font='Times New Roman')
    plt.ylabel(y_label, fontsize=3, font='Times New Roman')

    plt.ylim(ymin=0)
    plt.grid(True)
    plt.show()


def draw_jct_box_1(data_frame: pd.DataFrame,
                 algorithm_names,
                 title: str = None,
                 x_label: str = None,
                 y_label: str = None):

    frame1 = pd.DataFrame()
    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        frame1[an] = df['Job Completed Time(s)']

    print(frame1)
    f = frame1.boxplot(patch_artist=None, return_type='dict', notch=False, sym='o', vert=True, showmeans=True,
                       showfliers=False, meanprops={'marker': 'o', 'markerfacecolor': 'magenta', 'markersize': 2},
                       medianprops={'color': 'red', 'linewidth': 1})

    # 有多少box就对应设置多少颜色
    color1 = ['b', 'black', 'black', 'black', 'black', 'black',
              'black', 'black', 'black', 'black', 'black', 'black']
    color2 = ['b', 'b', 'black', 'black', 'black', 'black', 'black',
              'black', 'black', 'black', 'black', 'black', 'black',
              'black', 'black', 'black', 'black', 'black', 'black',
              'black', 'black', 'black', 'black', 'black',]

    for box, c in zip(f['boxes'], color1):
        # 箱体边框颜色
        box.set(color=c, linewidth=1)

    for whisker, d in zip(f['whiskers'], color2):
        whisker.set(color=d, linewidth=1)

    for cap, e in zip(f['caps'], color2):
        cap.set(color=e, linewidth=1)

    plt.xticks([x + 1 for x in range(len(algorithm_names))], algorithm_names, rotation=-270, fontsize=3,font='Times New Roman')
    plt.yticks(fontsize=3,font='Times New Roman')

    plt.title(title, fontsize=3, font='Times New Roman')
    plt.xlabel(x_label, fontsize=3, font='Times New Roman')
    plt.ylabel(y_label, fontsize=3, font='Times New Roman')
    plt.ylim(ymin=0)
    plt.grid(True)
