#include <stdint.h>

struct DecodedInstruction {
  uint32_t opcode;
  uint32_t rd;
  uint32_t funct3;
  uint32_t rs1;
  uint32_t rs2;
  uint32_t funct7;
  uint32_t i_imm;
  uint32_t s_imm;
  uint32_t u_imm;
};

void print_instruction(uint32_t instruction, const DecodedInstruction &inst);

inline DecodedInstruction decode_instruction(int32_t instruction) {
  DecodedInstruction decoded_instruction;
  decoded_instruction.opcode = instruction & 0x7f;
  decoded_instruction.rd = (instruction >> 7) & 0x1f;
  decoded_instruction.funct3 = (instruction >> 12) & 0x7;
  decoded_instruction.rs1 = (instruction >> 15) & 0x1f;
  decoded_instruction.rs2 = (instruction >> 20) & 0x1f;
  decoded_instruction.funct7 = (instruction >> 25) & 0x7f;
  decoded_instruction.i_imm = (instruction >> 20) & 0xfff;
  decoded_instruction.s_imm = ((instruction & 0xfe000000) >> 20) | decoded_instruction.rd;
  decoded_instruction.u_imm = instruction & 0xfffff000;
#ifdef DEBUG
  print_instruction(instruction, decoded_instruction);
#endif
  return decoded_instruction;
};
