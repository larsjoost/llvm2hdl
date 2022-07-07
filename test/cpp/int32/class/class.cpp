#include "class.h"

ClassTest::ClassTest(int a, int b) {
  this->a = a;
  this->b = b;
}

int ClassTest::add(void) {
  return this->a + this->b;
}
