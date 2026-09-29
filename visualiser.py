import base64
import io
import json
import os
import time

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "my-super-secret-key"

jwt = JWTManager(app)

DATABASE_URL = "sqlite:///analyses.db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    algorithm = Column(String(100), nullable=False)
    step = Column(Integer, nullable=False)
    n_max = Column(Integer, nullable=False)
    input_sizes = Column(Text, nullable=False)
    running_times = Column(Text, nullable=False)
    snapshot = Column(String(255), nullable=False)
    image_base64 = Column(Text, nullable=False)


Base.metadata.create_all(engine)


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "error": "I don't know you. Bye"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "error": "I don't know you. Bye"
    }), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "Token expired. Bye"
    }), 401


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


def unique_users(n):
    users = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 2}
    ]

    unique_users = []

    for i in range(len(users)):
        seen = False

        for j in range(len(unique_users)):
            if users[i]["id"] == unique_users[j]["id"]:
                seen = True
                break

        if not seen:
            unique_users.append(users[i])

    return unique_users


def matrix_multiplication(n):
    matrix = np.random.rand(n, n)
    return np.dot(matrix, matrix)


algorithms = {
    "linear_search": linear_search,
    "bubble_sort": bubble_sort,
    "binary_search": binary_search,
    "nested_loops": nested_loops,
    "matrix_multiplication": matrix_multiplication,
    "unique_users": unique_users
}


def time_complexity_visualizer(
    algorithm,
    algo_name,
    step,
    n_max
):
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
        "Time Complexity Visualization - {}".format(
            algo_name
        )
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

    return (
        input_sizes,
        times,
        image_path,
        image_base64
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Time Complexity Visualizer API",
        "endpoint": "/analyze",
        "login_endpoint": "/login",
        "save_endpoint": "/save_analysis",
        "algorithms": list(algorithms.keys())
    })


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if username != "admin" or password != "password":
        return jsonify({
            "error": "I don't know you. Bye"
        }), 401

    access_token = create_access_token(
        identity=username
    )

    response = jsonify({
        "message": "Login successful"
    })

    response.headers["Authorization"] = (
        "Bearer {}".format(access_token)
    )

    return response, 200


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}

        algo_name = data.get("algo")
        step = data.get("step")
        n_max = data.get("n_max")
    else:
        algo_name = request.args.get("algo")
        step = request.args.get("step")
        n_max = request.args.get("n_max")

    if not algo_name:
        return jsonify({
            "error": "Missing algo parameter"
        }), 400

    if step is None:
        return jsonify({
            "error": "Missing step parameter"
        }), 400

    if n_max is None:
        return jsonify({
            "error": "Missing n_max parameter"
        }), 400

    algo_name = str(algo_name).strip("'\"")
    step = str(step).replace(",", "")
    n_max = str(n_max).replace(",", "")

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
            "available_algorithms": list(
                algorithms.keys()
            )
        }), 400

    algorithm = algorithms[algo_name]

    try:
        (
            input_sizes,
            times,
            image_path,
            image_base64
        ) = time_complexity_visualizer(
            algorithm,
            algo_name,
            step,
            n_max
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


@app.route("/save_analysis", methods=["POST"])
@jwt_required()
def save_analysis():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    required_fields = [
        "algorithm",
        "step",
        "n_max",
        "input_sizes",
        "running_times",
        "snapshot",
        "image_base64"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": "Missing field: {}".format(field)
            }), 400

    session = Session()

    try:
        analysis = Analysis(
            algorithm=data["algorithm"],
            step=int(data["step"]),
            n_max=int(data["n_max"]),
            input_sizes=json.dumps(
                data["input_sizes"]
            ),
            running_times=json.dumps(
                data["running_times"]
            ),
            snapshot=data["snapshot"],
            image_base64=data["image_base64"]
        )

        session.add(analysis)
        session.commit()

        analysis_id = analysis.id

        return jsonify({
            "message": "Analysis saved successfully",
            "id": analysis_id
        }), 201

    except Exception as error:
        session.rollback()

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        session.close()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
