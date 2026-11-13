import os, sys, hashlib, gzip
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def pgen(SourceName):
    ch = "6stuv#*'~abcdnLMNziABCDopqrST()=?`'+23;:_,.-<>|45ijklPQR7890^?!?$%&/'mXYZ1wxyGHIJUVWefghKEFO"
    pw = ''
    otherName = 'SimplyPut'
    i = 1
    while len(pw) < 16:
        cc1 = ord(SourceName[len(SourceName) - i]) - 48
        cc2 = ord(otherName[i]) - 48
        pw = pw + ch[abs(cc1)] + ch[abs(cc2)]
        i += 1
        if len(pw) > 14: break
    return pw

def evp_bytes_to_key(password, salt, key_len=32, iv_len=16):
    digest = password + salt
    md5_hashes = []
    for _ in range(3):
        h = hashlib.md5(digest).digest()
        md5_hashes.append(h)
        digest = h + password + salt
    key = md5_hashes[0] + md5_hashes[1]
    iv = md5_hashes[2]
    return key, iv

def decrypt_firmware(bin_path, out_path=None):
    if not os.path.exists(bin_path):
        print(f"Error: {bin_path} not found.")
        return False
        
    pw = pgen('BEHRINGER_FLOW8_v11748')
    with open(bin_path, 'rb') as f:
        enc_data = f.read()

    salt = enc_data[8:16]
    ciphertext = enc_data[16:]
    key, iv = evp_bytes_to_key(pw.encode('latin1'), salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plain = unpadder.update(padded_plain) + unpadder.finalize()
    decomp = gzip.decompress(plain)

    if out_path is None:
        out_path = bin_path.replace('.bin', '_decompressed.bin')

    with open(out_path, 'wb') as f:
        f.write(decomp)

    print(f"Success! Decrypted size: {len(decomp)} bytes -> {out_path}")
    return True

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'BEHRINGER_FLOW8_v11748.bin'
    decrypt_firmware(target)
