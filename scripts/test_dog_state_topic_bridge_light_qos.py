#!/usr/bin/env python3
import unittest

import dog_state_topic_bridge_light as bridge
from rclpy.qos import DurabilityPolicy, HistoryPolicy, ReliabilityPolicy


class DogStateTopicBridgeLightQosTest(unittest.TestCase):
    def test_best_effort_qos_profile_uses_keep_last_volatile(self):
        qos = bridge.make_qos_profile("best_effort", 3)

        self.assertEqual(qos.reliability, ReliabilityPolicy.BEST_EFFORT)
        self.assertEqual(qos.history, HistoryPolicy.KEEP_LAST)
        self.assertEqual(qos.durability, DurabilityPolicy.VOLATILE)
        self.assertEqual(qos.depth, 3)

    def test_compute_publish_period_returns_none_when_unlimited(self):
        self.assertIsNone(bridge.compute_publish_period(0.0))
        self.assertIsNone(bridge.compute_publish_period(-1.0))

    def test_compute_publish_period_returns_seconds_for_positive_rate(self):
        self.assertAlmostEqual(bridge.compute_publish_period(150.0), 1.0 / 150.0)


if __name__ == "__main__":
    unittest.main()
