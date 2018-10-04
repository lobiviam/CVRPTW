import initialSolution


class LocalSearch:
    def __init__(self, graph, routes, capacity):
        self.capacity = capacity
        self.graph = graph
        self.initialSolution = routes
        self.optimized_routes = self.local_search(self.initialSolution)
        self.global_opt_solution = self.iter_loc_search(self.optimized_routes)

    def local_search(self, initial_solution):
        optimized_routes = []
        for route in initial_solution:
            new_route = self.get_optimized_route(route)
            optimized_routes.append(new_route)
        return optimized_routes

    def get_optimized_route(self, route):
        pairs = generate_all_possible_pairs_for_two_opt(len(route))
        for i, j in pairs:
            route_candidate = self.two_opt(route, i, j)
            if route_candidate != route:
                return self.get_optimized_route(route_candidate)
            else:
                continue
        return route

    def two_opt(self, route, i, j):
        a = route[i - 1]['node_id']
        b = route[i]['node_id']
        c = route[j - 1]['node_id']
        d = route[j]['node_id']
        distance_0 = self.graph[a][b]['weight'] + self.graph[c][d]['weight']
        distance_1 = self.graph[a][c]['weight'] + self.graph[b][d]['weight']
        if distance_0 > distance_1:
            route_candidate = route[:i] + [it for it in reversed(route[i:j])] + route[j:]
        else:
            return route
        for index in range(i, len(route_candidate)):  # compute services begin time beginning with node with index i
            previous_node_id = route_candidate[index - 1]['node_id']
            node_id = route_candidate[index]['node_id']
            node_begin_service_time = initialSolution.get_b_j(route_candidate[index]['ready_time'],
                                                              route_candidate[index - 1]['b_i'],
                                                              route_candidate[index - 1]['service_time'],
                                                              self.graph[previous_node_id][node_id]['weight'])
            route_candidate[index]['b_i'] = node_begin_service_time
        if is_route_valid(route_candidate, self.capacity):
            return route_candidate
        else:
            return route

    def iter_loc_search(self, optimised_routes):
        history = [optimised_routes]
        for _ in range(10):
            perturbated_routes = self.perturbation(optimised_routes.copy())
            optimised_routes = self.local_search(perturbated_routes.copy())
            history.append(optimised_routes)
        global_optimum_routes = min(history, key=lambda x: get_objective_function_value(self.graph, x))
        obj_func_val = get_objective_function_value(self.graph, global_optimum_routes)
        print(obj_func_val)
        return global_optimum_routes

    def perturbation(self, solution):
        perturbations_list = []
        route_pairs = generate_all_possible_pairs_of_routes(len(solution))
        for route_a_index, route_b_index in route_pairs:
            node_pair = generate_pairs_of_nodes_from_diffenet_routes(len(solution[route_a_index]),
                                                                     len(solution[route_b_index]))
            for node_a, node_b in node_pair:
                cand_list_swap = self.swap_operation(solution[route_a_index].copy(), solution[route_b_index].copy(),
                                                     node_a,
                                                     node_b)
                cand_list_cross = self.cross_operation(solution[route_a_index].copy(), solution[route_b_index].copy(),
                                                       node_a,
                                                       node_b)
                cand_list_relocate = self.relocate_operation(solution[route_a_index].copy(),
                                                             solution[route_b_index].copy(),
                                                             node_a,
                                                             node_b)
                if cand_list_swap[0]:
                    perturbations_list.append([cand_list_swap, route_a_index, route_b_index])
                if cand_list_cross[0]:
                    perturbations_list.append([cand_list_cross, route_a_index, route_b_index])
                if cand_list_cross[0]:
                    perturbations_list.append([cand_list_relocate, route_a_index, route_b_index])

        optimal_perturbation = max(perturbations_list, key=lambda x: x[0][3])
        solution[optimal_perturbation[1]] = optimal_perturbation[0][1]
        solution[optimal_perturbation[2]] = optimal_perturbation[0][2]
        return solution

    def swap_operation(self, route_a, route_b, node_a, node_b):
        old_distance = get_objective_function_value(self.graph, [route_a, route_b])
        route_a[node_a], route_b[node_b] = route_b[node_b], route_a[node_a]
        delta = old_distance - get_objective_function_value(self.graph, [route_a, route_b])

        route_b = self.update_b_i_for_route(route_b, node_b)
        route_a = self.update_b_i_for_route(route_a, node_a)

        perturbation_valid = is_route_valid(route_a, self.capacity) and is_route_valid(route_b, self.capacity)

        return [perturbation_valid, route_a, route_b, delta]

    def cross_operation(self, route_a, route_b, node_a, node_b):
        old_distance = get_objective_function_value(self.graph, [route_a, route_b])
        route_a, route_b = route_a[:node_a + 1] + route_b[node_b + 1:], route_b[:node_b + 1] + route_a[node_a + 1:]
        delta = old_distance - get_objective_function_value(self.graph, [route_a, route_b])
        route_b = self.update_b_i_for_route(route_b, node_b)
        route_a = self.update_b_i_for_route(route_a, node_a)
        perturbation_valid = is_route_valid(route_a, self.capacity) and is_route_valid(route_b, self.capacity)
        return [perturbation_valid, route_a, route_b, delta]

    def relocate_operation(self, route_a, route_b, node_a, node_b):
        old_distance = get_objective_function_value(self.graph, [route_a, route_b])
        route_b = route_b[:node_b] + [route_a.pop(node_a)] + route_b[node_b:]
        if len(route_a) > 2:
            route_a = self.update_b_i_for_route(route_a, node_a - 1)
        else:
            route_a = []
        route_b = self.update_b_i_for_route(route_b, node_b - 1)
        delta = old_distance - get_objective_function_value(self.graph, [route_a, route_b])
        perturbation_valid = is_route_valid(route_a, self.capacity) and is_route_valid(route_b, self.capacity)
        return [perturbation_valid, route_a, route_b, delta]

    def update_b_i_for_route(self, route, i):
        for index in range(i, len(route)):  # compute services begin time beginning with node with index i
            previous_node_id = route[index - 1]['node_id']
            node_id = route[index]['node_id']
            node_begin_service_time = initialSolution.get_b_j(route[index]['ready_time'],
                                                              route[index - 1]['b_i'],
                                                              route[index - 1]['service_time'],
                                                              self.graph[previous_node_id][node_id]['weight'])
            route[index]['b_i'] = node_begin_service_time
        return route


def is_route_valid(route, capacity):
    total_demand = 0
    for node in route:
        total_demand += node['demand']
        if (node['b_i'] <= node['due_date']) and (total_demand <= capacity):
            continue
        else:
            return False
    return True


def generate_all_possible_pairs_for_two_opt(n):
    pairs = []
    for i in range(1, n):
        for j in range(i + 2, n):
            pairs.append([i, j])
    return pairs


def generate_all_possible_pairs_of_routes(n):
    route_pairs = []
    for i in range(0, n):
        for j in range(i + 1, n):
            route_pairs.append([i, j])
    return route_pairs


def generate_pairs_of_nodes_from_diffenet_routes(n, m):
    node_pairs = []
    for i in range(1, n - 1):
        for j in range(1, m - 1):
            node_pairs.append((i, j))
    return node_pairs


def get_objective_function_value(graph, routes):
    total_value = 0
    for route in routes:
        for i in range(0, len(route) - 1):
            node_dict_i = route[i]
            node_dict_j = route[i + 1]
            node_i_id = node_dict_i['node_id']
            node_j_id = node_dict_j['node_id']
            distance = graph[node_i_id][node_j_id]['weight']
            total_value += distance
    return total_value
