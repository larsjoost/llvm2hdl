#include <stdint.h>

#include "test.h"

void test() {
  uint32_t *p = (uint32_t *)TEST_RESULT_ADDRESS;
  *p = TEST_RESULT_VALUE;
}
