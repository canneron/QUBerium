import json
from flask import Flask, request
from flask_classful import FlaskView, route 

class API(FlaskView):
    def __init__(self):
        self.api = Flask(__name__)
        
    def startApi(self, apiPort):
        API.register(self.api, route_base='/')
        self.api.run(host='localhost', port=apiPort)
        
    @route('/test', methods=['GET'])
    def info(self):
        return "test", 200
    
    def nodeInjection(self, iNode):
        global node
        node = iNode
        
    @route('/blockchain', methods=['GET'])
    def viewBlockchain(self):
        return node.bchain.toJson(), 200
    
    @route('transaction', methods=['POST'])
    def postTransaction(self):
        tx = request.get_json
        if not 'transaction' in tx:
            return "Incorrect format, JSON needed", 400
        node.addToChain(tx)
        return 201