#include <stdio.h>

#include "rv32i.h"
#include "instruction_set.h"
#include "instruction_decode.h"
#include "debug_print.h"

inline void rv32i_op_imm(DecodedInstruction& decoded_instruction, uint32_t* registers, uint32_t* memory) {
    uint32_t destination_register_number, value;
    destination_register_number = decoded_instruction.rd;
    value = decoded_instruction.i_imm;
    debug_printf("Write %u to register %u\n", value, destination_register_number);
    registers[destination_register_number] = value;
}

inline void rv32i_store(DecodedInstruction& decoded_instruction, uint32_t* registers, uint32_t* memory) {
    uint32_t base_address, address_offset, address, value, register_number;
    base_address = registers[decoded_instruction.rs1];
    address_offset = decoded_instruction.s_imm;
    address = base_address + address_offset;
    register_number = decoded_instruction.rs2;
    value = registers[register_number];
    debug_printf("Store 0x%08X from register %u to address 0x%08X\n", value, register_number, address);
    memory[address] = value;
}

inline void rv32i_parse_opcode(DecodedInstruction& decoded_instruction, uint32_t* registers, uint32_t* memory) {
  switch (decoded_instruction.opcode)
  {
  case OP_IMM:
    rv32i_op_imm(decoded_instruction, registers, memory);
    break;
  case STORE:
    rv32i_store(decoded_instruction, registers, memory);
    break;
  default:
    break;
  }
}

void rv32i(uint32_t* memory) {
  static uint32_t registers[32] = {};
  static uint32_t program_counter = 0;
  uint32_t instruction = memory[program_counter++];
  DecodedInstruction decoded_instruction = decode_instruction(instruction);
  rv32i_parse_opcode(decoded_instruction, registers, memory);
};
