#include "fir.h"
#include "test.h"

int main() {
  int ok = 1;
  ok &= almost_equal(fir(1.0), 1.0);
  ok &= almost_equal(fir(2.0), 4.0);
  ok &= almost_equal(fir(3.0), 10.0);
  return !ok;
}
