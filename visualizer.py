
import base64
import io
import os
import time

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from flask import Flask, jsonify, request


app = Flask(__name__)


def linear_search(n):
    numbers = list(range(n))
    target = n - 1

    for i in numbers:
        if i == target:
            return i

    return -1


def bubble_sort(n):
    numbers = list(range(n, 0, -1))

    for i in range(len(numbers)):
        for j in range(0, len(numbers) - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = (
                    numbers[j + 1],
                    numbers[j]
                )

    return numbers


def binary_search(n):
    numbers = list(range(n))
    target = n

    low = 0
    high = len(numbers) - 1

    while low <= high:
        middle = (low + high) // 2

        if numbers[middle] == target:
            return middle

        if numbers[middle] < target:
            low = middle + 1
        else:
            high = middle - 1

    return -1


def nested_loops(n):
    count = 0

    for i in range(n):
        for j in range(n):
            count += 1

    return count


def matrix_multiplication(n):
    matrix = np.random.rand(n, n)
    return np.dot(matrix, matrix)


algorithms = {
    "linear_search": linear_search,
    "bubble_sort": bubble_sort,
    "binary_search": binary_search,
    "nested_loops": nested_loops,
    "matrix_multiplication": matrix_multiplication
}


def time_complexity_visualizer(algorithm, algo_name, step, n_max):
    times = []
    input_sizes = []

    inputs = range(1, n_max + 1, step)

    for n in inputs:
        start_time = time.perf_counter()

        algorithm(n)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        input_sizes.append(n)
        times.append(elapsed_time)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        input_sizes,
        times,
        marker="o"
    )

    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Running Time (seconds)")
    ax.set_title(
        "Time Complexity Visualization - {}".format(algo_name)
    )

    ax.grid(True)

    plt.tight_layout()

    os.makedirs("snapshots", exist_ok=True)

    image_path = os.path.join(
        "snapshots",
        "{}_complexity.png".format(algo_name)
    )

    fig.savefig(image_path)

    image_buffer = io.BytesIO()

    fig.savefig(
        image_buffer,
        format="png"
    )

    image_buffer.seek(0)

    image_base64 = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    image_buffer.close()

    plt.close(fig)

    return input_sizes, times, image_path, image_base64


@app.route("/")
def home():
    return jsonify({
        "message": "Time Complexity Visualizer API",
        "endpoint": "/analyze",
        "algorithms": list(algorithms.keys())
    })


@app.route("/analyze")
def analyze():
    algo_name = request.args.get("algo")
    step = request.args.get("step")
    n_max = request.args.get("n_max")

    if not algo_name:
        return jsonify({
            "error": "Missing algo parameter"
        }), 400

    if not step:
        return jsonify({
            "error": "Missing step parameter"
        }), 400

    if not n_max:
        return jsonify({
            "error": "Missing n_max parameter"
        }), 400

    algo_name = algo_name.strip("'\"")
    step = step.replace(",", "")
    n_max = n_max.replace(",", "")

    try:
        step = int(step)
        n_max = int(n_max)
    except ValueError:
        return jsonify({
            "error": "step and n_max must be integers"
        }), 400

    if step <= 0:
        return jsonify({
            "error": "step must be greater than 0"
        }), 400

    if n_max <= 0:
        return jsonify({
            "error": "n_max must be greater than 0"
        }), 400

    if step > n_max:
        return jsonify({
            "error": "step cannot be greater than n_max"
        }), 400

    if algo_name not in algorithms:
        return jsonify({
            "error": "Unknown algorithm",
            "available_algorithms": list(algorithms.keys())
        }), 400

    algorithm = algorithms[algo_name]

    try:
        input_sizes, times, image_path, image_base64 = (
            time_complexity_visualizer(
                algorithm,
                algo_name,
                step,
                n_max
            )
        )
    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

    return jsonify({
        "algorithm": algo_name,
        "step": step,
        "n_max": n_max,
        "input_sizes": input_sizes,
        "running_times": times,
        "snapshot": image_path,
        "image_base64": image_base64
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )

