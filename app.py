from flask import Flask, request, jsonify, render_template
import urllib.parse
import requests

app = Flask(__name__)

main_api = "https://www.mapquestapi.com/directions/v2/route?"
key = "AA4DTyihAnKSzMGO7xg8XVDOKx8uoidE"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/directions', methods=['GET'])
def get_directions():
    orig = request.args.get('from')
    dest = request.args.get('to')
    unit = request.args.get('unit', 'km')  # Default to kilometers

    if not orig or not dest:
        return jsonify({"error": "Missing 'from' or 'to' parameters."}), 400

    url = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest})
    json_data = requests.get(url).json()
    
    json_status = json_data["info"]["statuscode"]
    if json_status == 0:
        distance = json_data["route"]["distance"]
        if unit == 'miles':
            distance = round(distance, 2)  # Use original distance in miles
        else:
            distance = round(distance * 1.61, 2)  # Convert to kilometers
        
        route_info = {
            "status": "success",
            "from": orig,
            "to": dest,
            "trip_duration": json_data["route"]["formattedTime"],
            "distance": distance,
            "maneuvers": [
                {
                    "narrative": each["narrative"],
                    "distance": round(each["distance"] * (1.61 if unit == 'km' else 1), 2)
                }
                for each in json_data["route"]["legs"][0]["maneuvers"]
            ]
        }
        return jsonify(route_info), 200
    elif json_status == 402:
        return jsonify({"error": "Invalid user inputs for one or both locations."}), 400
    elif json_status == 611:
        return jsonify({"error": "Missing an entry for one or both locations."}), 400
    else:
        return jsonify({"error": "Status Code: {}".format(json_status)}), 500

if __name__ == '__main__':
    app.run(debug=True)
