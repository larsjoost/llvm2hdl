
/*

                   The RISC-V Instruction Set Manual

  31         25 24     20 19     15 14    12 11     7 6          0
  ----------------------------------------------------------------
  |   funct7   |   rs2   |   rs1   | funct3 |   rd   |   opcode   | R-type
  ----------------------------------------------------------------

 */

//  Opcode
#define LOAD      0b0000011 
#define LOAD_FP   0b0000111 
#define custom_0  0b0001011 
#define MISC_MEM  0b0001111 
#define OP_IMM    0b0010011 
#define AUIPC     0b0010111 
#define OP_IMM_32 0b0011011
#define STORE     0b0100011 
#define STORE_FP  0b0100111 
#define custom_1  0b0101011 
#define AMO       0b0101111
#define OP        0b0110011
#define LUI       0b0110111
#define OP_32     0b0111011
#define MADD      0b1000011
#define MSUB      0b1000111
#define NMSUB     0b1001011
#define NMADD     0b1001111
#define OP_FP     0b1010011
// reserved       0b1010111
#define custom_2  0b1011011
#define BRANCH    0b1100011
#define JALR      0b1100111
// reserved       0b1101011
#define JAL       0b1101111
#define SYSTEM    0b1110011
// reserved       0b1110111
#define custom_3  0b1111011

void instruction_decode(int32_t instruction) {
  int32_t opcode = instruction & 0x7f;
  int32_t rd = (instruction >> 6) & 0xf;
  int32_t funct3 = (instruction >> 11) & 0x7;
  int32_t rs1 = (instruction >> 14) & 0x1f;
  int32_t rs2 = (instruction >> 19) & 0x1f;
  int32_t funct7 = (instruction >> 24) & 0x7f;
};

