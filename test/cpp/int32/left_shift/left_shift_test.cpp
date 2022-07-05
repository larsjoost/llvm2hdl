#include "left_shift.h"

int main() {
    int ok = (left_shift(0x10, 4) == 0x100);
    return !ok;
}
