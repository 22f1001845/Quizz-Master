<template>
    <div class="container my-5">
        <h4 class="mb-4 text-primary fw-bold">📘 Manage Subjects</h4>

        <!-- Add/Edit Subject Form -->
        <form
            @submit.prevent="saveSubject"
            class="row g-2 align-items-end mb-4 shadow-sm bg-light p-3 rounded"
        >
            <div class="col-md-5">
                <label class="form-label">Subject Name</label>
                <input
                    v-model="form.name"
                    type="text"
                    class="form-control"
                    placeholder="e.g., Mathematics"
                    required
                />
            </div>
            <div class="col-md-5">
                <label class="form-label">Description</label>
                <input
                    v-model="form.description"
                    type="text"
                    class="form-control"
                    placeholder="Short description..."
                />
            </div>
            <div class="col-md-2 d-grid">
                <button class="btn btn-primary">
                    {{ editing ? "Update" : "Add" }}
                </button>
            </div>
        </form>

        <!-- Subject List -->
        <ul class="list-group shadow-sm">
            <li
                v-for="s in subjects"
                :key="s.id"
                class="list-group-item d-flex justify-content-between align-items-center"
            >
                <div>
                    <strong>{{ s.name }}</strong>
                    <br />
                    <small class="text-muted">{{ s.description }}</small>
                </div>
                <div>
                    <button
                        class="btn btn-sm btn-warning me-2"
                        @click="edit(s)"
                    >
                        ✏️ Edit
                    </button>
                    <button
                        class="btn btn-sm btn-danger"
                        @click="deleteSubject(s.id)"
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
    name: "ManageSubjects",
    data() {
        return {
            subjects: [],
            form: { name: "", description: "", id: null },
            editing: false,
        };
    },
    async mounted() {
        await this.fetchSubjects();
    },
    methods: {
        async fetchSubjects() {
            const token = localStorage.getItem("token");
            const res = await axios.get("http://localhost:5000/subjects", {
                headers: { Authorization: `Bearer ${token}` },
            });
            this.subjects = res.data;
        },
        async saveSubject() {
            const token = localStorage.getItem("token");
            const url = "http://localhost:5000/admin/subject";
            const method = this.editing ? "put" : "post";

            await axios({
                method,
                url,
                data: this.form,
                headers: { Authorization: `Bearer ${token}` },
            });

            this.resetForm();
            await this.fetchSubjects();
        },
        edit(subject) {
            this.form = { ...subject };
            this.editing = true;
        },
        async deleteSubject(id) {
            const token = localStorage.getItem("token");
            await axios.delete("http://localhost:5000/admin/subject", {
                headers: { Authorization: `Bearer ${token}` },
                data: { id },
            });
            await this.fetchSubjects();
        },
        resetForm() {
            this.form = { name: "", description: "", id: null };
            this.editing = false;
        },
    },
};
</script>

<style scoped>
.list-group-item {
    transition: 0.2s ease;
    border-radius: 6px;
}
.list-group-item:hover {
    background-color: #f9f9f9;
}
.btn {
    font-weight: 500;
}
</style>
