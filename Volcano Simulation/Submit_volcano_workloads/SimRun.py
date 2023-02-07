from common.utils.json_http_client import JsonHttpClient
import time
import datetime
import csv
import json
import munch
import os
import math
import shutil
from json import dumps
#from figures.draw_pod_figures import draw_pods_figures
import prettytable
from figures.figures import draw_job_figures
from figures.figures import draw_job_figures1
from figures.figures import draw_job_figures2
import matplotlib.pyplot as plt
import numpy as np

def _get_key_or_empty(data, key):
    pods = munch.munchify(data[key])
    return pods if pods is not None else []

def reset(sim_base_url, node_file_url, workload_file_url):
    client = JsonHttpClient(sim_base_url)

    with open(node_file_url, 'r', encoding='utf-8') as file:
        nodes_file = file.read()

    with open(workload_file_url, 'r', encoding='utf-8') as file:
        workload_file = file.read()

    dicData = client.get_json('/reset', json={
        'period': "-1",
        'nodes': nodes_file,
        'workload': workload_file,
    })

    if str(dicData) == "0":
        print("still job runs，can not reset")
    else:
        print("---Simualtion Reset---")
        #print("仿真环境node信息：")
        #print(dumps(dicData["nodes"], indent=4))
        #print(_get_key_or_empty(dicData, "nodes"))

def step(sim_base_url, conf_file_url, pods_result_url, jobs_result_url, figures_result_url, scheduler):

    with plt.style.context('ieee'):

        client = JsonHttpClient(sim_base_url)

        succeed_headers = ["Pod_name", "Job_name", "Job_submit", "Pod_create", "Pod_start", "Pod_end", "Pod_wait_create", "Pod_wait_run", "Pod_wait_total",
                           "Pod_running_time", "Pod_total_time", "Running node", "Requests_memory", "Limits_memory", "Requests_cpu", "Limits_cpu", "Requests_gpu", "Limits_gpu"]
        succeed_table = prettytable.PrettyTable(succeed_headers)

        JCTheaders = ['Job Name', 'Job Completed Time(s)']
        JCT_table = prettytable.PrettyTable(JCTheaders)

        with open(conf_file_url, 'r', encoding='utf-8') as file:  # conf2是nodeorder
            conf_file = file.read()
        data = client.get_json('/step', json={
            'conf': conf_file,
        })

        wait = 0.2
        alljoblists = []
        # joblist = []
        # countJct= []
        # alljobstarttime = []
        # alljobendtime = []
        # allpodruntime = []
        while True:
            # 等待一段时间后获取集群信息，若返回1则表示集群未调度满一个周期，再等等
            time.sleep(wait)
            resultdata = client.get_json('/stepResult', json={
                'none': "",
            })
            #print("11111: \n", resultdata)
            if str(resultdata) == '0':
                continue
            else:
                print("---Simulation Start---")
                pod_result = os.path.join(pods_result_url, 'tasksSUM.csv')

                with open(pod_result, "w", encoding='utf-8', newline='') as file0:
                      succeed = []
                      writer = csv.writer(file0)
                      writer.writerow(succeed_headers)

                      job_result = os.path.join(jobs_result_url, 'coutJCT.csv')
                      with open(job_result, "w", encoding='utf-8', newline='') as file1:
                            writer1 = csv.writer(file1)
                            writer1.writerow(JCTheaders)

                            joblist = []
                            countJct = []
                            alljobstarttime = []
                            alljobendtime = []
                            allpodruntime = []
                            jobsublist = []

                            for jobName, job in resultdata["Jobs"].items():
                                #print(job)
                                job_sub = job["CreationTimestamp"]
                                if job_sub == None:
                                    job_sub = "0001-01-01T00:00:00Z"
                                job_sub = datetime.datetime.strptime(job_sub, "%Y-%m-%dT%H:%M:%SZ")
                                joblist.append(jobName)

                                # jobstarttime = []
                                # jobendtime = []
                                job_completes_flag = False
                                while not job_completes_flag:
                                    jobstarttime = []
                                    jobendtime = []
                                    job_completed_podnumber = 0
                                    print("0: ", job_completed_podnumber)
                                    for taskName, task in job["Tasks"].items():
                                        #print(task["Pod"]["metadata"]["labels"]["jobTaskNumber"])
                                        print("1: ", job_completed_podnumber)
                                        if job_completed_podnumber < int(task["Pod"]["metadata"]["labels"]["jobTaskNumber"]):
                                            if task["Pod"]["status"]["phase"] == "Succeeded":
                                                job_completed_podnumber += 1
                                                print("2: ", job_completed_podnumber)
                                                create = task["Pod"]["metadata"]["creationTimestamp"]
                                                #start = task["Pod"]["status"]["startTime"]
                                                start = task["Pod"]["status"]["containerStatuses"][0]["state"]["terminated"]["startedAt"]
                                                end = task["SimEndTimestamp"]
                                                if create == None:
                                                    create = "0001-01-01T00:00:00Z"
                                                if start == None:
                                                    start = "0001-01-01T00:00:00Z"
                                                if end == None:
                                                    end = "0001-01-01T00:00:00Z"
                                                create_time = datetime.datetime.strptime(create, "%Y-%m-%dT%H:%M:%SZ")
                                                start_time = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
                                                end_time = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
                                                pending_create_time = (create_time - job_sub).total_seconds()
                                                pending_execute_time = (start_time - create_time).total_seconds()
                                                pending_total_time = (start_time - job_sub).total_seconds()
                                                run_time = (end_time - start_time).total_seconds()
                                                total_time = pending_total_time + run_time
                                                row = [taskName, task["Pod"]["metadata"]["labels"]["job"], job_sub, create_time, start_time, end_time,
                                                       pending_create_time, pending_execute_time, pending_total_time, run_time, total_time, task["NodeName"],
                                                       task["Pod"]["spec"]["containers"][0]["resources"]["requests"]["cpu"],
                                                       task["Pod"]["spec"]["containers"][0]["resources"]["limits"]["cpu"],
                                                       task["Pod"]["spec"]["containers"][0]["resources"]["requests"]["memory"],
                                                       task["Pod"]["spec"]["containers"][0]["resources"]["limits"]["memory"],
                                                       task["Pod"]["spec"]["containers"][0]["resources"]["requests"]["nvidia.com/gpu"],
                                                       task["Pod"]["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"]]
                                                writer.writerow(row)
                                                succeed.append(row)
                                                succeed_table.add_row(row)

                                                jobstarttime.append(create_time)
                                                jobendtime.append(end_time)

                                                alljobstarttime.append(create_time)
                                                alljobendtime.append(end_time)
                                                allpodruntime.append(total_time)
                                                # print(taskName, ":", task["NodeName"], ",", create, ",", start, ",", end)
                                                if job_completed_podnumber == int(task["Pod"]["metadata"]["labels"]["jobTaskNumber"]) - int(task["Pod"]["metadata"]["labels"]["terminationLimit"]):
                                                    job_completes_flag = True
                                                    print("3: ", job_completed_podnumber)
                                        else:
                                           break

                                #job_jct = (max(jobendtime) - min(alljobstarttime)).total_seconds()
                                job_jct = (max(jobendtime) - min(jobstarttime)).total_seconds()
                                countJct.append(job_jct)
                            row1 = ['job1', max(countJct)]
                            alljoblists.append(row1)
                            writer1.writerow(row1)
                            JCT_table.add_row(row1)
                      #       print("len: ", len(alljobendtime))
                      #       print("len: ", len(alljobstarttime))
                      # print("len: ", len(countJct))
                      # print("len: ", len(joblist))

                break

        print(succeed_table)
        print(JCT_table)
        #print("Task运行最大值：", sorted(allpodruntime)[-1])
        tail_allpodruntime1 = []
        colorid = []
        tail_allpodruntime2 = sorted(allpodruntime)[int(len(allpodruntime) * math.pow(0.99,len(alljoblists))):len(allpodruntime)]
        task_id = []
        for i, podruntime in enumerate(allpodruntime):
            # if podruntime > (sum(allpodruntime)/len(allpodruntime))*1.3:
            #     tail_allpodruntime1.append(podruntime)
            #     colorid.append('blue')
            # else:
            if podruntime in tail_allpodruntime2:
                colorid.append('red')
            else:
                colorid.append('steelblue')
            task_id.append(i)

        print("Task completed%-1：", tail_allpodruntime1)
        print("Task completed%-2：", tail_allpodruntime2)

        #sort_allpodruntime = sorted(allpodruntime)[int(len(allpodruntime)*0.96):len(allpodruntime)]

        # 画图
        save_filename = scheduler + ".pdf"
        # nameid =[]
        # colorid = []
        # for i in allpodruntime:
        #     nameid.append('0')
        #     if i in sort_allpodruntime:
        #         colorid.append('blue')
        #     else:
        #         colorid.append('red')
        # print(nameid)
        # print(colorid)

        task_id.reverse()

        plt.barh(range(len(allpodruntime)), allpodruntime, color=colorid,  tick_label=task_id, height=0.2)
        # plt.bar(np.arange(len(allpodruntime)), allpodruntime, color=colorid, hatch='/', width=0.5)
        plt.yticks(np.arange(len(allpodruntime)), ())
        plt.xticks(size=8, font='Times New Roman')
        #plt.ylabel('Tasks', fontsize=8, font='Times New Roman')
        #plt.xlabel('Task tail latency(s)', fontsize=8, font='Times New Roman')
        #plt.title('Algorithm: '+ str(scheduler), fontsize=8, font='Times New Roman')
        # plt.ylim(0)
        plt.xlim(0)
        plt.savefig(os.path.join(figures_result_url, save_filename), dpi=1600)
        #plt.grid()
        plt.show()

        pod_result_1 = os.path.join(pods_result_url, 'tasksSUM.md')
        file2 = open(pod_result_1, 'w')
        file2.write(str(succeed_table) + "\n")
        file2.write('Total%d个Task。\n' % (len(allpodruntime)))
        file2.write('Task average time：%.2fs，Minimum time：%.2fs，Maximum time：%.2fs。 \n' % (sum(allpodruntime) / len(allpodruntime),
                                                                  min(allpodruntime), max(allpodruntime)))

        job_result_1 = os.path.join(jobs_result_url, 'coutJCT.md')
        file3 = open(job_result_1, 'w')
        file3.write(str(JCT_table) + "\n")
        file3.write('Summary: ' + "\n")
        file3.write('Total%d个Job。\n' % (len(countJct)))
        file3.write('Job average time：%.2fs，Minimum time：%.2fs，Maximum time：%.2fs。\n' % (sum(countJct) / len(countJct), min(countJct), max(countJct)))
        file3.write('Jobs MakeSpan is：%.2fs。\n' % max(countJct))

        time.sleep(0.5)
        file2.close()
        file3.close()

if __name__ == '__main__':

    sim_base_url = 'http://localhost:8006'
    node_file_url = 'common/nodes/nodes_7-0.yaml'
    workload_file_url = 'common/workloads/AI-workloads/wsl_test_mrp-2.yaml'

    if os.path.exists(os.path.join(os.getcwd(), "volcano-sim-result/")):
        shutil.rmtree(os.path.join(os.getcwd(), "volcano-sim-result/"))
    os.makedirs(os.path.join(os.getcwd(), "volcano-sim-result/"), exist_ok=False)
    print("Delete history folder！！！\n")

    for i in range(1):
        print("**************************************************** " + str(i+1) + " test: ****************************************************")

        # schedulers = ["GANG_LRP", "GANG_MRP", "GANG_BRA", "SLA_LRP", "SLA_MRP", "SLA_BRA",
        #               "GANG_DRF_LRP", "GANG_DRF_MRP", "GANG_DRF_BRA", "GANG_BINPACK", "SLA_BINPACK", "GANG_DRF_BINPACK"]

        # schedulers = ["GANG_LRP", "GANG_MRP", "GANG_BRA", "SLA_LRP", "SLA_MRP", "SLA_BRA",
        #               "GANG_DRF_LRP", "GANG_DRF_MRP", "GANG_DRF_BRA", "GANG_BINPACK", "SLA_BINPACK", "GANG_DRF_BINPACK", "Default"]

        #schedulers = ["GANG_BINPACK", "GANG_LRP", "GANG_MRP", "GANG_BRA", "DRF_BINPACK", "DRF_LRP", "DRF_MRP", "DRF_BRA", "SLA_BINPACK", "SLA_LRP", "SLA_MRP", "SLA_BRA"]
        #schedulers = ["GANG_BINPACK", "DRF_BINPACK", "SLA_BINPACK"]
        # schedulers = ["SLA_LRP", "SLA_MRP", "SLA_BRA", "DRF_LRP", "DRF_MRP", "DRF_BRA", "GANG_LRP", "GANG_MRP", "GANG_BRA",
        #               "GANG_DRF_LRP", "GANG_DRF_MRP", "GANG_DRF_BRA", "GANG_DRF_BINPACK"]
        schedulers = ["GANG_LRP", "GANG_MRP", "GANG_BRA"]
        for scheduler in schedulers:
            now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            # conf_file_url = 'common/scheduler_conf/conf_1.yaml'
            conf_file_url = 'common/scheduler_conf_sim/' + str(scheduler) + '.yaml'
            pods_result_url = "volcano-sim-result/tasks/" + str(now) + "-" + str(scheduler)
            jobs_result_url = "volcano-sim-result/jobs/" + str(now) + "-" + str(scheduler)
            figures_result_url = "volcano-sim-result/figures/" + str(now) + "-" + str(scheduler)

            os.makedirs(pods_result_url, exist_ok=True)
            os.makedirs(jobs_result_url, exist_ok=True)
            os.makedirs(figures_result_url, exist_ok=True)

            print("-----------------------------------------------------------------")
            print("In scheduling algorithm: " + str(scheduler) + "， simulation test：")
            reset(sim_base_url, node_file_url, workload_file_url)
            time.sleep(1)
            step(sim_base_url, conf_file_url, pods_result_url, jobs_result_url, figures_result_url, scheduler)
            time.sleep(1)
            #draw_pods_figures(os.path.join(pods_result_url, 'tasksSUM.csv'), figures_result_url, scheduler)
            print("-----------------------------------------------------------------")
            print("")

    print("****************************************************！！！Simulation Stop！！！****************************************************")

    time.sleep(1)
    # draw_job_figures(
    #     'volcano-sim-result/jobs',
    #     'volcano-sim-result/figures/box'
    # )
    # draw_job_figures1(
    #     'volcano-sim-result/jobs',
    #     'volcano-sim-result/figures/avg'
    # )
    draw_job_figures2(
        'volcano-sim-result/jobs',
        'volcano-sim-result/figures/JCTmakespan'
    )
