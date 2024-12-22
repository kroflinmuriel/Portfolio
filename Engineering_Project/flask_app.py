from flask import Flask, jsonify
from read_data_from_db import fetch_data  # Import the fetch_data function

# Initialize the Flask application
app = Flask(__name__)

# Define an API endpoint to serve data
@app.route('/api/sales', methods=['GET'])
def get_sales_data():
    try:
        # Fetch data from PostgreSQL using the function from read_data.py
        df = fetch_data()

        if df.empty:
            return jsonify({"error": "No data found"}), 404
        
        # Convert the dataframe to a dictionary for JSON serialization
        data = df.to_dict(orient="records")

        # Return the data as a JSON response
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
