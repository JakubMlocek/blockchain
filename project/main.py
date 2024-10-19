from flask import Flask, request, jsonify
import requests

from block import BLOCKCHAIN, Block

app = Flask(__name__)
PORT_USED = 5000

NODES = [] # a list of IPs with ports (e.g. 12.34.56.78:1337) as strings

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
    new_block = Block(data=data, prev_hash=prev_hash)
    new_block.mine()



@app.post('/nodes')
def add_node():
    """
    Join new node to the network - respond with IPs of known nodes and send the entire blockchain.
    This is called on the nodes already in the blockchain.
    """
    ip = f'{request.remote_addr}:{PORT_USED}'
    NODES.append(ip)
    return NODES[:-1]

@app.post('/init/<ip>')
def init_node(ip):
    """
    Join the blockchain. IP is an IP of a node known to be in the blockchain.
    IP can be None if this is the first node in the blockchain.
    This is called on a node that is NOT in the blockchain yet.
    """
    def call_node(ip):
        resp = requests.post(f'http://{ip}/nodes')
        if resp.status_code != 200:
            return
        for node in resp.json():
            if node in NODES:
                continue
            NODES.append(node)
            call_node(node)

    call_node(ip)
    return NODES


@app.get('/blocks')
def get_blocks():
    """
    Return a serialized blockchain.
    """
    pass


@app.get('/blocks/<id>')
def get_block(id):
    """
    Return a block with specific ID.
    """
    pass


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
            requests.post(f'http://{node}/blocks', json={'data': data, propagate: False})

    # start mining or do something about this block below...
    pass


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=PORT_USED)
