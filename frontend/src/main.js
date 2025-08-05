import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'

// Set token globally if it exists
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] =`Bearer ${token}` 
}

const app = createApp(App)
app.use(router)
app.mount('#app')
