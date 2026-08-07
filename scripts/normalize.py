import argparse

from electrical_kaoyan.models import DegreeType, ProgramIdentity, StudyMode

parser = argparse.ArgumentParser()
parser.add_argument("--school", required=True)
parser.add_argument("--college", required=True)
parser.add_argument("--major", required=True)
parser.add_argument("--major-name", default="电气工程")
parser.add_argument("--degree-type", choices=[item.value for item in DegreeType], required=True)
parser.add_argument("--study-mode", choices=[item.value for item in StudyMode], required=True)
parser.add_argument("--admission-year", type=int, required=True)
args = parser.parse_args()
identity = ProgramIdentity(school=args.school, college=args.college, major_code=args.major,
                           major_name=args.major_name, degree_type=args.degree_type,
                           study_mode=args.study_mode, admission_year=args.admission_year)
print(identity.program_id)
