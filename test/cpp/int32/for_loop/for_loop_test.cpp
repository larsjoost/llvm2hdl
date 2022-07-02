#include "for_loop.h"

int main() {
  int n[SIZE];
  int sum = 0;
  for (int i = 0 ; i < SIZE; i++) {
    int x = i + 1;
    n[i] = x;
    sum += x;
  }
  int ok = (for_loop(n) == sum);
  return !ok;
}
