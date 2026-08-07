import argparse
import json

from electrical_kaoyan.search import generate_queries

parser = argparse.ArgumentParser()
parser.add_argument("--school", required=True)
parser.add_argument("--college", required=True)
parser.add_argument("--major", required=True)
parser.add_argument("--admission-year", type=int, required=True)
parser.add_argument("--official-domain")
args = parser.parse_args()
print(json.dumps(generate_queries(args.school, args.college, args.major, args.admission_year,
                                  args.official_domain), ensure_ascii=False, indent=2))
