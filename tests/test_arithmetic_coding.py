import unittest

from arithmetic_coding_replication import ArithmeticCoder, paper_test_files


class TestArithmeticCoder(unittest.TestCase):
    def setUp(self):
        self.coder = ArithmeticCoder()

    def test_round_trip_small_inputs(self):
        samples = [b"", b"hello", b"a" * 1000, bytes(range(256))]
        for data in samples:
            with self.subTest(data_length=len(data)):
                encoded, nbits = self.coder.encode(data)
                decoded = self.coder.decode(encoded, nbits)
                self.assertEqual(decoded, data)

    def test_paper_datasets_round_trip(self):
        for name, data in paper_test_files().items():
            with self.subTest(dataset=name):
                encoded, nbits = self.coder.encode(data)
                decoded = self.coder.decode(encoded, nbits)
                self.assertEqual(decoded, data)

    def test_reported_paper_output_sizes(self):
        expected = {
            "Alphabet": 59292,
            "Skew statistics": 12092,
        }
        for name, data in paper_test_files().items():
            with self.subTest(dataset=name):
                encoded, _ = self.coder.encode(data)
                self.assertEqual(len(encoded), expected[name])


if __name__ == "__main__":
    unittest.main()
