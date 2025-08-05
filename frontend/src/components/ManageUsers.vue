<template>
  <div>
    <h4 class="fw-bold mb-3">👥 All Users</h4>

    <!-- Loader -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary"></div>
    </div>

    <!-- Users Table -->
    <table v-else-if="users.length" class="table table-striped">
      <thead>
        <tr>
          <th>#</th>
          <th>Username</th>
          <th>Full Name</th>
          <th>Email</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, index) in users" :key="user.id">
          <td>{{ index + 1 }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.fullname }}</td>
          <td>{{ user.email }}</td>
        </tr>
      </tbody>
    </table>

    <!-- No Users -->
    <div v-else class="alert alert-warning text-center">
      No users found.
    </div>
  </div>
</template>

<script>
export default {
  name: "ManageUsers",
  data() {
    return {
      users: [],
      loading: true,
    };
  },
  async mounted() {
    console.log("Fetching users...");
    const token = localStorage.getItem("token");
    try {
      const res = await fetch("http://localhost:5000/admin/users", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        console.error("Failed to fetch users. Status:", res.status);
        return;
      }

      const data = await res.json();
      console.log("Users data received:", data);
      this.users = data;
    } catch (err) {
      console.error("Error fetching users", err);
    } finally {
      this.loading = false;
    }
  },
};
</script>
