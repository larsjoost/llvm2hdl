#include "for_loop.h"

int main() {
  int n[SIZE] = {1, 2, 3};
  int ok = (for_loop(n) == 6);
  return !ok;
}
