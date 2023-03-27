#include "for_loop.h"

int main() {
  int values[SIZE] = {1, 2, 3};
  int ok = (for_loop(values) == 6);
  return !ok;
}
