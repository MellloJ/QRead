const toggleBtn = document.getElementById('toggleBtn');
const sidebar = document.getElementById('sidebar');
const content = document.getElementById('content');

toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    content.classList.toggle('collapsed');
    toggleBtn.classList.toggle('collapsed');
});