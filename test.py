from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def generate_image():
    # Get the text prompt from the request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field in the request body"}), 400
    text_prompt = data['text']
    
    # Return the image as a response
    return jsonify({"input": text_prompt, "pod": "1"}), 200

if __name__ == '__main__':
    app.run(debug=True)