package simulator

import (
	"encoding/json"
	v1 "k8s.io/api/core/v1"
	"sigs.k8s.io/yaml"
	batch "volcano.sh/apis/pkg/apis/batch/v1alpha1"
	"volcano.sh/apis/pkg/apis/scheduling"
	schedulingapi "volcano.sh/volcano/pkg/scheduler/api"
)

type WorkloadType struct {
	Workload   string `json:"workload"`
	Nodes      string `json:"nodes"`
	Period     string `json:"period"`
}

type ConfType struct {
	Conf string `json:"conf"`
}

//附带比基础node更多的信息
type V2Node struct {
	v1.Node

	//node计算速度，如0.8表示一个node完成一个负载的时间为正常时间的1/0.8倍
	CalculationSpeed float64 `json:"calculationSpeed"`

	//自己加的，node计算速度会下降，表示该值最低值
	MinimumSpeed float64 `json:"minimumSpeed"`

	//自己加的，node计算速度会下降，表示cpu占用率达到多少时开始下降
	SlowSpeedThreshold float64 `json:"slowSpeedThreshold"`

	//在该node上创建一个container需要的时间
	CtnCreationTime float64 `json:"ctnCreationTime"`

	//在该node上多创建一个container需要的额外时间，如创建3个，则第一个container创建时间为 CtnCreationTime+2*CtnCreationExtraTime
	CtnCreationExtraTime float64 `json:"ctnCreationExtraTime"`

	//在该node上多创建一个container需要的额外时间，如创建3个，则第一个container创建时间为 CtnCreationTime+2*CtnCreationExtraTime ，第二个为 CtnCreationTime+2*CtnCreationExtraTime+CtnCreationTimeInterVal
	CtnCreationTimeInterval int64 `json:"ctnCreationTimeInterval"`
}

type Info struct {
	Jobs           map[schedulingapi.JobID]*schedulingapi.JobInfo
	Nodes          map[string]*schedulingapi.NodeInfo
	NotCompletion  bool

	Done           bool `json:"done"`
	V1Nodes          []*v1.Node `json:"nodes"`
	Pods           []*v1.Pod `json:"pods"`
	Clock          string `json:"clock"`
}


func json2Job(jsonJob []byte) (error, *batch.Job)  {
	var job *batch.Job
	err := json.Unmarshal(jsonJob, &job) //json格式推荐使用Gi（memory，500Gi = 500GiB = 500 * 1024 * 1024 * 1024）和m（cpu，500m = 0.5 cores），
	return err,job
}
func json2Node(jsonNode []byte) (error, *v1.Node)  {
	var node *v1.Node
	err := json.Unmarshal(jsonNode, &node)
	return err,node
}
func Yaml2Nodes(yamlNodes []byte) (error, map[string][]*V2Node)  {
	detail := make(map[string][]*V2Node)
	jsond, err := yaml.YAMLToJSON([]byte(yamlNodes)) //jsond是一个yaml.Marshal后的string,转成json的 []byte
	json.Unmarshal(jsond, &detail) //[]byte到json
	return err,detail
}
func Yaml2Jobs(yamlJobs []byte) (error, map[string][]*batch.Job)  {
	detail := make(map[string][]*batch.Job)
	jsond, err := yaml.YAMLToJSON([]byte(yamlJobs)) //jsond是一个yaml.Marshal后的string,转成json的 []byte
	json.Unmarshal(jsond, &detail) //[]byte到json
	return err,detail
}
func Json2Queue(jsonQueue []byte) (error, *scheduling.Queue)  {
	var queue *scheduling.Queue
	err := json.Unmarshal(jsonQueue, &queue)
	return err,queue
}
