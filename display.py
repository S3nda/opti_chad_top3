import turtle
import time
import json
import os


def animate_path(dataset, itinerary):
    intersections = dataset["intersections"]
    roads = dataset["roads"]

    # Initialiser Turtle
    screen = turtle.Screen()
    screen.title("Animation de l'itinéraire")
    screen.setup(width=800, height=800)
    drawer = turtle.Turtle()
    drawer.speed(0)
    drawer.hideturtle()

    mover = turtle.Turtle()
    mover.shape("circle")
    mover.color("red")
    mover.penup()

    # Récupérer les positions des nœuds
    id_to_pos = {}
    scale = 25  # Agrandissement pour affichage écran

    for node in intersections:
        x = node["lng"] * scale
        y = node["lat"] * scale
        id_to_pos[node["id"]] = (x, y)

    # Tracer les routes
    drawer.pensize(2)
    drawer.color("gray")
    for road in roads:
        x1, y1 = id_to_pos[road["intersectionId1"]]
        x2, y2 = id_to_pos[road["intersectionId2"]]
        drawer.penup()
        drawer.goto(x1, y1)
        drawer.pendown()
        drawer.goto(x2, y2)

    # Tracer les nœuds
    for node_id, (x, y) in id_to_pos.items():
        drawer.penup()
        drawer.goto(x, y)
        drawer.dot(15, "blue")
        drawer.write(f"{node_id}", align="center", font=("Arial", 10, "bold"))

    # Animation du trajet
    mover.goto(id_to_pos[itinerary[0]])
    mover.pendown()
    for i in range(1, len(itinerary)):
        next_pos = id_to_pos[itinerary[i]]
        mover.setheading(mover.towards(next_pos))
        mover.goto(next_pos)
        time.sleep(0.5)

    turtle.done()


def load_first_dataset_and_solution(
    dataset_folder="./datasets", solution_folder="./solutions"
):
    # Lister les fichiers JSON dans les deux dossiers
    dataset_files = sorted(
        [f for f in os.listdir(dataset_folder) if f.endswith(".json")]
    )
    solution_files = sorted(
        [f for f in os.listdir(solution_folder) if f.endswith(".json")]
    )

    if not dataset_files or not solution_files:
        raise FileNotFoundError("Aucun fichier JSON trouvé dans l'un des dossiers.")

    # On prend le premier fichier (ordre alphabétique)
    dataset_path = os.path.join(dataset_folder, dataset_files[0])
    solution_path = os.path.join(solution_folder, solution_files[0])

    # Chargement des fichiers
    with open(dataset_path) as f_dataset:
        dataset = json.load(f_dataset)

    with open(solution_path) as f_solution:
        solution = json.load(f_solution)

    return dataset, solution


# Exécution
dataset, solution = load_first_dataset_and_solution()
animate_path(dataset, solution["itinerary"])
