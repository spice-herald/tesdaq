"""TODO:
    finish dosctring
"""

import redis
import time
import re
import ast

# Defines some states
WAIT = 0
RUN = 1
REDIS_FAILURE = -1

# Define commands passed from redis
CMD_START = "START"
CMD_STOP = "STOP"
CMD_CONFIG = "CONFIG"

class DAQListener:
    def __init__(
            self,
            redis_channels=['Dev1/ai0'],
            redis_host='localhost',
            redis_password='',
            redis_port=6379,
            redis_database=0,
            **kwargs):

        """ Abstraction for listening to redis messages to execute DAQ commands

        Arguments:
        ----------
        channels:   Array of strings which redis will subscribe to as channels. (Must be an array!)
        redis_host: Host to which redis connects (e.g. 'localhost')
        redis_port: Port which redis should use to connect (by default is 6379)
        redis_database: Redis DB to be used (default, 0).

        """
        try:
            r = redis.Redis(
                host=redis_host,
                password=redis_password,
                port=redis_port,
                db=redis_database
                )
            self.pubsub = r.pubsub()
            for c in redis_channels:
                self.pubsub.subscribe(c)
            self.STATE = WAIT

        # TODO: More specific exception here
        except Exception as e:
            self.STATE = REDIS_FAILURE
            print(e)

    def configure(self, **kwargs):
        # Should only take in keyword args as a parameter,
        # that will be passed as JSON to Redis from client end
        raise NotImplementedError("class {} must implement configure()".format(type(self).__name__))
    def start(self, **kwargs):
        # Should only take in keyword args as a parameter,
        # that will be passed as JSON to Redis from client end
        raise NotImplementedError("class {} must implement start()".format(type(self).__name__))
    def stop(self, **kwargs):
        # Should only take in keyword args as a parameter,
        # that will be passed as JSON to Redis from client end
        raise NotImplementedError("class {} must implement stop()".format(type(self).__name__))

    def wait(self):
        while self.STATE == WAIT:
            message = self.pubsub.get_message()
            if message:
                command = message['data']
                try:
                    command = str(command.decode("utf-8"))
                except AttributeError as e:
                    command = str(command)
                passed_args = _to_dict(command)
                if command.startwisth(CMD_START):
                    self.start(**passed_args)
                if command.startswith(CMD_CONFIG):
                    self.configure(**passed_args)
                if command.startswith(CMD_STOP):
                    self.stop(**passed_args)
            time.sleep(1)


def _to_dict(st):
    """
    Convienence Method to return Dict from Redis input
    """
    return ast.literal_eval(re.search('({.+})', st).group(0))

