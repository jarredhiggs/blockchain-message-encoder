import base64
import base58
import hashlib
import math


def convert_file_to_chunks(file, chunk_size):

    encoded = base64.b64encode(file)

    encoded_str = bytes.decode(encoded)
    chunks = []
    for chunk_num in range(0, math.ceil(len(encoded_str) / chunk_size)):
        start_sub = chunk_num * chunk_size
        end_sub = chunk_num * chunk_size + chunk_size
        substring = encoded_str[start_sub:end_sub]
        while len(substring) < chunk_size:
            substring += "@"
        chunks.append(substring)

    return chunks


def get_addresses_from_chunks(data, chunk_size, testnet = False):
    """
    :param data: List containing 62 character chunks of base64 data.
    """
    addresses = []
    for index in range(0, len(data)):
        hex_index = str(index).zfill(20 - chunk_size).encode()

        # Prepends an index to the data chunk. The index will always have 20 - <size of chunk> bytes. If the chunk size
        # is greater than 20, then a valid bitcoin address will not be formed.
        messagedata = hex_index + str(data[index]).encode()

        # Below steps are for creating Base58Check encoding
        # Add version byte in front of RIPEMD-160 hash
        # 0x00 for main net
        # 0x6F for test net
        versioned_messagedata = bytes.fromhex("6F" if testnet else "00") + messagedata

        # Perform SHA-256 hash on versioned ripemd160 then perform another SHA-256 on returned value
        sha256_versioned_ripemd160 = hashlib.sha256(versioned_messagedata).digest()

        # Perform another SHA-256 hash on returned value. First 4 bytes = address checksum
        hashed_checksum = hashlib.sha256(sha256_versioned_ripemd160).digest()
        address_checksum = hashed_checksum[:4]

        # Append address checksum to versioned ripemd-160 (prior to sha-256 double-hash) to get binary bitcoin address
        binary_btc_address = versioned_messagedata + address_checksum
        addresses.append(base58.b58encode(binary_btc_address))

    return addresses