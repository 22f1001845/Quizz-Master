<template>
    <div
        class="container d-flex flex-column justify-content-center align-items-center min-vh-100"
    >
        <div
            class="card shadow p-4 w-100"
            style="max-width: 400px"
        >
            <h3 class="text-center mb-4 text-primary fw-bold">
                {{ role === "admin" ? "👑 Admin Login" : "🙋 User Login" }}
            </h3>

            <div class="mb-3">
                <label for="email">Email</label>
                <input
                    id="email"
                    type="email"
                    class="form-control"
                    v-model="email"
                    placeholder="Enter email"
                />
            </div>

            <div class="mb-3">
                <label for="password">Password</label>
                <input
                    id="password"
                    type="password"
                    class="form-control"
                    v-model="password"
                    placeholder="Enter password"
                />
            </div>

            <div class="d-grid mb-2">
                <button
                    class="btn btn-primary"
                    :disabled="loading"
                    @click="login"
                >
                    {{ loading ? "Logging in..." : "Login" }}
                </button>
            </div>

            <div
                class="text-center mt-2"
                v-if="role !== 'admin'"
            >
                <p class="text-secondary">
                    Don't have an account?
                    <router-link to="/register">Register here</router-link>
                </p>
            </div>

            <div
                v-if="error"
                class="alert alert-danger mt-3"
                role="alert"
            >
                {{ error }}
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: "Login",
    data() {
        return {
            email: "",
            password: "",
            error: "",
            role: "user",
        };
    },
    created() {
        this.role = this.$route.query.role || "user";
    },
    methods: {
        async login() {
            this.error = "";
            this.loading = true;

            if (!this.email || !this.password) {
                this.error = "Please fill in all fields";
                this.loading = false;
                return;
            }

            try {
                const response = await axios.post(
                    "http://localhost:5000/login_main",
                    {
                        email: this.email,
                        password: this.password,
                    }
                );

                const token = response.data.token;
                localStorage.setItem("token", token);

                // Set token globally for all future axios requests
                axios.defaults.headers.common[
                    "Authorization"
                ] = `Bearer ${token}`;

                console.log(
                    "Authorization header set:",
                    axios.defaults.headers.common["Authorization"]
                );

                // Fetch user info
                const me = await axios.get("http://localhost:5000/me", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                const roles = me.data.roles;

                if (roles.includes("admin")) {
                    this.$router.push("/admin");
                } else {
                    this.$router.push("/dashboard");
                }
            } catch (err) {
                this.error =
                    err.response?.data?.message || "Login failed. Try again.";
            } finally {
                this.loading = false;
            }
        },
    },
};
</script>

<style scoped>
.card {
    border-radius: 12px;
}
input.form-control {
    padding: 10px;
}
.btn {
    font-size: 1.05rem;
    padding: 10px;
}
</style>
