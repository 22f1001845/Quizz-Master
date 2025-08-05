<template>
  <div class="container my-5">
    <h4 class="mb-4 text-danger fw-bold">❓ Manage Questions</h4>

    <!-- Add/Edit Form -->
    <form
      @submit.prevent="saveQuestion"
      class="row g-3 align-items-end mb-4 shadow-sm p-3 bg-light rounded"
    >
      <div class="col-md-4">
        <label class="form-label">Select Quiz</label>
        <select
          v-model="form.quiz_id"
          @change="fetchQuestions"
          class="form-select"
          required
        >
          <option disabled value="">-- Choose a Quiz --</option>
          <option
            v-for="q in quizzes"
            :key="q.id"
            :value="q.id"
          >
            Quiz #{{ q.id }} - {{ q.date_of_quiz }} ({{ q.subject_name }} - {{ q.chapter_name }})
          </option>
        </select>
      </div>

      <div class="col-md-8">
        <label class="form-label">Question</label>
        <input
          v-model="form.question_statement"
          type="text"
          placeholder="Write the question here..."
          class="form-control"
          required
        />
      </div>

      <div class="col-md-6">
        <input
          v-model="form.option1"
          type="text"
          class="form-control"
          placeholder="Option 1"
          required
        />
      </div>
      <div class="col-md-6">
        <input
          v-model="form.option2"
          type="text"
          class="form-control"
          placeholder="Option 2"
          required
        />
      </div>
      <div class="col-md-6">
        <input
          v-model="form.option3"
          type="text"
          class="form-control"
          placeholder="Option 3"
          required
        />
      </div>
      <div class="col-md-6">
        <input
          v-model="form.option4"
          type="text"
          class="form-control"
          placeholder="Option 4"
          required
        />
      </div>

      <div class="col-md-3">
        <label class="form-label">Correct Option</label>
        <select
          v-model="form.correct_option_id"
          class="form-select"
          required
        >
          <option disabled value="">Select Correct Option</option>
          <option :value="1">Option 1</option>
          <option :value="2">Option 2</option>
          <option :value="3">Option 3</option>
          <option :value="4">Option 4</option>
        </select>
      </div>

      <div class="col-md-2">
        <button class="btn btn-primary w-100">
          {{ editing ? "Update" : "Add" }}
        </button>
      </div>
    </form>

    <!-- Questions Accordion -->
    <div class="accordion shadow-sm" id="questionAccordion">
      <div
        class="accordion-item"
        v-for="q in questions"
        :key="q.id"
      >
        <h2 class="accordion-header">
          <button
            class="accordion-button collapsed"
            type="button"
            data-bs-toggle="collapse"
            :data-bs-target="'#q' + q.id"
          >
            🗨️ {{ q.question_statement }}
          </button>
        </h2>
        <div
          :id="'q' + q.id"
          class="accordion-collapse collapse"
        >
          <div class="accordion-body">
            <ul class="list-unstyled mb-3">
              <li><strong>1:</strong> {{ q.option1 }}</li>
              <li><strong>2:</strong> {{ q.option2 }}</li>
              <li><strong>3:</strong> {{ q.option3 }}</li>
              <li><strong>4:</strong> {{ q.option4 }}</li>
              <li class="text-success">
                <strong>✅ Correct Option:</strong> Option {{ q.correct_option_id }}
              </li>
            </ul>
            <div>
              <button class="btn btn-sm btn-warning me-2" @click="edit(q)">✏️ Edit</button>
              <button class="btn btn-sm btn-danger" @click="deleteQuestion(q.id)">🗑️ Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ManageQuestions",
  data() {
    return {
      quizzes: [],
      questions: [],
      form: {
        id: null,
        quiz_id: "",
        question_statement: "",
        option1: "",
        option2: "",
        option3: "",
        option4: "",
        correct_option_id: "",
      },
      editing: false,
    };
  },
  async mounted() {
    await this.fetchQuizzes();
  },
  methods: {
    async fetchQuizzes() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://localhost:5000/admin/quiz", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.quizzes = res.data;
      } catch (e) {
        console.error("Error fetching quizzes:", e);
      }
    },
    async fetchQuestions() {
      try {
        if (!this.form.quiz_id) return;
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://localhost:5000/admin/question?quiz_id=${this.form.quiz_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        this.questions = res.data;
      } catch (e) {
        console.error("Error fetching questions:", e);
      }
    },
    async saveQuestion() {
      try {
        const token = localStorage.getItem("token");
        const method = this.editing ? "put" : "post";
        await axios({
          method,
          url: "http://localhost:5000/admin/question",
          data: this.form,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.resetForm();
        await this.fetchQuestions();
      } catch (e) {
        console.error("Error saving question:", e);
      }
    },
    async deleteQuestion(id) {
      try {
        const token = localStorage.getItem("token");
        await axios.delete("http://localhost:5000/admin/question", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          data: { id },
        });
        await this.fetchQuestions();
      } catch (e) {
        console.error("Error deleting question:", e);
      }
    },
    edit(q) {
      this.form = { ...q };
      this.editing = true;
    },
    resetForm() {
      const quizId = this.form.quiz_id;
      this.form = {
        id: null,
        quiz_id: quizId,
        question_statement: "",
        option1: "",
        option2: "",
        option3: "",
        option4: "",
        correct_option_id: "",
      };
      this.editing = false;
    },
  },
};
</script>

<style scoped>
.accordion-button {
  font-weight: bold;
}
.accordion-item {
  margin-bottom: 10px;
  border-radius: 6px;
  overflow: hidden;
}
.btn {
  font-weight: 500;
}
</style>
