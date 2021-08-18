import argparse
import llvmlite.binding as llvm

from vhdlgen import VhdlGen

def main():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-f', dest='file_name', required=True,
    	                help='File name of the llvm ir file')
	parser.add_argument('--llvm-tree', dest='llvm_tree', action='store_true', default=False,
    	                help='Displays the complete parsed llvm tree')
	args = parser.parse_args()

	with open(args.file_name) as fh:
		text = fh.read()
	m = llvm.parse_assembly(text)

	c = VhdlGen()

	if args.llvm_tree:
		c.print_tree(m)

	c.parse(m)

if __name__ == "__main__":
    main()
