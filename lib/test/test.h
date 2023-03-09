#include <cmath>

inline int almost_equal(float a, float b) {
  const float accuracy = 0.00001f;
  float difference = std::fabs(a - b);
  float difference_threshold = a * accuracy; 
  return difference > difference_threshold;
};
