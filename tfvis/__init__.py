#! /usr/bin/env python -u
# coding=utf-8

__author__ = 'xl'


def timeline_visualize(run_metadata, output_file=None):
    """
Visualize TensorFlow tracing metadata as a html.
    :param run_metadata:
    :param output_file: (optional) path to store the visualization.
    :return: None if output_file is not None else return the html content.
    """
    from tfvis.timeline import TimelineVisualization
    return TimelineVisualization().visualize(run_metadata, output_file)
