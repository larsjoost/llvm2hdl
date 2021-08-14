package main

import "fmt"

type Instance struct {
	operation string
	a_input   string
	b_input   string
	tagInput  string
	q_output  string
	tagOutput string
	prev      *Instance
	next      *Instance
}

type InstanceContainer struct {
	library   string
	instances []*Instance
}

func getInstanceIndex(instance *Instance) int {
	if instance.prev == nil {
		return 0
	}
	return getInstanceIndex(instance.prev) + 1
}

func getPreviousTagName(instance *Instance) string {
	if instance.prev != nil {
		return instance.prev.tagOutput
	}
	return "tag_in"
}

func getNextTagName(instance *Instance) string {
	if instance.next != nil {
		return instance.next.tagInput
	}
	return "tag_out"
}

func (x *InstanceContainer) instanceToString(instance *Instance) string {
	library := "work"
	if len(x.library) > 0 {
		library = x.library
	}
	instanceName := fmt.Sprint("inst_", getInstanceIndex(instance)) + "_" + instance.operation
	return instanceName + ": entity " + library + "." + instance.operation + " is " +
		"port map (clk => clk, sreset => sreset" +
		", tag_in => " + getPreviousTagName(instance) +
		", a => " + instance.a_input +
		", b => " + instance.b_input +
		", tag_out => " + getNextTagName(instance) +
		", q => " + instance.q_output +
		");\n"
}

func (x *InstanceContainer) add(instance *Instance) {
	numberOfInstances := len(x.instances)
	if numberOfInstances > 0 {
		lastElementIndex := numberOfInstances - 1
		instance.prev = x.instances[lastElementIndex]
	}
	x.instances = append(x.instances, instance)
}

func (x InstanceContainer) toString() string {
	t := ""
	for _, i := range x.instances {
		t = t + x.instanceToString(i)
	}
	return t + "\n"
}
