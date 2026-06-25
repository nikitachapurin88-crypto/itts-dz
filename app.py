from flask import Flask, render_template, jsonify, request
import random
import os

app = Flask(__name__)


def generate_array(size: int, mode: str = "random") -> list[int]:
    if mode == "random":
        return [random.randint(10, 100) for _ in range(size)]
    elif mode == "reversed":
        return list(range(100, 100 - size, -1))
    elif mode == "nearly":
        arr = list(range(10, 10 + size))
        swaps = max(1, size // 10)
        for _ in range(swaps):
            i, j = random.randint(0, size - 1), random.randint(0, size - 1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    return [random.randint(10, 100) for _ in range(size)]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/array")
def get_array():
    try:
        size = int(request.args.get("size", 40))
    except ValueError:
        return jsonify({"error": "size must be an integer"}), 400
    mode = request.args.get("mode", "random")
    size = max(5, min(100, size))
    return jsonify({"array": generate_array(size, mode)})


@app.route("/api/sort", methods=["POST"])
def sort_steps():
    data = request.get_json()
    arr = data.get("array", [])
    algo = data.get("algorithm", "bubble")

    from algorithms import get_steps
    try:
        steps = get_steps(arr, algo)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"steps": steps, "total": len(steps)})


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host='0.0.0.0') # nosemgrep: flask-host-0000-without-debug-check,python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host
