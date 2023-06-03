#include "pointer.h"

int main() {
  static int a;
  set(&a);
  int ok = (a == 1);
  return !ok;
}
