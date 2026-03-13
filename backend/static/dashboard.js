const tableBody = document.querySelector("#employeesTable tbody");
const refreshBtn = document.getElementById("refreshBtn");
const assignBtn = document.getElementById("assignBtn");
const employeeIdInput = document.getElementById("employeeId");
const taskTitleInput = document.getElementById("taskTitle");
const taskDescInput = document.getElementById("taskDesc");
const assignResult = document.getElementById("assignResult");
const eventsEl = document.getElementById("events");

function escapeHtml(s) {
  return (s ?? "").toString().replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "<",
    ">": ">",
    '"': """,
    "'": "&#039;"
  }[c]));
}

function statusDotClass(status) {
  const s = (status || "").toLowerCase();
  if (s === "available" || s === "busy") return "dot-present";
  return "dot-absent";
}

function rowClass(status) {
  const s = (status || "").toLowerCase();
  if (s === "available" || s === "busy") return "table-success";
  return "table-danger";
}

function getDisplayStatus(status) {
  const s = (status || "").toLowerCase();
  if (s === "available" || s === "busy") return "Present";
  return "Absent";
}


function upsertRow(emp) {
  const id = emp.id;
  let tr = tableBody.querySelector(`tr[data-id="${CSS.escape(id)}"]`);
  if (!tr) {
    tr = document.createElement("tr");
    tr.dataset.id = id;
    tr.style.opacity = '0';

    tr.innerHTML = `
      <td><span class="status-dot"></span></td>
      <td class="mono"></td>
      <td></td>
      <td></td>
      <td class="badge text-bg-success fs-7"></td>
      <td class="mono"></td>
    `;

    tr.addEventListener("click", () => {
      employeeIdInput.value = id;
    });
    tableBody.appendChild(tr);
  }

  tr.className = rowClass(emp.status);
  tr.querySelector(".status-dot").className = `status-dot ${statusDotClass(emp.status)}`;
  tr.children[1].textContent = emp.id;
  tr.children[2].textContent = emp.name || "";

  tr.children[3].textContent = getDisplayStatus(emp.status);
  tr.children[4].className = emp.today_present ? 'badge text-bg-success' : 'badge text-bg-danger';
  tr.children[4].textContent = emp.today_present ? 'Present' : 'Absent';
  tr.children[5].textContent = emp.last_seen_at || "";

  // Fade in animation
  tr.style.transition = 'opacity 0.5s ease-in-out';
  tr.style.opacity = '1';
  tr.classList.add('fade-in');
}


async function refreshEmployees() {
  const res = await fetch("/api/employees");
  const data = await res.json();
  tableBody.innerHTML = "";
  const todayRes = await fetch("/api/today_attendance");
  const todayData = await todayRes.json();
  const todayMap = new Set(todayData.today_attendance.map(e => e.id));
  for (const emp of data.employees || []) {
    emp.today_present = todayMap.has(emp.id);
    upsertRow(emp);
  }
}

function logEvent(html) {
  const now = new Date().toISOString();
  const div = document.createElement("div");
  div.innerHTML = `<span class="text-muted mono">${now}</span> ${html}`;
  eventsEl.prepend(div);
}

refreshBtn.addEventListener("click", refreshEmployees);

assignBtn.addEventListener("click", async () => {
  assignResult.textContent = "";
  const employee_id = employeeIdInput.value.trim();
  const title = taskTitleInput.value.trim();
  const description = taskDescInput.value.trim();

  if (!employee_id || !title) {
    assignResult.innerHTML = `<span class="text-danger">Employee ID and title are required.</span>`;
    return;
  }

  const res = await fetch("/api/tasks/assign", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employee_id, title, description })
  });
  const data = await res.json();
  if (!res.ok) {
    assignResult.innerHTML = `<span class="text-danger">${escapeHtml(data.error || "Failed")}</span>`;
    return;
  }

  assignResult.innerHTML = `<span class="text-success">Assigned task #${escapeHtml(data.task?.id)} to ${escapeHtml(employee_id)}.</span>`;
  if (data.employee) upsertRow(data.employee);
  logEvent(`<b>Task assigned</b> → employee <span class="mono">${escapeHtml(employee_id)}</span>: ${escapeHtml(title)}`);
});


const socketStatus = document.getElementById("socketStatus");
const socket = io();
socket.on("connect", () => {
  if (socketStatus) {
    socketStatus.textContent = "Realtime Connected ✅";
    socketStatus.className = "socket-connected position-fixed top-0 end-0 m-3 badge p-2 shadow rounded-pill";
  }
  logEvent(`<span class="text-success">Socket connected</span>`);
});
socket.on("disconnect", () => {
  if (socketStatus) {
    socketStatus.textContent = "Realtime Disconnected 🔴";
    socketStatus.className = "socket-disconnected position-fixed top-0 end-0 m-3 badge p-2 shadow rounded-pill";
  }
});
socket.on("status_update", (msg) => {
  if (msg?.employee) {
    upsertRow(msg.employee);
    logEvent(`<b>Present</b> → <span class="mono">${escapeHtml(msg.employee.id)}</span>`);
  }
});
socket.on("task_assigned", (msg) => {
  const empId = msg?.employee?.id || msg?.task?.assigned_to;
  const title = msg?.task?.title;
  if (msg?.employee) upsertRow(msg.employee);
  logEvent(`<b>Task assigned</b> → <span class="mono">${escapeHtml(empId || "")}</span>: ${escapeHtml(title || "")}`);
});

// Auto refresh fallback
setInterval(refreshEmployees, 10000);


refreshEmployees();
