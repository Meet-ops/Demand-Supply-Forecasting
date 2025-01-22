from flask import Flask, request, render_template, jsonify
import pandas as pd
from sklearn.linear_model import LinearRegression
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        # Check if the file is in the request
        if 'sales' not in request.files:
            raise ValueError("No file part in the request. Please upload a file.")

        file = request.files['sales']

        # Check if the file has a name
        if file.filename == '':
            raise ValueError("No file selected. Please upload a valid file.")

        # Read the CSV file into a pandas DataFrame
        try:
            data = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
        except Exception as e:
            raise ValueError("Failed to read the file. Please ensure it is a valid CSV.")

        # Validate required columns
        if 'date' not in data.columns or 'sales' not in data.columns:
            raise ValueError("The CSV file must contain 'date' and 'sales' columns.")

        # Convert 'date' column to datetime
        data['date'] = pd.to_datetime(data['date'], errors='coerce')

        # Check for invalid dates
        if data['date'].isnull().any():
            raise ValueError("Invalid dates found in the 'date' column.")

        # Sort data by date
        data.sort_values('date', inplace=True)

        # Convert 'date' to numeric values (e.g., days since the first date)
        data['date_num'] = (data['date'] - data['date'].min()).dt.days

        # Prepare data for the regression model
        X = data[['date_num']].values  # Independent variable
        y = data['sales'].values      # Dependent variable

        # Train the regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict the next period's sales
        next_day = X[-1][0] + 1  # Next day in numeric form
        prediction = model.predict([[next_day]])

        # Alert for data fluctuation
        alert = "No alert"
        if data['sales'].var() > 1000:  # Adjust threshold as needed
            alert = "Data is fluctuating significantly!"

        return jsonify({"forecast": round(prediction[0], 2), "alert": alert})

    except ValueError as ve:
        # Handle specific input validation errors
        return jsonify({"error": str(ve)})
    except Exception as e:
        # Catch all other unexpected errors
        return jsonify({"error": "An unexpected error occurred. Please try again."})

if __name__ == '__main__':
    app.run(debug=True)
