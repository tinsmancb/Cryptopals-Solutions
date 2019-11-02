import string
from itertools import zip_longest

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed_length chunks or blocks"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def to_hex(bs, lower=True):
    # bytes.hex() should do the same thing
    f = lambda x: x.lower() if lower else x
    return f(''.join('{:02X}'.format(b) for b in bs))

def from_hex(s):
    # bytes.fromhex() should do the same thing

    good_chars = '01234567890ABCDEFabcdef'
    s = ''.join(c for c in s if c in good_chars)

    if len(s) % 2 == 1:
        s = '0' + s
    return bytes([int(c1 + c2, base=16) for c1, c2 in grouper(s, 2, '0')])

def to_base64(bs, c_62 = '+', c_63 = '/', pad = '='):
    # base64.encode() should do the same thing
    trans_table = string.ascii_uppercase \
                + string.ascii_lowercase \
                + string.digits + c_62 + c_63
    
    s = ''
    for b1, b2, b3 in grouper(bs, 3, 'x'):
        c1 = trans_table[b1 >> 2]
        if b2 == 'x':
            c2 = trans_table[(b1 % 4) << 4]
            c3 = pad
            c4 = pad
        elif b3 == 'x':
            c2 = trans_table[((b1 % 4) << 4) + (b2 >> 4)]
            c3 = trans_table[(b2 % 16) << 2]
            c4 = pad
        else:
            c2 = trans_table[((b1 % 4) << 4) + (b2 >> 4)]
            c3 = trans_table[((b2 % 16) << 2) + (b3 >> 6)]
            c4 = trans_table[(b3 % 64)]
        s = s + ''.join([c1, c2, c3, c4])

    return s



def from_base64(s, c_62 = '+', c_63 = '/', pad = '='):
    # base64.decode should do the same thing
    trans_table = string.ascii_uppercase \
                + string.ascii_lowercase \
                + string.digits + c_62 + c_63

    inv_table = {c: ii for ii, c in enumerate(trans_table)}

    s = ''.join(c for c in s if c in trans_table + pad)

    if not pad:
        pad = '='

    bs = b''

    for c1, c2, c3, c4 in grouper(s, 4, pad):
        b1 = (inv_table[c1] << 2) + (inv_table[c2] >> 4)
        if c3 == pad:
            bs = bs + bytes([b1])
        elif c4 == pad:
            b2 = ((inv_table[c2] % 16) << 4) + (inv_table[c3] >> 2)
            bs = bs + bytes([b1, b2])
        else:
            b2 = ((inv_table[c2] % 16) << 4) + (inv_table[c3] >> 2)
            b3 = ((inv_table[c3] % 4) << 6) + inv_table[c4]
            bs = bs + bytes([b1, b2, b3])

    return bs
        

def set1_challenge1():
    s = '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d'
    base64 = 'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t'
    assert(to_base64(from_hex(s)) == base64)
    assert(s == to_hex(from_base64(base64), lower=True))
