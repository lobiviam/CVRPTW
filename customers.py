import re
import networkx as nx
from scipy.spatial import distance


class Customers:
    def __init__(self, file_name):
        file = open('./instances/' + file_name)
        self.data = file.read().split('\n')
        self.vehicle_number = int(re.findall('[0-9]+', self.data[4])[0])
        self.capacity = int(re.findall('[0-9]+', self.data[4])[1])
        self.graph = self.create_graph()

    def create_graph(self):
        graph = nx.Graph()
        for i in range(9, len(self.data) - 1):
            customer_data = re.findall('[0-9]+', self.data[i])
            customer_dict = dict()
            # print(customer_data)
            cust_id = int(customer_data[0])
            customer_dict['x_coord'] = int(customer_data[1])
            customer_dict['y_coord'] = int(customer_data[2])
            customer_dict['demand'] = int(customer_data[3])
            customer_dict['ready_time'] = int(customer_data[4])
            customer_dict['due_date'] = int(customer_data[5])
            customer_dict['service_time'] = int(customer_data[6])

            graph.add_node(cust_id, **customer_dict)

            for node, node_information in graph.nodes(data=True):
                if cust_id != node:
                    node_coord = node_information['x_coord'], node_information['y_coord']
                    cust_coord = customer_dict['x_coord'], customer_dict['y_coord']
                    dist = distance.euclidean(node_coord, cust_coord)
                    graph.add_edge(node, cust_id, weight=dist)
        return graph




