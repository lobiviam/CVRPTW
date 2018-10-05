import customers
import initialSolution
import ils

import networkx as nx
import matplotlib.pyplot as plt


def plot_routes(_graph: nx.Graph, route_list):
    print(len(route_list))
    pos = dict(
        zip(_graph.nodes, zip(*[[it[1] for it in _graph.nodes.data(key)] for key in ("x_coord", "y_coord")])))
    color_map = plt.cm.get_cmap('cubehelix')
    for i, route in enumerate(route_list):
        color = color_map((i + 1) / len(route_list))
        nx.draw_networkx_nodes(_graph, nodelist=[it['node_id'] for it in route[1:-1]], pos=pos, node_size=50,
                               node_color=[color[:-1]] * len(route[1:-1]))
        for ind in range(1, len(route)):
            nx.draw_networkx_edges(_graph, pos=pos,
                                   edgelist=[(route[ind]['node_id'], route[ind - 1]['node_id'])],
                                   edge_color=[color])
    plt.show()


def result_output(file_name, solution):
    with open(file_name + '.sol', 'w') as out_file:
        for route in solution:
            for node in route:
                out_file.write(str(node['node_id']) + ' ' + str(node['b_i']) + ' ')
            out_file.write('\n')


def update_b_i_for_route(graph, route, i):
    for index in range(i, len(route)):  # compute services begin time beginning with node with index i
        previous_node_id = route[index - 1]['node_id']
        node_id = route[index]['node_id']
        node_begin_service_time = initialSolution.get_b_j(route[index]['ready_time'],
                                                          route[index - 1]['b_i'],
                                                          route[index - 1]['service_time'],
                                                          graph[previous_node_id][node_id]['weight'])
        route[index]['b_i'] = node_begin_service_time
    return route


if __name__ == '__main__':
    file_name = 'R168'
    customers = customers.Customers(file_name + '.TXT')
    graph = customers.graph
    capacity = customers.capacity
    initSolver = initialSolution.Heuristic(graph, capacity)
    initSolution = initSolver.routes
    local_search = ils.LocalSearch(graph, initSolution, capacity)
    global_optimum_routes = local_search.global_opt_solution
    result_solution = []
    for i in range(len(global_optimum_routes)):
        new = update_b_i_for_route(graph, global_optimum_routes[i], 1)
        result_solution.append(new)
    plot_routes(graph, result_solution)
    result_output(file_name, result_solution)
