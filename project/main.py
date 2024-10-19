from flask import Flask, request, jsonify
import requests

from block import BLOCKCHAIN, Block

app = Flask(__name__)
PORT = 5000

NODES = [] # a list of IPs with ports (e.g. 12.34.56.78:1337) as strings

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
    data = request.json['data'] # data to store in the block
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    prev_hash = BLOCKCHAIN[-1].hash if len(BLOCKCHAIN) > 0 else b'\x00' * 64
    new_block = Block(data, prev_hash)
    new_block.mine()
    return new_block
    # w tym momencie jest surowy block wykopany, trzeba poinformować resztę o nim

@app.get('/blocks')
def get_blocks():
    """
    Return a serialized blockchain.
    """
    pass


@app.get('/blocks/<id>')
def get_block(id):
    """
    Return a block with specific ID. The ID is the number of block in the BLOCKCHAIN list.
    """
    if id < 0 or id >= len(BLOCKCHAIN):
        print("incorrect id")
        return None
    print(BLOCKCHAIN[id])
    return BLOCKCHAIN[id]


@app.post('/blocks')
def add_block():
    block = Block.from_json(request.json)

    # verify block hashes are OK, check for consensus and add to blockchain if all is OK
    pass

@app.post('/data')
def store_data():
    """
    Anyone can call this to add some data to the blockchain.
    The node that receives a request to this endpoint should propagate it to other nodes if it is the first one to
    receive the call to this endpoint (indicated by "propagate" flag in the request).
    """
    propagate = request.json['propagate']
    data = request.json['data']

    if propagate:
        for node in NODES:
            requests.post(f'http://{node}/blocks', {'data': data, propagate: False})

    # start mining or do something about this block below...
    pass


if __name__ == '__main__':
    block1 = Block("some text", b'\x00' * 64)
    block1.mine()
    BLOCKCHAIN.append(block1)
    block2 = Block("more text", BLOCKCHAIN[-1].hash)
    block2.mine()
    BLOCKCHAIN.append(block2)
    block3 = Block("even more text", BLOCKCHAIN[-1].hash)
    block3.mine()
    BLOCKCHAIN.append(block3)
    app.run(debug=True, host='0.0.0.0', port=PORT)
