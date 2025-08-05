<template>
  <div class="container my-5">
    <h3 class="mb-4 text-primary fw-bold">🧠 Available Subjects</h3>

    <ul class="list-group shadow-sm">
      <li
        v-for="s in subjects"
        :key="s.id"
        class="list-group-item d-flex justify-content-between align-items-center"
      >
        <div>
          <strong>{{ s.name }}</strong>
        </div>
        <button
          class="btn btn-sm btn-outline-primary"
          @click="loadQuizzes(s.id)"
        >
          View Quizzes
        </button>
      </li>
    </ul>

    <div v-if="quizzes.length" class="mt-5">
      <h4 class="mb-3 text-success fw-semibold">📋 Quizzes</h4>
      <ul class="list-group shadow-sm">
        <li
          v-for="q in quizzes"
          :key="q.id"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>{{ q.name || 'Quiz ' + q.id }}</strong>
            <br />
            <small class="text-muted">{{ q.date_of_quiz }}</small>
            <span
              class="badge ms-2"
              :class="getStatusBadge(q)"
            >
              {{ getStatusText(q) }}
            </span>
          </div>
          <router-link
            :to="isAvailable(q) ? `/quiz/${q.id}` : '#'"
            class="btn btn-sm"
            :class="isAvailable(q) ? 'btn-success' : 'btn-secondary disabled'"
          >
            Attempt Quiz
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "QuizList",
  data() {
    return {
      subjects: [],
      quizzes: [],
      today: new Date().toISOString().split("T")[0], // Current date in YYYY-MM-DD
    };
  },
  async mounted() {
    const token = localStorage.getItem("token");
    const res = await fetch("http://localhost:5000/subjects", {
      headers: { Authorization: `Bearer ${token}` },
    });
    this.subjects = await res.json();
  },
  methods: {
    async loadQuizzes(subjectId) {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:5000/quizzes/${subjectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      this.quizzes = await res.json();
    },
    getStatusText(q) {
      if (q.date_of_quiz === this.today) return "Available Today";
      if (q.date_of_quiz > this.today) return "Upcoming";
      return "Ended";
    },
    getStatusBadge(q) {
      if (q.date_of_quiz === this.today) return "bg-success";
      if (q.date_of_quiz > this.today) return "bg-warning text-dark";
      return "bg-secondary";
    },
    isAvailable(q) {
      return q.date_of_quiz === this.today;
    },
  },
};
</script>

<style scoped>
.list-group-item {
  transition: background-color 0.2s ease;
}
.list-group-item:hover {
  background-color: #f8f9fa;
}
.btn {
  font-weight: 500;
}
.badge {
  font-size: 0.85rem;
  padding: 6px 10px;
  border-radius: 8px;
}
</style>
