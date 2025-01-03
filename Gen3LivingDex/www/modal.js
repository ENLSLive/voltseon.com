document.addEventListener("DOMContentLoaded", () => {
  const openModalBtn = document.getElementById("openModalBtn");

  // Open the modal
  if (openModalBtn) {
      openModalBtn.addEventListener("click", () => {
          createAndShowModal();
      });
  }

  function createAndShowModal() {
      // Create modal elements
      const modal = document.createElement("div");
      modal.id = "modal";
      modal.className = "modal";

      const modalContent = document.createElement("div");
      modalContent.className = "modal-content";

      const closeModalBtn = document.createElement("span");
      closeModalBtn.className = "close";
      closeModalBtn.innerHTML = "&times;";

      // Append close button and content to modal
      modalContent.appendChild(closeModalBtn);
      modalContent.innerHTML += `
          <h2>Modal Title</h2>
          <p>This is a dynamically generated popup modal. The page behind is disabled.</p>
      `;
      modal.appendChild(modalContent);
      document.body.appendChild(modal);

      // Show the modal
      modal.style.display = "block";

      // Close the modal when clicking on the close button
      closeModalBtn.addEventListener("click", () => {
          document.body.removeChild(modal);
      });

      // Close the modal if the user clicks outside the modal content
      window.addEventListener("click", (event) => {
          if (event.target === modal) {
              document.body.removeChild(modal);
          }
      });
  }
});