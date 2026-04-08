async function pollJob(jobId) {
    const statusEl = document.getElementById("jobStatus");
    const stepEl = document.getElementById("jobStep");
    const resultArea = document.getElementById("resultArea");

    const fetchJob = async () => {
        const res = await fetch(`/jobs/${jobId}`);
        if (!res.ok) {
            throw new Error(`Job-Status konnte nicht geladen werden (${res.status})`);
        }
        return await res.json();
    };

    const applyDoneState = (data) => {
        const result = data.result;

        document.getElementById("origDim").textContent =
            `${result.original_width} × ${result.original_height} px`;
        document.getElementById("heroDim").textContent =
            `${result.hero_width} × ${result.hero_height} px`;

        document.getElementById("origImg").src = result.original_image;
        document.getElementById("heroImg").src = result.hero_image;

        document.getElementById("videoMeta").textContent =
            `Modus: ${result.video_mode} | Effekt: ${result.video_style}`;

        const source = document.getElementById("videoSource");
        const video = document.getElementById("videoPlayer");
        source.src = result.video;
        video.load();

        document.getElementById("capInstagram").value = result.caption.instagram_caption;
        document.getElementById("capHashtags").value = result.caption.hashtags;
        document.getElementById("capStory").value = result.caption.story_text;
        document.getElementById("capPromo").value = result.caption.promo_text;

        resultArea.style.display = "block";
    };

    const tick = async () => {
        try {
            const data = await fetchJob();

            statusEl.textContent = `Status: ${data.status}`;
            stepEl.textContent = `Schritt: ${data.step || "-"}`;

            if (data.status === "done") {
                applyDoneState(data);
                return;
            }

            if (data.status === "failed") {
                stepEl.textContent = `Fehler: ${data.error || "Unbekannt"}`;
                return;
            }

            setTimeout(tick, 3000);
        } catch (err) {
            stepEl.textContent = `Fehler: ${err.message}`;
        }
    };

    tick();
}

document.addEventListener("DOMContentLoaded", () => {
    const jobCard = document.getElementById("jobCard");
    if (jobCard) {
        const jobId = jobCard.dataset.jobId;
        if (jobId) {
            pollJob(jobId);
        }
    }
});
