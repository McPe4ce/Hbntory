/* Backoffice interface.
 *
 * Served by Flask itself, so it shares the API's origin and the session cookie
 * travels with every call — no CORS handling needed anywhere.
 *
 * Which screen is shown depends on the role. That is a convenience only:
 * authorization is enforced in the backend route decorators, so hiding a screen
 * is never what keeps a user out of it.
 */

const el = (id) => document.getElementById(id);

/* ---------- Helpers ---------- */

/* Every call goes through here so the 401 handling lives in one place. */
async function api(method, path, body) {
  const response = await fetch(path, {
    method: method,
    credentials: "same-origin",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });

  // Session gone or expired: back to the login screen.
  if (response.status === 401) {
    showLogin();
    throw new Error("Please sign in again.");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }

  return data;
}

/* Runs an action, then shows either its confirmation or the error it raised.
   Every button and form goes through this, so no handler repeats try/catch. */
async function run(action, confirmation) {
  notify(null);

  try {
    await action();
    if (confirmation) {
      notify(confirmation, "ok");
    }
  } catch (error) {
    notify(error.message, "error");
  }
}

/* Pass null to hide the notice. */
function notify(message, kind) {
  const notice = el("notice");
  notice.textContent = message || "";
  notice.className = message ? "notice notice-" + kind : "notice hidden";
}

function tag(name, text, className) {
  const node = document.createElement(name);
  node.textContent = text;
  if (className) {
    node.className = className;
  }
  return node;
}

/* Builds a table row. Cells are plain text, or a node when they need to be
   something else (a button, a styled label). Text is never inserted as HTML. */
function row(...cells) {
  const tr = document.createElement("tr");

  for (const cell of cells) {
    const td = document.createElement("td");
    if (cell instanceof Node) {
      td.appendChild(cell);
    } else {
      td.textContent = cell;
    }
    tr.appendChild(td);
  }

  return tr;
}

/* ---------- Screens ---------- */

const VIEWS = ["view-login", "view-stock", "view-admin"];

function show(viewId) {
  VIEWS.forEach((id) => el(id).classList.toggle("hidden", id !== viewId));
}

function showLogin() {
  el("session").classList.add("hidden");
  show("view-login");
}

/* Reads the session, then shows the screen matching the role. */
async function start() {
  let user;

  try {
    user = await api("GET", "/auth/me");
  } catch {
    return showLogin();
  }

  el("session-user").textContent = user.email;
  el("session-scope").textContent = user.is_admin
    ? "Administrator"
    : "Branch: " + user.branch_name;
  el("session").classList.remove("hidden");

  if (user.is_admin) {
    show("view-admin");
    await loadBranches();
    await loadUsers();
  } else {
    el("stock-branch").textContent = user.branch_name;
    show("view-stock");
    await loadStock();
  }
}

/* ---------- Login ---------- */

el("login-form").addEventListener("submit", (event) => {
  event.preventDefault();

  run(async () => {
    await api("POST", "/auth/login", {
      email: el("login-email").value,
      password: el("login-password").value,
    });
    el("login-form").reset();
    await start();
  });
});

el("logout").addEventListener("click", () => {
  run(async () => {
    await api("POST", "/auth/logout");
    showLogin();
  });
});

/* ---------- Stock ---------- */

async function loadStock() {
  const stocks = await api("GET", "/stock");

  el("stock-rows").replaceChildren(
    ...stocks.map((stock) => row(stock.product_id, String(stock.quantity)))
  );
  el("stock-empty").classList.toggle("hidden", stocks.length > 0);
}

function changeStock(path) {
  run(async () => {
    await api("POST", path, {
      product_id: el("stock-product").value.trim(),
      quantity: Number(el("stock-quantity").value),
    });
    await loadStock();
  }, "Stock updated.");
}

el("stock-form").addEventListener("submit", (event) => {
  event.preventDefault();
  changeStock("/stock/add");
});

el("stock-remove").addEventListener("click", () => changeStock("/stock/remove"));

/* ---------- Users ---------- */

/* Branch names, so the table shows a name instead of a UUID. */
let branches = [];

async function loadBranches() {
  branches = await api("GET", "/admin/branches");

  el("user-branch").replaceChildren(
    ...branches.map((branch) => {
      const option = tag("option", branch.branch_name);
      option.value = branch.id;
      return option;
    })
  );
}

function branchName(branchId) {
  const branch = branches.find((b) => b.id === branchId);
  return branch ? branch.branch_name : "—";
}

function deactivateButton(user) {
  const button = tag("button", "Deactivate", "link");
  button.type = "button";

  button.addEventListener("click", () => {
    if (!window.confirm("Deactivate " + user.email + "?")) {
      return;
    }
    run(async () => {
      await api("DELETE", "/admin/users/" + user.id);
      await loadUsers();
    }, user.email + " deactivated.");
  });

  return button;
}

async function loadUsers() {
  const users = await api("GET", "/admin/users");

  el("user-rows").replaceChildren(
    ...users.map((user) => row(
      user.email,
      user.is_admin ? "—" : branchName(user.branch_id),
      user.is_admin ? "Admin" : "Common",
      user.is_active ? "Active" : tag("span", "Deactivated", "muted"),
      user.is_active && !user.is_admin ? deactivateButton(user) : ""
    ))
  );
}

el("user-form").addEventListener("submit", (event) => {
  event.preventDefault();

  run(async () => {
    await api("POST", "/admin/users", {
      email: el("user-email").value,
      password: el("user-password").value,
      branch_id: el("user-branch").value,
    });
    el("user-form").reset();
    await loadUsers();
  }, "User created.");
});

/* ---------- Go ---------- */

start();
