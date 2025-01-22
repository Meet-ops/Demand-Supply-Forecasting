document.getElementById('forecast-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch('/forecast', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const forecastOutput = document.getElementById('forecast-output');
        if (data.error) {
            forecastOutput.textContent = "Error: " + data.error;
        } else {
            forecastOutput.textContent = `Demand Forecast: ${data.forecast}\nAlert: ${data.alert}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
