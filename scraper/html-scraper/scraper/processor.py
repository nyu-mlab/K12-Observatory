""" Building blocks
"""
import abc
import concurrent.futures
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
        worker_pool: concurrent.futures.Executor = None,
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

        if worker_pool is not None:
            self.worker_pool = worker_pool
        else:
            self.worker_pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=None)

        middleware.prepare()
        self.middleware = middleware
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()

    def shutdown(self):
        self.worker.shutdown(wait=True, cancel_futures=True)

    @abc.abstractmethod
    def process(self, task: scraper.task.Task):
        raise NotImplementedError  # pragma: no cover
