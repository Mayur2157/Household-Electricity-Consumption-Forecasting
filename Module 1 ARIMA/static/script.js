document.addEventListener("DOMContentLoaded", function() {
    fetchSummary();
    document.querySelector('#historicalDataTab').addEventListener('click', fetchHistoricalData);
});

async function fetchSummary() {
    const response = await fetch('/summary');
    const summary = await response.json();

    document.getElementById('total-consumption').innerText = summary.total_consumption.toFixed(2) + " kWh";
    document.getElementById('average-daily-consumption').innerText = summary.average_daily_consumption.toFixed(2) + " kWh";
}

async function fetchHistoricalData() {
    try {
        const response = await fetch('/historical_data');
        if (!response.ok) {
            throw new Error('Failed to fetch historical data');
        }
        const historicalData = await response.json();

        // Process the fetched historical data, for example, display it on the page
        const historicalDataContainer = document.getElementById('historicalDataContainer');
        historicalDataContainer.innerHTML = '';

        const table = document.createElement('table');
        table.className = 'table table-striped';
        
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');
        
        const headerRow = document.createElement('tr');
        const headers = Object.keys(historicalData).map(key => {
            const th = document.createElement('th');
            th.innerText = key;
            return th;
        });
        
        headerRow.append(...headers);
        thead.appendChild(headerRow);

        const numRows = historicalData[Object.keys(historicalData)[0]].length;
        for (let i = 0; i < numRows; i++) {
            const row = document.createElement('tr');
            const cells = Object.keys(historicalData).map(key => {
                const td = document.createElement('td');
                td.innerText = historicalData[key][i];
                return td;
            });
            row.append(...cells);
            tbody.appendChild(row);
        }
        
        table.appendChild(thead);
        table.appendChild(tbody);
        historicalDataContainer.appendChild(table);
    } catch (error) {
        console.error('Error fetching historical data:', error.message);
    }
}

async function predictPower() {
    const weeksInput = document.getElementById('weeks-input');
    const weeks = weeksInput ? parseInt(weeksInput.value) : 1;

    const response = await fetch('/past_data');
    const pastData = await response.json();

    const response2 = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ past_data: pastData, weeks: weeks })
    });

    if (response2.ok) {
        const data = await response2.json();
        const forecastData = data.forecast.Global_active_power;
        const applianceBreakdownData = data.appliance_breakdown;
        const totalConsumption = forecastData.reduce((acc, val) => acc + val, 0);
        const averageDailyConsumption = totalConsumption / (weeks * 7);

        // Update total consumption and average daily consumption boxes
        document.getElementById('total-consumption-box').innerText = totalConsumption.toFixed(2) + " kWh";
        document.getElementById('average-daily-consumption-box').innerText = averageDailyConsumption.toFixed(2) + " kWh";

        // Clear existing graphs
        document.querySelector("#forecastGraph").innerHTML = '';
        document.querySelector("#applianceBreakdownGraph").innerHTML = '';

        // Display the new graphs
        displayForecastGraph(forecastData, weeks);
        displayApplianceBreakdownGraph(applianceBreakdownData, weeks);
    } else {
        console.error("Error fetching predictions:", response2.statusText);
    }
}

function displayForecastGraph(forecastData, weeks) {
    const categories = [];
    for (let i = 0; i < weeks * 7; i++) {
        categories.push('Day ' + (i + 1));
    }

    var options = {
        chart: {
            type: 'line',
            height: 350
        },
        series: [{
            name: 'Forecast',
            data: forecastData
        }],
        xaxis: {
            categories: categories
        }
    };

    var chart = new ApexCharts(document.querySelector("#forecastGraph"), options);
    chart.render();
}

function displayApplianceBreakdownGraph(applianceData, weeks) {
    const categories = [];
    for (let i = 0; i < weeks * 7; i++) {
        categories.push('Day ' + (i + 1));
    }

    var options = {
        chart: {
            type: 'bar',
            height: 350
        },
        series: Object.keys(applianceData).map(key => ({
            name: key,
            data: applianceData[key]
        })),
        xaxis: {
            categories: categories
        }
    };

    var chart = new ApexCharts(document.querySelector("#applianceBreakdownGraph"), options);
    chart.render();
}
