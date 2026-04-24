from random import SystemRandom

from flask_restful import Resource


class RandomNumberAPI(Resource):
    """Synthetic request-count endpoint used by the autoscaler demo."""

    def get(self):
        return [SystemRandom().randint(0, 200)]
