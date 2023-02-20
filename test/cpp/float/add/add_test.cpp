#include "add.h"
#include "test.h"

int main() {
  int ok = almost_equal(add(2.0, 3.0), 5.0);
  return !ok;
}
