import json
from lib.isbn_com import api
 
isbn_com = api()

print("Enter s to stop")
ans = None
while ans is None:
    ans = input("Enter isbn13: ")
    if not ans.startswith("s"):
        res = isbn_com.get_book_by_isbn(ans)
        print(json.dumps(res, indent=4, sort_keys=True))
        ans = None
