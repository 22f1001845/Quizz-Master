<template>
  <div class="home-container my-5">
    <!-- Hero Section -->
    <div class="hero-section text-center mb-5">
      <img
        src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
        alt="Quiz Banner"
        class="hero-image mb-4"
      />
      <h1 class="fw-bold text-primary">🎓 Welcome to Quiz Master</h1>
      <p class="lead text-muted">
        The ultimate platform to challenge your knowledge and boost learning!
      </p>
    </div>

    <!-- Action Cards -->
    <div class="row justify-content-center g-4">
      <!-- Login Card -->
      <div class="col-md-4">
        <div class="card action-card border-0 shadow-lg h-100">
          <div class="card-body d-flex flex-column justify-content-center">
            <h5 class="card-title text-primary fw-bold">🔐 Login</h5>
            <p class="card-text mb-3">
              Access your personalized dashboard and take quizzes.
            </p>
            <router-link to="/login" class="btn btn-primary w-100">
              Login Here
            </router-link>
          </div>
        </div>
      </div>

      <!-- Register Card -->
      <div class="col-md-4">
        <div class="card action-card border-0 shadow-lg h-100">
          <div class="card-body d-flex flex-column justify-content-center">
            <h5 class="card-title text-info fw-bold">🆕 New Here?</h5>
            <p class="card-text mb-3">
              Join our platform today and start attempting quizzes!
            </p>
            <router-link to="/register" class="btn btn-outline-info w-100">
              Register Now
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Home",
};
</script>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: auto;
  padding: 20px;
}

/* Hero Section */
.hero-section {
  padding: 20px;
}
.hero-image {
  width: 120px;
  height: 120px;
  object-fit: contain;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* Cards */
.action-card {
  border-radius: 14px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: #ffffff;
}
.action-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
.card-title {
  font-size: 1.4rem;
}
.card-text {
  font-size: 1rem;
  color: #495057;
}

/* Buttons */
.btn {
  font-weight: 600;
  border-radius: 10px;
  padding: 10px;
  transition: all 0.3s ease;
}
.btn:hover {
  transform: scale(1.05);
}
</style>
