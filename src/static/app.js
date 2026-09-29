document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  let messageTimeout;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    clearTimeout(messageTimeout);
    messageTimeout = setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.length = 1;

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const waitlist = details.waitlist || [];
        const spotsLeft = Math.max(details.max_participants - details.participants.length, 0);
        const renderPeople = (people, emptyText) =>
          people.length
            ? people
                .map(
                  (person) => `
                  <li>
                    <span>${escapeHtml(person)}</span>
                    <button type="button" class="remove-participant" data-email="${encodeURIComponent(person)}" aria-label="Unregister ${escapeHtml(person)}" title="Unregister">&#128465;</button>
                  </li>`
                )
                .join("")
            : `<li class="no-participants">${emptyText}</li>`;
        const participantsList = renderPeople(details.participants, "No participants yet");
        const availability =
          spotsLeft > 0
            ? `${spotsLeft} spots left`
            : `<span class="activity-full">Full</span> &ndash; ${waitlist.length} on waitlist`;
        const waitlistSection = waitlist.length
          ? `
          <div class="participants waitlist">
            <strong>Waitlist</strong>
            <ol>${renderPeople(waitlist, "")}</ol>
          </div>`
          : "";

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${availability}</p>
          <div class="participants">
            <strong>Participants</strong>
            <ul>${participantsList}</ul>
          </div>${waitlistSection}
        `;

        activitiesList.appendChild(activityCard);

        activityCard.querySelectorAll(".remove-participant").forEach((removeButton) => {
          removeButton.addEventListener("click", async () => {
            const participant = decodeURIComponent(removeButton.dataset.email);
            removeButton.disabled = true;

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(name)}/signup?email=${encodeURIComponent(participant)}`,
                { method: "DELETE" }
              );

              const result = await response.json().catch(() => ({}));

              if (!response.ok) {
                throw new Error(result.detail || "Unable to unregister participant");
              }

              showMessage(result.message, "success");
              await fetchActivities();
            } catch (error) {
              removeButton.disabled = false;
              console.error("Error unregistering participant:", error);
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, result.status === "waitlisted" ? "info" : "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
