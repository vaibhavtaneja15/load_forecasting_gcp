let chart;

// ================= CHART INITIALIZATION =================
window.onload = () => {
  const ctx = document.getElementById("loadChart");

  if (!ctx) {
    console.error("❌ Canvas element not found");
    return;
  }

  chart = new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Electrical Load (MW)",
          data: [],
          borderColor: "#00d9ff",
          backgroundColor: "rgba(0, 217, 255, 0.1)",
          fill: true,
          tension: 0.4,
          borderWidth: 3,
          pointRadius: 5,
          pointHoverRadius: 8,
          pointBackgroundColor: "#00d9ff",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointHoverBackgroundColor: "#ffffff",
          pointHoverBorderColor: "#00d9ff"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: {
        legend: {
          labels: {
            color: "#ffffff",
            font: { size: 14, weight: "600" }
          }
        },
        tooltip: {
          backgroundColor: "rgba(10, 14, 39, 0.9)",
          titleColor: "#00d9ff",
          bodyColor: "#ffffff",
          borderColor: "#00d9ff",
          borderWidth: 1,
          callbacks: {
            label: (context) =>
              `Load: ${context.parsed.y.toFixed(2)} MW`
          }
        }
      },
      scales: {
        y: {
          ticks: {
            color: "rgba(255,255,255,0.7)",
            callback: (v) => v + " MW"
          },
          grid: { color: "rgba(255,255,255,0.1)" },
          title: {
            display: true,
            text: "Load (MW)",
            color: "#00d9ff"
          }
        },
        x: {
          ticks: { color: "rgba(255,255,255,0.7)" },
          grid: { color: "rgba(255,255,255,0.05)" },
          title: {
            display: true,
            text: "Time",
            color: "#00d9ff"
          }
        }
      }
    }
  });

  console.log("✅ Chart initialized");
};

// ================= PREDICTION FUNCTION =================
function predict() {
  const payload = {
    date: document.getElementById("date").value,
    temperature: document.getElementById("temperature").value,
    humidity: document.getElementById("humidity").value,
    daytype: document.getElementById("daytype").value,
    season: document.getElementById("season").value
  };

  if (Object.values(payload).some(v => v === "" || v === null)) {
    alert("Please fill all fields");
    return;
  }

  const resultElement = document.getElementById("result");
  resultElement.innerText = "Calculating...";
  resultElement.style.opacity = "0.5";

  fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(res => {
      console.log("API response:", res);

      const loadMW = res.predicted_load;

      if (loadMW === undefined || loadMW === null || isNaN(loadMW)) {
        throw new Error("Invalid API response");
      }

      // ---------- UPDATE RESULT ----------
      resultElement.style.opacity = "1";
      resultElement.innerText = loadMW.toFixed(2) + " MW";

      // ---------- UPDATE CHART ----------
      const timestamp = new Date().toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });

      chart.data.labels.push(timestamp);
      chart.data.datasets[0].data.push(loadMW);

      if (chart.data.labels.length > 10) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
      }

      chart.update();

      // ---------- AUTO SCROLL (FIXED) ----------
      requestAnimationFrame(() => {
        const target =
          document.getElementById("loadChart") ||
          document.getElementById("result");

        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
            block: "center"
          });
        }
      });
    })
    .catch(err => {
      console.error("❌ Prediction failed:", err);
      resultElement.innerText = "-- MW";
      resultElement.style.opacity = "1";
      alert("Prediction failed. Try again.");
    });
}

// ================= ENTER KEY SUPPORT =================
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("keypress", e => {
      if (e.key === "Enter") predict();
    });
  });
});
