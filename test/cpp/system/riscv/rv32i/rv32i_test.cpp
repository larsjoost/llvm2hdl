#include "instruction_set.h"
#include "rv32i.h"
#include "test.h"
#include "memory.h"

int main() {
  static int timeout = 3;
  static int ok = 0;
  while (!ok && timeout-- > 0) {
    rv32i(instruction_memory);
    ok = (instruction_memory[TEST_RESULT_ADDRESS] == TEST_RESULT_VALUE);
  }
  return !ok;
}
