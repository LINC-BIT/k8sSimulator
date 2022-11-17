import datetime
import os

from matplotlib import pyplot as plt

from .jct_box import draw_jct_box, draw_jct_box_modify, draw_jct_box_1
from .job_data_reading import read_data_from_directories
from .makespan import draw_makespan
from .jct_avg import draw_jct_avg

#algorithms = ["conf_1", "conf_2", "conf_3", "conf_4", "conf_5", "conf_6", "conf_7", "conf_8", "conf_9", "conf_10", "conf_11", "conf_12"]
drl_name = 'DRL'


#def convert_name(name):
#    return drl_name if name not in algorithms else name


#def rename_model_as_drl(summary, jobs):
#    jobs['name'] = jobs['name'].map(convert_name)
#    summary['name'] = summary['name'].map(convert_name)


# 绘制makespan柱状图，JCT盒图，以及JCT的CDF
def draw_job_figures(
        root_dir: str,
        save_dir: str,
        treat_model_as_drl: bool = False,
        save_filename: str = None,
        show_figure: bool = True,
):
    with plt.style.context('ieee'):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        save_filename = save_filename or root_dir.replace('/', '_') + now + ".pdf"

        dirs = list_dir(root_dir)
        summary, jobs = read_data_from_directories(dirs)

        #if treat_model_as_drl:
        #    rename_model_as_drl(summary, jobs)

        algorithm_names = summary['name'].unique()
        #if drl_name in algorithm_names:
            #algorithm_names = list(algorithm_names)
            #algorithm_names.remove(drl_name)
            #algorithm_names.insert(0, drl_name)
        print(summary)
        print(jobs)

        os.makedirs(save_dir, exist_ok=True)

        #plt.figure(figsize=(18,6))
        #plt.subplot(131)
        #draw_makespan(summary, algorithm_names,
        #               title='Makespan',
        #               x_label='Different schedulers')

        # plt.subplot(121)
        draw_jct_box(jobs, algorithm_names,
                     title=None,
                     x_label='Different schedulers',
                     y_label='Job latency(s)')

        # plt.subplot(122)
        # draw_jct_avg(summary, algorithm_names,
        #               title=None,
        #               x_label='Different schedulers',
        #               y_label='Average JCT(s)')

        # draw_cdf(jobs, algorithm_names,
        #          title='JCT CDF',
        #          x_label='Job complete time(s)')

        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, save_filename), dpi=800)
        plt.show()


def draw_job_figures1(
        root_dir: str,
        save_dir: str,
        treat_model_as_drl: bool = False,
        save_filename: str = None,
        show_figure: bool = True,
):
    with plt.style.context('ieee'):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        save_filename = save_filename or root_dir.replace('/', '_') + now + ".pdf"

        dirs = list_dir(root_dir)
        summary, jobs = read_data_from_directories(dirs)

        #if treat_model_as_drl:
        #    rename_model_as_drl(summary, jobs)

        algorithm_names = summary['name'].unique()
        #if drl_name in algorithm_names:
            #algorithm_names = list(algorithm_names)
            #algorithm_names.remove(drl_name)
            #algorithm_names.insert(0, drl_name)
        print(summary)
        print(jobs)

        os.makedirs(save_dir, exist_ok=True)

        #plt.figure(figsize=(18,6))
        #plt.subplot(131)
        #draw_makespan(summary, algorithm_names,
        #               title='Makespan',
        #               x_label='Different schedulers')

        # plt.subplot(121)
        # draw_jct_box(jobs, algorithm_names,
        #              title=None,
        #              x_label='Different schedulers',
        #              y_label='Job latency(s)')

        # plt.subplot(122)
        draw_jct_avg(summary, algorithm_names,
                      title=None,
                      x_label='Different schedulers',
                      y_label='Average JCT(s)')

        # draw_cdf(jobs, algorithm_names,
        #          title='JCT CDF',
        #          x_label='Job complete time(s)')

        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, save_filename), dpi=800)
        plt.show()

def draw_job_figures2(
        root_dir: str,
        save_dir: str,
        treat_model_as_drl: bool = False,
        save_filename: str = None,
        show_figure: bool = True,
):
    with plt.style.context('ieee'):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        save_filename = save_filename or root_dir.replace('/', '_') + now + ".png"

        dirs = list_dir(root_dir)
        summary, jobs = read_data_from_directories(dirs)

        #if treat_model_as_drl:
        #    rename_model_as_drl(summary, jobs)

        algorithm_names = summary['name'].unique()
        if drl_name in algorithm_names:
            algorithm_names = list(algorithm_names)
            algorithm_names.remove(drl_name)
            algorithm_names.insert(0, drl_name)
        print(summary)
        print(jobs)

        os.makedirs(save_dir, exist_ok=True)

        #plt.figure(figsize=(18,6))
        #plt.subplot(131)
        draw_makespan(summary, algorithm_names,
                       title=None,
                       x_label=None)

        # plt.subplot(121)
        # draw_jct_box(jobs, algorithm_names,
        #              title=None,
        #              x_label='Different schedulers',
        #              y_label='Job latency(s)')

        # plt.subplot(122)
        # draw_jct_avg(summary, algorithm_names,
        #               title=None,
        #               x_label='Different schedulers',
        #               y_label='Average JCT(s)')

        # draw_cdf(jobs, algorithm_names,
        #          title='JCT CDF',
        #          x_label='Job complete time(s)')

        plt.tight_layout()
        #plt.savefig(os.path.join(save_dir, save_filename), dpi=800)
        plt.savefig(os.path.join(save_dir, save_filename))
        plt.show(block = True)

def list_dir(root_dir: str):
    dirs = os.listdir(root_dir)
    return [os.path.join(root_dir, d) for d in dirs if os.path.isdir(os.path.join(root_dir, d))]
