<template>
  <div class="dashboard-container my-5">
    <!-- Header Section -->
    <div class="header d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="welcome-title">👋 Welcome, {{ userName || "User" }}</h2>
        <p class="subtitle">Select a subject to view available quizzes</p>
      </div>
      <div>
        <router-link to="/summary" class="btn btn-info me-3">📊 View Summary</router-link>
        <button class="btn btn-sm btn-danger" @click="logout">🚪 Logout</button>
      </div>
    </div>

    <!-- Subjects Section -->
    <div class="card p-4 shadow subject-card mb-4">
      <h4 class="mb-3 text-dark">📘 Available Subjects</h4>
      <div v-if="subjects.length === 0" class="text-muted">No subjects available.</div>
      <div class="list-group">
        <button
          v-for="subject in subjects"
          :key="subject.id"
          class="list-group-item list-group-item-action subject-item"
          @click="loadQuizzes(subject.id)"
        >
          <strong>{{ subject.name }}</strong> - {{ subject.description }}
        </button>
      </div>
    </div>

    <!-- Quizzes Section -->
    <div v-if="quizzes.length > 0" class="card p-4 shadow quiz-card">
      <h4 class="mb-3 text-dark">📝 Quizzes under {{ selectedSubjectName }}</h4>
      <div class="table-responsive">
        <table class="table table-striped table-hover text-center">
          <thead class="table-primary">
            <tr>
              <th>#</th>
              <th>Date</th>
              <th>Duration</th>
              <th>Remarks</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(quiz, index) in quizzes" :key="quiz.id">
              <td>{{ index + 1 }}</td>
              <td>{{ quiz.date_of_quiz }}</td>
              <td>{{ quiz.duration_of_quiz }}</td>
              <td>{{ quiz.remarks }}</td>
              <td>
                <span
                  :class="{
                    'badge bg-success': isToday(quiz.date_of_quiz),
                    'badge bg-warning text-dark': isUpcoming(quiz.date_of_quiz),
                    'badge bg-secondary': isPast(quiz.date_of_quiz)
                  }"
                >
                  {{ getQuizStatus(quiz.date_of_quiz) }}
                </span>
              </td>
              <td>
                <router-link
                  v-if="isToday(quiz.date_of_quiz)"
                  :to="'/quiz/' + quiz.id"
                  class="btn btn-sm btn-outline-primary"
                >
                  ▶ Start Quiz
                </router-link>
                <button v-else class="btn btn-sm btn-outline-secondary" disabled>
                  {{ getQuizStatus(quiz.date_of_quiz) }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Dashboard",
  data() {
    return {
      subjects: [],
      quizzes: [],
      selectedSubjectName: "",
      userName: "",
      error: "",
    };
  },
  mounted() {
    this.fetchSubjects();
    this.fetchUser();
  },
  methods: {
    async fetchSubjects() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://localhost:5000/subjects", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.subjects = res.data;
      } catch (err) {
        this.error = err.response?.data?.message || "Failed to load subjects.";
      }
    },
    async loadQuizzes(subjectId) {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(`http://localhost:5000/quizzes/${subjectId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.quizzes = res.data;
        const subject = this.subjects.find((s) => s.id === subjectId);
        this.selectedSubjectName = subject ? subject.name : "";
      } catch (err) {
        this.error = err.response?.data?.message || "Failed to load quizzes.";
      }
    },
    async fetchUser() {
      const token = localStorage.getItem("token");
      if (!token) return;
      try {
        const res = await axios.get("http://localhost:5000/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.userName = res.data.fullname || "User";
      } catch (err) {
        this.userName = "User";
      }
    },
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },

    // Quiz Date Logic
    isToday(date) {
      const today = new Date().toISOString().split("T")[0];
      return date === today;
    },
    isUpcoming(date) {
      const today = new Date().toISOString().split("T")[0];
      return date > today;
    },
    isPast(date) {
      const today = new Date().toISOString().split("T")[0];
      return date < today;
    },
    getQuizStatus(date) {
      if (this.isToday(date)) return "Available";
      if (this.isUpcoming(date)) return "Upcoming";
      return "Ended";
    },
  },
};
</script>

<style scoped>
/* Background Gradient with Glassmorphism */
.dashboard-container {
  max-width: 1200px;
  margin: auto;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
  border-radius: 18px;
  box-shadow: 0 10px 25px rgba(31, 38, 135, 0.2);
}

/* Header Styling */
.welcome-title {
  font-weight: 800;
  color: #1d3557;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
}
.subtitle {
  font-size: 15px;
  color: #6c757d;
}

/* Card Styling */
.card {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* Subject List Items */
.subject-item {
  border-radius: 8px;
  transition: all 0.3s ease;
}
.subject-item:hover {
  background-color: #e9f5ff;
  transform: translateX(5px);
}

/* Buttons */
.btn-info {
  background: linear-gradient(90deg, #00c6ff, #0072ff);
  color: #fff;
  border: none;
  font-weight: 600;
}
.btn-info:hover {
  box-shadow: 0 5px 15px rgba(0, 114, 255, 0.3);
}

.btn-danger {
  font-weight: bold;
}

/* Table Styling */
.table th {
  font-weight: bold;
}
.table-hover tbody tr:hover {
  background-color: #f1faff;
}

.badge {
  font-size: 0.9rem;
  padding: 6px 12px;
  border-radius: 8px;
}
</style>
