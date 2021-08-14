package main

type VhdlGen struct {
	name            string
	ports           []string
	generics        []string
	instances       InstanceContainer
	returnDataWidth string
	returnName      string
}

func (x *VhdlGen) initialize(name string, returnDataWidth string) {
	x.name = name
	x.returnDataWidth = returnDataWidth
	x.returnName = "return_value"
	tagInputName := "tag_in"
	tagOutputName := "tag_out"
	x.ports = append(x.ports,
		"clk : IN std_ulogic",
		"sreset : IN std_ulogic",
		tagInputName+" : in std_ulogic_vector(0 to tag_width - 1) := (others => '0')",
		tagOutputName+" : out std_ulogic_vector(0 to tag_width - 1)",
		x.returnName+" : out std_ulogic_vector(0 to "+returnDataWidth+" - 1)")
	x.generics = append(x.generics,
		"tag_width : positive := 1")
}

func (x *VhdlGen) addInstance(instance *Instance) {
	x.instances.add(instance)
}

func (x *VhdlGen) addReturnInstance(instance *Instance) {
	instance.q_output = x.returnName
	x.addInstance(instance)
}

func (x *VhdlGen) addPort(port_description string) {
	x.ports = append(x.ports, port_description)
}

func (x *VhdlGen) headerToString() string {
	return "entity " + x.name + " is\n"
}

func (x *VhdlGen) tailToString() string {
	return "end entity " + x.name + ";\n"
}

func descriptorToString(name string, name_list *[]string) string {
	t := name + " (\n"
	delimiter := ""
	for _, i := range *name_list {
		t = t + delimiter + i
		delimiter = ";\n"
	}
	t = t + ");\n"
	return t
}

func (x *VhdlGen) genericsToString() string {
	return descriptorToString("generic", &x.generics)
}

func (x *VhdlGen) portsToString() string {
	return descriptorToString("port", &x.ports)
}

func (x *VhdlGen) entityToString() string {
	return x.headerToString() + x.genericsToString() + x.portsToString() + x.tailToString()
}

func (x *VhdlGen) instancesToString() string {
	return x.instances.toString()
}

func (x *VhdlGen) architectureToString() string {
	return "architecture rtl of " + x.name + " is\n" +
		"begin\n" +
		x.instancesToString() +
		"end architecture " + x.name + ";\n"
}

func (x *VhdlGen) toString() string {
	return x.entityToString() + x.architectureToString()
}
