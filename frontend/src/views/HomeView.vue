<template>
  <div class="container d-flex flex-column justify-content-center align-items-center min-vh-100">
    <div class="text-center border shadow p-5 rounded bg-light w-100" style="max-width: 500px;">
      <img src="@/assets/quiz-logo.png" alt="Quiz Master" class="logo mb-4" />
      <h1 class="mb-3 text-primary fw-bold">Welcome to Quiz Master</h1>
      <p class="lead text-secondary mb-4">Please select your role to continue</p>

      <div class="d-grid gap-3">
        <router-link to="/login" class="btn btn-outline-primary btn-lg">Login as User</router-link>
        <router-link to="/login" class="btn btn-outline-danger btn-lg">Login as Admin</router-link>
      </div>

      <div class="mt-4">
        <router-link to="/register" class="text-decoration-none">New here? <strong>Register Now</strong></router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserHome'
}
</script>

<style scoped>
.logo {
  width: 80px;
  height: 80px;
}
.btn-lg {
  font-size: 1.1rem;
  padding: 0.75rem;
  transition: 0.3s ease;
}
.btn-lg:hover {
  transform: scale(1.02);
}
</style>
