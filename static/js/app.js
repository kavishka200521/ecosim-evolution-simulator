let populationChart = null;
let fitnessChart = null;
let preyTraitChart = null;
let predatorTraitChart = null;

document.getElementById("runButton").addEventListener("click", runSimulation);
window.addEventListener("load", runSimulation);

function runSimulation() {
    const environment = document.getElementById("environment").value;
    const generations = document.getElementById("generations").value;
    const plants = document.getElementById("plants").value;
    const prey = document.getElementById("prey").value;
    const predators = document.getElementById("predators").value;

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("results").classList.add("hidden");

    fetch("/simulate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            environment: environment,
            generations: generations,
            plants: plants,
            prey: prey,
            predators: predators
        })
    })
        .then(response => response.json())
        .then(data => showResults(data))
        .finally(() => {
            document.getElementById("loading").classList.add("hidden");
            document.getElementById("results").classList.remove("hidden");
        });
}

function showResults(data) {
    document.getElementById("environmentTitle").textContent = data.environment;
    document.getElementById("environmentDescription").textContent = data.environment_description;

    document.getElementById("finalPlants").textContent = data.final_state.plants;
    document.getElementById("finalPrey").textContent = data.final_state.prey;
    document.getElementById("finalPredators").textContent = data.final_state.predators;

    renderExplanation(data.explanation);
    renderTraits("preyTraits", data.prey_traits);
    renderTraits("predatorTraits", data.predator_traits);
    renderPopulationChart(data.history);
    renderFitnessChart(data.prey_trait_history, data.predator_trait_history);
    renderPreyTraitChart(data.prey_trait_history);
    renderPredatorTraitChart(data.predator_trait_history);
}

function renderExplanation(explanation) {
    const list = document.getElementById("explanationList");
    list.innerHTML = "";

    explanation.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
    });
}

function renderTraits(elementId, traits) {
    const wrapper = document.getElementById(elementId);
    wrapper.innerHTML = "";

    Object.entries(traits).forEach(([name, value]) => {
        const percentage = Math.round(value * 100);

        const div = document.createElement("div");
        div.className = "trait";

        div.innerHTML = `
            <div class="trait-title">
                <span>${formatName(name)}</span>
                <span>${percentage}%</span>
            </div>
            <div class="bar">
                <span style="width:${percentage}%"></span>
            </div>
        `;

        wrapper.appendChild(div);
    });
}

function renderPopulationChart(history) {
    const ctx = document.getElementById("populationChart");

    if (populationChart) {
        populationChart.destroy();
    }

    populationChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: history.map(row => row.generation),
            datasets: [
                {
                    label: "Plants",
                    data: history.map(row => row.plants),
                    tension: 0.35
                },
                {
                    label: "Prey",
                    data: history.map(row => row.prey),
                    tension: 0.35
                },
                {
                    label: "Predators",
                    data: history.map(row => row.predators),
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true
        }
    });
}

function renderFitnessChart(preyHistory, predatorHistory) {
    const ctx = document.getElementById("fitnessChart");

    if (fitnessChart) {
        fitnessChart.destroy();
    }

    fitnessChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: preyHistory.map(row => row.generation),
            datasets: [
                {
                    label: "Prey Fitness",
                    data: preyHistory.map(row => row.fitness),
                    tension: 0.35
                },
                {
                    label: "Predator Fitness",
                    data: predatorHistory.map(row => row.fitness),
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 1
                }
            }
        }
    });
}

function renderPreyTraitChart(history) {
    const ctx = document.getElementById("preyTraitChart");

    if (preyTraitChart) {
        preyTraitChart.destroy();
    }

    preyTraitChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: history.map(row => row.generation),
            datasets: [
                {
                    label: "Speed",
                    data: history.map(row => row.speed),
                    tension: 0.35
                },
                {
                    label: "Camouflage",
                    data: history.map(row => row.camouflage),
                    tension: 0.35
                },
                {
                    label: "Reproduction",
                    data: history.map(row => row.reproduction),
                    tension: 0.35
                },
                {
                    label: "Energy Efficiency",
                    data: history.map(row => row.energy_efficiency),
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 1
                }
            }
        }
    });
}

function renderPredatorTraitChart(history) {
    const ctx = document.getElementById("predatorTraitChart");

    if (predatorTraitChart) {
        predatorTraitChart.destroy();
    }

    predatorTraitChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: history.map(row => row.generation),
            datasets: [
                {
                    label: "Speed",
                    data: history.map(row => row.speed),
                    tension: 0.35
                },
                {
                    label: "Hunting Skill",
                    data: history.map(row => row.hunting_skill),
                    tension: 0.35
                },
                {
                    label: "Reproduction",
                    data: history.map(row => row.reproduction),
                    tension: 0.35
                },
                {
                    label: "Energy Efficiency",
                    data: history.map(row => row.energy_efficiency),
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 1
                }
            }
        }
    });
}

function formatName(name) {
    return name
        .replaceAll("_", " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}