from pathlib import Path
import json


json_file = Path("/home/sean/.julia/packages/PowerSystemCaseBuilder/lf3Me/"
                 "data/serialized_system/NoArgs/c_sys14.json")

def main():
    with open(json_file, 'r') as f:
        data = json.load(f)
    print(data.keys())
    print(data['data'].keys())
                

if __name__ == '__main__':
    main()