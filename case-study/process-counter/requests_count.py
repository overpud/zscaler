from flask import Response
from flask_restful import Resource
from random import SystemRandom
import json


class RandomNumberAPI(Resource):
    """Random Number API"""

    def __init__(self):
        super(RandomNumberAPI, self).__init__()

    def get(self):
        """Gets random numbers"""
        min = 0
        max = 200
        count = 1
        # check for max values
        if count > 100:
            count = 100
        # list of numbers
        numbers = []
        # get the correct number of random numbers
        for i in range(0, count):
            numbers.append(SystemRandom().randint(min, max))
        # return numbers
        return Response(json.dumps(numbers),  mimetype='application/json')