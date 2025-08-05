<template>
  <div class="summary-container my-5">
    <!-- Header Section -->
    <div class="text-center mb-4">
      <h2 class="fw-bold title">📊 Your Quiz Summary</h2>
      <p class="subtitle">Track your progress and performance at a glance</p>
    </div>

    <!-- Back to Dashboard Button -->
    <div class="text-center mb-4">
      <button class="btn btn-back" @click="goToDashboard">
        🔙 Back to Dashboard
      </button>
    </div>

    <!-- Results Table -->
    <div v-if="results.length" class="table-wrapper">
      <table class="table table-hover text-center">
        <thead>
          <tr>
            <th>🆔 Quiz ID</th>
            <th>✅ Score (%)</th>
            <th>✔ Correct</th>
            <th>❓ Total</th>
            <th>📅 Attempted On</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="res in results" :key="res.quiz_id">
            <td>#{{ res.quiz_id }}</td>
            <td>
              <span
                class="badge"
                :class="getScoreClass(res.score)"
              >
                {{ res.score }}%
              </span>
            </td>
            <td>{{ res.correct_answers }}</td>
            <td>{{ res.total_questions }}</td>
            <td>{{ formatDate(res.attempted_on) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No Data Message -->
    <div v-else class="alert alert-info text-center mt-4">
      No quiz attempts found.
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Summary",
  data() {
    return {
      results: [],
    };
  },
  async mounted() {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get("http://localhost:5000/results", {
        headers: { Authorization: `Bearer ${token}` },
      });
      this.results = res.data;
    } catch (error) {
      console.error("Failed to load results:", error);
    }
  },
  methods: {
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleDateString() + " " + date.toLocaleTimeString();
    },
    goToDashboard() {
      this.$router.push("/dashboard");
    },
    getScoreClass(score) {
      if (score >= 80) return "bg-success";
      if (score >= 50) return "bg-warning text-dark";
      return "bg-danger";
    },
  },
};
</script>

<style scoped>
.summary-container {
  max-width: 1100px;
  margin: auto;
  padding: 25px;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
}

.title {
  font-size: 2rem;
  color: #1d3557;
}

.subtitle {
  font-size: 16px;
  color: #6c757d;
}

.btn-back {
  background: linear-gradient(90deg, #007bff, #00c6ff);
  color: #fff;
  border: none;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.btn-back:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0, 114, 255, 0.3);
}

.table-wrapper {
  background: #fff;
  padding: 20px;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.table thead {
  background: #007bff;
  color: white;
  font-weight: bold;
}

.table tbody tr {
  transition: background 0.3s ease;
}

.table tbody tr:hover {
  background: #f1faff;
}

.quiz-name {
  font-weight: 600;
}

.badge {
  font-size: 0.95rem;
  padding: 8px 12px;
  border-radius: 8px;
}
</style>
