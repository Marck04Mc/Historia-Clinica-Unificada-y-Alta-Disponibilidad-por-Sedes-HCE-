/**
 * Sistema HCE - JavaScript Utilities
 * Funciones comunes para todas las interfaces
 */

// ===================================================
// Gestión de autenticación
// ===================================================

function getToken() {
    return localStorage.getItem('token');
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// Verificar autenticación al cargar la página
function checkAuth() {
    if (!isAuthenticated() && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
    }
}

// ===================================================
// Gestión de información de sede
// ===================================================

async function loadSedeInfo() {
    try {
        const token = getToken();
        const response = await fetch('/auth/sede', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const sede = await response.json();
            updateSedeDisplay(sede);
        }
    } catch (error) {
        console.error('Error cargando información de sede:', error);
    }
}

function updateSedeDisplay(sede) {
    const sedeBadge = document.getElementById('sedeBadge');
    if (sedeBadge) {
        sedeBadge.textContent = `${sede.nombre} - ${sede.ciudad}`;
        
        // Aplicar color según ciudad
        if (sede.ciudad.toLowerCase().includes('bogotá')) {
            sedeBadge.style.backgroundColor = '#e74c3c';
        } else if (sede.ciudad.toLowerCase().includes('medellín')) {
            sedeBadge.style.backgroundColor = '#3498db';
        } else if (sede.ciudad.toLowerCase().includes('cali')) {
            sedeBadge.style.backgroundColor = '#27ae60';
        }
    }
}

// ===================================================
// Gestión de información de usuario
// ===================================================

function updateUserDisplay() {
    const user = getUser();
    if (user) {
        const userName = document.getElementById('userName');
        if (userName) {
            userName.textContent = `${user.nombres || user.username} (${user.rol})`;
        }
    }
}

// ===================================================
// Utilidades de API
// ===================================================

async function apiRequest(url, options = {}) {
    const token = getToken();
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    const response = await fetch(url, { ...options, ...defaultOptions });
    
    if (response.status === 401) {
        logout();
        throw new Error('Sesión expirada');
    }
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        throw new Error(error.detail || 'Error en la solicitud');
    }
    
    return response;
}

// ===================================================
// Utilidades de formato
// ===================================================

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ===================================================
// Utilidades de UI
// ===================================================

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading">Cargando...</div>';
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="error-message">${message}</div>`;
    }
}

function showSuccess(message) {
    alert(message); // En producción, usar toast o notificación
}

// ===================================================
// Validación de formularios
// ===================================================

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger-color)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });
    
    return isValid;
}

// ===================================================
// Inicialización
// ===================================================

document.addEventListener('DOMContentLoaded', () => {
    // Verificar autenticación
    checkAuth();
    
    // Cargar información de usuario y sede
    if (isAuthenticated()) {
        updateUserDisplay();
        loadSedeInfo();
    }
});

// ===================================================
// Manejo de errores global
// ===================================================

window.addEventListener('unhandledrejection', (event) => {
    console.error('Error no manejado:', event.reason);
    
    if (event.reason.message === 'Sesión expirada') {
        logout();
    }
});
