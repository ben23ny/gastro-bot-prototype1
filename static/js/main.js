function createVariantCard(variant, index) {
    const wrapper = document.createElement("div");
    wrapper.className = "card variant-card";

    wrapper.innerHTML = `
        <h2>${variant.label || `Variante ${index + 1}`}</h2>
        <p>Stil: ${variant.style_profile || "-"} | Modus: ${variant.video_mode || "-"} | Effekt: ${variant.video_style || "-"}</p>

        <div class="stats-grid">
            <div class="stat-box">
                <strong>Hero:</strong><br>
                ${variant.hero_width || "-"} × ${variant.hero_height || "-"} px
            </div>
        </div>

        <div class="image-grid">
            <div class="image-box">
                <h3>Hero Motiv</h3>
                <img src="${variant.hero_image || ""}" alt="Hero Motiv ${index + 1}">
            </div>
        </div>

        <div class="video-card-inner">
            <h3>Video</h3>
            <div class="video-preview">
                <video controls autoplay muted loop playsinline>
                    <source src="${variant.video || ""}" type="video/mp4">
                </video>
            </div>
        </div>

        <div class="caption-card-inner">
            <h3>Caption Paket</h3>
            <div class="caption-grid">
                <div class="caption-box">
                    <h4>Instagram Caption</h4>
                    <textarea readonly>${variant.caption?.instagram_caption || ""}</textarea>
                </div>
                <div class="caption-box">
                    <h4>Hashtags</h4>
                    <textarea readonly>${variant.caption?.hashtags || ""}</textarea>
                </div>
                <div class="caption-box">
                    <h4>Story Text</h4>
                    <textarea readonly>${variant.caption?.story_text || ""}</textarea>
                </div>
                <div class="caption-box">
                    <h4>Promo Text</h4>
                    <textarea readonly>${variant.caption?.promo_text || ""}</textarea>
                </div>
            </div>
        </div>
    `;

    return wrapper;
}

async function pollJob(jobId) {
    const statusEl = document.getElementById("jobStatus");
    const stepEl = document.getElementById("jobStep");
    const messageEl = document.getElementById("jobMessage");
    const progressTextEl = document.getElementById("jobProgressText");
    const progressBarEl = document.getElementById("jobProgressBar");
    const errorBoxEl = document.getElementById("jobErrorBox");
    const resultArea = document.getElementById("resultArea");

    const fetchJob = async () => {
        const res = await fetch(`/jobs/${jobId}`);
        if (!res.ok) {
            throw new Error(`Job-Status konnte nicht geladen werden (${res.status})`);
        }
        return await res.json();
    };

    const applyProgress = (data) => {
        const progress = Number(data.progress || 0);

        if (statusEl) statusEl.textContent = `Status: ${data.status || "-"}`;
        if (stepEl) stepEl.textContent = `Schritt: ${data.step || "-"}`;
        if (messageEl) messageEl.textContent = data.message || "";
        if (progressTextEl) progressTextEl.textContent = `${progress}%`;
        if (progressBarEl) progressBarEl.style.width = `${progress}%`;
    };

    const applyDoneState = (data) => {
        const result = data.result;
        if (!result) {
            throw new Error("Kein Ergebnis im Job gefunden.");
        }

        const origDim = document.getElementById("origDim");
        const variantCountText = document.getElementById("variantCountText");
        const origImg = document.getElementById("origImg");
        const variantsContainer = document.getElementById("variantsContainer");

        if (origDim) {
            origDim.textContent = `${result.original_width || "-"} × ${result.original_height || "-"} px`;
        }

        if (variantCountText) {
            variantCountText.textContent = `${result.variant_count || 0} Variante(n)`;
        }

        if (origImg) {
            origImg.src = result.original_image || "";
        }

        if (variantsContainer) {
            variantsContainer.innerHTML = "";
            const variants = Array.isArray(result.variants) ? result.variants : [];
            variants.forEach((variant, index) => {
                variantsContainer.appendChild(createVariantCard(variant, index));
            });
        }

        if (resultArea) {
            resultArea.style.display = "block";
        }
    };

    const showError = (message) => {
        if (errorBoxEl) {
            errorBoxEl.style.display = "block";
            errorBoxEl.textContent = message;
        }
    };

    const tick = async () => {
        try {
            const data = await fetchJob();
            console.log("Job data:", data);
            applyProgress(data);

            if (data.status === "done") {
                applyDoneState(data);
                return;
            }

            if (data.status === "failed") {
                showError(data.error || "Unbekannter Fehler");
                return;
            }

            setTimeout(tick, 2500);
        } catch (err) {
            console.error(err);
            showError(err.message);
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
