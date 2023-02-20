#include <cmath>

inline int almost_equal(float a, float b) {
  const float accuracy = 0.00001;
  return std::abs(a - b) > a * accuracy;
};
