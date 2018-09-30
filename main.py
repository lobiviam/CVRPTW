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
    # print(color_map)
    for i, route in enumerate(route_list):
        color = color_map((i + 1) / len(route_list))
        # print(color[:-1])
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


if __name__ == '__main__':
    file_name = 'C108'
    customers = customers.Customers(file_name + '.txt')
    graph = customers.graph
    capacity = customers.capacity
    initSolver = initialSolution.Heuristic(graph, capacity)
    initSolution = initSolver.routes
    print(ils.get_objective_function_value(graph, initSolution))
    local_search = ils.LocalSearch(graph, initSolution, capacity)
    optimazed_routes = local_search.optimized_routes
    # for route in optimazed_routes:
    #     print('\n')
    #     print(optimazed_routes)
    print(ils.get_objective_function_value(graph, optimazed_routes))
    plot_routes(graph, initSolution)
    result_output(file_name, optimazed_routes)
