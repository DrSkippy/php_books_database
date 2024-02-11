import json

config_file = "book_service/config/configuration.json"

with open(config_file, "r") as infile:
    config = json.load(infile)
    API_KEY = config["api_key"]
    ENDPOINT = config["endpoint"]

cases = [
    {"method": "GET", "endpoint_suffix": "configuration", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "valid_locations", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "recent", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "books_read/2020", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "status_read/1576", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "tag_counts/science", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "tags/1576", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "date_page_records/1", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "books_search?Author=Lewis", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT},
    {"method": "GET", "endpoint_suffix": "tags_search/science", "headers": f"x-api-key: {API_KEY}", "ENDPOINT": ENDPOINT}
]

for case in cases:
    print("curl -X {method} -H '{headers}' {ENDPOINT}/{endpoint_suffix} | jq .".format(**case))

