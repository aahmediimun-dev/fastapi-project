// ========== Configuration ==========
const API_URL = "http://localhost:8000/api";
let currentInvoiceId = null;
let chartInstance = null;

// ========== Initialize on Page Load ==========
window.addEventListener("load", () => {
    const token = localStorage.getItem("token");
    if (token) {
        showDashboard();
        loadDashboard();
    } else {
        showAuth();
    }
});

// ========== Auth Form Toggle ==========
function toggleForm(event) {
    event.preventDefault();
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    
    if (loginForm.style.display === "none") {
        loginForm.style.display = "block";
        registerForm.style.display = "none";
    } else {
        loginForm.style.display = "none";
        registerForm.style.display = "block";
    }
}

// ========== Show/Hide Containers ==========
function showAuth() {
    document.getElementById("auth-container").style.display = "flex";
    document.getElementById("dashboard-container").style.display = "none";
}

function showDashboard() {
    document.getElementById("auth-container").style.display = "none";
    document.getElementById("dashboard-container").style.display = "block";
}

// ========== Authentication Functions ==========

// Register
document.getElementById("register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError("register-error");
    
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const company_name = document.getElementById("register-company").value;
    const password = document.getElementById("register-password").value;
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, company_name, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Registration failed");
        }
        
        alert("Registration successful! Please login.");
        document.getElementById("register-form").reset();
        toggleForm({ preventDefault: () => {} });
    } catch (error) {
        showError("register-error", error.message);
    }
});

// Login
document.getElementById("login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError("login-error");
    
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            throw new Error("Invalid credentials");
        }
        
        const data = await response.json();
        
        // Store token and user info
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("username", data.username);
        
        // Switch to dashboard
        showDashboard();
        document.getElementById("user-name").textContent = `Welcome, ${data.username}!`;
        
        // Load dashboard data
        loadDashboard();
        
        // Clear form
        document.getElementById("login-form").reset();
    } catch (error) {
        showError("login-error", error.message);
    }
});

// Logout
function logout() {
    if (confirm("Are you sure you want to logout?")) {
        localStorage.removeItem("token");
        localStorage.removeItem("user_id");
        localStorage.removeItem("username");
        
        document.getElementById("login-form").reset();
        document.getElementById("register-form").reset();
        document.getElementById("login-form").style.display = "block";
        document.getElementById("register-form").style.display = "none";
        
        showAuth();
    }
}

// ========== Dashboard Functions ==========

async function loadDashboard() {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    
    document.getElementById("user-name").textContent = `Welcome, ${username}!`;
    
    try {
        const response = await fetch(`${API_URL}/dashboard/stats`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error("Failed to load dashboard");
        
        const data = await response.json();
        
        // Update stats
        document.getElementById("stat-total").textContent = data.total_invoices;
        document.getElementById("stat-amount").textContent = "$" + data.total_amount.toFixed(2);
        document.getElementById("stat-pending").textContent = data.pending;
        document.getElementById("stat-paid").textContent = data.paid;
        document.getElementById("stat-overdue").textContent = data.overdue;
        
        // Update table
        updateInvoicesTable(data.invoices);
        
        // Draw chart
        drawChart(data);
    } catch (error) {
        console.error("Error loading dashboard:", error);
        showError("upload-error", "Failed to load dashboard");
    }
}

function updateInvoicesTable(invoices) {
    const tbody = document.getElementById("invoices-body");
    
    if (invoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No invoices yet. Upload one to get started!</td></tr>';
        return;
    }
    
    tbody.innerHTML = invoices.map(inv => {
        const date = new Date(inv.uploaded_at);
        const dateStr = date.toLocaleDateString();
        const invoiceDate = inv.invoice_date ? new Date(inv.invoice_date).toLocaleDateString() : "N/A";
        
        return `
            <tr>
                <td>${escapeHtml(inv.filename)}</td>
                <td>$${inv.amount.toFixed(2)}</td>
                <td>${invoiceDate}</td>
                <td><span class="status-badge status-${inv.status}">${inv.status}</span></td>
                <td>${dateStr}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-edit btn-small" onclick="editStatus(${inv.id})">Status</button>
                        <button class="btn-delete btn-small" onclick="deleteInvoice(${inv.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function drawChart(data) {
    const ctx = document.getElementById("invoiceChart").getContext("2d");
    
    // Destroy previous chart if exists
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    chartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Paid", "Pending", "Overdue"],
            datasets: [{
                data: [data.paid, data.pending, data.overdue],
                backgroundColor: [
                    "rgba(39, 174, 96, 0.8)",      // Green - Paid
                    "rgba(231, 76, 60, 0.8)",      // Red - Pending
                    "rgba(243, 156, 18, 0.8)"      // Orange - Overdue
                ],
                borderColor: [
                    "rgba(39, 174, 96, 1)",
                    "rgba(231, 76, 60, 1)",
                    "rgba(243, 156, 18, 1)"
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        padding: 20,
                        font: { size: 14 }
                    }
                }
            }
        }
    });
}

// ========== Invoice Management ==========

// Upload Invoice
document.getElementById("upload-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError("upload-error");
    
    const token = localStorage.getItem("token");
    const file = document.getElementById("invoice-file").files[0];
    const amount = document.getElementById("invoice-amount").value;
    const invoice_date = document.getElementById("invoice-date").value;
    
    if (!file) {
        showError("upload-error", "Please select a file");
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("amount", amount);
        formData.append("invoice_date", invoice_date);
        
        const response = await fetch(`${API_URL}/invoices/upload`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Upload failed");
        }
        
        alert("Invoice uploaded successfully!");
        document.getElementById("upload-form").reset();
        loadDashboard();
    } catch (error) {
        showError("upload-error", error.message);
    }
});

// Delete Invoice
async function deleteInvoice(invoiceId) {
    if (!confirm("Are you sure you want to delete this invoice?")) return;
    
    const token = localStorage.getItem("token");
    
    try {
        const response = await fetch(`${API_URL}/invoices/${invoiceId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error("Delete failed");
        
        alert("Invoice deleted successfully!");
        loadDashboard();
    } catch (error) {
        alert("Error deleting invoice: " + error.message);
    }
}

// Edit Status
function editStatus(invoiceId) {
    currentInvoiceId = invoiceId;
    document.getElementById("status-modal").style.display = "flex";
}

// Save Status
async function saveStatus() {
    const token = localStorage.getItem("token");
    const status = document.getElementById("status-select").value;
    
    try {
        const response = await fetch(`${API_URL}/invoices/${currentInvoiceId}`, {
            method: "PUT",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ status })
        });
        
        if (!response.ok) throw new Error("Update failed");
        
        closeModal();
        loadDashboard();
        alert("Invoice status updated!");
    } catch (error) {
        alert("Error updating status: " + error.message);
    }
}

// Close Modal
function closeModal() {
    document.getElementById("status-modal").style.display = "none";
    currentInvoiceId = null;
}

// Close modal when clicking outside
window.addEventListener("click", (e) => {
    const modal = document.getElementById("status-modal");
    if (e.target === modal) {
        closeModal();
    }
});

// ========== Utility Functions ==========

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add("show");
    }
}

function clearError(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = "";
        element.classList.remove("show");
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ========== Auto-refresh (optional) ==========
// Uncomment to auto-refresh dashboard every 30 seconds
// setInterval(() => {
//     if (localStorage.getItem("token")) {
//         loadDashboard();
//     }
// }, 30000);
