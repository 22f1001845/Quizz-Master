<template>
    <div class="admin-dashboard container py-5">
        <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
                <h2 class="fw-bold text-primary">👑 Admin Control Panel</h2>
                <p class="text-muted">
                    Manage your entire quiz system with ease
                </p>
            </div>
            <div>
                <button
                    class="btn btn-info me-2"
                    @click="$router.push('/admin/summary')"
                >
                    📊 View Summary & Reports
                </button>
                <button
                    class="btn btn-sm btn-danger"
                    @click="logout"
                >
                    🚪 Logout
                </button>
            </div>
        </div>

        <div class="mb-4 position-relative">
            <input
                type="text"
                v-model="searchQuery"
                @input="debouncedSearch"
                placeholder="🔍 Search Users, Quizzes, or Subjects"
                class="form-control search-input"
            />
            <div
                v-if="isSearching"
                class="spinner-border text-primary search-loader"
            ></div>
        </div>

        <div
            v-if="hasResults"
            class="search-results mb-4"
        >
            <h5 class="fw-bold">Search Results:</h5>

            <div v-if="results.users.length">
                <h6>👥 Users</h6>
                <ul>
                    <li
                        v-for="user in results.users"
                        :key="user.id"
                    >
                        <span
                            v-html="highlight(user.username || user.fullname)"
                        ></span>
                    </li>
                </ul>
            </div>

            <div v-if="results.quizzes.length">
                <h6>📝 Quizzes</h6>
                <ul>
                    <li
                        v-for="quiz in results.quizzes"
                        :key="quiz.id"
                    >
                        <span v-html="highlight(quiz.name)"></span>
                    </li>
                </ul>
            </div>

            <div v-if="results.subjects.length">
                <h6>📚 Subjects</h6>
                <ul>
                    <li
                        v-for="subject in results.subjects"
                        :key="subject.id"
                    >
                        <span v-html="highlight(subject.name)"></span>
                    </li>
                </ul>
            </div>

            <div v-if="results.chapters.length">
                <h6>📚 Chapters</h6>
                <ul>
                    <li
                        v-for="chapter in results.chapters"
                        :key="chapter.id"
                    >
                        <span v-html="highlight(chapter.name)"></span>
                    </li>
                </ul>
            </div>
        </div>

        <div
            v-if="!hasResults && searchQuery.trim() && !isSearching && !error"
            class="alert alert-warning"
        >
            No results found for "<strong>{{ searchQuery }}</strong
            >"
        </div>

        <div
            v-if="error"
            class="alert alert-danger mt-4 text-center"
        >
            {{ error }}
        </div>

        <div class="nav-tabs-wrapper mb-4">
            <div
                class="btn-group w-100 shadow-sm"
                role="group"
            >
                <button
                    class="btn"
                    :class="
                        current === 'users' ? 'btn-dark' : 'btn-outline-dark'
                    "
                    @click="switchTab('users')"
                >
                    👥 Users
                </button>
                <button
                    class="btn"
                    :class="
                        current === 'subjects'
                            ? 'btn-primary'
                            : 'btn-outline-primary'
                    "
                    @click="switchTab('subjects')"
                >
                    📚 Subjects
                </button>
                <button
                    class="btn"
                    :class="
                        current === 'chapters'
                            ? 'btn-secondary'
                            : 'btn-outline-secondary'
                    "
                    @click="switchTab('chapters')"
                >
                    🧩 Chapters
                </button>
                <button
                    class="btn"
                    :class="
                        current === 'quizzes'
                            ? 'btn-success'
                            : 'btn-outline-success'
                    "
                    @click="switchTab('quizzes')"
                >
                    📝 Quizzes
                </button>
                <button
                    class="btn"
                    :class="
                        current === 'questions'
                            ? 'btn-warning text-white'
                            : 'btn-outline-warning'
                    "
                    @click="switchTab('questions')"
                >
                    ❓ Questions
                </button>
            </div>
        </div>

        <div class="component-section bg-light p-4 shadow rounded">
            <ManageUsers v-if="current === 'users'" />
            <ManageSubjects v-if="current === 'subjects'" />
            <ManageChapters v-if="current === 'chapters'" />
            <ManageQuizzes v-if="current === 'quizzes'" />
            <ManageQuestions v-if="current === 'questions'" />
        </div>
    </div>
</template>

<script>
import ManageUsers from "./ManageUsers.vue";
import ManageSubjects from "./ManageSubjects.vue";
import ManageChapters from "./ManageChapters.vue";
import ManageQuizzes from "./ManageQuizzes.vue";
import ManageQuestions from "./ManageQuestions.vue";
import _ from "lodash"; // For debounce

export default {
    name: "AdminDashboard",
    components: {
        ManageUsers,
        ManageSubjects,
        ManageChapters,
        ManageQuizzes,
        ManageQuestions,
    },
    data() {
        return {
            current: localStorage.getItem("admin_tab") || "subjects",
            error: "",
            searchQuery: "",
            isSearching: false,
            results: { users: [], quizzes: [], subjects: [], chapters: [] },
        };
    },
    computed: {
        hasResults() {
            return (
                this.results.users.length ||
                this.results.quizzes.length ||
                this.results.subjects.length ||
                this.results.chapters.length
            );
        },
    },
    methods: {
        logout() {
            localStorage.removeItem("token");
            this.$router.push("/");
        },
        switchTab(tab) {
            this.current = tab;
            localStorage.setItem("admin_tab", tab);
        },
        async performSearch() {
            if (!this.searchQuery.trim()) {
                this.results = {
                    users: [],
                    quizzes: [],
                    subjects: [],
                    chapters: [],
                };
                this.isSearching = false;
                this.error = ""; // Clear error
                return;
            }
            this.isSearching = true;
            this.error = ""; // Clear previous error
            const token = localStorage.getItem("token");
            try {
                const res = await fetch(
                    `http://localhost:5000/admin/search?q=${this.searchQuery}`,
                    { headers: { Authorization: `Bearer ${token}` } }
                );

                if (!res.ok) {
                    const errorData = await res.json();
                    throw new Error(
                        errorData.message || `HTTP error! status: ${res.status}`
                    );
                }

                this.results = await res.json();
            } catch (err) {
                console.error("Search failed", err);
                this.error = `Search failed: ${err.message}`; // Display error to user
                this.results = { users: [], quizzes: [], subjects: [] }; // Clear results on error
            } finally {
                this.isSearching = false;
            }
        },
        highlight(text) {
            if (!text) return "";
            const regex = new RegExp(`(${this.searchQuery})`, "gi");
            return text.replace(regex, "<mark>$1</mark>");
        },
        debouncedSearch: _.debounce(function () {
            this.performSearch();
        }, 400),
    },
    async mounted() {
        const token = localStorage.getItem("token");
        if (!token) {
            this.$router.push("/");
            return;
        }

        try {
            const res = await fetch("http://localhost:5000/me", {
                headers: { Authorization: `Bearer ${token}` },
            });
            const user = await res.json();

            if (!user.roles.includes("admin")) {
                this.error = "Access denied: Admins only.";
                setTimeout(() => this.$router.push("/"), 2000);
            }
        } catch (err) {
            this.error = "Session expired. Redirecting to login.";
            setTimeout(() => this.$router.push("/"), 2000);
        }
    },
};
</script>

<style scoped>
/* Search Bar Styling */
.search-input {
    padding-left: 2.5rem;
    font-size: 16px;
}
.search-loader {
    position: absolute;
    top: 50%;
    right: 15px;
    width: 20px;
    height: 20px;
    transform: translateY(-50%);
}

/* Search Results */
.search-results {
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}
.search-results h6 {
    margin-top: 10px;
    font-weight: bold;
    color: #495057;
}
.search-results ul {
    list-style: none;
    padding-left: 0;
}
.search-results li {
    padding: 5px 0;
    font-size: 14px;
}
mark {
    background: #ffeb3b;
    padding: 0 2px;
}

/* Component Section */
.component-section {
    min-height: 320px;
    padding: 25px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 16px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
}
</style>
