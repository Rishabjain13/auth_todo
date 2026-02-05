const token = sessionStorage.getItem("access_token");
const role = sessionStorage.getItem("role");

if (!token || role !== "admin") {
    alert("Unauthorized");
    location.href = "/";
}

async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        ...options,
        headers: {
            ...(options.headers || {}),
            Authorization: `Bearer ${token}`,
        },
    });

    if (res.status === 401) {
        sessionStorage.clear();
        window.location.href = "/login";
        throw new Error("Unauthorized");
    }

    return res;
}


async function loadAdminInfo() {
    const res = await apiFetch("/me");
    const user = await res.json();

    document.getElementById("username").textContent = user.name;
    document.getElementById("useremail").textContent = user.email;
}


async function showStats() {
    const users = await (await apiFetch("/admin/users")).json();
    const tasks = await (await apiFetch("/admin/tasks")).json();

    adminTitle.textContent = "System Overview";

    adminData.innerHTML = `
        <div class="admin-card">👥 Total Users: ${users.length}</div>
        <div class="admin-card">📋 Total Tasks: ${tasks.length}</div>
        <div class="admin-card">✅ Completed Tasks: ${tasks.filter(t => t.completed).length}</div>
        <div class="admin-card">🔄 Shared Tasks: ${tasks.filter(t => t.shared_with.length > 0).length}</div>
    `;
}

async function loadUsers() {
    const users = await (await apiFetch("/admin/users")).json();

    adminTitle.textContent = "All Users";

    adminData.innerHTML = users.map(u => `
        <div class="admin-card">
            <b>${u.name}</b><br>
            ${u.email}<br>
            Role: <b>${u.role}</b>
        </div>
    `).join("");
}

async function loadAdminTasks() {
    const search = document.getElementById("searchInput")?.value.trim();

    let url = "/admin/tasks";
    if (search) {
        url += `?search=${encodeURIComponent(search)}`;
    }

    const res = await apiFetch(url);
    const tasks = await res.json();

    adminTitle.textContent = "All Tasks";

    if (!tasks.length) {
        adminData.innerHTML = "<p>No tasks found</p>";
        return;
    }

    adminData.innerHTML = tasks.map(t => `
        <div class="admin-card">
            <b>${t.title}</b><br>
            Owner: <b>${t.owner_email}</b><br>
            Priority: ${t.priority}<br>
            Completed: ${t.completed ? "Yes" : "No"}<br>

            <div class="shared-section">
                ${
                    t.shared_with.length
                        ? t.shared_with.map(s =>
                            `<span class="badge shared">
                                ${s.user_email} (${s.permission.toUpperCase()})
                             </span>`
                          ).join(" ")
                        : `<span class="badge owner">Not Shared</span>`
                }
            </div>

            <br>
            <button class="danger" onclick="deleteTask(${t.id})">
                🗑 Delete
            </button>
        </div>
    `).join("");
}

async function loadAuditLogs() {
    const user = document.getElementById("filterUser")?.value.trim();
    const action = document.getElementById("filterAction")?.value;

    let url = "/admin/audit-logs?";
    if (user) url += `user=${encodeURIComponent(user)}&`;
    if (action) url += `action=${encodeURIComponent(action)}`;

    const res = await fetch(url, {
        headers: {
            Authorization: `Bearer ${sessionStorage.getItem("access_token")}`
        }
    });

    if (!res.ok) {
        console.error("Audit log fetch failed");
        return;
    }

    const logs = await res.json();
    const tbody = document.getElementById("auditTable");
    tbody.innerHTML = "";

    logs.forEach(l => {
        tbody.innerHTML += `
            <tr>
                <td>${l.email}</td>
                <td>
                    <span class="audit-role ${l.role.toLowerCase()}">
                        ${l.role}
                    </span>
                </td>
                <td>
                    <span class="audit-badge ${l.action.toLowerCase()}">
                        ${l.action}
                    </span>
                </td>
                <td>${l.entity}</td>
                <td>${new Date(l.timestamp).toLocaleString()}</td>
            </tr>
        `;
    });
}


loadAuditLogs();


async function deleteTask(taskId) {
    if (!confirm("Are you sure you want to delete this task?")) return;

    await apiFetch(`/admin/tasks/${taskId}`, { method: "DELETE" });
    loadAdminTasks();
}


function logout() {
    sessionStorage.clear();
    location.href = "/login";
}


loadAdminInfo();
showStats();
