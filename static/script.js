document.addEventListener("DOMContentLoaded", function(){
    // Call handleFormSubmission with the default city on page load
    handleFormSubmission("Jakarta");

    document.getElementById("cityInput").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            handleFormSubmission(document.getElementById("cityInput").value);
        }
    });

    function handleFormSubmission(city) {
        fetchWeatherData(city);
    }

    function fetchWeatherData(city) {
        fetch("/get_weather", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({"city": city}),
        })
        .then(response => response.json())
        .then(data => {
            updateWeatherTable(data);
        })
        .catch(error => console.error("Error:", error));
    }

    function updateWeatherTable(weatherData) {
        const todayForecast = weatherData.forecast.forecastday;
        const temperatureDay = [];
        const temperatureNight = [];

        for (const obj of todayForecast) {
            const value = obj.hour;
            temperatureDay.push(value[11].temp_c);
            temperatureNight.push(value[8].temp_c);
          }
        
        // Update forecast 
        document.getElementById("today_weather_condition").textContent = todayForecast[0].day.condition.text;
        document.getElementById("tomorrow_weather_condition").textContent = todayForecast[1].day.condition.text;
        document.getElementById("day_after_tomorrow_weather_condition").textContent = todayForecast[2].day.condition.text;

        // Update temperatute 
        document.getElementById("today_day_temperature").textContent = temperatureDay[0];
        document.getElementById("today_night_temperature").textContent = temperatureNight[0];
        document.getElementById("tomorrow_day_temperature").textContent = temperatureDay[1];
        document.getElementById("tomorrow_night_temperature").textContent = temperatureNight[1];
        document.getElementById("day_after_tomorrow_day_temperature").textContent = temperatureDay[2];
        document.getElementById("day_after_tomorrow_night_temperature").textContent = temperatureNight[2];
        
        // update date
        document.getElementById("today_date").textContent = todayForecast[0].date;
        document.getElementById("tomorrow_date").textContent = todayForecast[1].date;
        document.getElementById("day_after_tomorrow_date").textContent = todayForecast[2].date;

        // update location
        document.getElementById("location-name").textContent = weatherData.location.name;
        document.getElementById("location-region").textContent = weatherData.location.region;
        document.getElementById("location-country").textContent = weatherData.location.country;

    }
});
