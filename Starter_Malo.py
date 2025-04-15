import json
import random
import time
from collections import defaultdict
from os import times

import networkx as nx
import test_solution
import datetime
from evaluate_node import evaluate_node


def solve(dataset_txt, base_id):
    dataset = json.loads(dataset_txt)
    G = nx.DiGraph()

    for edge in dataset['roads']:
        if edge['isOneWay']:
            G.add_edge(edge['intersectionId1'], edge['intersectionId2'], length=edge['length'], one_way=True)
        else:
            G.add_edge(edge['intersectionId1'], edge['intersectionId2'], length=edge['length'], one_way=False)
            G.add_edge(edge['intersectionId2'], edge['intersectionId1'], length=edge['length'], one_way=False)

    dist_to_base = nx.single_source_dijkstra_path_length(G, base_id, weight='length')

    visited_roads = set()
    visited_nodes = defaultdict(int)
    curr_node = base_id
    path = [base_id]

    num_days = dataset['numDays']
    max_battery = dataset['batteryCapacity']

    for day_i in range(num_days):
        battery_remaining = max_battery

        while True:
            visited_nodes[curr_node] += 1
            neighbors = list(G.neighbors(curr_node))
            random.shuffle(neighbors)

            best_score = -float('inf')
            next_node = None
            next_edge_len = None

            for nxt in neighbors:
                edge_len = G[curr_node][nxt]['length']

                # S'il n'y a aucune route non visitée entre curr_node et ce voisin, on skip
                if (curr_node, nxt) in visited_roads and (nxt, curr_node) in visited_roads:
                    continue

                # Est-ce que ce voisin mène à au moins une route non visitée ?
                has_unexplored = any(
                    (nxt, nn) not in visited_roads and (nn, nxt) not in visited_roads
                    for nn in G.neighbors(nxt)
                )
                if not has_unexplored:
                    continue

                # Ne pas revenir trop souvent au même nœud
                if visited_nodes[nxt] > 4:
                    continue

                # Peut-on y aller ?
                if day_i < num_days - 1:
                    if battery_remaining < edge_len + dist_to_base.get(nxt, float('inf')):
                        continue
                else:
                    if battery_remaining < edge_len:
                        continue

                score = evaluate_node(curr_node, nxt, visited_roads, G, battery_remaining, max_battery, dist_to_base, base_id)
                if score > best_score:
                    best_score = score
                    next_node = nxt
                    next_edge_len = edge_len

            if next_node is None:
                # Retour à la base si pas dernier jour et pas déjà à la base
                if day_i < num_days - 1 and curr_node != base_id:
                    try:
                        path_to_base = nx.shortest_path(G, source=curr_node, target=base_id, weight='length')
                        for i in range(1, len(path_to_base)):
                            e_len = G[path_to_base[i - 1]][path_to_base[i]]['length']
                            if battery_remaining < e_len:
                                break
                            path.append(path_to_base[i])
                            visited_roads.add((path_to_base[i - 1], path_to_base[i]))
                            visited_roads.add((path_to_base[i], path_to_base[i - 1]))
                            battery_remaining -= e_len
                            curr_node = path_to_base[i]
                    except nx.NetworkXNoPath:
                        pass
                break  # Fin de journée

            # Avancer
            path.append(next_node)
            visited_roads.add((curr_node, next_node))
            visited_roads.add((next_node, curr_node))
            battery_remaining -= next_edge_len
            curr_node = next_node

            # Retour forcé si on ne pourra plus rentrer
            if day_i < num_days - 1:
                if dist_to_base.get(curr_node, float('inf')) > battery_remaining:
                    try:
                        path_to_base = nx.shortest_path(G, source=curr_node, target=base_id, weight='length')
                        for i in range(1, len(path_to_base)):
                            e_len = G[path_to_base[i - 1]][path_to_base[i]]['length']
                            if battery_remaining < e_len:
                                break
                            path.append(path_to_base[i])
                            visited_roads.add((path_to_base[i - 1], path_to_base[i]))
                            visited_roads.add((path_to_base[i], path_to_base[i - 1]))
                            battery_remaining -= e_len
                            curr_node = path_to_base[i]
                    except nx.NetworkXNoPath:
                        pass
                    break  # Fin de journée forcée

    return json.dumps({"chargeStationId": base_id, "itinerary": path})




dataset_file = "2_pacman"
dataset = open(f'.\\datasets\\{dataset_file}.json').read()

#print('---------------------------------')
#print(f'Solving {dataset_file}')
score = 0
solution = 0
is_valid = False
#while score < 100:
for i in range(100):
    for  j in range (307):
        new_solution = solve(dataset, j)
    new_score, is_valid, message = test_solution.getSolutionScore(new_solution, dataset)
    if new_score > score and is_valid:
        score = new_score
        solution = new_solution
#print('---------------------------------')
#score, is_valid, message = test_solution.getSolutionScore(solution, dataset)
print(test_solution.getSolutionScore(solution, dataset))
if is_valid:
    print('✅ Solution is valid!')
    print(f'Message: {message}')
    print(f'Score: {score:_}')

    save = input('Save solution? (y/n): ')
    if save.lower() == 'y':
        date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'{dataset_file}_{score}_{date}'

        with open(f'.\\solutions\\{file_name}.json', 'w') as f:
            f.write(solution)
        print('Solution saved')
    else:
        print('Solution not saved')

else:
    print('❌ Solution is invalid')
    print(f'Message: {message}')
