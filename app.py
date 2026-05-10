
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

ENVIRONMENTS = {
"Grassland": {
    "description": "Balanced open environment with moderate food and visibility.",
    "plant_growth": 1.15,
    "prey_camouflage_bonus": 0.90,
    "predator_speed_bonus": 1.00
},
"Savannah": {
    "description": "Open dry grassland where speed and energy efficiency are important.",
    "plant_growth": 0.95,
    "prey_camouflage_bonus": 1.05,
    "predator_speed_bonus": 1.15
},
"Forest": {
    "description": "Dense habitat where camouflage helps prey survive.",
    "plant_growth": 1.25,
    "prey_camouflage_bonus": 1.25,
    "predator_speed_bonus": 0.85
},
"Desert": {
    "description": "Harsh environment with low food and high energy pressure.",
    "plant_growth": 0.65,
    "prey_camouflage_bonus": 1.15,
    "predator_speed_bonus": 1.05
},
"Arctic": {
    "description": "Cold environment with slow growth and high survival pressure.",
    "plant_growth": 0.75,
    "prey_camouflage_bonus": 1.20,
    "predator_speed_bonus": 0.90
},
"Wetland": {
    "description": "Resource-rich but unstable ecosystem with rapid population changes.",
    "plant_growth": 1.45,
    "prey_camouflage_bonus": 1.00,
    "predator_speed_bonus": 0.95
}}

def clamp(value, low, high):
    return max(low, min(high, value))

def create_prey():
    return {
        "speed": random.uniform(0.25, 0.80),
        "camouflage": random.uniform(0.20, 0.85),
        "reproduction": random.uniform(0.15, 0.70),
        "energy_efficiency": random.uniform(0.20, 0.85)
    }

def create_predator():
    return {
        "speed": random.uniform(0.25, 0.85),
        "hunting_skill": random.uniform(0.20, 0.85),
        "reproduction": random.uniform(0.10, 0.55),
        "energy_efficiency": random.uniform(0.20, 0.80)
    }

def mutate_traits(traits):
    new_traits = dict(traits)
    for trait in new_traits:
        if random.random() < 0.10:
            new_traits[trait] = clamp(new_traits[trait] + random.uniform(-0.06, 0.06), 0.05, 1.0)
    return new_traits

def prey_fitness(prey, predator, environment):
    env = ENVIRONMENTS[environment]
    survival = (
        prey["speed"] * 0.30
        + prey["camouflage"] * env["prey_camouflage_bonus"] * 0.35
        + prey["energy_efficiency"] * 0.25
        + prey["reproduction"] * 0.10
    )
    predator_pressure = predator["speed"] * env["predator_speed_bonus"] * 0.25 + predator["hunting_skill"] * 0.35
    return clamp(survival - predator_pressure * 0.35, 0.05, 1.0)

def predator_fitness(predator, prey, environment):
    env = ENVIRONMENTS[environment]
    survival = (
        predator["hunting_skill"] * 0.38
        + predator["speed"] * env["predator_speed_bonus"] * 0.28
        + predator["energy_efficiency"] * 0.22
        + predator["reproduction"] * 0.12
    )
    prey_defence = prey["speed"] * 0.20 + prey["camouflage"] * env["prey_camouflage_bonus"] * 0.25
    return clamp(survival - prey_defence * 0.25, 0.05, 1.0)

def explain(final_state, prey_traits, predator_traits, environment):
    reasons = []
    if final_state["prey"] <= 10:
        reasons.append("The prey population nearly collapsed because predator pressure or low resources became too strong.")
    elif final_state["prey"] > final_state["predators"] * 6:
        reasons.append("The prey population became dominant because food and survival traits were favourable.")
    if final_state["predators"] <= 5:
        reasons.append("Predators struggled because hunting success or prey availability became too low.")
    elif final_state["predators"] > final_state["prey"] * 0.5:
        reasons.append("Predators became very successful due to strong hunting traits.")
    if prey_traits["camouflage"] > 0.75:
        reasons.append("Prey camouflage evolved strongly, helping prey avoid predators.")
    if predator_traits["hunting_skill"] > 0.75:
        reasons.append("Predator hunting skill evolved strongly, increasing prey capture.")
    if environment in ["Desert", "Arctic"]:
        reasons.append(f"The {environment} environment created harsh resource pressure.")
    if not reasons:
        reasons.append("The ecosystem reached a fairly balanced state.")
    return reasons[:5]

def run_simulation(environment, generations, plants, prey_count, predator_count):
    prey_traits = create_prey()
    predator_traits = create_predator()

    history = []
    prey_trait_history = []
    predator_trait_history = []
    env = ENVIRONMENTS[environment]

    for generation in range(generations + 1):
        prey_fit = prey_fitness(prey_traits, predator_traits, environment)
        predator_fit = predator_fitness(predator_traits, prey_traits, environment)

        plant_growth = int(plants * 0.10 * env["plant_growth"])
        plant_eaten = int(min(plants, prey_count * 0.45))
        plants = clamp(plants + plant_growth - plant_eaten, 0, 5000)

        food_factor = clamp(plants / max(1, prey_count * 3), 0.0, 1.5)
        prey_births = int(prey_count * prey_traits["reproduction"] * prey_fit * food_factor * 0.35)

        hunting_pressure = predator_traits["hunting_skill"] * predator_traits["speed"] * env["predator_speed_bonus"]
        prey_defence = prey_traits["speed"] * 0.35 + prey_traits["camouflage"] * env["prey_camouflage_bonus"] * 0.35
        predation_rate = clamp(hunting_pressure - prey_defence * 0.45, 0.02, 0.45)

        prey_eaten = int(min(prey_count, predator_count * predation_rate * 1.7))
        prey_deaths = int(prey_count * (0.03 + (1 - prey_traits["energy_efficiency"]) * 0.04))
        prey_count = clamp(prey_count + prey_births - prey_eaten - prey_deaths, 0, 10000)

        predator_births = int(predator_count * predator_traits["reproduction"] * predator_fit * clamp(prey_eaten / max(1, predator_count), 0, 1.5) * 0.18)
        predator_deaths = int(predator_count * (0.06 + (1 - predator_traits["energy_efficiency"]) * 0.06))
        if prey_count < predator_count:
            predator_deaths += int(predator_count * 0.08)
        predator_count = clamp(predator_count + predator_births - predator_deaths, 0, 5000)

        prey_traits = mutate_traits(prey_traits)
        predator_traits = mutate_traits(predator_traits)

        history.append({"generation": generation, "plants": plants, "prey": prey_count, "predators": predator_count})
        prey_trait_history.append({"generation": generation, "speed": round(prey_traits["speed"], 3), "camouflage": round(prey_traits["camouflage"], 3), "reproduction": round(prey_traits["reproduction"], 3), "energy_efficiency": round(prey_traits["energy_efficiency"], 3), "fitness": round(prey_fit, 3)})
        predator_trait_history.append({"generation": generation, "speed": round(predator_traits["speed"], 3), "hunting_skill": round(predator_traits["hunting_skill"], 3), "reproduction": round(predator_traits["reproduction"], 3), "energy_efficiency": round(predator_traits["energy_efficiency"], 3), "fitness": round(predator_fit, 3)})

    final_state = history[-1]
    return {
        "environment": environment,
        "environment_description": env["description"],
        "final_state": final_state,
        "prey_traits": {k: round(v, 3) for k, v in prey_traits.items()},
        "predator_traits": {k: round(v, 3) for k, v in predator_traits.items()},
        "history": history,
        "prey_trait_history": prey_trait_history,
        "predator_trait_history": predator_trait_history,
        "explanation": explain(final_state, prey_traits, predator_traits, environment)
    }

@app.route("/")
def index():
    return render_template("index.html", environments=ENVIRONMENTS.keys())

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json()
    environment = data.get("environment", "Grassland")
    generations = max(10, min(int(data.get("generations", 80)), 200))
    plants = max(100, min(int(data.get("plants", 1200)), 5000))
    prey = max(10, min(int(data.get("prey", 250)), 5000))
    predators = max(1, min(int(data.get("predators", 40)), 1000))
    return jsonify(run_simulation(environment, generations, plants, prey, predators))

if __name__ == "__main__":
    app.run(debug=True)
