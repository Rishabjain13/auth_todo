const activitySocket = new WebSocket("ws://localhost:8000/ws/activity");

activitySocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const feed = document.getElementById("activityFeed");
    if (!feed) return;

    const p = document.createElement("p");

    p.innerHTML = `
        <b>${data.email}</b>
        <span style="color:#3f3fb5;font-weight:600">
            (${data.role})
        </span>
        ${data.action}
        <i>${data.title ?? ""}</i>
    `;

    feed.prepend(p);
};
