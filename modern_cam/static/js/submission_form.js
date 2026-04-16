(() => {
    const metricsRoot = document.querySelector("[data-submission-metrics]");
    if (!metricsRoot) {
        return;
    }

    const titleField = document.querySelector("[data-character-target='title']");
    const abstractField = document.querySelector("[data-word-target='abstract']");
    const topicFields = document.querySelectorAll("input[name='topics']");
    const authorForms = () => Array.from(document.querySelectorAll("#author-formset .formset-entry")).filter((entry) => {
        const deleteField = entry.querySelector("input[name$='-DELETE']");
        return !(deleteField && deleteField.checked);
    });
    const titleCount = metricsRoot.querySelector("[data-character-count-title]");
    const abstractCount = metricsRoot.querySelector("[data-word-count-abstract]");
    const topicCount = metricsRoot.querySelector("[data-topic-count]");
    const authorCount = metricsRoot.querySelector("[data-author-count]");
    const previewTitle = document.querySelector("[data-preview-title]");
    const previewType = document.querySelector("[data-preview-type]");
    const previewTopicSummary = document.querySelector("[data-preview-topic-summary]");
    const previewAbstract = document.querySelector("[data-preview-abstract]");

    const wordCount = (value) => {
        const matches = (value || "").trim().match(/\b[\w'-]+\b/g);
        return matches ? matches.length : 0;
    };

    const escapeHtml = (value) =>
        value
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;");

    const update = () => {
        if (titleField && titleCount) {
            titleCount.textContent = String(titleField.value.trim().length);
        }
        if (abstractField && abstractCount) {
            abstractCount.textContent = String(wordCount(abstractField.value));
        }
        if (topicFields.length && topicCount) {
            topicCount.textContent = String(Array.from(topicFields).filter((field) => field.checked).length);
        }
        if (authorCount) {
            authorCount.textContent = String(authorForms().length);
        }
        if (previewTitle && titleField) {
            previewTitle.textContent = titleField.value.trim() || "Untitled abstract";
        }
        if (previewType) {
            const selectedOption = document.querySelector("#id_presentation_type option:checked");
            previewType.textContent = selectedOption ? selectedOption.textContent : "Presentation type";
        }
        if (previewTopicSummary && topicFields.length) {
            const labels = Array.from(topicFields)
                .filter((field) => field.checked)
                .map((field) => {
                    const label = document.querySelector(`label[for='${field.id}']`);
                    return label ? label.textContent.trim() : "";
                })
                .filter(Boolean);
            previewTopicSummary.textContent = labels.length ? labels.join(" · ") : "No topics selected";
        }
        if (previewAbstract && abstractField) {
            const safe = escapeHtml(abstractField.value.trim() || "Start typing to preview the abstract body here.");
            previewAbstract.innerHTML = safe.replaceAll("\n", "<br>");
        }
    };

    if (titleField) {
        titleField.addEventListener("input", update);
    }
    if (abstractField) {
        abstractField.addEventListener("input", update);
    }
    document.addEventListener("change", update);
    document.addEventListener("click", () => window.requestAnimationFrame(update));
    update();
})();
