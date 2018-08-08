#! /usr/bin/env python -u
# coding=utf-8
from __future__ import absolute_import
from __future__ import with_statement

import math
import pickle
import time
from io import open

__author__ = 'Sayed Hadi Hashemi'


class Timeline(object):
    _elapsed = 0

    def __init__(self, comm_op_name=None, horovod=False, run_metadata=None):
        self.run_metadata = run_metadata
        self.options = None
        self.comm_op_name = comm_op_name if comm_op_name is not None else "RecvTensor"
        self.horovod = horovod

    def __is_communication_op(self, op):
        if self.horovod:
            return " = HorovodAllreduce(" in op.timeline_label
        else:
            return op.node_name == self.comm_op_name

    def __enter__(self):
        from tensorflow import RunMetadata, RunOptions

        self.__start = time.time()
        self.run_metadata = RunMetadata()
        self.options = RunOptions(trace_level=RunOptions.FULL_TRACE, output_partition_graphs=True)

        return self

    def __exit__(self, *args):
        self._elapsed = time.time() - self.__start

    @property
    def kwargs(self):
        if self.run_metadata is None:
            raise Exception("TensorFlow is not found")
        return dict(run_metadata=self.run_metadata, options=self.options)

    def visualize(self, output_file=None, device_pattern=None):
        from tfvis._details import DataLoader, TimelineVisualizer

        data_loader = DataLoader(self.run_metadata, device_pattern)
        visualizer = TimelineVisualizer(data_loader)
        return visualizer.visualize(output_file)

    def iteration_time(self, device_search_pattern=None):
        max_time = 0
        min_time = math.inf
        device_search = "" if device_search_pattern is None else device_search_pattern
        all_ops = []
        for device in [d for d in self.run_metadata.step_stats.dev_stats if device_search in d.device]:
            all_ops += device.node_stats
        for op in sorted(all_ops, key=lambda a: a.all_start_micros):
            min_time = min(min_time, op.all_start_micros)
            max_time = max(max_time, op.all_start_micros + op.all_end_rel_micros)
        return max_time - min_time if min_time != math.inf else 0

    def communication_elapsed_time(self, device_search_pattern=None, exclude_pattern=None):
        max_time = 0
        min_time = math.inf
        device_search = "" if device_search_pattern is None else device_search_pattern
        all_ops = []
        for device in [d for d in self.run_metadata.step_stats.dev_stats if device_search in d.device]:
            all_ops += device.node_stats
        for op in sorted(all_ops, key=lambda a: a.all_start_micros):
            if not self.__is_communication_op(op):
                continue
            if exclude_pattern is not None and exclude_pattern in op.timeline_label:
                continue
            min_time = min(min_time, op.all_start_micros)
            max_time = max(max_time, op.all_start_micros + op.all_end_rel_micros)
        return max_time - min_time if min_time != math.inf else 0

    def communication_time(self, device_search_pattern=None, exclude_pattern=None):
        device_search = "" if device_search_pattern is None else device_search_pattern
        all_ops = []
        for device in [d for d in self.run_metadata.step_stats.dev_stats if device_search in d.device]:
            all_ops += device.node_stats

        last_ = -math.inf
        total = 0
        for op in sorted(all_ops, key=lambda a: a.all_start_micros):
            if not self.__is_communication_op(op):
                continue
            if exclude_pattern is not None and exclude_pattern in op.timeline_label:
                continue
            if op.all_start_micros > last_:
                total += op.all_end_rel_micros
            elif op.all_start_micros + op.all_end_rel_micros > last_:
                total += op.all_start_micros + op.all_end_rel_micros - last_
            last_ = max(last_, op.all_start_micros + op.all_end_rel_micros)

        return total

    def computation_time(self, device_search_pattern=None, exclude_pattern=None):
        device_search = "" if device_search_pattern is None else device_search_pattern
        all_ops = []
        for device in [d for d in self.run_metadata.step_stats.dev_stats if device_search in d.device]:
            all_ops += device.node_stats

        last_ = -math.inf
        total = 0
        for op in sorted(all_ops, key=lambda a: a.all_start_micros):
            if exclude_pattern is not None and exclude_pattern in op.timeline_label:
                continue
            if op.all_start_micros > last_:
                total += op.all_end_rel_micros
            elif op.all_start_micros + op.all_end_rel_micros > last_:
                total += op.all_start_micros + op.all_end_rel_micros - last_
            last_ = max(last_, op.all_start_micros + op.all_end_rel_micros)

        return total

    @property
    def wall_clock_elapsed(self):
        return self._elapsed

    @classmethod
    def from_pickle(cls, pickle_file_name, **kwargs):
        with open(pickle_file_name, "rb") as fp:
            run_metadata = pickle.load(fp)
        return cls(run_metadata=run_metadata, **kwargs)

    def to_pickle(self, pickle_file_name):
        if self.run_metadata is None:
            raise Exception("No data has been collected yet")

        with open(pickle_file_name, "wb") as fp:
            pickle.dump(self.run_metadata, fp)
