import asyncio
from . import common

class Client(object):
    level_normal = 'normal'
    level_low = 'low'
    level_high = 'high'

    def __init__(self):
        self._agent = None

    @asyncio.coroutine
    def do(self, func_name, workload, unique = None, level = 'normal', background=False):
        payload = {
            'func_name': func_name,
            'unique': unique,
            'workload': workload
        }
        if background:
            if level == self.level_low:
                yield from self._agent.send(common.SUBMIT_JOB_LOW_BG, payload)
            elif level == self.level_high:
                yield from self._agent.send(common.SUBMIT_JOB_HIGH_BG, payload)
            else:
                yield from self._agent.send(common.SUBMIT_JOB_BG, payload)
        else:
            if level == self.level_low:
                yield from self._agent.send(common.SUBMIT_JOB_LOW, payload)
            elif level == self.level_high:
                yield from self._agent.send(common.SUBMIT_JOB_HIGH, payload)
            else:
                yield from self._agent.send(common.SUBMIT_JOB, payload)

        cmd_type, cmd_args = yield from self._agent.read()

        if cmd_type == common.JOB_CREATED:
            job_handle = cmd_args['job_handle']

        if background:
            return job_handle
        else:
            return self.result

    @property
    def result(self):
        cmd_type, cmd_args = yield from self._agent.read()
        return cmd_type, cmd_args

    @asyncio.coroutine
    def add_server(self, host, port, ssl = False):
        reader, writer = yield from asyncio.open_connection(host, port, ssl=ssl)
        self._agent = common.BaseAgent(reader, writer)