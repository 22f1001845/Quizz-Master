<template>
    <div class="container my-4">
        <h4 class="mb-4 text-success fw-bold">📘 Manage Chapters</h4>

        <!-- Add/Edit Form -->
        <form
            @submit.prevent="saveChapter"
            class="row g-2 align-items-end mb-4 shadow-sm p-3 bg-light rounded"
        >
            <div class="col-md-3">
                <label class="form-label">Subject</label>
                <select
                    v-model="form.subjectid"
                    class="form-select"
                    required
                >
                    <option
                        disabled
                        value=""
                    >
                        Select Subject
                    </option>
                    <option
                        v-for="sub in subjects"
                        :key="sub.id"
                        :value="sub.id"
                    >
                        {{ sub.name }}
                    </option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Chapter Name</label>
                <input
                    v-model="form.name"
                    type="text"
                    class="form-control"
                    placeholder="Enter Chapter Name"
                    required
                />
            </div>
            <div class="col-md-4">
                <label class="form-label">Description</label>
                <input
                    v-model="form.description"
                    type="text"
                    class="form-control"
                    placeholder="Enter Description"
                />
            </div>
            <div class="col-md-2">
                <button class="btn btn-success w-100">
                    {{ editing ? "Update Chapter" : "Add Chapter" }}
                </button>
            </div>
        </form>

        <!-- Chapters List -->
        <ul class="list-group shadow-sm">
            <li
                v-for="ch in chapters"
                :key="ch.id"
                class="list-group-item d-flex justify-content-between align-items-center"
            >
                <div>
                    <strong>{{ ch.name }}</strong>
                    <span class="text-muted"
                        >({{ subjectName(ch.subjectid) }})</span
                    >
                    <br />
                    <small class="text-secondary">{{ ch.description }}</small>
                </div>
                <div>
                    <button
                        class="btn btn-sm btn-warning me-2"
                        @click="edit(ch)"
                    >
                        ✏️ Edit
                    </button>
                    <button
                        class="btn btn-sm btn-danger"
                        @click="deleteChapter(ch.id)"
                    >
                        🗑️ Delete
                    </button>
                </div>
            </li>
        </ul>
    </div>
</template>

<script>
import axios from "axios";
export default {
    name: "ManageChapters",
    data() {
        return {
            subjects: [],
            chapters: [],
            form: { name: "", description: "", subjectid: "", id: null },
            editing: false,
        };
    },
    async mounted() {
        await this.fetchSubjects();
        await this.fetchChapters();
    },
    methods: {
        async fetchSubjects() {
            const res = await axios.get("http://localhost:5000/subjects", {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
            });
            this.subjects = res.data;
        },
        async fetchChapters() {
            const res = await axios.get("http://localhost:5000/admin/chapter", {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
            });
            this.chapters = res.data;
        },
        subjectName(id) {
            const s = this.subjects.find((sub) => sub.id === id);
            return s ? s.name : "";
        },
        async saveChapter() {
            const token = localStorage.getItem("token");
            const url = "http://localhost:5000/admin/chapter";
            const method = this.editing ? "put" : "post";

            await axios({
                method,
                url,
                data: this.form,
                headers: { Authorization: `Bearer ${token}` },
            });

            this.form = { name: "", description: "", subjectid: "", id: null };
            this.editing = false;
            await this.fetchChapters();
        },
        edit(ch) {
            this.form = { ...ch };
            this.editing = true;
        },
        async deleteChapter(id) {
            const token = localStorage.getItem("token");
            await axios.delete("http://localhost:5000/admin/chapter", {
                headers: { Authorization: `Bearer ${token}` },
                data: { id },
            });
            await this.fetchChapters();
        },
    },
};
</script>

<style scoped>
.list-group-item {
    border-radius: 5px;
    transition: background 0.2s;
}
.list-group-item:hover {
    background-color: #f8f9fa;
}
.btn {
    font-weight: 500;
}
</style>
