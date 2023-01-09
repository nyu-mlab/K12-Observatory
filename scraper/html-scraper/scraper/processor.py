""" Building blocks
"""
import abc
import graphlib
import itertools
import multiprocessing as mp

import scraper.task

# TODO: rename file


class BaseWorker(abc.ABC):
    """Remote worker base class"""

    def __init__(
        self,
        middleware: graphlib.TopologicalSorter | dict | tuple | list,
        n_worker: int = None,
    ):
        # Sanitize middleware DAG
        if isinstance(middleware, graphlib.TopologicalSorter):
            pass
        elif isinstance(middleware, dict):
            middleware = graphlib.TopologicalSorter(middleware)
        elif isinstance(middleware, (list, tuple)):
            # Preserve original order
            mw_graph = graphlib.TopologicalSorter()
            if len(middleware) == 1:
                mw_graph.add(middleware[0])
            else:
                # pairwise(empty list or list with one item) returns nothing
                for predecessor, node in itertools.pairwise(middleware):
                    mw_graph.add(node, predecessor)
            middleware = mw_graph
        elif middleware is None:
            middleware = graphlib.TopologicalSorter({})
        else:
            raise ValueError(
                f"type of argument <middleware>: {type(middleware)}")

        middleware.prepare()
        self.middleware = middleware
        self.task_queue = mp.Queue()
        self.finished_queue = mp.Queue()
        self.worker_pool = mp.Pool(processes=n_worker)

    def run_forever(self):
        while True:
            self.worker_pool.apply_async(self.process,
                                         self.task_queue.get(block=True))

    def shutdown(self):
        # TODO: should we call .terminate() to stop immediately?
        self.worker_pool.close()
        self.worker_pool.join()

    @classmethod
    @abc.abstractmethod
    def _process(cls, task: scraper.task.Task) -> scraper.task.Task:
        raise NotImplementedError

    @abc.abstractmethod
    def process(self, task: scraper.task.Task):
        raise NotImplementedError
