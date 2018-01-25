# TensorFlow Runtime Tracing Metadata Visualization
This library visualizes the runtime trace of TensorFlow. 

Compare to built-in Chrome Tracing Format:
* Retains op execution details. (e.g., RecvTensor ops source and destination)
* Separates network ops from computing
* Faster Navigation

Example: timeline of Inception execution is available [here](http://htmlpreview.github.io/?https://github.com/xldrx/tensorflow-runtime-metadata-visualization/blob/master/example-inception-train-4w-1ps.html)
![Alt text](example-inception-train-4w-1ps.png?raw=true "Inception Timeline")

## How to use
Given a collected `runtime_metadata`:
```python
import tfvis
...
tfvis.timeline_visualize(runtime_metadata, "example.html")
```

## How to Collect Runtime Metadata in TensorFlow
```python
...

with tf.train.MonitoredTrainingSession(...) as sess:
	...
	run_metadata = tf.RunMetadata()
	sess.run(train, **timeline.kwargs())
	options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
	sess.run(train_op, run_metadata=self.run_metadata, options=self.options)
...

```

## Known Issues
* Has been tested only on Python 3
* Hover boxes may not be appropriately placed.

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
