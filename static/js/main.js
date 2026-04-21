/* ═══════════════════════════════════════
   QuoteVerse — Main JavaScript
   Handles: Theme, Nav, Infinite Scroll,
   Like/Fav, Copy, Share, Toasts, Comments
   ═══════════════════════════════════════ */

// ── THEME TOGGLE ─────────────────────────────────────────────────
const THEME_KEY = 'qv_theme';
const html = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
    localStorage.setItem(THEME_KEY, theme);
}

// Init theme
applyTheme(localStorage.getItem(THEME_KEY) || 'dark');

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = html.getAttribute('data-theme');
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });
}

// ── HAMBURGER MENU ────────────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        const spans = hamburger.querySelectorAll('span');
        const isOpen = navLinks.classList.contains('open');
        spans[0].style.transform = isOpen ? 'rotate(45deg) translate(5px,5px)' : '';
        spans[1].style.opacity = isOpen ? '0' : '';
        spans[2].style.transform = isOpen ? 'rotate(-45deg) translate(5px,-5px)' : '';
    });
    document.addEventListener('click', (e) => {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('open');
        }
    });
}

// ── NAVBAR SCROLL EFFECT ──────────────────────────────────────────
window.addEventListener('scroll', () => {
    const nb = document.getElementById('navbar');
    if (nb) {
        nb.style.background = window.scrollY > 20
            ? 'rgba(10,10,15,0.97)'
            : 'rgba(10,10,15,0.85)';
    }
}, { passive: true });

// ── TOAST SYSTEM ──────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer') || createToastContainer();
    const icons = { success: 'check-circle', danger: 'exclamation-circle', info: 'info-circle', warning: 'exclamation-triangle' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${icons[type] || 'info-circle'}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

function createToastContainer() {
    const c = document.createElement('div');
    c.id = 'toastContainer';
    c.className = 'toast-container';
    document.body.appendChild(c);
    return c;
}

// Auto-close flash toasts
document.querySelectorAll('.toast[data-auto-close]').forEach(toast => {
    const delay = parseInt(toast.dataset.autoClose) || 4000;
    setTimeout(() => toast.remove(), delay);
});

// ── LIKE SYSTEM ───────────────────────────────────────────────────
function toggleLike(quoteId, btn) {
    fetch(`/api/like/${quoteId}`, { method: 'POST' })
        .then(r => {
            if (r.status === 401) {
                showToast('Please login to like quotes ❤️', 'info');
                return null;
            }
            return r.json();
        })
        .then(data => {
            if (!data) return;
            btn.classList.toggle('liked', data.liked);
            const countEl = btn.querySelector('.like-count');
            if (countEl) countEl.textContent = data.count;
            if (data.liked) {
                showToast('Liked! ❤️', 'success');
                // Animate
                btn.style.transform = 'scale(1.2)';
                setTimeout(() => btn.style.transform = '', 200);
            }
        });
}

// ── FAVORITE SYSTEM ───────────────────────────────────────────────
function toggleFavorite(quoteId, btn) {
    fetch(`/api/favorite/${quoteId}`, { method: 'POST' })
        .then(r => {
            if (r.status === 401) {
                showToast('Please login to save favorites ⭐', 'info');
                return null;
            }
            return r.json();
        })
        .then(data => {
            if (!data) return;
            btn.classList.toggle('saved', data.favorited);
            showToast(data.favorited ? 'Saved to favorites! ⭐' : 'Removed from favorites.', 'success');
        });
}

// ── COPY QUOTE ────────────────────────────────────────────────────
function copyQuote(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Quote copied to clipboard! 📋', 'success');
        if (btn) {
            const original = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => btn.innerHTML = original, 1500);
        }
    }).catch(() => {
        // Fallback
        const el = document.createElement('textarea');
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        showToast('Copied! 📋', 'success');
    });
}

// Copy Instagram caption
function copyCaption(quoteText) {
    const caption = `✨ "${quoteText}" ✨\n\n📌 Save this for the days you need it most.\n💬 Tag someone who needs to see this!\n\n#motivation #quotes #inspiration #mindset #growth`;
    navigator.clipboard.writeText(caption).then(() => {
        showToast('Instagram caption copied! 📸', 'success');
    });
}

// ── COMMENT MODAL ─────────────────────────────────────────────────
let currentCommentQuoteId = null;

function openCommentModal(quoteId) {
    currentCommentQuoteId = quoteId;
    const overlay = document.getElementById('commentModalOverlay');
    const list = document.getElementById('commentList');
    if (!overlay) return;

    list.innerHTML = '<div class="spinner" style="margin:2rem auto;"></div>';
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    fetch(`/api/comment/${quoteId}`, {
        method: 'GET',
        headers: { 'X-Fetch-Comments': '1' }
    }).catch(() => {
        // If endpoint doesn't support GET, show message
        list.innerHTML = '<p class="no-comments">Comments available on the quote page.</p>';
    });
}

function closeCommentModal() {
    const overlay = document.getElementById('commentModalOverlay');
    if (overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function submitComment() {
    if (!currentCommentQuoteId) return;
    const input = document.getElementById('commentInput');
    const text = input.value.trim();
    if (!text) return;

    fetch(`/api/comment/${currentCommentQuoteId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    }).then(r => {
        if (r.status === 401) { showToast('Please login to comment.', 'info'); return null; }
        return r.json();
    }).then(data => {
        if (!data || data.error) return;
        const list = document.getElementById('commentList');
        const noComments = list.querySelector('.no-comments');
        if (noComments) noComments.remove();
        const div = document.createElement('div');
        div.className = 'comment-item';
        div.innerHTML = `
            <div class="comment-avatar">${data.username[0].toUpperCase()}</div>
            <div class="comment-body">
                <strong>${data.username}</strong>
                <span class="comment-date">Just now</span>
                <p>${data.text}</p>
            </div>`;
        list.prepend(div);
        input.value = '';
        showToast('Comment posted! 💬', 'success');
    });
}

// ── IMAGE MODAL ────────────────────────────────────────────────────
function openImageModal(text, author) {
    const overlay = document.getElementById('imageModalOverlay');
    if (!overlay) return;
    document.getElementById('posterText').textContent = `"${text}"`;
    document.getElementById('posterAuthor').textContent = `— ${author}`;
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    const overlay = document.getElementById('imageModalOverlay');
    if (overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close modals on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});

// ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay').forEach(o => {
            o.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
});

// ── INFINITE SCROLL ────────────────────────────────────────────────
const trigger = document.getElementById('infiniteScrollTrigger');
let isLoading = false;

if (trigger && trigger.dataset.hasNext === 'true') {
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !isLoading && trigger.dataset.hasNext === 'true') {
            loadMoreQuotes();
        }
    }, { threshold: 0.1, rootMargin: '200px' });
    observer.observe(trigger);
}

const CATEGORY_COLORS = {
    'Success':'#f59e0b','Study':'#3b82f6','Gym':'#ef4444','Love':'#ec4899',
    'Breakup':'#8b5cf6','Money':'#10b981','Discipline':'#f97316','Life':'#06b6d4',
    'Mindset':'#6366f1','Hinglish':'#84cc16'
};
const CATEGORY_ICONS = {
    'Success':'🏆','Study':'📚','Gym':'💪','Love':'❤️','Breakup':'💔',
    'Money':'💰','Discipline':'🎯','Life':'🌱','Mindset':'🧠','Hinglish':'🇮🇳'
};

function loadMoreQuotes() {
    const grid = document.getElementById('quoteGrid');
    const loadIndicator = document.getElementById('loadIndicator');
    if (!grid || !trigger) return;

    isLoading = true;
    if (loadIndicator) loadIndicator.style.display = 'flex';

    const page = trigger.dataset.page;
    const category = trigger.dataset.category;
    const url = `/api/quotes?page=${page}${category ? `&category=${category}` : ''}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            data.quotes.forEach(q => {
                const color = CATEGORY_COLORS[q.category] || '#6366f1';
                const icon = CATEGORY_ICONS[q.category] || '📝';
                const card = document.createElement('div');
                card.className = 'quote-card';
                card.dataset.id = q.id;
                card.style.cssText = `--card-color: ${color}`;
                card.innerHTML = `
                    <div class="card-glow"></div>
                    <div class="card-header">
                        <span class="category-badge" style="background:${color}22;color:${color};border-color:${color}44">
                            ${icon} ${q.category}
                        </span>
                        <span class="quote-views"><i class="fas fa-eye"></i> ${q.views}</span>
                    </div>
                    <blockquote class="quote-text">${q.text}</blockquote>
                    <div class="quote-author">— ${q.author}</div>
                    <div class="card-actions">
                        <button class="action-btn like-btn ${q.liked ? 'liked' : ''}" onclick="toggleLike(${q.id}, this)">
                            <i class="fas fa-heart"></i><span class="like-count">${q.likes_count}</span>
                        </button>
                        <button class="action-btn save-btn ${q.favorited ? 'saved' : ''}" onclick="toggleFavorite(${q.id}, this)">
                            <i class="fas fa-star"></i>
                        </button>
                        <button class="action-btn comment-btn" onclick="openCommentModal(${q.id})">
                            <i class="fas fa-comment"></i> <span>${q.comments_count}</span>
                        </button>
                        <button class="action-btn copy-btn" onclick="copyQuote('${q.text.replace(/'/g, "\\'")}', this)">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="action-btn download-btn" onclick="openImageModal('${q.text.replace(/'/g, "\\'")}', '${q.author}')">
                            <i class="fas fa-image"></i>
                        </button>
                        <div class="share-dropdown">
                            <button class="action-btn share-btn"><i class="fas fa-share-alt"></i></button>
                            <div class="share-menu">
                                <a href="https://wa.me/?text=${encodeURIComponent(q.text + ' — ' + q.author)}" target="_blank" class="share-item whatsapp"><i class="fab fa-whatsapp"></i> WhatsApp</a>
                                <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(q.text)}&hashtags=QuoteVerse" target="_blank" class="share-item twitter"><i class="fab fa-x-twitter"></i> Twitter/X</a>
                                <button class="share-item instagram" onclick="copyCaption('${q.text.replace(/'/g, "\\'")}')"><i class="fab fa-instagram"></i> Copy Caption</button>
                            </div>
                        </div>
                    </div>`;
                grid.appendChild(card);
            });

            trigger.dataset.hasNext = data.has_next ? 'true' : 'false';
            trigger.dataset.page = data.next_page || '';

            if (!data.has_next && loadIndicator) {
                loadIndicator.innerHTML = '<span style="color:var(--text-muted)">✨ You\'ve seen all quotes!</span>';
                loadIndicator.style.display = 'flex';
            } else if (loadIndicator) {
                loadIndicator.style.display = 'none';
            }
        })
        .finally(() => { isLoading = false; });
}

// ── SWIPE GESTURE (Mobile) ─────────────────────────────────────────
let touchStartY = 0;
document.addEventListener('touchstart', e => { touchStartY = e.touches[0].clientY; }, { passive: true });
document.addEventListener('touchend', e => {
    const delta = touchStartY - e.changedTouches[0].clientY;
    if (delta > 60 && !isLoading) {
        const trigger = document.getElementById('infiniteScrollTrigger');
        if (trigger && trigger.dataset.hasNext === 'true') loadMoreQuotes();
    }
}, { passive: true });

// ── STREAK TRACKING ────────────────────────────────────────────────
(function checkStreak() {
    const today = new Date().toDateString();
    const lastVisit = localStorage.getItem('qv_last_visit');
    if (lastVisit !== today) {
        localStorage.setItem('qv_last_visit', today);
    }
})();
