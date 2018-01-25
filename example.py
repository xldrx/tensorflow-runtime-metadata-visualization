#! /usr/bin/env python -u
# coding=utf-8
import pickle

import tfvis
__author__ = 'xl'

if __name__ == '__main__':
    with open("example-inception-train-4w-1ps.pickle", "rb") as fp:
        metadata = pickle.load(fp)
    tfvis.timeline_visualize(metadata, "example-inception-train-4w-1ps.html")
