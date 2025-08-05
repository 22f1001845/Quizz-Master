<template>
  <div class="container d-flex flex-column justify-content-center align-items-center min-vh-100">
    <div class="card shadow p-4 w-100" style="max-width: 600px;">
      <h3 class="text-center mb-4 text-success fw-bold">🧾 User Registration</h3>

      <form @submit.prevent="register">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">Full Name</label>
            <input type="text" class="form-control" v-model="fullname" required />
          </div>

          <div class="col-md-6 mb-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" v-model="email" required />
          </div>

          <div class="col-md-6 mb-3">
            <label class="form-label">Password</label>
            <input type="password" class="form-control" v-model="password" required />
          </div>

          <div class="col-md-6 mb-3">
            <label class="form-label">Date of Birth</label>
            <input type="date" class="form-control" v-model="dob" required />
          </div>

          <div class="col-md-6 mb-3">
            <label class="form-label">Gender</label>
            <select class="form-select" v-model="gender" required>
              <option value="">Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>

          <div class="col-md-6 mb-3">
            <label class="form-label">Country</label>
            <input type="text" class="form-control" v-model="country" required />
          </div>

          <div class="col-md-12 mb-3">
            <label class="form-label">Qualification</label>
            <input type="text" class="form-control" v-model="qualification" required />
          </div>
        </div>

        <div class="d-grid mt-3">
          <button class="btn btn-success">✅ Register</button>
        </div>

        <div class="mt-3 text-center">
          <p class="text-secondary">
            Already have an account?
            <router-link to="/login" class="text-decoration-none">Login here</router-link>
          </p>
        </div>

        <div v-if="error" class="alert alert-danger mt-3" role="alert">
          {{ error }}
        </div>

        <div v-if="success" class="alert alert-success mt-3" role="alert">
          {{ success }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Register',
  data() {
    return {
      fullname: '',
      email: '',
      password: '',
      dob: '',
      gender: '',
      country: '',
      qualification: '',
      error: '',
      success: ''
    }
  },
  methods: {
    async register() {
      this.error = ''
      this.success = ''

      try {
        await axios.post('http://localhost:5000/register', {
          fullname: this.fullname,
          email: this.email,
          password: this.password,
          dob: this.dob,
          gender: this.gender,
          country: this.country,
          qualification: this.qualification
        })

        this.success = '🎉 Registration successful! Please login.'
        this.fullname = this.email = this.password = this.dob = this.gender = this.country = this.qualification = ''
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed. Try again.'
      }
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 12px;
}
.form-control,
.form-select {
  padding: 10px;
}
.btn {
  font-size: 1.05rem;
  padding: 10px;
}
</style>
