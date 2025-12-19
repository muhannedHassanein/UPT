document.addEventListener("DOMContentLoaded", () => {

  const tbody = document.getElementById("sensor-body");
  const searchInput = document.getElementById("search-time");
  let chart;
  let allData = [];

  async function fetchData() {
    try {
      const response = await fetch("/all-data");
      const data = await response.json();

      if(data.error){
        tbody.innerHTML = `<tr><td colspan="5" class="text-red-500">${data.error}</td></tr>`;
        return;
      }

      allData = data;
      updateTable();
      updateChart();

    } catch(err){
      console.error(err);
    }
  }

  function updateTable() {
    const filter = searchInput.value.toLowerCase();
    tbody.innerHTML = "";

    allData.filter(entry => entry.time && entry.time.toLowerCase().includes(filter))
      .forEach(entry => {
        const row = document.createElement("tr");
        row.className = "fade-up show";
        row.innerHTML = `
          <td class="border px-4 py-2">${entry.time || ''}</td>
          <td class="border px-4 py-2">${entry.temperature || 0}</td>
          <td class="border px-4 py-2">${entry.gas || 0}</td>
          <td class="border px-4 py-2 font-bold ${entry.light ? 'text-green-500':'text-red-500'}">${entry.light || 0}</td>
          <td class="border px-4 py-2 font-bold ${entry.motion ? 'text-green-500':'text-red-500'}">${entry.motion || 0}</td>
        `;
        tbody.appendChild(row);
      });
  }

  function updateChart() {
    const labels = allData.map(d => d.time);
    const tempData = allData.map(d => d.temperature);
    const gasData = allData.map(d => d.gas);

    if(!chart){
      const ctx = document.getElementById("sensorChart").getContext("2d");
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Temperature (°C)',
              data: tempData,
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.3)',
              tension: 0.3,
              pointBackgroundColor: 'rgba(255, 99, 132, 1)',
            },
            {
              label: 'Gas',
              data: gasData,
              borderColor: 'rgba(54, 162, 235, 1)',
              backgroundColor: 'rgba(54, 162, 235, 0.3)',
              tension: 0.3,
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            }
          ]
        },
        options: {
          responsive: true,
          animation: { duration: 500 },
          plugins: {
            legend: { labels: { color: 'white' }, position: 'top' },
            zoom: {
              pan: { enabled: true, mode: 'x' },
              zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
            }
          },
          scales: {
            x: { 
              display: true,
              ticks: { color: 'white' },
              grid: { color: 'rgba(255,255,255,0.2)' }
            },
            y: { 
              beginAtZero: true,
              ticks: { color: 'white' },
              grid: { color: 'rgba(255,255,255,0.2)' }
            }
          }
        }
      });
    } else {
      chart.data.labels = labels;
      chart.data.datasets[0].data = tempData;
      chart.data.datasets[1].data = gasData;
      chart.update();
    }
  }

  // Search listener
  searchInput.addEventListener("input", updateTable);

  // Initial fetch & refresh every 30s
  fetchData();
  setInterval(fetchData, 30000);

});
