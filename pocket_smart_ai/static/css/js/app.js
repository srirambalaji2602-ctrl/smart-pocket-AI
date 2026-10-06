async function api(url, options = {}) {

    const response = await fetch(
        url,
        {
            credentials: "same-origin",
            ...options
        }
    );

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Something went wrong"
        );
    }

    return data;
}


function showMessage(
    id,
    message,
    ok = false
) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent = message;

    element.style.color =
        ok
            ? "#0f9d72"
            : "#dc2626";
}


async function loadSession() {

    try {

        const data =
            await api(
                "/session-info"
            );

        const auth =
            document.getElementById(
                "authLink"
            );

        const logout =
            document.getElementById(
                "logoutBtn"
            );

        if (data.authenticated) {

            if (auth) {

                auth.textContent =
                    "Dashboard";

                auth.href =
                    "/dashboard";
            }

            if (logout) {

                logout.classList.remove(
                    "hidden"
                );
            }

        } else {

            if (logout) {

                logout.classList.add(
                    "hidden"
                );
            }
        }

    } catch (error) {

        console.error(error);
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadSession();

        const logout =
            document.getElementById(
                "logoutBtn"
            );

        if (logout) {

            logout.onclick =
                async () => {

                    try {

                        await api(
                            "/logout",
                            {
                                method: "POST"
                            }
                        );

                        location.href =
                            "/";

                    } catch (error) {

                        console.error(
                            error
                        );
                    }
                };
        }
    }
);


function formObject(form) {

    const object = {};

    new FormData(form)
        .forEach(
            (value, key) => {
                object[key] = value;
            }
        );

    return object;
}


async function bindAuthForm(
    formId,
    url,
    messageId
) {

    const form =
        document.getElementById(
            formId
        );

    if (!form) {
        return;
    }

    form.onsubmit =
        async (event) => {

            event.preventDefault();

            try {

                const payload =
                    formObject(form);

                await api(
                    url,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

                showMessage(
                    messageId,
                    "Success! Redirecting...",
                    true
                );

                setTimeout(
                    () => {
                        location.href =
                            "/dashboard";
                    },
                    500
                );

            } catch (error) {

                showMessage(
                    messageId,
                    error.message
                );
            }
        };
}


function parseItems(raw) {

    const output = {};

    (
        raw || ""
    )
        .split(",")
        .forEach(
            part => {

                const [
                    key,
                    value
                ] =
                    part
                        .split(":")
                        .map(
                            item =>
                                item.trim()
                        );

                if (key) {

                    output[
                        key.toLowerCase()
                    ] =
                        Math.max(
                            1,
                            parseInt(
                                value || "1",
                                10
                            ) || 1
                        );
                }
            }
        );

    return output;
}


function renderResult(
    data,
    target
) {

    const element =
        document.getElementById(
            target
        );

    if (!element) {
        return;
    }

    const allocations =
        Object.entries(
            data.allocations || {}
        )
            .map(
                ([key, value]) =>
                    `
                    <div>
                        <small>
                            ${escapeHtml(key)}
                        </small>

                        <b>
                            ₹${Number(value)
                                .toLocaleString("en-IN")}
                        </b>
                    </div>
                    `
            )
            .join("");


    const recommendations =
        (
            data.recommendations || []
        )
            .map(
                item =>
                    `
                    <article class="rec">

                        <div class="rec-top">

                            <div>

                                <span class="platform">
                                    ${escapeHtml(
                                        item.platform
                                    )}
                                </span>

                                <h4>
                                    ${escapeHtml(
                                        item.name
                                    )}
                                </h4>

                            </div>

                            <div class="price">
                                ₹${Number(
                                    item.estimated_price
                                ).toLocaleString("en-IN")}
                            </div>

                        </div>

                        <p>
                            ${escapeHtml(
                                item.reason
                            )}

                            · Qty
                            ${item.quantity}
                        </p>

                        ${
                            item.search_url
                                ?
                                `
                                <a
                                    class="btn secondary"
                                    target="_blank"
                                    rel="noopener"
                                    href="${escapeAttr(
                                        item.search_url
                                    )}"
                                >
                                    Search platform ↗
                                </a>
                                `
                                :
                                ""
                        }

                    </article>
                    `
            )
            .join("");


    element.innerHTML = `

        <div class="result-summary">

            <h3>
                ${escapeHtml(
                    data.summary
                )}
            </h3>

            <p class="muted">

                Estimated spend:

                <b>
                    ₹${Number(
                        data.allocated_total
                    ).toLocaleString("en-IN")}
                </b>

                /

                ₹${Number(
                    data.budget
                ).toLocaleString("en-IN")}

                ·

                ${
                    data.ai_used
                        ? "Gemini AI"
                        : "Local fallback"
                }

            </p>

        </div>


        <h3>
            Budget allocation
        </h3>

        <div class="allocation">
            ${allocations}
        </div>


        <h3>
            Recommendations
        </h3>

        <div class="rec-grid">

            ${
                recommendations ||
                `
                <p class="muted">
                    No recommendations returned.
                </p>
                `
            }

        </div>


        <h3>
            Tips
        </h3>

        <ul class="tips">

            ${
                (
                    data.tips || []
                )
                    .map(
                        tip =>
                            `
                            <li>
                                ${escapeHtml(
                                    tip
                                )}
                            </li>
                            `
                    )
                    .join("")
            }

        </ul>
    `;
}


async function bindHomePlanner() {

    const form =
        document.getElementById(
            "homeForm"
        );

    if (!form) {
        return;
    }

    form.onsubmit =
        async event => {

            event.preventDefault();

            showMessage(
                "homeMsg",
                "Generating...",
                true
            );

            const formData =
                formObject(form);

            const payload = {

                budget:
                    Number(
                        formData.budget
                    ),

                rooms:
                    (
                        formData.rooms ||
                        ""
                    )
                        .split(",")
                        .map(
                            value =>
                                value.trim()
                        )
                        .filter(
                            Boolean
                        ),

                style:
                    formData.style,

                city:
                    formData.city,

                items:
                    parseItems(
                        formData.items
                    ),

                notes:
                    formData.notes
            };

            try {

                const result =
                    await api(
                        "/generate-home",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );

                renderResult(
                    result,
                    "homeResult"
                );

                showMessage(
                    "homeMsg",
                    "Plan generated.",
                    true
                );

            } catch (error) {

                showMessage(
                    "homeMsg",
                    error.message
                );
            }
        };
}


async function bindPartyPlanner() {

    const form =
        document.getElementById(
            "partyForm"
        );

    if (!form) {
        return;
    }

    form.onsubmit =
        async event => {

            event.preventDefault();

            showMessage(
                "partyMsg",
                "Generating...",
                true
            );

            const formData =
                formObject(form);

            const payload = {

                budget:
                    Number(
                        formData.budget
                    ),

                guests:
                    Number(
                        formData.guests
                    ),

                event_type:
                    formData.event_type,

                venue:
                    formData.venue,

                city:
                    formData.city,

                food_preference:
                    formData.food_preference,

                notes:
                    formData.notes
            };

            try {

                const result =
                    await api(
                        "/generate-party",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );

                renderResult(
                    result,
                    "partyResult"
                );

                showMessage(
                    "partyMsg",
                    "Plan generated.",
                    true
                );

            } catch (error) {

                showMessage(
                    "partyMsg",
                    error.message
                );
            }
        };
}


async function bindJewelryPlanner() {

    const form =
        document.getElementById(
            "jewelryForm"
        );

    if (!form) {
        return;
    }

    form.onsubmit =
        async event => {

            event.preventDefault();

            showMessage(
                "jewelryMsg",
                "Generating...",
                true
            );

            try {

                const result =
                    await api(
                        "/generate-jewelry",
                        {
                            method: "POST",

                            body:
                                new FormData(
                                    form
                                )
                        }
                    );

                renderResult(
                    result,
                    "jewelryResult"
                );

                showMessage(
                    "jewelryMsg",
                    "Plan generated.",
                    true
                );

            } catch (error) {

                showMessage(
                    "jewelryMsg",
                    error.message
                );
            }
        };
}


async function loadDashboard() {

    try {

        const session =
            await api(
                "/session-info"
            );

        if (!session.authenticated) {

            location.href =
                "/login";

            return;
        }

        const hello =
            document.getElementById(
                "hello"
            );

        if (hello) {

            hello.textContent =
                `Hi, ${
                    session.user.full_name ||
                    session.user.email.split("@")[0]
                } 👋`;
        }

        const history =
            await api(
                "/history"
            );

        const recent =
            document.getElementById(
                "recentPlans"
            );

        if (!recent) {
            return;
        }

        recent.innerHTML =
            (
                history
                    .slice(0, 5)
                    .map(
                        item =>
                            `
                            <div class="history-card">

                                <div>

                                    <span class="pill">
                                        ${escapeHtml(
                                            item.planner_type
                                        )}
                                    </span>

                                    <h3>
                                        ${escapeHtml(
                                            item.response.summary
                                        )}
                                    </h3>

                                    <p class="muted">

                                        Budget
                                        ₹${Number(
                                            item.response.budget
                                        ).toLocaleString(
                                            "en-IN"
                                        )}

                                    </p>

                                </div>

                                <span class="muted">

                                    ${new Date(
                                        item.created_at
                                    ).toLocaleString()}

                                </span>

                            </div>
                            `
                    )
                    .join("")
            )
            ||
            `
            <div class="notice">
                No plans yet.
                Pick a planner above.
            </div>
            `;

    } catch (error) {

        location.href =
            "/login";
    }
}


async function loadHistory() {

    try {

        const history =
            await api(
                "/history"
            );

        const element =
            document.getElementById(
                "historyList"
            );

        if (!element) {
            return;
        }

        element.innerHTML =
            (
                history
                    .map(
                        item =>
                            `
                            <div class="history-card">

                                <div>

                                    <span class="pill">
                                        ${escapeHtml(
                                            item.planner_type
                                        )}
                                    </span>

                                    <h3>
                                        ${escapeHtml(
                                            item.response.summary
                                        )}
                                    </h3>

                                    <p class="muted">

                                        ₹${Number(
                                            item.response.budget
                                        ).toLocaleString(
                                            "en-IN"
                                        )}

                                        ·

                                        ${
                                            item.response
                                                .recommendations
                                                ?.length || 0
                                        }

                                        recommendations

                                    </p>

                                </div>

                                <span class="muted">

                                    ${new Date(
                                        item.created_at
                                    ).toLocaleString()}

                                </span>

                            </div>
                            `
                    )
                    .join("")
            )
            ||
            `
            <div class="notice">
                No history yet.
            </div>
            `;

    } catch (error) {

        const element =
            document.getElementById(
                "historyList"
            );

        if (element) {

            element.innerHTML =
                `
                <div class="notice">
                    ${escapeHtml(
                        error.message
                    )}
                </div>
                `;
        }
    }
}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]
    );
}


function escapeAttr(value) {

    return escapeHtml(
        value
    ).replace(
        /`/g,
        "&#096;"
    );
}