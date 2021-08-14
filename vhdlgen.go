package main

type VhdlGen struct {
	name            string
	ports           []string
	generics        []string
	assignment      []string
	returnDataWidth string
}

func (x *VhdlGen) initialize(name string, returnDataWidth string) {
	x.name = name
	x.returnDataWidth = returnDataWidth
	x.ports = append(x.ports,
		"clk : IN std_ulogic",
		"sreset : IN std_ulogic",
		"tag_in : in std_ulogic_vector(0 to tag_width - 1) := (others => '0')",
		"tag_out : out std_ulogic_vector(0 to tag_width - 1)",
		"return_value : out std_ulogic_vector(0 to "+returnDataWidth+" - 1)")
	x.generics = append(x.generics,
		"tag_width : positive := 1")
}

func (x *VhdlGen) addReturnAssignment(assignment string) {
	x.assignment = append(x.assignment, "return_value <= "+assignment)
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

func (x *VhdlGen) assignmentToString() string {
	t := ""
	for _, i := range x.assignment {
		t = t + i
	}
	return t + "\n"
}

func (x *VhdlGen) architectureToString() string {
	return "architecture rtl of " + x.name + " is\n" +
		"begin\n" +
		x.assignmentToString() +
		"end architecture " + x.name + ";\n"
}

func (x *VhdlGen) toString() string {
	return x.entityToString() + x.architectureToString()
}
