let samplesCache = {};
let benchmarkChart = null;

document.addEventListener("DOMContentLoaded", () => {
    fetchSamples();
    fetchAnalytics();
});

function switchTab(tabId) {
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));

    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    const activeSec = document.getElementById(`sec-${tabId}`);
    if (activeBtn) activeBtn.classList.add("active");
    if (activeSec) activeSec.classList.add("active");
}

async function fetchSamples() {
    try {
        const res = await fetch("/api/samples");
        if (res.ok) {
            samplesCache = await res.json();
        }
    } catch (err) {
        console.warn("Não foi possível carregar amostras prévias:", err);
    }
}

function loadSample(levelKey) {
    if (samplesCache[levelKey]) {
        document.getElementById("classify-input-text").value = samplesCache[levelKey].text;
    } else {
        const fallbackTexts = {
            "Ensino Fundamental I": "O menino viu o gato no jardim. O gato era bonito e correu atrás da bola de meia. A mãe chamou para comer sopa.",
            "Ensino Fundamental II": "Tanto o registro formal quanto o informal atendem a necessidades de comunicação. O domínio da gramática normativa é importante para a vida escolar.",
            "Ensino Médio": "Um recurso presente em qualquer planilha eletrônica é o referenciamento relativo e absoluto de células em fórmulas matemáticas.",
            "Ensino Superior": "A gestão de logística e localização em redes cíclicas envolve a otimização de nós centrais para minimizar distâncias ponderadas."
        };
        document.getElementById("classify-input-text").value = fallbackTexts[levelKey] || "";
    }
}

function clearClassifierInput() {
    document.getElementById("classify-input-text").value = "";
    document.getElementById("classifier-results").classList.add("hidden");
    document.getElementById("classifier-placeholder").classList.remove("hidden");
    document.getElementById("predicted-badge").innerText = "Aguardando Análise";
    document.getElementById("predicted-badge").className = "badge badge-neutral";
}

async function handleClassify() {
    const text = document.getElementById("classify-input-text").value.trim();
    if (!text) {
        alert("Por favor, insira um texto para analisar.");
        return;
    }

    const btn = document.getElementById("btn-classify");
    btn.disabled = true;
    btn.innerText = "Analisando...";

    try {
        const res = await fetch("/api/classify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Erro ao classificar o texto.");
        }

        const data = await res.json();
        renderClassifierResults(data);

    } catch (err) {
        alert("Erro: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Analisar e Classificar Texto`;
    }
}

function renderClassifierResults(data) {
    document.getElementById("classifier-placeholder").classList.add("hidden");
    document.getElementById("classifier-results").classList.remove("hidden");

    document.getElementById("res-predicted-level").innerText = data.predicted_level;
    document.getElementById("res-model-used").innerText = `Modelo Utilizado: ${data.model_used}`;

    const badge = document.getElementById("predicted-badge");
    badge.innerText = `Predito: ${data.predicted_level}`;
    badge.className = "badge badge-accent";

    const container = document.getElementById("prob-bars-container");
    container.innerHTML = "";

    const orderedLabels = ["Ensino Fundamental I", "Ensino Fundamental II", "Ensino Médio", "Ensino Superior"];
    orderedLabels.forEach(lbl => {
        const prob = data.probabilities[lbl] || 0;
        const pct = (prob * 100).toFixed(1);
        const isMax = lbl === data.predicted_level;

        const itemHtml = `
            <div class="prob-item">
                <div class="prob-info">
                    <span>${lbl}</span>
                    <strong>${pct}%</strong>
                </div>
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill ${isMax ? 'highlight' : ''}" style="width: ${pct}%"></div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML("beforeend", itemHtml);
    });

    const canRatio = data.canonicity.ratio;
    const canPct = (canRatio * 100).toFixed(1);
    document.getElementById("res-canonicity-ratio").innerText = `${canPct}%`;
    document.getElementById("res-canon-count").innerText = data.canonicity.canonical_count;
    document.getElementById("res-total-words").innerText = data.canonicity.total_words;

    const deg = canRatio * 360;
    document.getElementById("score-circle").style.background =
        `conic-gradient(var(--accent) ${deg}deg, var(--border-subtle) ${deg}deg)`;

    const canonChips = document.getElementById("canon-chips");
    const nonCanonChips = document.getElementById("non-canon-chips");
    canonChips.innerHTML = "";
    nonCanonChips.innerHTML = "";

    data.canonicity.canonical_samples.forEach(s => {
        const syll = s.syllables.length ? s.syllables.join("-") : s.word;
        canonChips.insertAdjacentHTML("beforeend", `<span class="chip chip-canonical" title="Sílabas: ${syll}">${s.word}</span>`);
    });
    if (!data.canonicity.canonical_samples.length) {
        canonChips.innerHTML = `<span class="text-muted" style="font-size:0.75rem;">Nenhuma palavra CV encontrada</span>`;
    }

    data.canonicity.non_canonical_samples.forEach(s => {
        nonCanonChips.insertAdjacentHTML("beforeend", `<span class="chip chip-non-canonical">${s.word}</span>`);
    });
    if (!data.canonicity.non_canonical_samples.length) {
        nonCanonChips.innerHTML = `<span class="text-muted" style="font-size:0.75rem;">Nenhuma palavra não-CV encontrada</span>`;
    }

    document.getElementById("stat-flesch").innerText = data.features.flesch_reading_ease;
    document.getElementById("stat-avg-sentence").innerText = data.features.avg_sentence_length;
    document.getElementById("stat-avg-word").innerText = data.features.avg_word_length;
    document.getElementById("stat-complex").innerText = `${(data.features.complex_word_ratio * 100).toFixed(1)}%`;
}

function updateIntensityLabel(val) {
    document.getElementById("lbl-intensity-val").innerText = `${val}%`;
}

function copyFromClassifier() {
    const text = document.getElementById("classify-input-text").value.trim();
    if (text) {
        document.getElementById("mutate-input-text").value = text;
    } else {
        alert("Nenhum texto no classificador para copiar.");
    }
}

async function handleMutate() {
    const text = document.getElementById("mutate-input-text").value.trim();
    if (!text) {
        alert("Por favor, insira o texto que deseja mutar.");
        return;
    }

    const ops = [];
    if (document.getElementById("chk-synonym").checked) ops.push("synonym");
    if (document.getElementById("chk-antonym").checked) ops.push("antonym");
    if (document.getElementById("chk-gender").checked) ops.push("gender");
    if (document.getElementById("chk-paraphrase").checked) ops.push("paraphrase");

    if (ops.length === 0) {
        alert("Selecione pelo menos um operador de mutação.");
        return;
    }

    const intensity = parseFloat(document.getElementById("input-intensity").value) / 100.0;

    const btn = document.getElementById("btn-mutate");
    btn.disabled = true;
    btn.innerText = "Mutando Texto...";

    try {
        const res = await fetch("/api/mutate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, operations: ops, intensity })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Erro ao mutar o texto.");
        }

        const data = await res.json();
        renderMutationResults(data);

    } catch (err) {
        alert("Erro: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.13 15.57a10 10 0 1 0 3.8-11.66l-5.43 5.43"></path></svg> Gerar Mutação e Avaliar Impacto`;
    }
}

function renderMutationResults(data) {
    const resultsContainer = document.getElementById("mutation-results");
    resultsContainer.classList.remove("hidden");

    const shiftTitle = document.getElementById("shift-title");
    const shiftDesc = document.getElementById("shift-desc");
    const shiftIconBox = document.getElementById("shift-icon-box");

    if (data.complexity_changed) {
        shiftTitle.innerText = `Shift de Complexidade Detectado (${data.before.predicted_level} → ${data.after.predicted_level})`;
        shiftDesc.innerText = `As mutações sintáticas/semânticas alteraram a classificação do modelo para um novo nível escolar.`;
        shiftIconBox.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg>`;
    } else {
        shiftTitle.innerText = `Nível de Complexidade Mantido (${data.before.predicted_level})`;
        shiftDesc.innerText = `As mutações alteraram a superfície do texto, mas o nível de complexidade predito permaneceu estável.`;
        shiftIconBox.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    }

    document.getElementById("mut-before-level").innerText = data.before.predicted_level;
    document.getElementById("mut-original-text").innerText = data.original_text;
    document.getElementById("mut-before-canon").innerText = `${(data.before.canonicity_ratio * 100).toFixed(1)}%`;
    document.getElementById("mut-before-flesch").innerText = data.before.features.flesch_reading_ease || 0;

    document.getElementById("mut-after-level").innerText = data.after.predicted_level;
    document.getElementById("mut-mutated-text").innerText = data.mutated_text;
    document.getElementById("mut-after-canon").innerText = `${(data.after.canonicity_ratio * 100).toFixed(1)}%`;
    document.getElementById("mut-after-flesch").innerText = data.after.features.flesch_reading_ease || 0;

    const diffViewer = document.getElementById("diff-viewer-content");
    diffViewer.innerHTML = "";

    data.diff_tokens.forEach(tok => {
        if (tok.type === "equal") {
            diffViewer.insertAdjacentText("beforeend", tok.text + " ");
        } else if (tok.type === "replace") {
            diffViewer.insertAdjacentHTML("beforeend", `<span class="diff-tok-replace" title="Substituiu: ${tok.old}">${tok.new}</span> `);
        } else if (tok.type === "insert") {
            diffViewer.insertAdjacentHTML("beforeend", `<span class="diff-tok-insert">${tok.text}</span> `);
        } else if (tok.type === "delete") {
            diffViewer.insertAdjacentHTML("beforeend", `<span class="diff-tok-delete">${tok.text}</span> `);
        }
    });
}

async function fetchAnalytics() {
    try {
        const res = await fetch("/api/analytics");
        if (!res.ok) return;
        const data = await res.json();

        if (data.benchmark_results) {
            renderBenchmarkTable(data.benchmark_results);
            renderBenchmarkChart(data.benchmark_results);
            renderConfusionMatrix(data.benchmark_results, data.active_model);
        }
    } catch (err) {
        console.warn("Analytics não disponíveis:", err);
    }
}

function renderBenchmarkTable(results) {
    const tbody = document.querySelector("#table-benchmark-metrics tbody");
    tbody.innerHTML = "";

    Object.entries(results).forEach(([modelName, metrics]) => {
        const row = `
            <tr>
                <td><strong>${modelName}</strong></td>
                <td>${(metrics.accuracy * 100).toFixed(2)}%</td>
                <td>${metrics.f1_macro.toFixed(4)}</td>
                <td>${metrics.f1_weighted.toFixed(4)}</td>
                <td>${metrics.precision.toFixed(4)}</td>
                <td>${metrics.recall.toFixed(4)}</td>
            </tr>
        `;
        tbody.insertAdjacentHTML("beforeend", row);
    });
}

function renderBenchmarkChart(results) {
    const ctx = document.getElementById("chart-models-benchmark");
    if (!ctx) return;

    const labels = Object.keys(results);
    const accuracies = labels.map(k => (results[k].accuracy * 100).toFixed(2));
    const f1s = labels.map(k => (results[k].f1_macro * 100).toFixed(2));

    if (benchmarkChart) benchmarkChart.destroy();

    benchmarkChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Acurácia (%)',
                    data: accuracies,
                    backgroundColor: '#2563eb',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                },
                {
                    label: 'F1-Score Macro (%)',
                    data: f1s,
                    backgroundColor: '#3f3f46',
                    borderColor: '#52525b',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#fafafa' } }
            },
            scales: {
                x: { ticks: { color: '#a1a1aa' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#a1a1aa' }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 50, max: 100 }
            }
        }
    });
}

function renderConfusionMatrix(results, activeModelName) {
    const container = document.getElementById("confusion-matrix-table-container");
    if (!container) return;

    const modelKey = activeModelName && results[activeModelName] ? activeModelName : Object.keys(results)[0];
    const cm = results[modelKey].confusion_matrix;
    const labels = ["EF I", "EF II", "EM", "ES"];

    let tableHtml = `
        <table class="custom-table" style="text-align:center;">
            <thead>
                <tr>
                    <th>Real \\ Predito</th>
                    ${labels.map(l => `<th>${l}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
    `;

    cm.forEach((row, i) => {
        tableHtml += `<tr><td><strong>${labels[i]}</strong></td>`;
        row.forEach((val, j) => {
            const isDiag = i === j;
            const bg = isDiag ? 'rgba(37, 99, 235, 0.2)' : 'rgba(255, 255, 255, 0.02)';
            tableHtml += `<td style="background:${bg}; font-weight:${isDiag ? '600' : 'normal'};">${val}</td>`;
        });
        tableHtml += `</tr>`;
    });

    tableHtml += `</tbody></table>`;
    container.innerHTML = tableHtml;
}
