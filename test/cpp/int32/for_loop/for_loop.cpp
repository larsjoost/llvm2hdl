#include "for_loop.h"

int for_loop(const int a[SIZE]) {
  int s = 0;
  for (int i = 0; i < SIZE; i++) {
    s += a[i];
  }
  return s;
}
