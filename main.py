import idx2numpy
from datetime import datetime
import matplotlib.pyplot as plt
import math
import requests

step = 50


def to_string(data):
    output = ""
    for x in data:
        for y in x:
            output += "%03d" % y
    return output


def to_list(data):
    k = int(math.sqrt(len(data) / 3))
    output = [[0 for i in range(k)] for i in range(k)]
    for i in range(k):
        for j in range(k):
            output[i][j] = int(data[(i * k + j) * 3:(i * k + j + 1) * 3])
    return output


def send_data(amount):
    global top_hash
    start = datetime.now()
    for i in range(amount):
        files = {
            'file': (top_hash + "\n" + str(i) + "\n" + to_string(imagearray[i])),
        }
        response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=files)
        p = response.json()
        hash = p['Hash']
        top_hash = hash
        print(str(i) + ' https://ipfs.infura.io/ipfs/' + hash)
        if i % step == 0:
            f = open("steps.txt", "a")
            f.write(str(i) + " " + hash + "\n")
            f.close()

    try:
        f = open("top_hash.txt", "w+")
        f.write(top_hash)
        f.close()
        print("Top hash successfully updated.")
    except:
        print("Error updating top hash. Check file.")
        exit(-1)

    end = datetime.now()
    print("Data upload done after", (end - start), amount, "items sent.")


def get_data(amount):
    start = datetime.now()
    retrieved_data = []
    top_hash_local = top_hash
    i = 0
    while i < amount:
        params = (
            ('arg', top_hash_local),
        )
        response = requests.post('https://ipfs.infura.io:5001/api/v0/block/get', params=params)
        my_response_data = response.text.split('\n')
        print("Recieved", top_hash_local)
        top_hash_local = my_response_data[1][-46:]
        retrieved_data.append(my_response_data[3][:2352])
        i += 1
        if not top_hash_local.startswith("Qm"):
            break
    end = datetime.now()
    print("Data receival done after", (end - start), len(retrieved_data), "items recieved.")
    return retrieved_data


def get_block(block_id):
    global top_hash
    data = ""
    top_hash_local = top_hash
    f = open("steps.txt", "r")
    lines = f.readlines()
    for l in lines:
        if int(l[0:1]) > block_id:
            top_hash_local = l[2:]
            break

    condition = True
    while condition:
        params = (
            ('arg', top_hash_local),
        )
        response = requests.post('https://ipfs.infura.io:5001/api/v0/block/get', params=params)
        my_response_data = response.text.split('\n')
        this_id = int(my_response_data[2])
        if this_id == block_id:
            condition = False
            data = my_response_data[3][:2352]
        top_hash_local = my_response_data[1][-46:]

    return data


imagefile = 't10k-images.idx3-ubyte'
imagearray = idx2numpy.convert_from_file(imagefile)

f = open("top_hash.txt", "r")
top_hash = f.read()
f.close()

send_data(2)
# data = get_data(4)
# print(to_list(get_block(2)))
