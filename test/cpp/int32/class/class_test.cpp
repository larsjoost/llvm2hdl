#include "class.h"

int main() {
  ClassTest a(1, 2);
  int ok = (a.add() == 3);
  return !ok;
}
