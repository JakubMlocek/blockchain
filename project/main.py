from flask import Flask, request
import requests

from block import BLOCKCHAIN, Block

app = Flask(__name__)

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
    pass

@app.post('/nodes')
def add_node():
    """
    Join new node to the network - respond with IPs of known nodes and send the entire blockchain.
    This is called on the nodes already in the blockchain.
    """
    pass

@app.post('/init/<ip>')
def init_node(ip):
    """
    Join the blockchain. IP is an IP of a node known to be in the blockchain.
    IP can be None if this is the first node in the blockchain.
    This is called on a node that is NOT in the blockchain yet.
    """
    pass


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
    app.run(debug=True)
