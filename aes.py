from itertools import islice, product

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes, random

from byteconvert import to_hex, from_hex, from_base64
from fixed_xor import fixed_xor

def aes_ecb_encrypt(key, plain_text):
    "Wrapper to encrypt a string using AES in ECB mode."
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plain_text)

def aes_ecb_decrypt(key, cipher_text):
    "Wrapper to decrypt a string using AES in ECB mode."
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(cipher_text)

def pkcs7_pad(bs, block_size=16):
    "Implement PKCS#7 padding."
    bytes_needed = block_size - (len(bs) % block_size)
    if bytes_needed != block_size:
        return bs + bytes([bytes_needed]*bytes_needed)

    return bs

def pkcs7_unpad(bs, block_size=16):
    "Unpad a string with PKCS#7, raising a ValueError if not padded correctly."
    if len(bs) % block_size != 0:
        raise ValueError('bs does not have the right length '
                         'for a PKCS#7 padded string with '
                         'block_size {}'.format(block_size))

    last_byte = bs[-1]
    for b in bs[-last_byte:]:
        if b != last_byte:
            raise ValueError('bs is not a PKCS#7 padded string.')

    return bs[:-last_byte]

def aes_cbc_encrypt(key, iv, plain_text):
    "Implement CBC mode encryption using our ECB mode wrapper."
    cipher_text = bytearray(b'')
    last_ctext = iv
    it = iter(plain_text)
    blocks = []
    for ii in range(len(plain_text)//16):
        blocks.append(bytes(islice(it, 16)))

    for block in blocks:
        last_ctext = aes_ecb_encrypt(key, fixed_xor(block, last_ctext))
        cipher_text += last_ctext

    return bytes(cipher_text)

def aes_cbc_decrypt(key, iv, cipher_text):
    "Implement CBC mode decrytion using our ECB mode wrapper."
    plain_text = bytearray(b'')
    last_ctext = iv
    it = iter(cipher_text)
    blocks = []
    for ii in range(len(cipher_text)//16):
        blocks.append(bytes(islice(it, 16)))

    for block in blocks:
        plain_text += fixed_xor(aes_ecb_decrypt(key, block), last_ctext)
        last_ctext = block

    return bytes(plain_text)

def aes_black_box_encrypt(plain_text):
    "Encrypt a message with a random key, using ECB or CBC with equal probability."
    key = get_random_bytes(16)

    num_random_bytes = random.randint(5, 10)
    plain_text = get_random_bytes(num_random_bytes) + \
                 plain_text + \
                 get_random_bytes(16 - num_random_bytes)

    algo = random.choice(['ECB', 'CBC'])
    if algo == 'ECB':
        return algo, aes_ecb_encrypt(key, plain_text)

    iv = get_random_bytes(16)
    return algo, aes_cbc_encrypt(key, iv, plain_text)

def ecb_score(cipher_text):
    "Test if a string has been encrypted in ECB mode by looking for identical 16-byte blocks."
    it = iter(cipher_text)
    num_slices = len(cipher_text) // 16
    slices = []
    for jj in range(num_slices):
        slices.append(bytes(islice(it, 16)))

    score = sum([bs1 == bs2 for bs1, bs2 in product(slices, repeat=2)])
    score = (score - len(slices))//2
    return score

def detect_ecb(black_box):
    "Decide if a function is encrypting using ECB or CBC."
    plain_text = bytes([0x00] * 64)
    true, cipher_text = black_box(plain_text)
    score = ecb_score(cipher_text)
    guess = 'ECB' if score > 0 else 'CBC'
    return guess, true

def challenge7():
    "Solution for challenge 7."
    f = open('7.txt')
    cipher_text = from_base64(f.read())
    print(aes_ecb_decrypt(b'YELLOW SUBMARINE', cipher_text).decode())

def challenge8():
    "Solution for challenge 8."
    f = open('8.txt')
    cipher_texts = [from_hex(l) for l in f]
    best_score = 0
    best_ctext = ''
    for ii, ctext in enumerate(cipher_texts):
        score = ecb_score(ctext)
        if score > best_score:
            best_score = score
            best_ctext = ctext
    print("Best ciphertext, scoring {}:".format(best_score))
    it = iter(best_ctext)
    for ii in range(len(best_ctext)//16):
        print(to_hex(bytes(islice(it, 16))))
    print("Trial Decryption: {}".format(aes_ecb_decrypt(b"YELLOW SUBMARINE", best_ctext)))

def challenge9():
    "Solution for challenge 9."
    assert pkcs7_pad(b'YELLOW SUBMARINE', block_size=20) == b'YELLOW SUBMARINE\x04\x04\x04\x04'

def challenge10():
    "Solution for challenge 10."
    f = open('10.txt')
    cipher_text = from_base64(f.read())
    key = b'YELLOW SUBMARINE'
    iv = bytes([0]*16)
    plain_text = aes_cbc_decrypt(key, iv, cipher_text)
    print(plain_text.decode())
    assert aes_cbc_encrypt(key, iv, plain_text) == cipher_text

def challenge11():
    "Solution for challenge 11."
    for ii in range(16):
        guess, true = detect_ecb(aes_black_box_encrypt)
        exclaim = 'YAY!' if guess == true else 'BOO!'
        print('Algorithm predicted {}, actually {}. {}'.format(guess, true, exclaim))
