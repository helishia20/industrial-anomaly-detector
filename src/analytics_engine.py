import math

class WelfordStreamAnalyzer:
    """
    Computes streaming mean and variance using Welford's online algorithm.
    Ensures O(1) time complexity and constant memory usage.
    """
    def __init__(self, threshold=3.0, warmup=5):
        self.threshold = threshold
        self.warmup = warmup
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0

    def process_sample(self, value):
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.M2 += delta * delta2

        # Prevent processing before calibration (Warm-up phase)
        if self.count < self.warmup or self.count < 2:
            return False, 0.0, self.mean

        variance = self.M2 / (self.count - 1)
        std_dev = math.sqrt(variance)

        #  Prevent division by zero if standard deviation is zero
        if std_dev == 0.0:
            return False, 0.0, self.mean

        z_score = (value - self.mean) / std_dev
        is_anomaly = abs(z_score) > self.threshold

        return is_anomaly, z_score, self.mean