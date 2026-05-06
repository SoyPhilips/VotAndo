const app = {
    currentUser: null,
    currentView: 'hero-view',

    init() {
        this.bindEvents();
        this.checkAuth();
        this.loadTheme();
        this.showView('hero-view');
    },

    bindEvents() {
        // Navigation
        document.getElementById('nav-home').onclick = () => this.showView('hero-view');
        document.getElementById('nav-proposals').onclick = () => this.showView('proposals-view');
        document.getElementById('nav-admin').onclick = () => this.showView('admin-view');
        document.getElementById('btn-login-view').onclick = () => this.showView('login-view');
        document.getElementById('btn-register-view').onclick = () => this.showView('register-view');
        document.getElementById('btn-logout').onclick = () => this.logout();
        document.getElementById('user-email').onclick = () => this.showView('profile-view');
        document.getElementById('theme-toggle').onclick = () => this.toggleTheme();

        // Forms
        document.getElementById('login-form').onsubmit = (e) => this.handleLogin(e);
        document.getElementById('register-form').onsubmit = (e) => this.handleRegister(e);
        document.getElementById('create-proposal-form').onsubmit = (e) => this.handleCreateProposal(e);
        document.getElementById('request-creator-form').onsubmit = (e) => this.handleRequestCreator(e);
        document.getElementById('btn-delete-account').onclick = () => this.confirmDeleteAccount();

        // Links
        document.getElementById('link-to-register').onclick = () => this.showView('register-view');
        document.getElementById('link-to-login').onclick = () => this.showView('login-view');
    },

    checkAuth() {
        const user = localStorage.getItem('user');
        if (user) {
            this.currentUser = JSON.parse(user);
            this.updateAuthUI();
        }
    },

    updateAuthUI() {
        const authLinks = document.getElementById('auth-links');
        const userMenu = document.getElementById('user-menu');
        const userEmail = document.getElementById('user-email');
        const navAdmin = document.getElementById('nav-admin');

        if (this.currentUser) {
            authLinks.classList.add('hidden');
            userMenu.classList.remove('hidden');
            userEmail.textContent = this.currentUser.email;
            if (this.currentUser.is_admin) {
                navAdmin.classList.remove('hidden');
            } else {
                navAdmin.classList.add('hidden');
            }
        } else {
            authLinks.classList.remove('hidden');
            userMenu.classList.add('hidden');
            navAdmin.classList.add('hidden');
        }
    },

    showView(viewId) {
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        document.getElementById(viewId).classList.remove('hidden');
        this.currentView = viewId;

        if (viewId === 'proposals-view') this.loadProposals();
        if (viewId === 'profile-view') this.loadProfile();
    },

    async loadProfile() {
        if (!this.currentUser) return;
        document.getElementById('profile-email').textContent = this.currentUser.email;
        
        try {
            const reqs = await API.getMyRequests();
            const statusContainer = document.getElementById('request-status-container');
            const statusBadge = document.getElementById('request-status-badge');
            const form = document.getElementById('request-creator-form');

            if (reqs.length > 0) {
                const latest = reqs[reqs.length - 1];
                statusContainer.classList.remove('hidden');
                statusBadge.textContent = latest.status.toUpperCase();
                statusBadge.className = `status-badge status-${latest.status}`;
                
                if (latest.status === 'pending' || latest.status === 'approved') {
                    form.classList.add('hidden');
                } else {
                    form.classList.remove('hidden');
                }
            } else {
                statusContainer.classList.add('hidden');
                form.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading profile requests:', error);
        }
    },

    async handleRequestCreator(e) {
        e.preventDefault();
        const reason = document.getElementById('request-reason').value;

        try {
            await API.submitProposalRequest(reason);
            this.showToast('Solicitud enviada con éxito', 'success');
            this.loadProfile();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const data = await API.login(email, password);
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            this.currentUser = data.user;
            this.updateAuthUI();
            this.showToast('¡Bienvenido!', 'success');
            this.showView('proposals-view');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    async handleRegister(e) {
        e.preventDefault();
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        try {
            await API.register(email, password);
            this.showToast('Registro exitoso. Ya puedes iniciar sesión.', 'success');
            this.showView('login-view');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    async loadProposals() {
        const grid = document.getElementById('proposals-grid');
        grid.innerHTML = '<p>Cargando propuestas...</p>';

        try {
            const proposals = await API.getProposals();
            grid.innerHTML = '';
            proposals.forEach(p => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <span class="card-category">${p.category}</span>
                    <h3 class="card-title">${p.title}</h3>
                    <p class="card-desc">${p.description}</p>
                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
                        Votos actuales: <strong>${p.vote_count}</strong>
                    </div>
                    <div class="card-footer">
                        <span class="status-badge ${p.status === 'active' ? 'status-active' : 'status-finished'}">${p.status === 'active' ? 'Activa' : 'Finalizada'}</span>
                        <button class="btn btn-primary" onclick="app.vote(${p.id}, '${p.title}')" ${p.status !== 'active' ? 'disabled' : ''}>Votar</button>
                    </div>
                `;
                grid.appendChild(card);
            });
        } catch (error) {
            grid.innerHTML = `<p style="color: var(--danger)">Error al cargar propuestas: ${error.message}</p>`;
        }
    },

    async vote(proposalId, title) {
        this.openModal(
            'Confirmar Voto',
            `¿Estás seguro de que quieres votar por la propuesta: "${title}"?`,
            async () => {
                try {
                    const res = await API.castVote(proposalId);
                    this.showToast('¡Voto registrado con éxito!', 'success');
                    this.closeModal();
                    this.loadProposals(); // Refresh
                } catch (error) {
                    this.showToast(error.message, 'error');
                    this.closeModal();
                }
            }
        );
    },

    async handleCreateProposal(e) {
        e.preventDefault();
        const data = {
            title: document.getElementById('prop-title').value,
            category: document.getElementById('prop-category').value,
            description: document.getElementById('prop-desc').value,
            start_date: document.getElementById('prop-start').value,
            end_date: document.getElementById('prop-end').value
        };

        try {
            await API.createProposal(data);
            this.showToast('Propuesta creada con éxito', 'success');
            e.target.reset();
            this.showView('proposals-view');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    async confirmDeleteAccount() {
        if (confirm('¿ESTÁS SEGURO? Esta acción es irreversible y eliminará todos tus datos.')) {
            try {
                await API.deleteAccount();
                this.logout();
                this.showToast('Tu cuenta ha sido eliminada.', 'success');
            } catch (error) {
                this.showToast(error.message, 'error');
            }
        }
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.currentUser = null;
        this.updateAuthUI();
        this.showView('hero-view');
        this.showToast('Sesión cerrada');
    },

    // UI Helpers
    showToast(msg, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMsg = document.getElementById('toast-msg');
        toastMsg.textContent = msg;
        toast.style.borderColor = type === 'error' ? 'var(--danger)' : (type === 'success' ? 'var(--success)' : 'var(--border)');
        toast.classList.remove('hidden');
        toast.style.transform = 'translateY(0)';
        
        setTimeout(() => {
            toast.style.transform = 'translateY(200%)';
            setTimeout(() => toast.classList.add('hidden'), 300);
        }, 3000);
    },

    openModal(title, body, onConfirm) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').textContent = body;
        const confirmBtn = document.getElementById('modal-confirm');
        confirmBtn.onclick = onConfirm;
        document.getElementById('modal').classList.remove('hidden');
    },

    closeModal() {
        document.getElementById('modal').classList.add('hidden');
    },

    toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    },

    loadTheme() {
        const saved = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', saved);
    }
};

window.onload = () => app.init();
