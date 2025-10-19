function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('stat-version').textContent = data.version.toUpperCase();
            document.getElementById('stat-requests').textContent = data.requests;
            document.getElementById('stat-response').textContent = data.response_time;
            document.getElementById('stat-status').textContent = data.uptime;
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    setInterval(updateStats, 5000);
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
