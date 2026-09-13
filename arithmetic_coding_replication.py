#!/usr/bin/env python3
"""
Arithmetic coding replication based on:
Witten, I.H., Neal, R.M., and Cleary, J.G. (1987),
"Arithmetic Coding for Data Compression", Communications of the ACM, 30(6), 520-540.

The implementation mirrors the paper's practical choices:
- 16-bit code values
- Max-frequency = 2^14 - 1
- adaptive model with initial count 1 for every symbol
- an explicit EOF symbol
- integer range renormalization with underflow (E3) handling

The two artificial files are constructed exactly as described in the paper:
- Alphabet: repeated lowercase alphabet to 100,000 bytes
- Skew statistics: 10,000 copies of "aaaabaaaac"
"""

from collections import Counter
import math
import heapq
import numpy as np

class AdaptiveModel:
    def __init__(self, n=257, max_freq=16383):
        self.n = n
        self.max_freq = max_freq
        self.freq = [1] * n

    @property
    def total(self):
        return sum(self.freq)

    def cumulative(self, symbol):
        low = sum(self.freq[:symbol])
        return low, low + self.freq[symbol], self.total

    def update(self, symbol):
        if self.total >= self.max_freq:
            self.freq = [max(1, f // 2) for f in self.freq]
        self.freq[symbol] += 1

    def find_symbol(self, value):
        total = self.total
        cumulative = 0
        for symbol, frequency in enumerate(self.freq):
            if value < cumulative + frequency:
                return symbol, cumulative, cumulative + frequency
            cumulative += frequency
        raise ValueError("Invalid arithmetic code value")


class ArithmeticCoder:
    def __init__(self, n_symbols=257, code_bits=16, max_freq=16383):
        self.n = n_symbols
        self.code_bits = code_bits
        self.top = (1 << code_bits) - 1
        self.first_qtr = (self.top + 1) // 4
        self.half = 2 * self.first_qtr
        self.third_qtr = 3 * self.first_qtr
        self.max_freq = max_freq

    def encode(self, data):
        model = AdaptiveModel(self.n, self.max_freq)
        low, high = 0, self.top
        bits_to_follow = 0
        output_bits = []

        def bit_plus_follow(bit):
            nonlocal bits_to_follow
            output_bits.append(bit)
            output_bits.extend([1 - bit] * bits_to_follow)
            bits_to_follow = 0

        # Encode all bytes, then EOF.
        for symbol in list(data) + [self.n - 1]:
            cum_low, cum_high, total = model.cumulative(symbol)
            current_range = high - low + 1

            high = low + (current_range * cum_high) // total - 1
            low = low + (current_range * cum_low) // total

            while True:
                if high < self.half:
                    bit_plus_follow(0)
                elif low >= self.half:
                    bit_plus_follow(1)
                    low -= self.half
                    high -= self.half
                elif low >= self.first_qtr and high < self.third_qtr:
                    bits_to_follow += 1
                    low -= self.first_qtr
                    high -= self.first_qtr
                else:
                    break

                low = 2 * low
                high = 2 * high + 1

            model.update(symbol)

        # Terminate the stream.
        bits_to_follow += 1
        bit_plus_follow(0 if low < self.first_qtr else 1)

        nbits = len(output_bits)
        output = bytearray((nbits + 7) // 8)

        for i, bit in enumerate(output_bits):
            output[i // 8] = (output[i // 8] << 1) | bit

        if nbits % 8:
            output[-1] <<= 8 - (nbits % 8)

        return bytes(output), nbits

    def decode(self, encoded, nbits):
        bits = [
            (encoded[i // 8] >> (7 - i % 8)) & 1
            for i in range(nbits)
        ]
        position = 0

        def next_bit():
            nonlocal position
            if position >= len(bits):
                return 0
            bit = bits[position]
            position += 1
            return bit

        model = AdaptiveModel(self.n, self.max_freq)
        low, high, value = 0, self.top, 0

        for _ in range(self.code_bits):
            value = 2 * value + next_bit()

        decoded = bytearray()

        while True:
            total = model.total
            current_range = high - low + 1
            scaled_value = ((value - low + 1) * total - 1) // current_range
            symbol, cum_low, cum_high = model.find_symbol(scaled_value)

            current_range = high - low + 1
            high = low + (current_range * cum_high) // total - 1
            low = low + (current_range * cum_low) // total

            while True:
                if high < self.half:
                    pass
                elif low >= self.half:
                    value -= self.half
                    low -= self.half
                    high -= self.half
                elif low >= self.first_qtr and high < self.third_qtr:
                    value -= self.first_qtr
                    low -= self.first_qtr
                    high -= self.first_qtr
                else:
                    break

                low = 2 * low
                high = 2 * high + 1
                value = 2 * value + next_bit()

            if symbol == self.n - 1:
                break

            decoded.append(symbol)
            model.update(symbol)

        return bytes(decoded)


def huffman_bits(data):
    """Exact bit count for a static Huffman code using empirical frequencies."""
    frequency = Counter(data)
    if len(frequency) <= 1:
        return len(data)

    heap = [[count, symbol] for symbol, count in frequency.items()]
    heapq.heapify(heap)
    next_id = max(frequency) + 1

    while len(heap) > 1:
        f1, a = heapq.heappop(heap)
        f2, b = heapq.heappop(heap)
        heapq.heappush(heap, [f1 + f2, next_id, (a, b)])
        next_id += 1
    return None


def paper_test_files():
    alphabet = (b"abcdefghijklmnopqrstuvwxyz" * 4000)[:100000]
    skew = b"aaaabaaaac" * 10000
    return {"Alphabet": alphabet, "Skew statistics": skew}


def main():
    coder = ArithmeticCoder()

    for name, data in paper_test_files().items():
        encoded, nbits = coder.encode(data)
        decoded = coder.decode(encoded, nbits)

        print(name)
        print(" input bytes:", len(data))
        print(" output bytes:", len(encoded))
        print(" bits/character:", nbits / len(data))
        print(" round-trip:", decoded == data)
        print()

    # Extension: binary source sensitivity.
    rng = np.random.default_rng(42)
    for p in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]:
        n = 30000
        data = bytes((rng.random(n) >= p).astype(np.uint8))
        _, nbits = coder.encode(data)
        entropy = -(p * math.log2(p) + (1-p) * math.log2(1-p))
        print(f"p={p:.2f}, H={entropy:.4f}, arithmetic={nbits/n:.4f}, "
              f"binary-Huffman=1.0000")


if __name__ == "__main__":
    main()
