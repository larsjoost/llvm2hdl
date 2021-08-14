package main

type Instance struct {
	library   string
	operation string
	a_input   string
	b_input   string
	q_output  string
}

func (x *Instance) toString() string {
	library := "work"
	if len(x.library) > 0 {
		library = x.library
	}
	return "entity " + library + "." + x.operation + " is " +
		"port map (clk => clk, sreset => sreset, " +
		", a => " + x.a_input +
		", b => " + x.b_input +
		", q => " + x.q_output +
		");\n"
}
