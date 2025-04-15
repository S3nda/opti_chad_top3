
def evaluate_node(current, neighbor, visited_roads, G, battery_remaining, max_battery, dist_to_base, base_id):
    score = 0

    edge = (current, neighbor)

    # Si route déjà visitée → pénalité
    if edge in visited_roads or (neighbor, current) in visited_roads:
        score -= 1000

    # Bonus si le voisin mène à plein de routes non visitées
    unexplored_neighbors = 0
    for nn in G.neighbors(neighbor):
        if (neighbor, nn) not in visited_roads:
            unexplored_neighbors += 1
    score += 10 * unexplored_neighbors

    # Plus proche → mieux
    score -= G[current][neighbor]['length']

    # Ajout du "magnet" vers la base quand la batterie est basse
    ratio = battery_remaining / max_battery
    if ratio < 0.5:
        # Plus la batterie est faible, plus on valorise la proximité avec la base
        base_distance = dist_to_base.get(neighbor, float('inf'))
        if base_distance < float('inf'):
            score += int((1 - ratio) * 50 / (1 + base_distance))  # plus c'est proche, plus c'est boosté


    return score