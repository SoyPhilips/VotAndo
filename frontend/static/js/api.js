const API = {
    baseUrl: '/api',

    async request(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        const headers = {
            'Content-Type': 'application/json',
            'X-Anon-Voter-ID': this.getAnonId(),
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Algo salió mal');
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    getAnonId() {
        let anonId = localStorage.getItem('anon_voter_id');
        if (!anonId) {
            anonId = 'anon_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('anon_voter_id', anonId);
        }
        return anonId;
    },

    // Auth
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    async register(email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    async deleteAccount() {
        return this.request('/auth/me', { method: 'DELETE' });
    },

    // Proposals
    async getProposals() {
        return this.request('/proposals');
    },

    async createProposal(proposalData) {
        return this.request('/proposals', {
            method: 'POST',
            body: JSON.stringify(proposalData)
        });
    },

    // Voting
    async castVote(proposalId) {
        return this.request('/vote', {
            method: 'POST',
            body: JSON.stringify({ proposal_id: proposalId })
        });
    },

    // Requests
    async submitProposalRequest(reason) {
        return this.request('/proposal-request', {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    },

    async getMyRequests() {
        return this.request('/my-requests');
    }
};
