function showToast(sender, text, time, groupName = null) {
    const container = document.getElementById("toast-container");

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

const socket = new WebSocket(
    "ws://" + window.location.host + "/ws/notifications/"
);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === "notify_message") {
        showToast(data.sender, data.text, data.created_at, data.group_name);
    }
};
