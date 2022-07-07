#include "struct.h"

int main() {
  StructTest a = {1, 2};
  int ok = (struct_func(a) == 3);
  return !ok;
}
