#! /usr/bin/env python -u
# coding=utf-8
from __future__ import absolute_import
from tfvis import Timeline

__author__ = 'xl'

if __name__ == '__main__':
    Timeline.from_pickle("example-inception-train-4w-1ps.pickle").visualize("example-inception-train-4w-1ps.html")
