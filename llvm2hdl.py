from instance_statistics import InstanceStatistics
import os
import argparse
import llvmlite.binding as llvm

from file_writer import FileWriter
from vhdlgen import VhdlGen

def arguments():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-f', dest='file_name', required=True,
    	                help='File name of the llvm ir file')
	parser.add_argument('-o', dest='output_file_name', required=False, default=None,
    	                help='Output file name')
	parser.add_argument('-v', dest='verbose', action='store_true', default=False,
    	                help='Set verbosity on')
	parser.add_argument('--llvm-tree', dest='llvm_tree', action='store_true', default=False,
    	                help='Displays the complete parsed llvm tree')
	return parser.parse_args()

def main():
	args = arguments()

	with open(args.file_name) as fh:
		text = fh.read()
	m = llvm.parse_assembly(text)

	c = VhdlGen()

	if args.llvm_tree:
		c.print_tree(m)

	if args.output_file_name is not None:
		output_file_name = args.output_file_name
	else:
		pre, ext = os.path.splitext(args.file_name)	
		output_file_name = pre + ".vhd"
	
	statistics = InstanceStatistics()

	with open(output_file_name, 'w') as fh:
		file_writer = FileWriter(fh)
		c.parse(m, file_writer, statistics)
	
	if args.verbose:
		statistics.print()

if __name__ == "__main__":
    main()
