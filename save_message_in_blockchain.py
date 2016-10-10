import argparse
import base64
import subprocess

import datetime

import btc_address_utility
import json
import base58
import imghdr


def send_image(messagefile, chunk_size):
    from_account = "TODO"
    send_amount = "0.000015"
    chunk_size = chunk_size

    chunks = btc_address_utility.convert_file_to_chunks(messagefile, chunk_size)
    addresses = btc_address_utility.get_addresses_from_chunks(chunks, chunk_size, True)

    res = []
    reqs_per_tx = 400
    for i in range(0, len(addresses), reqs_per_tx):
        req = {}
        for x in range(0, reqs_per_tx):
            if i+x < len(addresses):
                req[addresses[i+x]] = send_amount

        res.append(subprocess.check_output(
            ["bitcoin-cli", r"-datadir=bitcoin-testnet-box/1", "sendmany", "", json.dumps(req)]).decode().strip())
        req = {}

    out = {"encoded_addresses": addresses, "transactionId": res, "dataChunkSize": chunk_size}
    return json.dumps(out)


def retrieve_image(tx_ids, chunk_size, address_list = None):
    addresses = address_list
    if address_list is not None:
        tx_ids = []

    for tx_id in tx_ids:
        print("\nRetrieving_image with tx_id: " + tx_id)
    # Get all sentto addresses from tx and loop
    # TODO

    indexed_data = {}
    for address in addresses:
        data = base58.b58decode(address)[1:-4].decode()
        indexed_data[int(data[:(20 - chunk_size)])] = data[(20 - chunk_size):].strip("@")

    imagedata = ""
    for i in range(0, len(indexed_data)):
        imagedata += indexed_data[i]

    imagedata = imagedata.encode()

    return base64.decodebytes(imagedata)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    # Encode and send image or retrieve from address?
    action = arg_parser.add_mutually_exclusive_group(required=False)
    action.add_argument('-s', '--send', help="Send an encoded file to the blockchain", action="store_true")
    action.add_argument('-r', '--retrieve', help="Retrieve an encoded file from the blockchain", action="store_true")

    # Input file or output file for operation
    filearg = arg_parser.add_mutually_exclusive_group(required=False)
    filearg.add_argument("-i", "--infile", help="The file to encode into blockchain addresses, if applicable.", action="store", nargs="?")
    filearg.add_argument("-o", "--outfile", help="The location to save the retrieved image, if applicable.", action="store", nargs="?")

    args = arg_parser.parse_args()
    infile = args.infile or 'input.jpeg'

    print(infile)

    with open(infile, "rb") as f:
        file = f.read()
        send_res = send_image(file, 14)

    image = retrieve_image('tx_id placeholder', 14, json.loads(send_res)['encoded_addresses'])

    file_extension = imghdr.what("", image)
    with open("image" + datetime.datetime.now().strftime('%Y-%m-%d_%Hh-%Mm-%Ss') + "." + file_extension, "wb") as outfile:
        outfile.write(image)
