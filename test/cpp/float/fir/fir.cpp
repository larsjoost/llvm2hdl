#include "fir.h"

float fir(float x) {
  static float buffer[SIZE];
  for (int i = SIZE - 1; i > 0; i--) {
    buffer[i] = buffer[i - 1];
  }
  buffer[0] = x;
  float result = 0.0;
  for (int i = 0; i < SIZE; i++) {
    result += buffer[i] * coefficients[i];
  }
  return result;
};
