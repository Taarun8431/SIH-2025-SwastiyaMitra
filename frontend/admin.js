const API_BASE_URL = 'http://localhost:8000';
let adminToken = localStorage.getItem('adminToken');
let map = null;
let heatmapLayer = null;
let markersLayer = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (adminToken) {
        verifyTokenAndLoad();
    }
});

async function verifyTokenAndLoad() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.role === 'admin') {
                showDashboard();
            } else {
                logout();
            }
        } else {
            logout();
        }
    } catch (error) {
        console.error('Token verification failed:', error);
        logout();
    }
}

async function adminLogin() {
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;
    const status = document.getElementById('loginStatus');

    status.style.color = '#666';
    status.textContent = 'Authenticating...';

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            adminToken = data.access_token;
            localStorage.setItem('adminToken', adminToken);
            verifyTokenAndLoad();
        } else {
            status.style.color = 'var(--danger)';
            status.textContent = 'Invalid credentials';
        }
    } catch (error) {
        status.style.color = 'var(--danger)';
        status.textContent = 'Connection error';
    }
}

function showDashboard() {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('dashboardInterface').classList.remove('hidden');
    loadStats();
}

function logout() {
    localStorage.removeItem('adminToken');
    location.reload();
}

function switchTab(tabId, element) {
    // Update Nav
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if (element) element.classList.add('active');

    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));

    // Show selected
    document.getElementById(`${tabId}Tab`).classList.remove('hidden');

    // Special handling for map
    if (tabId === 'map') {
        setTimeout(() => {
            initMap();
        }, 100);
    } else if (tabId === 'users') {
        loadUsers();
    }
}

// --- Analytics & Stats ---

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/stats`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const data = await response.json();

            // Animate numbers
            animateValue('totalMigrants', 0, data.totals.migrants, 1000);
            animateValue('totalEncounters', 0, data.totals.encounters, 1000);

            const districtCount = Object.keys(data.by_district).length;
            animateValue('districtsCount', 0, districtCount, 1000);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// --- Map Integration ---

async function initMap() {
    if (map) {
        map.invalidateSize();
        return;
    }

    // Initialize map centered on Kerala
    map = L.map('map').setView([10.8505, 76.2711], 7);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Fetch migrant data for map
    try {
        const response = await fetch(`${API_BASE_URL}/migrant/`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const migrants = await response.json();
            renderMapData(migrants);
        }
    } catch (error) {
        console.error('Error loading map data:', error);
    }
}

function renderMapData(migrants) {
    // Create marker group
    markersLayer = L.layerGroup();

    migrants.forEach(migrant => {
        if (migrant.location_lat && migrant.location_lng) {
            const marker = L.circleMarker([migrant.location_lat, migrant.location_lng], {
                radius: 8,
                fillColor: "#4361ee",
                color: "#fff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            });

            marker.bindPopup(`
                <strong>${migrant.name}</strong><br>
                ID: ${migrant.id}<br>
                District: ${migrant.district_in_kerala || 'Unknown'}
            `);

            markersLayer.addLayer(marker);
        }
    });

    markersLayer.addTo(map);
}

function toggleLayer(type) {
    if (type === 'markers' && markersLayer) {
        if (map.hasLayer(markersLayer)) {
            map.removeLayer(markersLayer);
        } else {
            map.addLayer(markersLayer);
        }
    }
    // Heatmap logic would go here if using a plugin
}

// --- User Management ---

async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/users`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const users = await response.json();
            const tbody = document.getElementById('userTableBody');
            tbody.innerHTML = '';

            users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>#${user.id}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div class="avatar" style="width: 30px; height: 30px; font-size: 12px;">${user.username.charAt(0).toUpperCase()}</div>
                            ${user.username}
                        </div>
                    </td>
                    <td><span class="badge badge-${user.role}">${user.role}</span></td>
                    <td><span style="color: var(--success); font-size: 0.9em;">● Active</span></td>
                    <td>
                        ${user.username !== 'admin' ?
                        `<button class="btn-sm btn-danger" style="border:none; border-radius: 5px; cursor: pointer;" onclick="deleteUser(${user.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>` :
                        '<span style="color: var(--gray); font-size: 0.8em;">System</span>'}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Modal Functions
function openUserModal() {
    document.getElementById('userModal').classList.add('active');
}

function closeUserModal() {
    document.getElementById('userModal').classList.remove('active');
    document.getElementById('userModalStatus').textContent = '';
}

async function createUser() {
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newPassword').value;
    const role = document.getElementById('newRole').value;
    const status = document.getElementById('userModalStatus');

    if (!username || !password) {
        status.textContent = 'Please fill all fields';
        status.style.color = 'var(--danger)';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}`
            },
            body: JSON.stringify({ username, password, role })
        });

        if (response.ok) {
            status.textContent = 'User created successfully!';
            status.style.color = 'var(--success)';
            setTimeout(() => {
                closeUserModal();
                loadUsers();
                // Clear form
                document.getElementById('newUsername').value = '';
                document.getElementById('newPassword').value = '';
            }, 1000);
        } else {
            const data = await response.json();
            status.textContent = data.detail || 'Failed to create user';
            status.style.color = 'var(--danger)';
        }
    } catch (error) {
        status.textContent = 'Connection error';
        status.style.color = 'var(--danger)';
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            loadUsers();
        } else {
            alert('Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}
