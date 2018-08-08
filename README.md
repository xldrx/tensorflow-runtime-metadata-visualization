# TensorFlow Runtime Tracing Metadata Visualization
This library visualizes the runtime trace of TensorFlow. 

Compare to built-in Chrome Tracing Format:
* Retains op execution details. (e.g., RecvTensor ops source and destination)
* Separates network ops from computing
* Faster Navigation

Example: timeline of Inception execution is available [here](http://htmlpreview.github.io/?https://github.com/xldrx/tensorflow-runtime-metadata-visualization/blob/master/example-inception-train-4w-1ps.html)
![Inception Timeline](example-inception-train-4w-1ps.png?raw=true "Inception Timeline")

## How to use
1. Collect Runtime metadata in TensorFlow:
    ```python
    from tfvis import Timeline
    ...
    
    with tf.train.MonitoredTrainingSession(...) as sess:
        ...
        with Timeline() as timeline:
            sess.run(train_op, **timeline.kwargs)
        ...
    ```
2. Visualize:
    ```python
    ...
    timeline.visualize("example.html")
    ...
    ```

## Frequently Asked Questions
### `Horovod` Support?
Pass `horovod=True` to `Timeline`:
```python
with Timeline(horovod=True) as timeline:
        sess.run(train_op, **timeline.kwargs)
```

### Save for later?
Use this:
```python
with Timeline(horovod=True) as timeline:
        sess.run(train_op, **timeline.kwargs)
        
timeline.to_pickle("example.pickle")
...
timeline.from_pickle("example.pickle", horovod=True)
```

### Collect Runtime Metadata Natively?
Use this:
```python
...

with tf.train.MonitoredTrainingSession(...) as sess:
	...
	run_metadata = tf.RunMetadata()
	options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
	sess.run(train_op, run_metadata=run_metadata, options=options)
...
```

Store:
```python
import pickle

with open("example.pickle", "wb") as fp:
        pickle.load(run_metadata, fp)
```

Load and Visualize:
```python
    from tfvis import Timeline
    Timeline.from_pickle("example.pickle").visualize("example.html")
```

## Cite this tool
```latex
@misc{Hashemi2018,
  author = {Sayed Hadi Hashemi},
  title = {TensorFlow Runtime Tracing Metadata Visualization},
  year = {2018},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/xldrx/tensorflow-runtime-metadata-visualization}},
}
```
