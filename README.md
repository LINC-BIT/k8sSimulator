# K8sSim：A Kubernetes cluster simualtor
![image](k8ssim.png)
# Introduction
## 1. Kubernetes Simualtion：responsible for the scheduling of ***generic workloads*** in Kubernetes simulation scheduler (For a generic workload, tasks in a job are submitted to excute sequentially)
### 1.1. k8s-simulator-prop：Kubernetes simualtion scheduler
* k8s/example: ***the startup program of Kubernetes simualtion scheduler*** 
  * conf.go: port is used to specify the execution port of the simulation scheduler, **e.g. port = ":8002"**
  * ***how to start:*** 
    * ***cd ~/k8s/example***
    * ***go bulid***
    * ***example.exe (Windows system); ./example/example port (Linux system)***

### 1.2. k8s-benchmark：Simulation environment
* common/test_workloads: some generic workloads to test (user-submitted workloads, e.g. ce/ce-bra.yaml)
* common/nodes: some configuration files of node resources (simulation nodes, c2e2.yaml)
* common/summarizing: some formatted codes for the scheduling results of jobs and tasks, which is easy to analyze and use visually
* run_sim_workload.py: ***the startup program used to submit the workload and node configuration*** 
  * workload_dir: specifying the folder where the test workload is located
  * sim_node_conf: specifying the simulation nodes for this test
  * schedulers: specifying the names of the multiple Kubernetes scheduling algorithms to be run (e.g. bra, lrp, mrp)
  * repeat_times: number of repeated runs
  * sim_base_url: the port on which the simulation scheduler will run (**e.g. 'http://localhost:8002'**)
  * result_dir: the location where the simulation results will be saved
  * ***how to start:***
    * ***python3.8 run_sim_workload.py***

## 2. Volcano Simulation：responsible for the scheduling of ***AI workloads*** in Volcano simulation scheduler (For a AI workload, tasks in a job are executed concurrently by task-group)
### 2.1. Volcano_simulator：Volcano simualtion scheduler
* cmd/sim: ***the startup program of Volcano simualtion scheduler*** 
  * conf.go: port is used to specify the execution port of the simulation scheduler, **e.g. var port = ":8006"**
  * ***how to start:*** 
    * ***cd ~/cmd/sim***
    * ***go bulid***
    * ***sim.exe (Windows system); ./sim/sim port (Linux system)***

### 2.2. Submit_volcano_workloads：Simulation environment
* common/workloads: some AI workloads to test (user-submitted workloads, e.g. AI-workloads/wsl_test_mrp-2.yaml)
* common/nodes: some configuration files of node resources (simulation nodes, nodes_7-0.yaml)
* SimRun.py: ***the startup program used to submit the workload and node configuration*** 
  * sim_base_url: the port on which the simulation scheduler will run (**e.g. 'http://localhost:8006'**)
  * node_file_url: specifying the simulation nodes for this test
  * workload_file_url: specifying the folder where the test workload is located
  * schedulers: specifying the names of the multiple Volcano scheduling algorithms to be run (e.g. GANG_BRA, GANG_MRP, GANG_LRP)
  * pods_result_url: the location where the pods' simulation results will be saved
  * jobs_result_url: the location where the jobs' simulation results will be saved
  * figures_result_url: the location where the result figures will be saved
  * ***how to start:***
    * ***python3.8 SimRun.py***

# Contact information
## Beijing Institute of Technology
Shilin Wen, Rui Han, Ke Qiu, Xiaoxin Ma, Zeqing Li, Hongjie Deng, and Chi Harold Liu
## E-mail
Shilin Wen: 3120185530@bit.edu.cn
## Version
This project version is K8sSim v1.0.

