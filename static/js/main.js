let chartInstance = null;

// Fetch list of companies
async function loadCompanies() {
  const response = await fetch('/companies');
  const companies = await response.json();

  const dropdown = document.getElementById('companyDropdown');
  dropdown.innerHTML = "";

  companies.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.symbol;
    opt.textContent = `${c.name} (${c.symbol})`;
    dropdown.appendChild(opt);
  });
}

// Load stock data and draw chart
async function loadData(){
  const symbol = document.getElementById('companyDropdown').value;

  const response = await fetch(`/data/${symbol}`);
  const data = await response.json();

  const labels = data.map(x => new Date(x.Date).toLocaleDateString());
  const closePrices = data.map(x => Number(x.Close));

  const ctx = document.getElementById('chart').getContext('2d');
  if(chartInstance) chartInstance.destroy(); // remove old graph

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: symbol + " Closing Price",
        data: closePrices,
        borderWidth: 2,
        borderColor: "#007bff",
        fill: false,
        tension: 0.4
      }]
    }
  });
}

loadCompanies();
