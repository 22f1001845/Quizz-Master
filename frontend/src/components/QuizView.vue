// src/components/QuizView.vue
<template>
    <div class="container my-5">
        <h3 class="mb-4 text-center text-primary fw-bold">📝 Quiz Attempt</h3>

        <div
            v-if="!quizStarted && !result"
            class="text-center"
        >
            <button
                class="btn btn-primary btn-lg"
                @click="startQuiz"
            >
                ▶️ Start Quiz
            </button>
        </div>

        <div
            v-if="quizStarted && !result"
            class="text-end text-danger fw-bold fs-5"
        >
            ⏱️ Time Left: {{ minutes }}:{{
                seconds.toString().padStart(2, "0")
            }}
        </div>

        <form
            v-if="quizStarted && !result"
            @submit.prevent="submitQuiz"
        >
            <div
                v-for="(q, index) in questions"
                :key="q.id"
                class="mb-4 card p-4 shadow-sm question-card"
            >
                <p class="fw-semibold">
                    Q{{ index + 1 }}. {{ q.question_statement }}
                </p>

                <div
                    class="form-check my-2"
                    v-for="opt in 4"
                    :key="`q${q.id}-opt${opt}`"
                >
                    <input
                        class="form-check-input"
                        type="radio"
                        :name="q.id"
                        :value="opt"
                        v-model="answers[q.id]"
                        :id="`q${q.id}-opt${opt}`"
                    />
                    <label
                        class="form-check-label"
                        :for="`q${q.id}-opt${opt}`"
                    >
                        {{ q[`option${opt}`] }}
                    </label>
                </div>
            </div>

            <div class="text-center">
                <button class="btn btn-success btn-lg px-4">
                    ✅ Submit Quiz
                </button>
            </div>
        </form>

        <div
            v-if="result !== null"
            class="alert alert-info mt-5 text-center p-4"
        >
            <h4 class="fw-bold">🎉 Quiz Submitted Successfully!</h4>
            <p class="fs-5">
                Your Score: <strong>{{ result }}%</strong>
            </p>
            <router-link
                class="btn btn-outline-primary mt-3"
                to="/summary"
            >
                📊 View All Results
            </router-link>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: "QuizView",
    data() {
        return {
            questions: [],
            answers: {},
            result: null,
            quizStarted: false,
            timeLeft: 0,
            timerInterval: null,
        };
    },
    computed: {
        minutes() {
            return Math.floor(this.timeLeft / 60);
        },
        seconds() {
            return this.timeLeft % 60;
        },
    },
    methods: {
        async startQuiz() {
            this.quizStarted = true;
            this.startTimer();
        },
        startTimer() {
            this.timerInterval = setInterval(() => {
                if (this.timeLeft > 0) {
                    this.timeLeft--;
                } else {
                    clearInterval(this.timerInterval);
                    this.submitQuiz(); // auto submit on time end
                }
            }, 1000);
        },
        async submitQuiz() {
            clearInterval(this.timerInterval);
            const quizId = this.$route.params.id;
            const token = localStorage.getItem("token");

            try {
                const res = await axios.post(
                    `http://localhost:5000/quiz/${quizId}/submit`,
                    this.answers,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                this.result = res.data.score;
            } catch (err) {
                console.error("Submit error:", err);
            }
        },
    },
    async mounted() {
        const quizId = this.$route.params.id;
        const token = localStorage.getItem("token");
        try {
            const res = await axios.get(
                `http://localhost:5000/quiz/${quizId}/questions`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            this.questions = res.data.questions;
            this.timeLeft = res.data.duration_of_quiz;
        } catch (err) {
            console.error("Error loading quiz:", err);
        }
    },
};
</script>

<style scoped>
.question-card {
    border-radius: 12px;
    transition: 0.3s;
}
.question-card:hover {
    background-color: #f9f9f9;
}
.form-check-label {
    font-weight: 500;
}
</style>