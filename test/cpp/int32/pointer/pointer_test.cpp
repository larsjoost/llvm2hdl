#include "pointer.h"

int main() {
  int a;
  set(&a);
  int ok = (a == 1);
  return !ok;
}
