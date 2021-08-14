package main

import (
	"flag"
	"fmt"
	"log"
	"reflect"
	"strconv"
	"strings"

	"github.com/ianlancetaylor/demangle"
	"github.com/kr/pretty"
	"github.com/llir/llvm/asm"
	"github.com/llir/llvm/ir"
	"github.com/llir/llvm/ir/types"
	"github.com/llir/llvm/ir/value"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	print_llvm := flag.Bool("llvm-tree", false, "Prints the parsed llvm tree")
	flag.Parse()

	file_names := flag.Args()
	for _, file_name := range file_names {
		m, err := asm.ParseFile(file_name)
		if err != nil {
			log.Fatalf("%+v", err)
		}
		if *print_llvm {
			pretty.Println(m)
		} else {
			fmt.Print(genCode(m))
		}
	}
}

func getInstLoad(x *ir.InstLoad) string {
	return getValue(x.Src)
}

func getInstAlloca(x *ir.InstAlloca) string {
	return x.LocalName
}

func getInstStore(x *ir.InstStore) string {
	return getValue(x.Dst) + " <= " + getValue(x.Src)
}

func getParamDefinition(x *ir.Param) string {
	bitWidth := intToa(getBitWidth(x.Type()))
	return getParamName(x) + " : IN std_ulogic_vector(0 to " + bitWidth + " - 1)"
}

func demangleName(x string) string {
	name, err := demangle.ToString(x)
	if err != nil {
		name = x
		log.Println(err, ": "+x)
	}
	return name
}

func getParamName(x *ir.Param) string {
	return x.LocalName
}

func intToa(x uint64) string {
	return strconv.Itoa(int(x))
}

func getBitWidth(x types.Type) uint64 {
	switch x := x.(type) {
	case *types.IntType:
		return x.BitSize
	default:
		log.Fatal("Unknown value: " + reflect.TypeOf(x).String())
	}
	return 0
}

func getValue(x value.Value) string {
	switch x := x.(type) {
	case *ir.InstLoad:
		return getInstLoad(x)
	case *ir.InstAlloca:
		return getInstAlloca(x)
	case *ir.Param:
		return getParamName(x)
	default:
		log.Fatal("Unknown value: " + reflect.TypeOf(x).String())
	}
	return ""
}

func getInstanceAdd(add *ir.InstAdd) *Instance {
	return &Instance{operation: "add", a_input: getValue(add.X), b_input: getValue((add.Y))}
}

func getInstance(x value.Value) *Instance {
	switch x := x.(type) {
	case *ir.InstAdd:
		return getInstanceAdd(x)
	default:
		log.Fatal("Unknown instance: " + reflect.TypeOf(x).String())
	}
	return nil
}

func getTermRet(term *ir.TermRet) *Instance {
	return getInstance(term.X)
}

// genCallgraph returns the callgraph in Graphviz DOT format of the given LLVM
// IR module.
func genCode(m *ir.Module) string {
	buf := &strings.Builder{}
	// For each function of the module.
	codeGen := &VhdlGen{}
	for _, f := range m.Funcs {
		// Add caller node.
		caller := demangleName(f.Ident())
		returnDataWidth := intToa(getBitWidth(f.Sig.RetType))
		codeGen.initialize(caller, returnDataWidth)
		// For each basic block of the function.
		for _, params := range f.Params {
			codeGen.addPort(getParamDefinition(params))
		}
		for _, block := range f.Blocks {
			// For each non-branching instruction of the basic block.
			for _, inst := range block.Insts {
				// Type switch on instruction to find call instructions.
				switch inst := inst.(type) {
				case *ir.InstCall:
					callee := inst.Callee.Ident()
					// Add edges from caller to callee.
					fmt.Fprintf(buf, "\t%q -> %q\n", caller, callee)
				case *ir.InstLoad:
					buf.WriteString(getInstLoad(inst) + " -- Load\n")
				case *ir.InstAlloca:
					buf.WriteString(getInstAlloca(inst) + " -- Alloca\n")
				case *ir.InstAdd:
					codeGen.addInstance(getInstance(inst))
				case *ir.InstStore:
					buf.WriteString(getInstStore(inst) + "; -- Store\n")
				default:
					log.Fatal("Unknown inst: " + reflect.TypeOf(inst).String())
				}
			}
			// Terminator of basic block.
			term := block.Term
			switch term := term.(type) {
			case *ir.TermRet:
				codeGen.addReturnInstance(getTermRet(term))
			}
		}
	}
	return codeGen.toString()
}
