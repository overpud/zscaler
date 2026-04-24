import sys
import unittest
from pathlib import Path


AUTOSCALER_DIR = Path(__file__).resolve().parents[1] / "autoscaler"
sys.path.insert(0, str(AUTOSCALER_DIR))

from scaling import ScalingPolicy, build_policy, calculate_scale


class ScalingPolicyTest(unittest.TestCase):
    def test_scales_up_when_requests_per_replica_exceed_threshold(self):
        decision = calculate_scale(
            current_replicas=2,
            requests_count=120,
            policy=ScalingPolicy(min_replicas=1, max_replicas=4),
        )

        self.assertEqual(decision.target_replicas, 3)
        self.assertEqual(decision.reason, "scale_up_threshold_exceeded")

    def test_does_not_scale_above_max_replicas(self):
        decision = calculate_scale(
            current_replicas=4,
            requests_count=400,
            policy=ScalingPolicy(min_replicas=1, max_replicas=4),
        )

        self.assertEqual(decision.target_replicas, 4)
        self.assertEqual(decision.reason, "within_thresholds")

    def test_corrects_deployments_above_max_replicas(self):
        decision = calculate_scale(
            current_replicas=8,
            requests_count=400,
            policy=ScalingPolicy(min_replicas=1, max_replicas=4),
        )

        self.assertEqual(decision.target_replicas, 4)
        self.assertEqual(decision.reason, "above_max_replicas")

    def test_scales_down_when_requests_per_replica_are_low(self):
        decision = calculate_scale(
            current_replicas=3,
            requests_count=30,
            policy=ScalingPolicy(min_replicas=1, max_replicas=4),
        )

        self.assertEqual(decision.target_replicas, 2)
        self.assertEqual(decision.reason, "scale_down_threshold_met")

    def test_recovers_zero_replica_deployments(self):
        decision = calculate_scale(
            current_replicas=0,
            requests_count=100,
            policy=ScalingPolicy(min_replicas=1, max_replicas=4),
        )

        self.assertEqual(decision.target_replicas, 1)
        self.assertEqual(decision.reason, "below_min_replicas")

    def test_builds_policy_from_custom_resource_spec(self):
        policy = build_policy(
            {
                "minReplicas": 2,
                "maxReplicas": 8,
                "scaleUpThreshold": 75,
                "scaleDownThreshold": 25,
            }
        )

        self.assertEqual(policy.min_replicas, 2)
        self.assertEqual(policy.max_replicas, 8)
        self.assertEqual(policy.scale_up_threshold, 75)
        self.assertEqual(policy.scale_down_threshold, 25)

    def test_rejects_invalid_thresholds(self):
        with self.assertRaises(ValueError):
            build_policy({"scaleUpThreshold": 10, "scaleDownThreshold": 10})


if __name__ == "__main__":
    unittest.main()
