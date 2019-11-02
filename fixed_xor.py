from byteconvert import from_hex, to_hex

def fixed_xor(bs1, bs2):
    return bytes([b1 ^ b2 for b1, b2 in zip(bs1, bs2)])

def set1_challenge2():
    bs1 = from_hex('1c0111001f010100061a024b53535009181c')
    bs2 = from_hex('686974207468652062756c6c277320657965')
    bs_xor = fixed_xor(bs1, bs2)
    print(to_hex(bs_xor))
    assert to_hex(bs_xor) == '746865206b696420646f6e277420706c6179'
