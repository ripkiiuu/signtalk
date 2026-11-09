import unittest

import numpy as np

from ai.features import FEATURE_SCHEMA, temporal_summary


class TemporalSummaryTests(unittest.TestCase):
    def test_fixed_feature_width_and_presence(self):
        sequence = np.zeros((4, 2, 21, 3), dtype=np.float32)
        mask = np.zeros((4, 2), dtype=np.uint8)
        mask[:, 1] = 1
        sequence[:, 1, :, 0] = .25
        vector = temporal_summary(sequence, mask)
        self.assertEqual(FEATURE_SCHEMA, "normalized-hand-temporal-summary-v1")
        self.assertEqual(vector.shape, (884,))
        self.assertTrue(np.isfinite(vector).all())
        self.assertEqual(vector[0], 0.0)
        self.assertEqual(vector[442], 1.0)

    def test_empty_frame_sequence_does_not_create_nan(self):
        vector = temporal_summary(np.zeros((8, 2, 21, 3), np.float32), np.zeros((8, 2), np.uint8))
        self.assertEqual(vector.shape, (884,))
        self.assertTrue(np.equal(vector, 0).all())


if __name__ == "__main__":
    unittest.main()
