import os
import argparse
from llvmlite.binding import ModuleRef, parse_assembly

from instance_statistics import InstanceStatistics
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

    with open(args.file_name, 'r') as file_handle:
        text = file_handle.read()
    _llvm: ModuleRef = parse_assembly(text)

    _vhdlgen = VhdlGen()

    if args.llvm_tree:
        _vhdlgen.print_tree(_llvm)

    if args.output_file_name is not None:
        output_file_name = args.output_file_name
    else:
        pre, _ = os.path.splitext(args.file_name)
        output_file_name = pre + ".vhd"

    statistics = InstanceStatistics()

    with open(output_file_name, 'w') as file_handle:
        file_writer = FileWriter(file_handle)
        _vhdlgen.parse(_llvm, file_writer, statistics)

    if args.verbose:
        statistics.print()

if __name__ == "__main__":
    main()
