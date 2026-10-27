import json
from pathlib import Path
import subprocess


def run(values):
    script = Path(__file__).resolve().parents[1] / "web" / "transform.js"
    result = subprocess.run(["node", str(script)], input=json.dumps(values),
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout)
