/*
Copyright 2018 The Kubernetes Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package framework

import (
	"fmt"
	"math"

	"k8s.io/klog"

	"volcano.sh/volcano/pkg/scheduler/api"
	"volcano.sh/volcano/pkg/scheduler/metrics"
)

// Operation type
type Operation int8

const (
	// Evict op
	Evict = iota
	// Pipeline op
	Pipeline
	// Allocate op
	Allocate
)

type operation struct {
	name   Operation
	task   *api.TaskInfo
	reason string
}

// Statement structure
type Statement struct {
	operations []operation
	ssn        *Session
}

// NewStatement returns new statement object
func NewStatement(ssn *Session) *Statement {
	return &Statement{
		ssn: ssn,
	}
}

// Evict the pod
func (s *Statement) Evict(reclaimee *api.TaskInfo, reason string) error {
	// Update status in session
	if job, found := s.ssn.Jobs[reclaimee.Job]; found {
		if err := job.UpdateTaskStatus(reclaimee, api.Releasing); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				reclaimee.Namespace, reclaimee.Name, api.Releasing, s.ssn.UID, err)
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			reclaimee.Job, s.ssn.UID)
	}

	// Update task in node.
	if node, found := s.ssn.Nodes[reclaimee.NodeName]; found {
		err := node.UpdateTask(reclaimee)
		if err != nil {
			klog.Errorf("Failed to update task <%v/%v> in node %v for: %s",
				reclaimee.Namespace, reclaimee.Name, reclaimee.NodeName, err.Error())
			return err
		}
	}

	for _, eh := range s.ssn.eventHandlers {
		if eh.DeallocateFunc != nil {
			eh.DeallocateFunc(&Event{
				Task: reclaimee,
			})
		}
	}

	s.operations = append(s.operations, operation{
		name:   Evict,
		task:   reclaimee,
		reason: reason,
	})

	return nil
}

func (s *Statement) evict(reclaimee *api.TaskInfo, reason string) error {
	if err := s.ssn.cache.Evict(reclaimee, reason); err != nil {
		if e := s.unevict(reclaimee); e != nil {
			klog.Errorf("Faled to unevict task <%v/%v>: %v.",
				reclaimee.Namespace, reclaimee.Name, e)
		}
		return err
	}

	return nil
}

func (s *Statement) unevict(reclaimee *api.TaskInfo) error {
	// Update status in session
	job, found := s.ssn.Jobs[reclaimee.Job]
	if found {
		if err := job.UpdateTaskStatus(reclaimee, api.Running); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				reclaimee.Namespace, reclaimee.Name, api.Releasing, s.ssn.UID, err)
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			reclaimee.Job, s.ssn.UID)
	}

	// Update task in node.
	if node, found := s.ssn.Nodes[reclaimee.NodeName]; found {
		err := node.UpdateTask(reclaimee)
		if err != nil {
			klog.Errorf("Failed to update task <%v/%v> in node %v for: %s",
				reclaimee.Namespace, reclaimee.Name, reclaimee.NodeName, err.Error())
			return err
		}
	}

	for _, eh := range s.ssn.eventHandlers {
		if eh.AllocateFunc != nil {
			eh.AllocateFunc(&Event{
				Task: reclaimee,
			})
		}
	}

	return nil
}

// Pipeline the task for the node
func (s *Statement) Pipeline(task *api.TaskInfo, hostname string) error {
	job, found := s.ssn.Jobs[task.Job]
	if found {
		if err := job.UpdateTaskStatus(task, api.Pipelined); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Pipelined, s.ssn.UID, err)
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			task.Job, s.ssn.UID)
	}

	task.NodeName = hostname

	if node, found := s.ssn.Nodes[hostname]; found {
		if err := node.AddTask(task); err != nil {
			klog.Errorf("Failed to pipeline task <%v/%v> to node <%v> in Session <%v>: %v",
				task.Namespace, task.Name, hostname, s.ssn.UID, err)
		}
		klog.V(3).Infof("After pipelined Task <%v/%v> to Node <%v>: idle <%v>, used <%v>, releasing <%v>",
			task.Namespace, task.Name, node.Name, node.Idle, node.Used, node.Releasing)
	} else {
		klog.Errorf("Failed to find Node <%s> in Session <%s> index when binding.",
			hostname, s.ssn.UID)
	}

	for _, eh := range s.ssn.eventHandlers {
		if eh.AllocateFunc != nil {
			eh.AllocateFunc(&Event{
				Task: task,
			})
		}
	}

	s.operations = append(s.operations, operation{
		name: Pipeline,
		task: task,
	})

	return nil
}

func (s *Statement) pipeline(task *api.TaskInfo) {
}

func (s *Statement) unpipeline(task *api.TaskInfo) error {
	job, found := s.ssn.Jobs[task.Job]
	if found {
		if err := job.UpdateTaskStatus(task, api.Pending); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Pipelined, s.ssn.UID, err)
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			task.Job, s.ssn.UID)
	}

	if node, found := s.ssn.Nodes[task.NodeName]; found {
		if err := node.RemoveTask(task); err != nil {
			klog.Errorf("Failed to pipeline task <%v/%v> to node <%v> in Session <%v>: %v",
				task.Namespace, task.Name, task.NodeName, s.ssn.UID, err)
		}
		klog.V(3).Infof("After pipelined Task <%v/%v> to Node <%v>: idle <%v>, used <%v>, releasing <%v>",
			task.Namespace, task.Name, node.Name, node.Idle, node.Used, node.Releasing)
	} else {
		klog.Errorf("Failed to find Node <%s> in Session <%s> index when binding.",
			task.NodeName, s.ssn.UID)
	}

	for _, eh := range s.ssn.eventHandlers {
		if eh.DeallocateFunc != nil {
			eh.DeallocateFunc(&Event{
				Task: task,
			})
		}
	}
	task.NodeName = ""

	return nil
}

// Allocate the task to node
func (s *Statement) Allocate(task *api.TaskInfo, nodeInfo *api.NodeInfo) (err error) {
	podVolumes, err := s.ssn.cache.GetPodVolumes(task, nodeInfo.Node)
	if err != nil {
		return err
	}

	hostname := nodeInfo.Name
	if err := s.ssn.cache.AllocateVolumes(task, hostname, podVolumes); err != nil {
		return err
	}
	defer func() {
		if err != nil {
			s.ssn.cache.RevertVolumes(task, podVolumes)
		}
	}()

	task.Pod.Spec.NodeName = hostname
	task.PodVolumes = podVolumes

	// Only update status in session
	job, found := s.ssn.Jobs[task.Job]
	if found {
		if err := job.UpdateTaskStatus(task, api.Allocated); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Allocated, s.ssn.UID, err)
			return err
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			task.Job, s.ssn.UID)
		return fmt.Errorf("failed to find job %s", task.Job)
	}

	task.NodeName = hostname
	if node, found := s.ssn.Nodes[hostname]; found {
		if err := node.AddTask(task); err != nil { //更新节点资源
			klog.Errorf("Failed to add task <%v/%v> to node <%v> in Session <%v>: %v",
				task.Namespace, task.Name, hostname, s.ssn.UID, err)
			return err
		}
		klog.V(3).Infof("After allocated Task <%v/%v> to Node <%v>: idle <%v>, used <%v>, releasing <%v>",
			task.Namespace, task.Name, node.Name, node.Idle, node.Used, node.Releasing)
	} else {
		klog.Errorf("Failed to find Node <%s> in Session <%s> index when binding.",
			hostname, s.ssn.UID)
		return fmt.Errorf("failed to find node %s", hostname)
	}

	// Callbacks
	for _, eh := range s.ssn.eventHandlers {
		if eh.AllocateFunc != nil {
			eh.AllocateFunc(&Event{
				Task: task,
			})
		}
	}

	// Update status in session
	klog.V(3).Info("Allocating operations ...")
	s.operations = append(s.operations, operation{
		name: Allocate,
		task: task,
	})

	return nil
}

// Allocate the task to node，在snapshot数据上进行了假设的allocate，但未真正执行，真正执行的操作由方法Commit()负责
func (s *Statement) AllocateV2(task *api.TaskInfo, nodeInfo *api.NodeInfo) (err error) {
	////分配volumes，考虑不要
	//podVolumes, err := s.ssn.cache.GetPodVolumes(task, nodeInfo.Node)
	//if err != nil {
	//	return err
	//}
	//
	//hostname := nodeInfo.Name
	//if err := s.ssn.cache.AllocateVolumes(task, hostname, podVolumes); err != nil {
	//	return err
	//}
	//defer func() {
	//	if err != nil {
	//		s.ssn.cache.RevertVolumes(task, podVolumes)
	//	}
	//}()
	//
	//task.Pod.Spec.NodeName = hostname
	//task.PodVolumes = podVolumes

	// Only update status in session，考虑保留
	hostname := nodeInfo.Name
	job, found := s.ssn.Jobs[task.Job]
	if found {
		if err := job.UpdateTaskStatus(task, api.Allocated); err != nil { //更新ssn中task状态，虽然task是引用，但添加到node中的task是状态更新后的clone
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Allocated, s.ssn.UID, err)
			return err
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			task.Job, s.ssn.UID)
		return fmt.Errorf("failed to find job %s", task.Job)
	}

	task.NodeName = hostname
	if node, found := s.ssn.Nodes[hostname]; found {
		if err := node.AddTask(task); err != nil { //更新节点资源和map
			klog.Errorf("Failed to add task <%v/%v> to node <%v> in Session <%v>: %v",
				task.Namespace, task.Name, hostname, s.ssn.UID, err)
			return err
		}
		klog.V(3).Infof("After allocated Task <%v/%v> to Node <%v>: idle <%v>, used <%v>, releasing <%v>",
			task.Namespace, task.Name, node.Name, node.Idle, node.Used, node.Releasing)
	} else {
		klog.Errorf("Failed to find Node <%s> in Session <%s> index when binding.",
			hostname, s.ssn.UID)
		return fmt.Errorf("failed to find node %s", hostname)
	}

	// Callbacks，考虑去掉
	for _, eh := range s.ssn.eventHandlers {
		if eh.AllocateFunc != nil {
			eh.AllocateFunc(&Event{
				Task: task,
			})
		}
	}

	// Update status in session
	klog.V(3).Info("Allocating operations ...")
	s.operations = append(s.operations, operation{ //把操作写到数组中，之后若是jobReady了才真正执行操作
		name: Allocate,
		task: task,
	})
	return nil
}

func (s *Statement) allocate(task *api.TaskInfo) error {
	if err := s.ssn.cache.AddBindTask(task); err != nil { //更新cache中和ssn中task状态，并把cache中node也添加上该task
		return err
	}

	if job, found := s.ssn.Jobs[task.Job]; found { //更新ssn的job中该task的状态
		if err := job.UpdateTaskStatus(task, api.Binding); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Binding, s.ssn.UID, err)
			return err
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			task.Job, s.ssn.UID)
		return fmt.Errorf("failed to find job %s", task.Job)
	}

	metrics.UpdateTaskScheduleDuration(metrics.Duration(task.Pod.CreationTimestamp.Time))
	return nil
}

func (s *Statement) allocateV2(task *api.TaskInfo) error {
	//if err := s.ssn.cache.AddBindTask(task); err != nil {
	//	return err
	//}

	//找到该task（复制品）在cache中对应的真实job和task
	clusterJob, found := s.ssn.Cluster.Jobs[task.Job]
	if !found {
		return fmt.Errorf("failed to find Job %v for Task %v",
			task.Job, task.UID)
	}
	clusterTask, found := clusterJob.Tasks[task.UID]
	if !found {
		return fmt.Errorf("failed to find task in status %v by id %v",
			task.Status, task.UID)
	}

	//找到该task（复制品）在cache中对应的真实node
	clusterNode, found := s.ssn.Cluster.Nodes[task.NodeName] //找到该task（复制品）在cache中对应的真实node
	if !found {
		return fmt.Errorf("failed to bind Task %v to host %v, host does not exist",
			task.UID, task.NodeName)
	}

	//修改真实task状态
	//originalStatus := task.Status
	if err := clusterJob.UpdateTaskStatus(clusterTask, api.Binding); err != nil {
		return err
	}
	clusterTask.Pod.Spec.NodeName = task.NodeName //drl中需要此信息
	//和NumaInfo有关，暂时不管
	//err := task.SetPodResourceDecision()
	//if err != nil {
	//	return fmt.Errorf("set task %v/%v resource decision failed, err %v", task.Namespace, task.Name, err)
	//}
	//task.NumaInfo = task.NumaInfo.Clone()
	// Add task to the node.

	maxCountDown := float64(0)

	//因为有新的binding task，所有任务创建时间++
	for _, otherTask := range clusterNode.Tasks{
		if otherTask.Status != api.Binding {
			continue
		}
		otherTask.CtnCreationCountDown += clusterNode.CtnCreationExtraTime
	}

	//令task的container创建时间为 node中其它binding task的创建时间 和 node默认时间 中的最大值
	for _, otherTask := range clusterNode.Tasks{
		if otherTask.Status != api.Binding {
			continue
		}
		maxCountDown = math.Max(otherTask.CtnCreationCountDown, maxCountDown)
	}
	clusterTask.CtnCreationCountDown = math.Max(clusterNode.CtnCreationTime, maxCountDown)

	clusterNode.AddTask(clusterTask)


	if job, found := s.ssn.Jobs[task.Job]; found {
		if err := job.UpdateTaskStatus(task, api.Binding); err != nil {//更新ssn中的job中该task的状态
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Binding, s.ssn.UID, err)
			return err
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when binding.",
			task.Job, s.ssn.UID)
		return fmt.Errorf("failed to find job %s", task.Job)
	}

	metrics.UpdateTaskScheduleDuration(metrics.Duration(task.Pod.CreationTimestamp.Time))
	return nil
}

// unallocate the pod for task
func (s *Statement) unallocate(task *api.TaskInfo) error {
	s.ssn.cache.RevertVolumes(task, task.PodVolumes)

	// Update status in session
	job, found := s.ssn.Jobs[task.Job]
	if found {
		if err := job.UpdateTaskStatus(task, api.Pending); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Pending, s.ssn.UID, err)
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when unallocating.",
			task.Job, s.ssn.UID)
	}

	if node, found := s.ssn.Nodes[task.NodeName]; found {
		klog.V(3).Infof("Remove Task <%v> on node <%v>", task.Name, task.NodeName)
		err := node.RemoveTask(task)
		if err != nil {
			klog.Errorf("Failed to remove Task <%v> on node <%v>: %s", task.Name, task.NodeName, err.Error())
		}
	}

	for _, eh := range s.ssn.eventHandlers {
		if eh.DeallocateFunc != nil {
			eh.DeallocateFunc(&Event{
				Task: task,
			})
		}
	}
	task.NodeName = ""

	return nil
}

// unallocate the pod for task
func (s *Statement) unallocateV2(task *api.TaskInfo) error {
	//s.ssn.cache.RevertVolumes(task, task.PodVolumes)

	// Update status in session
	job, found := s.ssn.Jobs[task.Job]
	if found {
		if err := job.UpdateTaskStatus(task, api.Pending); err != nil {
			klog.Errorf("Failed to update task <%v/%v> status to %v in Session <%v>: %v",
				task.Namespace, task.Name, api.Pending, s.ssn.UID, err)
		}
	} else {
		klog.Errorf("Failed to find Job <%s> in Session <%s> index when unallocating.",
			task.Job, s.ssn.UID)
	}

	if node, found := s.ssn.Nodes[task.NodeName]; found {
		klog.V(3).Infof("Remove Task <%v> on node <%v>", task.Name, task.NodeName)
		err := node.RemoveTask(task)
		if err != nil {
			klog.Errorf("Failed to remove Task <%v> on node <%v>: %s", task.Name, task.NodeName, err.Error())
		}
	}

	//貌似和Allocate()中的eventHandlers相对应，考虑去掉
	for _, eh := range s.ssn.eventHandlers {
		if eh.DeallocateFunc != nil {
			eh.DeallocateFunc(&Event{
				Task: task,
			})
		}
	}
	task.NodeName = ""

	return nil
}

// Discard operation for evict, pipeline and allocate
func (s *Statement) DiscardV0() {
	klog.V(3).Info("Discarding operations ...")
	for i := len(s.operations) - 1; i >= 0; i-- {
		op := s.operations[i]
		op.task.GenerateLastTxContext()
		switch op.name {
		case Evict:
			err := s.unevict(op.task)
			if err != nil {
				klog.Errorf("Failed to unevict task: %s", err.Error())
			}
		case Pipeline:
			err := s.unpipeline(op.task) //不重写也能跑
			if err != nil {
				klog.Errorf("Failed to unpipeline task: %s", err.Error())
			}
		case Allocate:
			err := s.unallocate(op.task)
			if err != nil {
				klog.Errorf("Failed to unallocate task: %s", err.Error())
			}
		}
	}
}

// Discard operation for evict, pipeline and allocate
func (s *Statement) Discard() {
	klog.V(3).Info("Discarding operations ...")
	for i := len(s.operations) - 1; i >= 0; i-- {
		op := s.operations[i]
		op.task.GenerateLastTxContext()
		switch op.name {
		case Evict:
			//由于注释掉了Commit()中的evict(op.task)，因此把与其对应的unevict(op.task)也注释掉
			fmt.Println("尝试unevict，但未实现")
			//err := s.unevict(op.task)
			//if err != nil {
			//	klog.Errorf("Failed to unevict task: %s", err.Error())
			//}
		case Pipeline:
			err := s.unpipeline(op.task) //不重写也能跑
			if err != nil {
				klog.Errorf("Failed to unpipeline task: %s", err.Error())
			}
		case Allocate:
			err := s.unallocateV2(op.task)
			if err != nil {
				klog.Errorf("Failed to unallocate task: %s", err.Error())
			}
		}
	}
}

// Commit operation for evict and pipeline
func (s *Statement) CommitV0() {
	klog.V(3).Info("Committing operations ...")
	for _, op := range s.operations {
		op.task.ClearLastTxContext()
		switch op.name {
		case Evict:
			err := s.evict(op.task, op.reason)
			if err != nil {
				klog.Errorf("Failed to evict task: %s", err.Error())
			}
		case Pipeline:
			s.pipeline(op.task)
		case Allocate:
			err := s.allocate(op.task)
			if err != nil {
				s.ssn.cache.RevertVolumes(op.task, op.task.PodVolumes)
				klog.Errorf("Failed to allocate task: for %s", err.Error())
			}
		}
	}
}

// Commit operation for evict and pipeline
func (s *Statement) Commit() {
	klog.V(3).Info("Committing operations ...")
	for _, op := range s.operations {
		op.task.ClearLastTxContext()
		switch op.name {
		case Evict:
			fmt.Println("尝试evict，但尚未实现")
			//未完全了解evict机制，故未重写
			//err := s.evict(op.task, op.reason)
			//if err != nil {
			//	klog.Errorf("Failed to evict task: %s", err.Error())
			//}
		case Pipeline:
			s.pipeline(op.task) //源码中未实现
		case Allocate:
			s.allocateV2(op.task)
			//err := s.allocate(op.task)
			//if err != nil {
			//	s.ssn.cache.RevertVolumes(op.task, op.task.PodVolumes)
			//	klog.Errorf("Failed to allocate task: for %s", err.Error())
			//}
		}
	}
}
