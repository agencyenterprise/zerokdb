import struct
import math

# Initialize variables
s = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4

# Use integer part of sines of integers (Radians) as constants
K = [int((1 << 32) * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]


def left_rotate(x, amount):
    x &= 0xFFFFFFFF
    return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF


def md5(message):
    # Convert message to bytearray
    msg = bytearray(message, "utf-8")
    orig_len_in_bits = (8 * len(msg)) & 0xFFFFFFFFFFFFFFFF
    msg.append(0x80)

    while (len(msg) * 8) % 512 != 448:
        msg.append(0)

    msg += struct.pack("<Q", orig_len_in_bits)

    # Initial hash values
    A = 0x67452301
    B = 0xEFCDAB89
    C = 0x98BADCFE
    D = 0x10325476

    # Process each 512-bit chunk
    for chunk_offset in range(0, len(msg), 64):
        a, b, c, d = A, B, C, D
        chunk = msg[chunk_offset : chunk_offset + 64]
        M = list(struct.unpack("<16I", chunk))
        for i in range(64):
            if 0 <= i <= 15:
                F = (b & c) | (~b & d)
                g = i
            elif 16 <= i <= 31:
                F = (d & b) | (~d & c)
                g = (5 * i + 1) % 16
            elif 32 <= i <= 47:
                F = b ^ c ^ d
                g = (3 * i + 5) % 16
            elif 48 <= i <= 63:
                F = c ^ (b | ~d)
                g = (7 * i) % 16

            temp = D
            D = C
            C = B
            B = (B + left_rotate((A + F + K[i] + M[g]), s[i])) & 0xFFFFFFFF
            A = temp

        # Add this chunk's hash to result so far
        A = (A + a) & 0xFFFFFFFF
        B = (B + b) & 0xFFFFFFFF
        C = (C + c) & 0xFFFFFFFF
        D = (D + d) & 0xFFFFFFFF

    # Produce the final hash value (little-endian)
    return "".join("{:02x}".format(x) for x in struct.pack("<4I", A, B, C, D))


# Example usage
if __name__ == "__main__":
    message = "Hello, World!"
    hash_result = md5(message)
    print(f"MD5('{message}') = {hash_result}")
