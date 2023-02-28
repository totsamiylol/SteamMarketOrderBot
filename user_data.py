import json

def get_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('user_data.json', 'w') as f:
            json.dump({"accounts": [], "proxy": [], "driver_path": "Not selected"}, f)
        return {"accounts": [], "proxy": [], "driver_path": "Not selected"}

def save_data(key, value):
    data = get_data()
    with open('user_data.json', 'w') as f:
        data[key] = value
        json.dump(data, f)
