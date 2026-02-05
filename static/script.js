document.addEventListener("DOMContentLoaded",async () => {

    let accessToken = sessionStorage.getItem("access_token");

    const dateEl = document.getElementById("todayDate");
    if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
    }

    const taskInput = document.getElementById("taskInput");
    const prioritySelect = document.getElementById("prioritySelect");

    const todayTasksBox = document.getElementById("todayTasks");
    const completedTasksBox = document.getElementById("completedTasks");

    const doneCountEl = document.getElementById("doneCount");
    const pendingCountEl = document.getElementById("pendingCount");
    const overdueCountEl = document.getElementById("overdueCount");

    let currentShareTaskId = null;

    async function apiFetch(url, options = {}) {
        options.headers = {
            ...(options.headers || {}),
            Authorization: `Bearer ${accessToken}`
        };

        const res = await fetch(url, options);

        if (res.status === 401) {
            sessionStorage.removeItem("access_token");
            window.location.href = "/login";
        }

        return res;
    }

    async function loadUser() {
        if (!accessToken) {
            window.location.href = "/login";
            return;
        }

        const res = await apiFetch("/me");
        if (!res.ok) return;

        const user = await res.json();
        document.getElementById("username").textContent = user.name;
        document.getElementById("useremail").textContent = user.email;
        
        sessionStorage.setItem("user_id", user.id);
        sessionStorage.setItem("email", user.email);
        sessionStorage.setItem("role", user.role);

        if (user.role === "admin") {
            document.getElementById("adminBtn")?.classList.remove("hidden");
        }
        return user;
    }

    async function loadTasks() {
        const res = await apiFetch("/tasks");
        if (!res.ok) return;

        const tasks = await res.json();

        todayTasksBox.innerHTML = "";
        completedTasksBox.innerHTML = "";

        let done = 0;
        let pending = 0;
        let overdue = 0;

        // normalize today's date (important!)
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        tasks.forEach(task => {
            const div = document.createElement("div");
            div.className = "task";

            let dueDateHtml = "";
            let isOverdue = false;

            if (task.due_date) {
                const due = new Date(task.due_date);
                due.setHours(0, 0, 0, 0);

                if (!task.completed && due < today) {
                    isOverdue = true;
                    div.classList.add("overdue");
                    overdue++;
                }

                dueDateHtml = `
                    <span class="due-date ${isOverdue ? "late" : ""}">
                        📅 ${due.toLocaleDateString("en-IN")}
                    </span>
                `;
            }

            const isOwner = task.permission === "owner";
            const isEditor = task.permission === "editor";
            const isViewer = task.permission === "viewer";

            div.innerHTML = `
                <input type="checkbox"
                    ${task.completed ? "checked" : ""}
                    ${isViewer ? "disabled" : ""}>

                <span class="title">
                    ${task.completed ? `<s>${task.title}</s>` : task.title}
                </span>

                ${dueDateHtml}

                <span class="${task.priority.toLowerCase()}">
                    ${task.priority}
                </span>

                <span class="perm ${task.permission}">
                    ${task.permission.toUpperCase()}
                </span>

                ${isOwner ? `<button class="share">➤</button>` : ``}
                ${(isOwner || isEditor) ? `<button class="edit">✏️</button>` : ``}
                ${isOwner ? `<button class="delete">🗑</button>` : ``}
            `;

            /* ===== EVENTS ===== */

            if (!isViewer) {
                div.querySelector("input").addEventListener("change", async () => {
                    await apiFetch(`/tasks/${task.id}`, {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            title: task.title,
                            priority: task.priority,
                            completed: !task.completed,
                            due_date: task.due_date   // ✅ IMPORTANT
                        })
                    });
                    loadTasks();
                });
            }

            if (isOwner || isEditor) {
                div.querySelector(".edit")?.addEventListener("click", async () => {
                    const newTitle = prompt("Edit task title", task.title);
                    if (!newTitle) return;

                    const newPriority = prompt(
                        "Edit priority (High / Medium / Low)",
                        task.priority
                    );
                    if (!["High", "Medium", "Low"].includes(newPriority)) return;

                    await apiFetch(`/tasks/${task.id}`, {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            title: newTitle,
                            priority: newPriority,
                            completed: task.completed,
                            due_date: task.due_date   // ✅ IMPORTANT
                        })
                    });
                    loadTasks();
                });
            }

            if (isOwner) {
                div.querySelector(".delete")?.addEventListener("click", async () => {
                    await apiFetch(`/tasks/${task.id}`, { method: "DELETE" });
                    loadTasks();
                });

                div.querySelector(".share")?.addEventListener("click", () => {
                    currentShareTaskId = task.id;
                    document.getElementById("shareModal").classList.remove("hidden");
                });
            }

            /* ===== COUNTS ===== */

            if (task.completed) {
                done++;
                completedTasksBox.appendChild(div);
            } else {
                pending++;
                todayTasksBox.appendChild(div);
            }
        });

        doneCountEl.textContent = done;
        pendingCountEl.textContent = pending;
        overdueCountEl.textContent = overdue;

        const toast = document.getElementById("overdueToast");
        const toastCount = document.getElementById("overdueToastCount");

        if (overdue > 0 && !sessionStorage.getItem("overdue_notified")) {
            toastCount.textContent = overdue;
            toast.classList.remove("hidden");

            sessionStorage.setItem("overdue_notified", "true");

            setTimeout(() => {
                toast.classList.add("hidden");
            }, 5000);
        }

        // 🔄 Reset notification when no overdue tasks
        if (overdue === 0) {
            sessionStorage.removeItem("overdue_notified");
        }
    }
    


    async function addTask() {
        const title = taskInput.value.trim();
        if (!title) {
            alert("Task title required");
            return;
        }

        await apiFetch("/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title: title,
                priority: prioritySelect.value,
                completed: false,
                due_date: document.getElementById("dueDate").value || null
            })
        });

        // reset UI
        taskInput.value = "";
        document.getElementById("dueDate").value = "";
        document.getElementById("templateSelect").value = "";

        loadTasks();
    }

    window.shareTask = async function () {
        const email = document.getElementById("shareEmail").value.trim();
        const permission = document.getElementById("sharePermission").value;

        if (!email) return alert("Email required");

        await apiFetch(`/tasks/${currentShareTaskId}/share?user_email=${email}&permission=${permission}`, {
            method: "POST"
        });

        document.getElementById("shareModal").classList.add("hidden");
        document.getElementById("shareEmail").value = "";
        alert("Task shared successfully");
    };

    window.closeShareModal = function () {
        document.getElementById("shareModal").classList.add("hidden");
    };

    window.logout = function () {
        sessionStorage.removeItem("access_token");
        fetch("/logout", { method: "POST" });
        window.location.href = "/login";
    };

    window.addTask = addTask;
    const userId = sessionStorage.getItem("user_id");

    if (!userId) {
        console.warn("User ID missing, activity feed disabled");
    } else {
        const activitySocket = new WebSocket(
            `ws://localhost:8000/ws/activity/${userId}`
        );

        activitySocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const feed = document.getElementById("activityFeed");
            if (!feed) return;

            const p = document.createElement("p");
            p.innerHTML = `
            <b>${data.email}</b> (${data.role})
            ${data.action} ${data.entity}:
            <i>${data.title ?? ""}</i>
            `;

            feed.prepend(p);
        };
    }    
    async function initActivityFeed() {
        const userId = sessionStorage.getItem("user_id");
    
        if (!userId) {
            console.warn("User ID missing, activity feed disabled");
            return;
        }

        const activitySocket = new WebSocket(
            `ws://localhost:8000/ws/activity`
        );
    
        activitySocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const feed = document.getElementById("activityFeed");
            if (!feed) return;

            const myEmail = sessionStorage.getItem("email");
            if (!data.visible_to || !data.visible_to.includes(myEmail)) return;
    
            const p = document.createElement("p");
            p.innerHTML = `
                <b>${data.actor_email}</b> (${data.role})
                ${data.action} ${data.entity}:
                <i>${data.title ?? ""}</i>
            `;

           feed.prepend(p);
        };
    }


    async function loadTemplates() {
        const res = await apiFetch("/templates");
        if (!res.ok) return;

        const templates = await res.json();
        const select = document.getElementById("templateSelect");

        select.innerHTML = `<option value="">📋 Use Template</option>`;

        templates.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.id;
            opt.textContent = t.name;
            opt.dataset.title = t.title;
            opt.dataset.priority = t.priority;
            select.appendChild(opt);
        });
    }

    window.saveTemplate = async function () {
        const title = taskInput.value.trim();
        if (!title) return alert("Task title required");

        await apiFetch("/templates", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: title,
                title: title,
                priority: prioritySelect.value
            })
        });

        alert("Template saved");
        loadTemplates();
    };

    window.useTemplate = function () {
        const select = document.getElementById("templateSelect");
        const option = select.selectedOptions[0];
        if (!option || !option.value) return;

        // Fill inputs only
        taskInput.value = option.dataset.title;
        prioritySelect.value = option.dataset.priority;
    };


    await loadUser();
    initActivityFeed();
    loadTasks();
    loadTemplates();   
});