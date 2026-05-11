(function () {
    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    const sidebar = document.querySelector(".sidebar");
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", () => sidebar.classList.toggle("show"));
    }

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.querySelector(button.dataset.passwordToggle);
            if (!input) return;
            input.type = input.type === "password" ? "text" : "password";
            const icon = button.querySelector("i");
            if (icon) icon.className = input.type === "password" ? "bi bi-eye" : "bi bi-eye-slash";
        });
    });

    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const button = form.querySelector("button[type='submit'], input[type='submit']");
            if (!button || button.dataset.noLoading === "true") return;
            button.classList.add("disabled");
            if (button.tagName === "BUTTON") {
                button.dataset.originalText = button.innerHTML;
                button.innerHTML = "<span class='spinner-border spinner-border-sm me-2'></span>Processing";
            }
        });
    });

    document.querySelectorAll("[data-table-search]").forEach((input) => {
        const table = document.querySelector(input.dataset.tableSearch);
        if (!table) return;
        input.addEventListener("input", () => {
            const term = input.value.toLowerCase();
            const rows = table.querySelectorAll("tbody tr").length ? table.querySelectorAll("tbody tr") : table.children;
            Array.from(rows).forEach((row) => {
                row.hidden = !row.textContent.toLowerCase().includes(term);
            });
            table.dispatchEvent(new CustomEvent("table-filtered"));
        });
    });

    document.querySelectorAll("table[data-sortable] thead th").forEach((header, index) => {
        header.addEventListener("click", () => {
            const table = header.closest("table");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr")).filter((row) => row.children.length > 1);
            const asc = header.dataset.sortDirection !== "asc";
            rows.sort((a, b) => {
                const left = a.children[index].textContent.trim().toLowerCase();
                const right = b.children[index].textContent.trim().toLowerCase();
                return asc ? left.localeCompare(right, undefined, { numeric: true }) : right.localeCompare(left, undefined, { numeric: true });
            });
            header.dataset.sortDirection = asc ? "asc" : "desc";
            rows.forEach((row) => tbody.appendChild(row));
        });
    });

    document.querySelectorAll("[data-dark-toggle]").forEach((button) => {
        const saved = localStorage.getItem("guist-dark-mode");
        if (saved === "true") document.body.classList.add("dark-mode");
        button.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            localStorage.setItem("guist-dark-mode", document.body.classList.contains("dark-mode"));
        });
    });

    document.querySelectorAll("table[data-paginate]").forEach((table) => {
        const pageSize = Number(table.dataset.paginate || 8);
        const tbody = table.querySelector("tbody");
        if (!tbody) return;
        const pager = document.createElement("div");
        pager.className = "pagination-lite";
        const prev = document.createElement("button");
        const next = document.createElement("button");
        const label = document.createElement("span");
        prev.className = "btn btn-soft btn-sm";
        next.className = "btn btn-soft btn-sm";
        prev.type = "button";
        next.type = "button";
        prev.innerHTML = "<i class='bi bi-chevron-left'></i>";
        next.innerHTML = "<i class='bi bi-chevron-right'></i>";
        pager.append(prev, label, next);
        table.closest(".table-responsive").after(pager);
        let page = 1;

        const render = () => {
            const rows = Array.from(tbody.querySelectorAll("tr")).filter((row) => row.children.length > 1 && !row.hidden);
            const pages = Math.max(Math.ceil(rows.length / pageSize), 1);
            page = Math.min(page, pages);
            rows.forEach((row, index) => {
                row.style.display = index >= (page - 1) * pageSize && index < page * pageSize ? "" : "none";
            });
            label.textContent = `Page ${page} of ${pages}`;
            prev.disabled = page <= 1;
            next.disabled = page >= pages;
            pager.hidden = rows.length <= pageSize;
        };

        prev.addEventListener("click", () => {
            page -= 1;
            render();
        });
        next.addEventListener("click", () => {
            page += 1;
            render();
        });
        table.addEventListener("table-filtered", () => {
            page = 1;
            render();
        });
        render();
    });

    document.querySelectorAll("[data-counter]").forEach((counter) => {
        const target = Number(counter.dataset.counter || counter.textContent.replace(/[^0-9.]/g, ""));
        if (!Number.isFinite(target)) return;
        let current = 0;
        const suffix = counter.dataset.suffix || "";
        const step = Math.max(target / 35, 1);
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.round(current) + suffix;
        }, 24);
    });
})();
