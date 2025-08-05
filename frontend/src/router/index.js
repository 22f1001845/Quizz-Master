import { createRouter, createWebHistory } from "vue-router";

// Import components
import Login from "../components/login.vue";
import Register from "../components/Register.vue";
import Dashboard from "../components/Dashboard.vue";
import QuizView from "../components/QuizView.vue";
import Summary from "../components/Summary.vue";
import QuizList from "../components/QuizList.vue";


import AdminDashboard from "../components/AdminDashboard.vue";
import AdminSummary from "../components/AdminSummary.vue"; 
import ManageChapters from "../components/ManageChapters.vue";
import ManageQuestions from "../components/ManageQuestions.vue";
import ManageQuizzes from "../components/ManageQuizzes.vue";
import ManageSubjects from "../components/ManageSubjects.vue";
import ManageUsers from "../components/ManageUsers.vue";


import HomeView from "../components/HomeView.vue";

const routes = [
    // Public routes
    { path: "/", component: HomeView },
    { path: "/register", component: Register },
    { path: "/login", component: Login },

    // User routes
    {
        path: "/dashboard",
        component: Dashboard,
        meta: { requiresAuth: true, role: "user" },
    },
    {
        path: "/quiz/:id",
        component: QuizView,
        meta: { requiresAuth: true, role: "user" },
    },
    {
        path: "/summary",
        component: Summary,
        meta: { requiresAuth: true, role: "user" },
    },
    {
        path: "/quizlist",
        component: QuizList,
        meta: { requiresAuth: true, role: "user" },
    },

    // Admin routes
{
    path: "/admin",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
},
{
    path: "/admin/summary",
    component: AdminSummary,
    meta: { requiresAuth: true, role: "admin" },
},
{
    path: "/admin/chapters",
    component: ManageChapters,
    meta: { requiresAuth: true, role: "admin" },
},
{
    path: "/admin/questions",
    component: ManageQuestions,
    meta: { requiresAuth: true, role: "admin" },
},
{
    path: "/admin/quizzes",
    component: ManageQuizzes,
    meta: { requiresAuth: true, role: "admin" },
},
{
    path: "/admin/subjects",
    component: ManageSubjects,
    meta: { requiresAuth: true, role: "admin" },
},
{
    path: "/admin/users",
    component: ManageUsers,
    meta: { requiresAuth: true, role: "admin" },
},



    // Catch-all fallback
    { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Navigation Guard
router.beforeEach(async (to, from, next) => {
    const publicRoutes = ["/", "/register", "/login"];
    if (publicRoutes.includes(to.path)) return next();

    const token = localStorage.getItem("token");
    if (!token) return next("/");

    try {
        const res = await fetch("http://localhost:5000/me", {
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Unauthorized");

        const user = await res.json();
        const roles = user.roles || [];

        // Role-based redirection
        if (to.meta.role === "admin" && !roles.includes("admin")) return next("/");
        if (to.meta.role === "user" && roles.includes("admin")) return next("/admin");

        next();
    } catch (err) {
        localStorage.removeItem("token");
        next("/");
    }
});

export default router;
