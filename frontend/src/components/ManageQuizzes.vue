<template>
  <div class="container my-5">
    <h4 class="mb-4 text-danger fw-bold">📚 Manage Quizzes</h4>

    <!-- Add/Edit Form -->
    <form @submit.prevent="saveQuiz" class="row g-3 mb-4 shadow-sm p-3 bg-light rounded">
      <div class="col-md-4">
        <label class="form-label">Select Subject</label>
        <select v-model="form.subjectid" class="form-select" required>
          <option disabled value="">-- Choose a Subject --</option>
          <option v-for="sub in subjects" :key="sub.id" :value="sub.id">
            {{ sub.name }}
          </option>
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">Select Chapter</label>
        <select v-model="form.chapterid" class="form-select" required>
          <option disabled value="">-- Choose a Chapter --</option>
          <option v-for="chap in chapters" :key="chap.id" :value="chap.id">
            {{ chap.name }}
          </option>
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">Date of Quiz</label>
        <input v-model="form.date_of_quiz" type="date" class="form-control" required />
      </div>

      <div class="col-md-4">
        <label class="form-label">Duration (minutes)</label>
        <input v-model="form.duration_of_quiz" type="number" class="form-control" required />
      </div>

      <div class="col-md-6">
        <label class="form-label">Remarks</label>
        <input v-model="form.remarks" type="text" class="form-control" placeholder="Any remarks..." />
      </div>

      <div class="col-md-2 d-flex align-items-end">
        <button class="btn btn-primary w-100">{{ editing ? 'Update' : 'Add' }}</button>
      </div>
    </form>

    <!-- Quiz Table -->
    <div class="table-responsive">
      <table class="table table-bordered table-striped">
        <thead class="table-secondary">
          <tr>
            <th>ID</th>
            <th>Subject</th>
            <th>Chapter</th>
            <th>Date</th>
            <th>Duration (min)</th>
            <th>Remarks</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="q in quizzes" :key="q.id">
            <td>{{ q.id }}</td>
            <td>{{ q.subject_name }}</td>
            <td>{{ q.chapter_name }}</td>
            <td>{{ q.date_of_quiz }}</td>
            <td>{{ q.duration_of_quiz }}</td>
            <td>{{ q.remarks }}</td>
            <td>
              <button class="btn btn-sm btn-warning me-2" @click="edit(q)">✏️ Edit</button>
              <button class="btn btn-sm btn-danger" @click="deleteQuiz(q.id)">🗑️ Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ManageQuiz',
  data() {
    return {
      subjects: [],
      chapters: [],
      quizzes: [],
      form: {
        id: null,
        subjectid: '',
        chapterid: '',
        date_of_quiz: '',
        duration_of_quiz: '',
        remarks: ''
      },
      editing: false
    };
  },
  async mounted() {
    await this.fetchSubjects();
    await this.fetchChapters();
    await this.fetchQuizzes();
  },
  methods: {
    async fetchSubjects() {
      try {
        const res = await axios.get('http://localhost:5000/admin/subject', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.subjects = res.data.subjects || res.data;
      } catch (err) {
        console.error('Error fetching subjects:', err);
      }
    },
    async fetchChapters() {
      try {
        const res = await axios.get('http://localhost:5000/admin/chapter', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.chapters = res.data.chapters || res.data;
      } catch (err) {
        console.error('Error fetching chapters:', err);
      }
    },
    async fetchQuizzes() {
      try {
        const res = await axios.get('http://localhost:5000/admin/quiz', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.quizzes = res.data;
      } catch (err) {
        console.error('Error fetching quizzes:', err);
      }
    },
    async saveQuiz() {
      try {
        const token = localStorage.getItem('token');
        const method = this.editing ? 'put' : 'post';
        await axios({
          method,
          url: 'http://localhost:5000/admin/quiz',
          data: this.form,
          headers: { Authorization: `Bearer ${token}` }
        });
        this.resetForm();
        await this.fetchQuizzes();
      } catch (err) {
        console.error('Error saving quiz:', err);
      }
    },
    edit(q) {
      this.form = {
        id: q.id,
        subjectid: q.subjectid,
        chapterid: q.chapterid,
        date_of_quiz: q.date_of_quiz,
        duration_of_quiz: q.duration_of_quiz,
        remarks: q.remarks
      };
      this.editing = true;
    },
    async deleteQuiz(id) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete('http://localhost:5000/admin/quiz', {
          headers: { Authorization: `Bearer ${token}` },
          data: { id }
        });
        await this.fetchQuizzes();
      } catch (err) {
        console.error('Error deleting quiz:', err);
      }
    },
    resetForm() {
      this.form = {
        id: null,
        subjectid: '',
        chapterid: '',
        date_of_quiz: '',
        duration_of_quiz: '',
        remarks: ''
      };
      this.editing = false;
    }
  }
};
</script>

<style scoped>
.table th,
.table td {
  vertical-align: middle;
}
</style>
