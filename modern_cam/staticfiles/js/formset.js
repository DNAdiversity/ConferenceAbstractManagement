document.addEventListener("click", (event) => {
  const addButton = event.target.closest("[data-add-formset]");
  if (addButton) {
    const container = document.querySelector(addButton.dataset.addFormset);
    const template = document.querySelector(addButton.dataset.template);
    if (!container || !template) {
      return;
    }

    const totalInput = document.querySelector('[name="authors-TOTAL_FORMS"]');
    const currentIndex = Number(totalInput.value);
    const markup = template.innerHTML.replaceAll("__prefix__", currentIndex);
    container.insertAdjacentHTML("beforeend", markup);
    totalInput.value = currentIndex + 1;
    return;
  }

  const removeButton = event.target.closest("[data-remove-form]");
  if (removeButton) {
    const entry = removeButton.closest(".formset-entry");
    if (!entry) {
      return;
    }

    const deleteInput = entry.querySelector('input[type="checkbox"][name$="-DELETE"]');
    if (deleteInput) {
      deleteInput.checked = true;
      entry.hidden = true;
    } else {
      entry.remove();
    }
  }
});
