from .settings import TEMPLATE_SCAN_SERVICE_PATH
import subprocess


SERVICE_INIT_COMMAND = [TEMPLATE_SCAN_SERVICE_PATH, '-update-templates']

try:
    result = subprocess.run(SERVICE_INIT_COMMAND, capture_output=True, text=True)
    print("Output:", result.stdout)
    print("Error:", result.stderr)
except Exception as e:
    print("Error executing command:", e)
