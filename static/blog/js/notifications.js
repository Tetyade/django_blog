function showToast(sender, text, time, groupName = null) {
    const container = document.getElementById("toast-container");

    if (!container) {
        return;
    }

    const toast = document.createElement("div");
    toast.className = "toast";
    let headerText = sender;
    if (groupName) {
        headerText = `${groupName} | ${sender}`;
    }
    toast.innerHTML = `
        <strong>${headerText}</strong>
        <p>${text}</p>
        <small>${time}</small>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function addNotificationToList(data) {
    const list = document.querySelector('.notif-list');
    if (!list) return;
    const emptyMsg = list.querySelector('div[style*="text-align: center"]');
    if (emptyMsg) emptyMsg.remove();

    let avatarHtml = '';
    if (data.avatar_url) {
        avatarHtml = `<img src="${data.avatar_url}">`;
    } else {
        avatarHtml = `<div class="placeholder">${data.sender.charAt(0).toUpperCase()}</div>`;
    }

    const li = document.createElement('li');
    li.className = 'notif-item';
    
    li.style.animation = "fadeIn 0.5s";

    li.innerHTML = `
        <div class="actor-avatar">
            <a href="/profile/${data.actor_uuid}/"> ${avatarHtml}
            </a>
        </div>

        <div class="notif-content">
            <a href="${data.target_url}">
                <strong>${data.sender}</strong>
                <span class="verb-text">
                    ${data.text}
                </span>
            </a>
            <span class="notif-time">Тільки що</span>
        </div>

        <a href="/notifications/delete/${data.notification_uuid}/" class="delete-btn" title="Видалити">×</a>
    `;

    list.prepend(li);
}

const socket = new WebSocket(
    "ws://" + window.location.host + "/ws/notifications/"
);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === "notify_message") {
        showToast(data.sender, data.text, data.created_at, data.group_name);
        if (data.is_on_list_page) {
            addNotificationToList(data);
        }
    }
};
