// Admin Dashboard JavaScript

// Navigation
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            item.classList.add('active');
            
            // Hide all sections
            sections.forEach(section => section.classList.remove('active'));
            
            // Show selected section
            const sectionId = item.getAttribute('data-section') + '-section';
            document.getElementById(sectionId).classList.add('active');
            
            // Update page title
            const title = item.textContent.trim();
            document.getElementById('page-title').textContent = title;
        });
    });
    
    // Load initial data
    loadDashboardData();
});

// API Configuration
const API_BASE = 'http://localhost:8000/api/v1';
let authToken = localStorage.getItem('adminToken') || '';

// Set auth header
function getHeaders() {
    return {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
    };
}

// Load dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/admin/stats`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            updateDashboard(data);
        } else if (response.status === 401) {
            window.location.href = '/login.html';
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update dashboard with stats
function updateDashboard(data) {
    document.getElementById('total-users').textContent = data.total_users || 0;
    document.getElementById('total-keys').textContent = data.active_api_keys || 0;
    document.getElementById('requests-today').textContent = data.requests_today || 0;
    document.getElementById('avg-response').textContent = 
        (data.average_response_time || 0).toFixed(0) + 'ms';
}

// Load users
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/admin/users`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const users = await response.json();
            renderUsersTable(users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Render users table
function renderUsersTable(users) {
    const tbody = document.getElementById('users-table');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.email}</td>
            <td><span class="badge badge-${user.role === 'admin' ? 'warning' : 'success'}">${user.role}</span></td>
            <td><span class="badge badge-${user.is_active ? 'success' : 'danger'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td>${user.quota_limit}</td>
            <td>
                <button class="btn-outline" onclick="editUser('${user.id}')">Edit</button>
                <button class="btn-danger" onclick="deleteUser('${user.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Refresh data
async function refreshData() {
    await loadDashboardData();
    const currentSection = document.querySelector('.content-section.active').id;
    
    if (currentSection === 'users-section') {
        await loadUsers();
    }
}

// Logout
function logout() {
    localStorage.removeItem('adminToken');
    window.location.href = '/';
}

// Placeholder functions
function createUser() {
    alert('Create user modal would open here');
}

function editUser(userId) {
    alert(`Edit user ${userId}`);
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        // API call to delete user
        console.log(`Deleting user ${userId}`);
    }
}

// Auto-load users when users section is active
document.addEventListener('DOMContentLoaded', function() {
    const usersNav = document.querySelector('[data-section="users"]');
    usersNav.addEventListener('click', loadUsers);
});
