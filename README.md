
# Time Complexity Visualizer API

A Flask API that measures and visualizes the running time of different algorithms.

```bash
python visualizer.py
```

The server runs at:

```text
http://localhost:8000
```

## Example Request

```text
http://localhost:8000/analyze?algo=linear_search&step=10&n_max=100
```

## Supported Algorithms

* linear_search
* bubble_sort
* binary_search
* nested_loops
* matrix_multiplication

The response includes running times, a saved graph image, and a Base64-encoded version of the graph.
