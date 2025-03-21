// Progress tracking
function updateProgress(element, value, total) {
    const radius = 20;
    const circumference = radius * 2 * Math.PI;
    const progress = value / total;
    const dashoffset = circumference * (1 - progress);
    element.style.strokeDashoffset = dashoffset;
}

// Interactive code editor
function initCodeEditor(elementId) {
    if (document.getElementById(elementId)) {
        const editor = CodeMirror.fromTextArea(document.getElementById(elementId), {
            lineNumbers: true,
            mode: "javascript",
            theme: "monokai",
            autoCloseBrackets: true,
            matchBrackets: true,
            lineWrapping: true
        });
        return editor;
    }
}

// Project search and filter
function filterProjects(query) {
    const projects = document.querySelectorAll('.project-card');
    projects.forEach(project => {
        const title = project.querySelector('.card-title').textContent.toLowerCase();
        const description = project.querySelector('.card-text').textContent.toLowerCase();
        const tags = project.querySelector('.project-tags').textContent.toLowerCase();
        
        if (title.includes(query) || description.includes(query) || tags.includes(query)) {
            project.style.display = 'block';
        } else {
            project.style.display = 'none';
        }
    });
}

// Notifications system
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.querySelector('.toast-container').appendChild(toast);
    new bootstrap.Toast(toast).show();
}

// Dark mode with local storage
function initDarkMode() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    document.documentElement.setAttribute('data-bs-theme', darkMode ? 'dark' : 'light');
    updateDarkModeButton(darkMode);
}

function toggleDarkMode() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    document.documentElement.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('darkMode', !isDark);
    updateDarkModeButton(!isDark);
}

function updateDarkModeButton(isDark) {
    const button = document.getElementById('darkModeToggle');
    if (button) {
        button.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
}

// Enhanced Toast Notifications
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
                <i class="fas fa-${type === 'success' ? 'check-circle' : 
                                 type === 'error' ? 'exclamation-circle' : 
                                 'info-circle'} ms-2"></i>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    toast.style.transform = 'translateY(0)';
    
    setTimeout(() => {
        toast.style.transform = 'translateY(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Progress bar
const progressBar = document.createElement('div');
progressBar.className = 'scroll-progress-bar';
document.body.appendChild(progressBar);

window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progressBar.style.width = scrolled + '%';
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey) {
        switch(e.key) {
            case '/':
                e.preventDefault();
                document.querySelector('.search-form input').focus();
                break;
            case 'd':
                e.preventDefault();
                document.getElementById('darkModeToggle').click();
                break;
        }
    }
});

// Scroll to top button
const scrollTopBtn = document.createElement('button');
scrollTopBtn.className = 'scroll-top-btn';
scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
document.body.appendChild(scrollTopBtn);

scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
        scrollTopBtn.classList.add('show');
    } else {
        scrollTopBtn.classList.remove('show');
    }
});

// Lazy Loading Images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
});

// Enhanced Comment System
function initializeCommentSystem() {
    const commentForms = document.querySelectorAll('.comment-form');
    
    commentForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                appendComment(data.comment);
                form.reset();
                showToast('Comment added successfully!', 'success');
            } else {
                showToast('Error adding comment', 'error');
            }
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initDarkMode();
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    
    // Add animation classes
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('animate-fade-in');
    });

    initializeCommentSystem();
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });
});

// Theme Toggle with Animation
const themeToggle = document.getElementById('darkModeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        document.documentElement.setAttribute('data-theme-switching', 'true');
        setTimeout(() => {
            toggleDarkMode();
            document.documentElement.removeAttribute('data-theme-switching');
        }, 300);
    });
}

// Smooth Scroll Implementation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
