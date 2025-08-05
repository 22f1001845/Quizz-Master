<template>
  <div class="charts-section">
    <h4 class="fw-bold mb-3">📊 Analytics Overview</h4>
    <div class="row">
      <div class="col-md-6 mb-4">
        <canvas id="quizzesChart"></canvas>
      </div>
      <div class="col-md-6 mb-4">
        <canvas id="scoresChart"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
// ✅ Import Chart.js
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

export default {
  name: "AdminCharts",
  props: ["quizData", "scoreData"],

  mounted() {
    this.renderQuizzesChart();
    this.renderScoresChart();
  },

  methods: {
    renderQuizzesChart() {
      const ctx = document.getElementById("quizzesChart").getContext("2d");
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: this.quizData.map(q => q.quiz_name),
          datasets: [
            {
              label: "Attempts per Quiz",
              data: this.quizData.map(q => q.attempts),
              backgroundColor: "#007bff"
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: "Top Quizzes by Attempts" }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    },

    renderScoresChart() {
      const ctx = document.getElementById("scoresChart").getContext("2d");
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: ["0-30%", "30-60%", "60-90%", "90-100%"],
          datasets: [
            {
              data: this.scoreData,
              backgroundColor: ["#dc3545", "#ffc107", "#28a745", "#17a2b8"]
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: "Score Distribution" }
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.charts-section {
  background: linear-gradient(135deg, #ffffff, #f1f5f9);
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(31, 38, 135, 0.2);
  backdrop-filter: blur(10px);
  margin-top: 20px;
  animation: fadeIn 0.6s ease;
}

/* Heading Styling */
.charts-section h4 {
  font-weight: 700;
  font-size: 22px;
  color: #1d3557;
  margin-bottom: 20px;
  text-align: center;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
}

/* Canvas Styling */
canvas {
  width: 100% !important;
  height: 350px !important;
  background: #fff;
  border-radius: 12px;
  padding: 15px;
  box-shadow: inset 0 4px 10px rgba(0, 0, 0, 0.05);
}

/* Row gap for charts */
.row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

/* Fade-in Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
