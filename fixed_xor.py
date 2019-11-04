from byteconvert import from_hex, to_hex, from_base64
import numpy as np
import string
from itertools import cycle, islice

def fixed_xor(bs1, bs2):
    if isinstance(bs2, int):
        return bytes([b ^ bs2 for b in bs1])
    return bytes([b1 ^ b2 for b1, b2 in zip(bs1, bs2)])


def repeating_key_xor(bs, key):
    return fixed_xor(bs, cycle(key))


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


def freq_score(bs, non_letter_penalty=50, non_print_penalty=9950):
    etaoin = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
    scores = {c: ii for ii, c in enumerate(etaoin)}
    scores.update({c: ii for ii, c in enumerate(etaoin.lower())})
    scores.update({c: non_letter_penalty for c in string.digits \
                                                + string.punctuation \
                                                + string.whitespace})
    letters = bs.decode(errors='replace')

    score = 0
    for c in letters:
        score += scores.get(c, non_print_penalty)

    return score

def hamming_dist(bs1, bs2):
    diff = fixed_xor(bs1, bs2)
    return sum(['{0:08b}'.format(x).count('1') for x in diff])

def break_single_byte_xor(bs):
    key_scores = [(key, freq_score(fixed_xor(bs, key))) for key in range(256)]
    top_keys = sorted(key_scores, key=lambda x: x[1])
    return top_keys[0][0]

def break_repeating_key_xor(bs, min_key=2, max_key=40):
    keysize_score = 8*len(bs)
    keysize = 0
    for k in range(min_key, max_key+1):
        it = iter(bs)
        s0 = bytes(islice(it, k))
        scores = []
        for ii in range(len(bs)//k):
            s1 = bytes(islice(it, k))
            scores.append(hamming_dist(s0, s1)/k)
            s0 = s1
        score = sum(scores)/len(scores)
        if score < keysize_score:
            keysize_score = score
            keysize = k

    split_bs = []
    it = iter(bs)
    for i in range(len(bs)//keysize):
        split_bs.append(list(islice(it, keysize)))

    sub_bs = []
    for i in range(keysize):
        sub_bs.append(bytes([b[i] for b in split_bs]))

    key = bytes([break_single_byte_xor(bs) for bs in sub_bs])
    return key

            


def challenge2():
    bs1 = from_hex('1c0111001f010100061a024b53535009181c')
    bs2 = from_hex('686974207468652062756c6c277320657965')
    bs_xor = fixed_xor(bs1, bs2)
    print(to_hex(bs_xor))
    assert to_hex(bs_xor) == '746865206b696420646f6e277420706c6179'
    
def challenge3():
    cipher = from_hex('1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736')
    key = break_single_byte_xor(cipher)
    print(fixed_xor(cipher, key))

def challenge4():
    f = open('4.txt', 'r')
    ciphers = [from_hex(l) for l in f]
    best_score = float('inf')
    for c in ciphers:
        key = break_single_byte_xor(c)
        plain = fixed_xor(c, key)
        score = freq_score(plain)
        if score < best_score:
            best_plain = fixed_xor(c, key)
            best_score = score
    print(best_plain)


def challenge5():
    plain = b"Burning 'em, if you ain't quick and nimble\nI go crazy when I hear a cymbal"
    cipher = repeating_key_xor(plain, b'ICE')
    check = '0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a26226324272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b20283165286326302e27282f'
    assert to_hex(cipher) == check
    assert repeating_key_xor(from_hex(check), b'ICE') == plain


def challenge6():
    f = open('6.txt', 'r')
    bs = from_base64(f.read())
    key = break_repeating_key_xor(bs)
    print(key)
    print(repeating_key_xor(bs, key).decode())
