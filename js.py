import json

json_string = '{"N":[{"line":"4","min":2,"term":"Woodlawn"},{"line":"6","min":2,"term":"Pelham Bay Park"}],"S":[{"line":"6","min":2,"term":"Brooklyn Bridge"},{"line":"6","min":5,"term":"Brooklyn Bridge"}]}';
parsed = json.loads(json_string)

print(parsed['S'])