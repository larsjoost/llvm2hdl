#include <stdio.h>

#include "instruction_decode.h"

void print_instruction(uint32_t instruction, const DecodedInstruction &inst) {
    printf("Instruction = 0x%08X\n", instruction);
    printf("opcode = 0x%02X\n", inst.opcode);
    printf("rd = 0x%02X\n", inst.rd);
    printf("funct3 = 0x%02X\n", inst.funct3);
    printf("rs1 = 0x%02X\n", inst.rs1);
    printf("rs2 = 0x%02X\n", inst.rs2);
    printf("funct7 = 0x%02X\n", inst.funct7);
    printf("I-Type imm = 0x%03X (%u)\n", inst.i_imm, inst.i_imm);
    printf("S-Type imm = 0x%03X (%u)\n", inst.s_imm, inst.s_imm);
    printf("U-Type imm = 0x%08X (%u)\n", inst.u_imm, inst.u_imm);
}
