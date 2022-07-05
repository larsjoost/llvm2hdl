#include "and.h"

int main() {
    int ok = (bitwise_and(0x24, 0x0F) == 4);
    return !ok;
}
