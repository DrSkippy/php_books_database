import json
import subprocess
import random

sample_data = {"<target_year>": "2022",
               "<book_id>": "1873",
               "<tag>": "science",
               "<current>": "science",
               "<updated>": "science",
               "<year>": "2020",
               "<match_str>": "Lewis",
               "<window>": "20",
               "<record_id>": "50"
               }

print("Sample data for endpoints:")
for k, v in sample_data.items():
    print(f"{k}: {v}")
print("\n")

print("Geeting all of the GET endpoints from book_service/books/api.py")
command = "cat book_service/books/api.py | grep app.route | grep -v POST | grep -v PUT | cut -d\\' -f2"
result = subprocess.check_output(command, shell=True)
result = result.decode("utf-8").strip().split("\n")
endpoints = []
for line in result:
    for k, v in sample_data.items():
        line = line.replace(k, v)
    print(line)
    endpoints.append(line)
print("\n")

config_file = "book_service/config/configuration.json"

with open(config_file, "r") as infile:
    config = json.load(infile)
    API_KEY = config["api_key"]
    ENDPOINT = config["endpoint"]

print("\nGenerating curl commands for common API calls:\n")
template = {"method": "GET", "endpoint_suffix": None, "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT}
cases = []
for endpoint in endpoints:
    _template = template.copy()
    _template["endpoint_suffix"] = endpoint
    cases.append(_template)

for case in cases:
    if "png" in case["endpoint_suffix"]:
        name = "test_" + str(int(random.random()*1000000)) + ".png"
        print("curl -X {method} -H '{headers}' {ENDPOINT}/{endpoint_suffix} -o ".format(**case) + name)
    else:
        print("curl -X {method} -H '{headers}' {ENDPOINT}/{endpoint_suffix} | jq .".format(**case))
