from flask import Flask, request, jsonify
import requests
import threading
import time
from block import BLOCKCHAIN, Block

app = Flask(__name__)
PORT = 5000

NODES = []  # a list of IPs with ports (e.g. 12.34.56.78:1337) as strings
BRANCHES = {}  # Dictionary to hold different blockchain branches by their starting block hash

@app.post('/init/<addr>')
def init_node(addr):
    """
    Join the blockchain. IP is an IP of a node known to be in the blockchain.
    IP can be None if this is the first node in the blockchain.
    This is called on a node that is NOT in the blockchain yet.
    """
    def post_nodes(node):
        resp = requests.post(f'http://{node}/nodes')
        if resp.status_code != 200:
            return
        NODES.append(node)
        nodes = resp.json()['nodes']
        for n in nodes:
            if n not in NODES:
                post_nodes(n)
        return resp.json()['blockchain']

    blockchain = post_nodes(addr)
    BLOCKCHAIN.extend([Block.from_json(block) for block in blockchain])
    return NODES

@app.get('/nodes')
def get_nodes():
    return NODES

@app.post('/nodes')
def add_node():
    """
    Join new node to the network - respond with IPs of known nodes and send the entire blockchain.
    This is called on the nodes already in the blockchain.
    """
    if f'{request.remote_addr}:{PORT}' not in NODES:
        NODES.append(f'{request.remote_addr}:{PORT}')
    return {
        'nodes': NODES[:-1],
        'blockchain': [block.json() for block in BLOCKCHAIN]
    }

@app.post('/mine')
def mine_block():
    """
    Start mining for new block to store in the blockchain.
    This should receive the "information" that is to be stored in the blockchain in POST body (json).
    We can make this either automatic (node starts mining when it receives a query to store new data),
    or to be invoked by the "owner" of the machine (user behind the node).
    """
    data = request.json['data']  # data to store in the block
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    prev_hash = BLOCKCHAIN[-1].hash if len(BLOCKCHAIN) > 0 else b'\x00' * 64
    new_block = Block(data, prev_hash)
    new_block.mine()
    BLOCKCHAIN.append(new_block)

    # Propagate the mined block to all other nodes
    for node in NODES:
        try:
            requests.post(f'http://{node}/store_data', json=new_block.json())
        except requests.exceptions.RequestException:
            continue

    return jsonify(new_block.json()), 200

@app.post('/store_data')
def store_data():
    """
    Anyone can call this to add some data to the blockchain.
    The node that receives a request to this endpoint should propagate it to other nodes if it is the first one to
    receive the call to this endpoint (indicated by "propagate" flag in the request).
    """
    json_data = request.json
    if 'prev_hash' not in json_data:
        return jsonify({'error': 'Invalid block data'}), 400

    new_block = Block.from_json(json_data)
    prev_hash = new_block.prev_hash.hex()

    if len(BLOCKCHAIN) == 0 or BLOCKCHAIN[-1].hash == new_block.prev_hash:
        BLOCKCHAIN.append(new_block)
    else:
        # If there's a conflict, we add to a branch
        if prev_hash not in BRANCHES:
            BRANCHES[prev_hash] = [new_block]
        else:
            BRANCHES[prev_hash].append(new_block)

    # Start consensus mechanism after a short delay to determine the longest valid chain
    threading.Timer(10.0, resolve_conflicts).start()

    return jsonify({'status': 'Block received'}), 200

def resolve_conflicts():
    """
    Resolve conflicts by adopting the longest chain available.
    """
    global BLOCKCHAIN

    longest_chain = BLOCKCHAIN
    # Iterate over all branches to find the longest valid chain
    for branch_start, branch_blocks in BRANCHES.items():
        potential_chain = BLOCKCHAIN[:]
        for block in branch_blocks:
            if potential_chain[-1].hash == block.prev_hash:
                potential_chain.append(block)
        if len(potential_chain) > len(longest_chain):
            longest_chain = potential_chain

    # If a longer chain is found, adopt it
    if longest_chain != BLOCKCHAIN:
        BLOCKCHAIN = longest_chain
        print("Blockchain updated to the longest chain.")

@app.get('/blocks')
def get_blocks():
    """
    Return a serialized blockchain.
    """
    return jsonify([block.json() for block in BLOCKCHAIN]), 200

@app.get('/blocks/<id>')
def get_block(id):
    """
    Return a block with specific ID. The ID is the number of block in the BLOCKCHAIN list.
    """
    id_int = int(id)

    if id_int < 0 or id_int >= len(BLOCKCHAIN):
        return jsonify({'error': 'Block ID out of range'}), 404

    block = BLOCKCHAIN[id_int]
    return jsonify({'block': repr(block)}), 200


if __name__ == '__main__':
    # Initializing blockchain with three blocks
    #block1 = Block("some text", b'\x00' * 64)
    #block1.mine()
    #BLOCKCHAIN.append(block1)
    #block2 = Block("more text", BLOCKCHAIN[-1].hash)
    #block2.mine()
    #BLOCKCHAIN.append(block2)
    #block3 = Block("even more text", BLOCKCHAIN[-1].hash)
    #block3.mine()
    #BLOCKCHAIN.append(block3)
    app.run(debug=True, host='0.0.0.0', port=PORT)