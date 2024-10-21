import hashlib


BLOCKCHAIN = []


class Block:

    def __init__(self, data: str, prev_hash: bytes):
        """
        data is the data stored in the block.
        prev_hash should be hex string of the hash.
        """
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = None

    def mine(self, increments=1):
        """To add some variability between how the nodes mine, increments can be changed"""
        while not self.verify_hash():
            self.nonce += increments
            m = hashlib.sha256()
            m.update(self.prev_hash)
            m.update(self.data.encode('utf-8'))
            m.update(self.nonce.to_bytes(32, byteorder='big'))
            self.hash = m.digest()

    def verify_hash(self):
        HASH_END = b'\x13\x37' # just pick some random value the hash has to end with
        m = hashlib.sha256()
        m.update(BLOCKCHAIN[-1].hash if len(BLOCKCHAIN) > 0 else b'\x00' * 64)
        m.update(self.data.encode('utf-8'))
        m.update(self.nonce.to_bytes(32, byteorder='big'))
        if self.hash is None or not self.hash.endswith(HASH_END) or self.hash != m.digest():
            return False
        return True

    @staticmethod
    def from_json(json_data):
        block = Block(json_data['data'], bytes.fromhex(json_data['prev_hash']))
        block.hash = bytes.fromhex(json_data['hash'])
        block.nonce = json_data['nonce']
        return block

    def json(self):
        return {
            'data': self.data,
            'prev_hash': self.prev_hash.hex(),
            'hash': self.hash.hex(),
            'nonce': self.nonce
        }

    def __repr__(self):
        return str({
            'data': self.data,
            'prev_hash': self.prev_hash.hex(),
            'hash': self.hash.hex(),
            'nonce': self.nonce
        })

if __name__ == "__main__":
    block1 = Block("some text", b'\x00' * 64)
    block1.mine()
    BLOCKCHAIN.append(block1)
    block2 = Block("more text", BLOCKCHAIN[-1].hash)
    block2.mine()
    BLOCKCHAIN.append(block2)
    block3 = Block("even more text", BLOCKCHAIN[-1].hash)
    block3.mine()
    BLOCKCHAIN.append(block3)
    print(*BLOCKCHAIN, sep='\n')

