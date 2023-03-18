from hashlib import sha256

# This class contains the consensus mechanism used to secure the chain
# A raffle is held based on the number of stakes each node has using the previous block's hash as a seed and a winner is generated
# The winner then validates and creates the block to be broadcasted across the network to other nodes
class PoS:
    def __init__(self, pk, stake):
        # Staking pool
        self.nodes = {}
        # Node adds itself to staking pool automatically
        self.addNode(pk, stake)
        
    # Keys for the staking pool are held as each node's public key in string form with their corresponding stake
    def addNode(self, validator, stake):
        key = validator.e + validator.n
        if key not in list(self.nodes.keys()):
            self.nodes[key] = stake
        else:
            print ("Node already in staking pool")
        
    def addStake(self, validator, stake):
        key = validator.e + validator.n
        if key in list(self.nodes.keys()):
            self.nodes[key] += stake
        else:
            print ("Node not in staking pool")
            
    def subStake(self, validator, stake):
        key = validator.e + validator.n
        if key in list(self.nodes.keys()):
            self.nodes[key] -= stake
        else:
            print ("Node not in staking pool")
            
    def getStake(self, val):
        key = val.e + val.n
        if key in list(self.nodes.keys()):
            return self.nodes[key]
        else:
            return 0
    
    # Function to generate the validator - lastHash variable from the previous block acts as the seed for the target number
    def generateValidator(self, lastHash):
        # Dictionary to hold each node's guesses
        pool = {}
        for staker in self.nodes.keys():
            # Each node is give n amount of numbers, with n being the amount of tokens they have staked
            for chance in range(self.nodes[staker]):
                # Their public key + the number of their stake is hashed to produce a guess and stored in the pool as an int
                guessStr = str(staker) + str(chance)
                guess = int(sha256(guessStr.encode("utf-8")).hexdigest(), 16)
                pool[guess] = staker
        # The seed is hashed to produce a target number to hit as an int
        # This will be different each time a new block is added, but reproducable locally to check the validator on a block is correct
        targetStr = (lastHash).encode("utf-8")
        targetNum = int(sha256(targetStr).hexdigest(), 16)
        nearestGuess = None
        # For each guess in the pool, find the closest one to the target number and store it
        for guess in pool.keys():
            if nearestGuess == None:
                nearestGuess = guess
            else:
                if abs(guess - targetNum) < abs(nearestGuess - targetNum):
                    nearestGuess = guess
        # The winner is the staker with the number closest to the target number, and their public key string is returned
        # Nodes with a bigger stake have a higher chance of winning, but each node can win
        print("Winner is:", pool[nearestGuess])
        return pool[nearestGuess]
