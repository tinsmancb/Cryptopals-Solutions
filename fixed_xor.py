from byteconvert import from_hex, to_hex
import numpy as np
import string

def fixed_xor(bs1, bs2):
    if isinstance(bs2, int):
        return bytes([b ^ bs2 for b in bs1])
    return bytes([b1 ^ b2 for b1, b2 in zip(bs1, bs2)])

def lev_dist_naive(s1, s2):
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    if s1[-1] == s2[-1]:
        cost = 0
    else:
        cost = 1

    return min([lev_dist(s1[:-1], s2) + 1,
                lev_dist(s1, s2[:-1]) + 1,
                lev_dist(s1[:-1], s2[:-1]) + cost])


def lev_dist(s1, s2):
    l1 = len(s1)
    l2 = len(s2)

    d = np.zeros((l1+1, l2+1))
    d[1:, 0] = np.arange(1, l1+1)
    d[0, 1:] = np.arange(1, l2+1).T

    for ii in np.arange(1, l1+1):
        for jj in np.arange(1, l2+1):
            if s1[ii-1] == s2[jj-1]:
                cost = 0
            else:
                cost = 1

            d[ii, jj] = min(d[ii-1, jj] + 1,
                            d[ii, jj-1] + 1,
                            d[ii-1, jj-1] + cost)
    return d[l1, l2]


def freq_score(bs):
    etaoin = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
    scores = {c: ii for ii, c in enumerate(etaoin)}
    letters = str(bs).upper()

    score = 0
    for c in letters:
        score = score + scores.get(c, 26)

    return score


def break_single_byte_xor(bs):
    key_scores = [(key, freq_score(fixed_xor(bs, key))) for key in range(256)]
    top_key = sorted(key_scores, key=lambda x: x[1])[0][0]
    return top_key, fixed_xor(bs, top_key)

def set1_challenge2():
    bs1 = from_hex('1c0111001f010100061a024b53535009181c')
    bs2 = from_hex('686974207468652062756c6c277320657965')
    bs_xor = fixed_xor(bs1, bs2)
    print(to_hex(bs_xor))
    assert to_hex(bs_xor) == '746865206b696420646f6e277420706c6179'
    
def set1_challenge3():
    cipher = from_hex('1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736')
    return break_single_byte_xor(cipher)
