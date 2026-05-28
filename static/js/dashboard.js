// static/js/dashboard.js
// Dashboard Functionality with Chart.js

document.addEventListener('DOMContentLoaded', () => {
    initDashboardCharts();
    initTableSearch();
});

// Initialize All Charts
function initDashboardCharts() {
    // Growth Chart
    const growthCtx = document.getElementById('growthChart');
    if (growthCtx) {
        new Chart(growthCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Total Students',
                    data: [980, 1050, 1120, 1180, 1210, 1248],
                    borderColor: '#00f5ff',
                    backgroundColor: 'rgba(0, 245, 255, 0.1)',
                    tension: 0.4,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.1)' } },
                    x: { grid: { color: 'rgba(255,255,255,0.1)' } }
                }
            }
        });
    }

    // Attendance Trend Chart (for analytics.html)
    const attendanceCtx = document.getElementById('attendanceChart');
    if (attendanceCtx) {
        fetch('/api/attendance_trend')
            .then(response => response.json())
            .then(data => {
                new Chart(attendanceCtx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Attendance %',
                            data: data.attendance,
                            borderColor: '#00f5ff',
                            backgroundColor: 'rgba(0, 245, 255, 0.16)',
                            tension: 0.35,
                            borderWidth: 3,
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                grid: { color: 'rgba(255,255,255,0.1)' }
                            },
                            x: { grid: { color: 'rgba(255,255,255,0.1)' } }
                        }
                    }
                });
            })
            .catch(console.error);
    }

    // Marks Performance Chart (for marks.html)
    const marksCtx = document.getElementById('marksChart');
    if (marksCtx) {
        new Chart(marksCtx, {
            type: 'bar',
            data: {
                labels: ['Math', 'Physics', 'Chemistry', 'English', 'CS'],
                datasets: [{
                    label: 'Average Score',
                    data: [85, 78, 92, 88, 95],
                    backgroundColor: '#7209b7',
                    borderRadius: 8
                }]
            },
            options: { responsive: true }
        });
    }
}

// Live Search Filter for Tables
function initTableSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    searchInput.addEventListener('keyup', filterTable);
}

function filterTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toUpperCase();
    const table = document.querySelector('.glass-table');
    if (!table) return;
    
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const text = row.textContent || row.innerText;
        row.style.display = text.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    }
}

// Make functions globally available
window.filterTable = filterTable;