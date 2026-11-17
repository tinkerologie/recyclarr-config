"""Parse tracked configuration and enforce pinned Actions with explicit permissions."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from ruamel.yaml import YAML

yaml = YAML(typ="safe")
yaml.constructor.add_constructor("!secret", lambda loader, node: loader.construct_scalar(node))
files = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
# Include newly added workflow files in local pre-commit validation too.
files += [str(p) for p in Path(".github/workflows").glob("*.yml")]
for name in sorted(set(files) - {""}):
    path = Path(name)
    if not path.is_file():
        continue
    if path.suffix in {".yml", ".yaml"}:
        data = yaml.load(path.read_text())
        if path.parent == Path(".github/workflows"):
            assert isinstance(data, dict) and "permissions" in data, f"{path}: explicit permissions required"
            for ref in re.findall(r"(?m)^\s*(?:-\s*)?uses:\s*([^\s#]+)", path.read_text()):
                assert ref.startswith("./") or re.search(r"@[0-9a-f]{40}$", ref), f"{path}: unpinned {ref}"
    elif path.suffix == ".json":
        json.loads(path.read_text())
    elif path.suffix == ".xml":
        ET.parse(path)
print("Tracked YAML, JSON, XML and Actions policy validation passed.")
