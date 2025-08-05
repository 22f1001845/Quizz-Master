<template>
    <div class="admin-summary container py-5">
        <h2 class="fw-bold text-primary mb-4 text-center">
            📊 Summary & Reports
        </h2>

        <div class="row text-center mb-4">
            <div class="col-md-4 mb-3">
                <div class="card summary-card shadow border-0">
                    <div class="card-body">
                        <h5 class="fw-bold">📚 Subjects</h5>
                        <p class="display-5 text-primary">
                            {{ summary.subjects }}
                        </p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card summary-card shadow border-0">
                    <div class="card-body">
                        <h5 class="fw-bold">📝 Quizzes</h5>
                        <p class="display-5 text-success">
                            {{ summary.quizzes }}
                        </p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card summary-card shadow border-0">
                    <div class="card-body">
                        <h5 class="fw-bold">👥 Users</h5>
                        <p class="display-5 text-warning">
                            {{ summary.users }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <AdminCharts
            v-if="chartData.quizData && chartData.scoreData"
            :quizData="chartData.quizData"
            :scoreData="chartData.scoreData"
        />

        <div class="action-buttons mt-4 text-center">
            <button
                class="btn btn-secondary me-2"
                @click="$router.push('/admin')"
            >
                🔙 Back to Dashboard
            </button>
            <button
                class="btn btn-primary me-2"
                @click="triggerDailyReminder"
            >
                📩 Send Daily Reminder
            </button>
            <button
                class="btn btn-success me-2"
                @click="triggerMonthlyReport"
            >
                📊 Send Monthly Report
            </button>
            <button
                class="btn btn-info"
                @click="exportCSV"
            >
                📥 Export CSV
            </button>
        </div>

        <div
            v-if="statusMessage"
            class="alert alert-info mt-4 text-center"
        >
            {{ statusMessage }}
        </div>
    </div>
</template>

<script>
import AdminCharts from "./AdminCharts.vue";

export default {
    name: "AdminSummary",
    components: { AdminCharts },
    data() {
        return {
            summary: { subjects: 0, quizzes: 0, users: 0 },
            chartData: {},
            statusMessage: "",
        };
    },
    methods: {
        async fetchSummary() {
            const token = localStorage.getItem("token");
            try {
                const res = await fetch("http://localhost:5000/admin/summary", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                this.summary = await res.json();
            } catch (err) {
                console.error("Failed to fetch summary", err);
            }
        },
        async fetchChartData() {
            const token = localStorage.getItem("token");
            try {
                const res = await fetch(
                    "http://localhost:5000/admin/chart-data",
                    {
                        headers: { Authorization: `Bearer ${token}` },
                    }
                );
                this.chartData = await res.json();
            } catch (err) {
                console.error("Failed to fetch chart data", err);
            }
        },
        async triggerDailyReminder() {
            this.statusMessage = "Sending daily reminders...";
            await fetch("http://localhost:5000/trigger-daily-reminder", {
                method: "POST",
            });
            this.statusMessage = "✅ Daily reminders sent successfully!";
            setTimeout(() => (this.statusMessage = ""), 3000);
        },
        async triggerMonthlyReport() {
            this.statusMessage = "Generating and sending monthly report...";
            await fetch("http://localhost:5000/trigger-monthly-report", {
                method: "POST",
            });
            this.statusMessage = "✅ Monthly report sent successfully!";
            setTimeout(() => (this.statusMessage = ""), 3000);
        },
        async exportCSV() {
            this.statusMessage = "Generating CSV report...";
            const token = localStorage.getItem("token");
            const res = await fetch(
                "http://localhost:5000/admin/export-users-csv",
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            const data = await res.json();
            const taskId = data.task_id;

            const interval = setInterval(async () => {
                const check = await fetch(
                    `http://localhost:5000/download/${taskId}`
                );
                if (check.status === 200) {
                    const blob = await check.blob();
                    if (blob.type === "text/csv") {
                        clearInterval(interval);
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "users_report.csv";
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        this.statusMessage = "✅ CSV Downloaded!";
                        setTimeout(() => (this.statusMessage = ""), 3000);
                    }
                }
            }, 2000);
        },
    },
    mounted() {
        this.fetchSummary();
        this.fetchChartData();
    },
};
</script>

<style scoped>
.admin-summary {
    max-width: 1200px;
    margin: auto;
    padding: 25px;
    background: linear-gradient(135deg, #f9f9ff, #e3f2fd);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
}

/* Cards */
.summary-card {
    border-radius: 14px;
    background: linear-gradient(135deg, #ffffff, #f1f1f1);
    transition: all 0.3s ease;
}
.summary-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* Buttons */
.action-buttons .btn {
    font-weight: 600;
    padding: 10px 18px;
    border-radius: 8px;
    transition: 0.3s;
}
.action-buttons .btn:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
</style>
