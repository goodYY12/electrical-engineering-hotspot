import argparse
import json
from pathlib import Path

from electrical_kaoyan.parsers import extract_pdf

parser = argparse.ArgumentParser()
parser.add_argument("path", type=Path)
args = parser.parse_args()
result = extract_pdf(args.path)
print(json.dumps({"pages": result.pages, "tables": result.tables,
                  "needs_ocr": result.needs_ocr}, ensure_ascii=False))
