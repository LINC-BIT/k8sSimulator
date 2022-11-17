import json
import pymysql

def read_json_file(filename):
    with open(filename, "r") as fp:
        data = json.load(fp)
        return data

#def read_sql_file(tracetimeid:int,workloadtypeid:int,jobconsist_tasknumber:int,job_tasknum:int,requestcpu_min:int,requestcpu_max:int,
#                  requestmem_min: float,requestmem_max: float,instancerunningtime_min:int,instancerunningtime_max:int):
def read_sql_file(tracetimeid:int,workloadtypeid:int,jobconsist_tasknumber:int,job_tasknum:int,job_num:int):
    # set mysql table parameters
    requestcpu_min = 0
    requestcpu_max = 0
    requestmem_min = 0.0
    requestmem_max = 0.0
    instancerunningtime_min = 0
    instancerunningtime_max = 0

    # mysql connect
    connection = pymysql.connect(host='10.4.21.109', user='root', password='abcd2439774702', db='alibaba')
    cursor = connection.cursor()
    print('Connect mysql succeed!')

    # select jobs from getjob_0_modified
    sql1 = 'select job_name from getjob_5_modified_%d where jct > %d' % (tracetimeid, job_tasknum)
    cursor.execute(sql1)
    result1 = cursor.fetchall()
    print("SQL job number: ",len(result1))
    print("-----------------------------")

    # select instances from batch_instance_1_0
    alljobdict = []
    for i, row1 in enumerate(result1):

        # jobname match
        sql2 = "select job_name,start_time,end_time,cpu_avg,cpu_max,mem_avg,mem_max from batch_instance_2_%d " \
               "where job_name='%s'" % (tracetimeid, row1[0])
        cursor.execute(sql2)
        result2 = cursor.fetchall()

        # select insatnces of jobname matched
        singlejobdict = {}
        singlejobdict['job.tasks'] = []
        for j, row2 in enumerate(result2):

            # get values
            jobname = row2[0]
            instance_starttime = int(row2[1])
            instance_endtime = int(row2[2])
            request_cpu = int(row2[3])
            limit_cpu = int(row2[4])
            request_mem = float(row2[5])
            limit_mem = float(row2[6])
            instance_runningtime = instance_endtime - instance_starttime

            # low cpu, low memory
            if workloadtypeid == 1:
                if (request_cpu > 10 and request_cpu <= 50) and (request_mem <= 0.05) and (instance_runningtime >= 20):
                #if ((request_cpu >= requestcpu_min and request_cpu < requestcpu_max) and (request_mem >= requestmem_min and request_mem < requestmem_max)
                #        and (instance_runningtime >= instancerunningtime_min and instance_runningtime < instancerunningtime_max)):
                    singlejobdict['job.tasks'].append(row2)

            # low cpu, high memory
            if workloadtypeid == 2:
                if (request_cpu > 10 and request_cpu <= 50) and (request_mem >= 0.7 and request_mem <= 0.8) and (instance_runningtime >= 20):
                #if ((request_cpu >= requestcpu_min and request_cpu < requestcpu_max) and (request_mem >= requestmem_min and request_mem < requestmem_max)
                #        and (instance_runningtime >= instancerunningtime_min and instance_runningtime < instancerunningtime_max)):
                    singlejobdict['job.tasks'].append(row2)

            # high cpu, low memory
            if workloadtypeid == 3:
                if (request_cpu > 100 and request_cpu < 200) and (request_mem <= 0.05) and (instance_runningtime >= 20):
                #if ((request_cpu >= requestcpu_min and request_cpu < requestcpu_max) and (request_mem >= requestmem_min and request_mem < requestmem_max)
                #        and (instance_runningtime >= instancerunningtime_min and instance_runningtime < instancerunningtime_max)):
                    singlejobdict['job.tasks'].append(row2)

            # high cpu, high memory
            if workloadtypeid == 4:
                if (request_cpu > 100 and request_cpu < 200) and (request_mem >= 0.7 and request_mem <= 0.8) and (instance_runningtime >= 20):
                    singlejobdict['job.tasks'].append(row2)
                #if ((request_cpu >= requestcpu_min and request_cpu < requestcpu_max) and (request_mem >= requestmem_min and request_mem < requestmem_max)
                #        and (instance_runningtime >= instancerunningtime_min and instance_runningtime < instancerunningtime_max)):

        if (len(singlejobdict['job.tasks']) >= jobconsist_tasknumber):
            alljobdict.append(singlejobdict)

        if (len(alljobdict) == job_num + 2):
            break

    return alljobdict









