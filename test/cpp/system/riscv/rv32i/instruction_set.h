
/*

                   The RISC-V Instruction Set Manual

  31         25 24     20 19     15 14    12 11     7 6          0
  ----------------------------------------------------------------
  |   funct7   |   rs2   |   rs1   | funct3 |   rd   |   opcode   | R-type
  ----------------------------------------------------------------

  ----------------------------------------------------------------
  |        imm[11:0]     |   rs1   | funct3 |   rd   |   opcode   | I-type
  ----------------------------------------------------------------

  ----------------------------------------------------------------
  | imm[11:5]  |   rs2   |   rs1   | funct3 |imm[4:0]|   opcode   | S-type
  ----------------------------------------------------------------

  ----------------------------------------------------------------
  |                imm[31:12]               |   rd   |   opcode   | U-type
  ----------------------------------------------------------------

 */

//  Opcode
#define LOAD      0x03 // 0b0000011 
#define LOAD_FP   0x07 // 0b0000111 
#define custom_0  0x0B // 0b0001011 
#define MISC_MEM  0x0F // 0b0001111 
#define OP_IMM    0x13 // 0b0010011 
#define AUIPC     0x17 // 0b0010111 
#define OP_IMM_32 0x1B // 0b0011011
#define STORE     0x23 // 0b0100011 
#define STORE_FP  0x27 // 0b0100111 
#define custom_1  0x2B // 0b0101011 
#define AMO       0x2F // 0b0101111
#define OP        0x33 // 0b0110011
#define LUI       0x37 // 0b0110111
#define OP_32     0x3B // 0b0111011
#define MADD      0x43 // 0b1000011
#define MSUB      0x47 // 0b1000111
#define NMSUB     0x4B // 0b1001011
#define NMADD     0x4F // 0b1001111
#define OP_FP     0x53 // 0b1010011
// reserved       0b1010111
#define custom_2  0x5B // 0b1011011
#define BRANCH    0x63 // 0b1100011
#define JALR      0x67 // 0b1100111
// reserved       0b1101011
#define JAL       0x6F // 0b1101111
#define SYSTEM    0x73 // 0b1110011
// reserved       0b1110111
#define custom_3  0x7B // 0b1111011
