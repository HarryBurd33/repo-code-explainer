# Encode subprocess input and decode its output using JSON.
import json
# Resolve the JavaScript path relative to this source file.
from pathlib import Path
# Start Node and collect its output through subprocess pipes.
import subprocess


# Send values to the Node transform and return its decoded JSON result.
def run(values):
    # Find web/transform.js beneath the project root, independent of working directory.
    script = Path(__file__).resolve().parents[1] / "web" / "transform.js"
    # Start node via PATH and send serialized values to standard input as text.
    # Capture stdout and stderr; nonzero exit raises CalledProcessError.
    # The script expects an array, keeps values >= 0, and doubles them in order.
    result = subprocess.run(["node", str(script)], input=json.dumps(values),
                            text=True, capture_output=True, check=True)
    # Decode the script's stdout; malformed JSON raises a decoding error.
    return json.loads(result.stdout)
