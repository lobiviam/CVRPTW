class Heuristic:
    def __init__(self, graph, capacity):
        self.graph = graph
        self.capacity = capacity
        self.routes = self.nearest_neighbor_heuristic()

    def nearest_neighbor_heuristic(self):
        graph = self.graph.copy()
        route_list = []
        cond = True
        while cond:
            new_route, modified_graph = self.get_route(graph)
            graph = modified_graph.copy()
            route_list.append(new_route)
            cond = len(graph.nodes) > 1
        return route_list

    def get_route(self, graph):
        first_node_in_route, last_node_in_route = graph.nodes(data=True)[0].copy(), graph.nodes(data=True)[0].copy()
        first_node_in_route['node_id'] = 0
        last_node_in_route['node_id'] = 0
        first_node_in_route['b_i'] = 0
        route = [first_node_in_route, last_node_in_route]
        capacity = self.capacity
        graph_copy = graph.copy()
        while True:
            node_metrics_dict = {}
            for node, node_info in [it for it in graph_copy.nodes(data=True) if it[0] != 0]:
                last_added_node = route[-2]
                weight = graph[node][last_added_node['node_id']]['weight']
                b_j = get_b_j(node_info['ready_time'], last_added_node['b_i'], last_added_node['service_time'],
                              weight)
                t_ij = get_T_i_j(last_added_node['b_i'], b_j, last_added_node['service_time'])
                v_ij = get_v_i_j(node_info['due_date'], last_added_node['b_i'], last_added_node['service_time'],
                                 weight)
                c_ij = get_c_ij(weight, t_ij, v_ij, 0.95, 0.0, 0.05)
                node_metrics_dict[node] = c_ij

            if len(node_metrics_dict.keys()) == 0:
                break
            next_node_id = min(set(node_metrics_dict.keys()), key=node_metrics_dict.get)
            next_node_info = graph.nodes(data=True)[next_node_id]
            last_added_node = route[-2]
            assert last_added_node != 0
            weight = graph[next_node_id][last_added_node['node_id']]['weight']
            next_node_b_i = get_b_j(next_node_info['ready_time'], last_added_node['b_i'],
                                    last_added_node['service_time'],
                                    weight)
            buffr_node_info = next_node_info.copy()
            buffr_node_info['node_id'] = next_node_id
            buffr_node_info['b_i'] = next_node_b_i

            last_node_in_route_b_i = get_b_j(last_node_in_route['ready_time'], next_node_b_i,
                                             next_node_info['service_time'],
                                             graph[next_node_id][last_node_in_route['node_id']]['weight'])

            if (capacity - next_node_info['demand']) < 0 \
                    or last_node_in_route_b_i > last_node_in_route['due_date'] \
                    or buffr_node_info['b_i'] > buffr_node_info['due_date']:
                break
            route.insert(-1, buffr_node_info)
            graph_copy.remove_node(next_node_id)
            last_node_in_route['b_i'] = last_node_in_route_b_i
            capacity -= next_node_info['demand']
        return route, graph_copy


def get_b_j(e_j, b_i, s_i, weight_i_j):  # compute services begin time
    """
    :param e_j: ready time for second node
    :param b_i: service begin time for first node
    :param s_i: service time of first node
    :param weight_i_j: distance between nodes
    :return: service begin time for second node
    """
    return max([e_j, b_i + s_i + weight_i_j])


def get_T_i_j(b_i, b_j, s_i):
    """

    :param b_i: service begin time for first node
    :param b_j: service begin time for second node
    :param s_i: service time of first node
    :return: T_ij - the time difference between the completion of service at i and the beginning of service at j
    """
    return b_j - (b_i + s_i)


def get_v_i_j(l_j, b_i, s_i, t_ij):
    """

    :param l_j: due date for second node
    :param b_i: service begin time for first node
    :param s_i: service time of first node
    :param t_ij: distance between nodes
    :return: urgency of delivery to customer j
    """
    return l_j - (b_i + s_i + t_ij)


def get_c_ij(d_ij, t_ij, v_ij, a1, a2, a3):
    """

    :param d_ij: distance between nodes
    :param t_ij: the time difference between the completion of service at i and the beginning of service at j
    :param v_ij: urgency of delivery to customer j
    :return: metric used in nearest neighbor heuristic
    """
    return a1 * d_ij + a2 * t_ij + a3 * v_ij
