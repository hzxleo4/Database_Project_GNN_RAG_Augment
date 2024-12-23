import networkx as nx
from collections import deque
#import walker

import json
with open('entities_names.json') as f:
    entities_names = json.load(f)
names_entities = {v: k for k, v in entities_names.items()}
def get_neigbors(g, node, depth=1):
    output = {}
    layers = dict(nx.bfs_successors(g, source=node, depth_limit=depth))
    nodes = [node]
    for i in range(1,depth+1):
        output[i] = []
        for x in nodes:
            output[i].extend(layers.get(x,[]))
        nodes = output[i]
    return output
def build_graph(graph: list, entities=None, encrypt=False) -> nx.Graph:
    print("build graph")
    G = nx.Graph()
    for triplet in graph:
        h, r, t = triplet
        #entities=[]
        if encrypt:
            if (h in names_entities) and (names_entities[h]  in entities):
                h = names_entities[h]
            if (t in names_entities) and (names_entities[t]  in entities):
                t = names_entities[t]
        G.add_edge(h, t, relation=r.strip())
    print("n_of_nodes",G.number_of_nodes())
    print("n_of_edges",G.number_of_edges())
    return G

# 定义一个函数来进行宽度优先搜索
def bfs_with_rule(graph, start_node, target_rule, max_p = 10):
    result_paths = []
    queue = deque([(start_node, [])])  # 使用队列存储待探索节点和对应路径
    while queue:
        current_node, current_path = queue.popleft()

        # 如果当前路径符合规则，将其添加到结果列表中
        if len(current_path) == len(target_rule):
            result_paths.append(current_path)
            # if len(result_paths) >= max_p:
            #     break
            
        # 如果当前路径长度小于规则长度，继续探索
        if len(current_path) < len(target_rule):
            if current_node not in graph:
                continue
            for neighbor in graph.neighbors(current_node):
                # 剪枝：如果当前边类型与规则中的对应位置不匹配，不继续探索该路径
                rel = graph[current_node][neighbor]['relation']
                if rel != target_rule[len(current_path)] or len(current_path) > len(target_rule):
                    continue
                queue.append((neighbor, current_path + [(current_node, rel,neighbor)]))
    
    return result_paths
def get_neigbors(graph: nx.Graph, node, depth=1):
    output = {}
    layers = dict(nx.bfs_successors(graph, source=node, depth_limit=depth))
    nodes = [node]
    for i in range(1,depth+1):
        output[i] = []
        for x in nodes:
            output[i].extend(layers.get(x,[]))
        nodes = output[i]
    return output
def add_graph_structure(a_entity: list, graph: nx.Graph, exist_path) -> list:
    new_path = []
    # print("a_entity",a_entity)
    for t in a_entity:
        if t not in graph:
            continue
        nei_t_list = get_neigbors(graph,t)
        # print("nei_t_list",nei_t_list)
        for nei_t in nei_t_list[1]:
            # print("nei_t",nei_t)
            if nei_t in a_entity:
                if((t,nei_t) not in exist_path):
                    temp = []
                    exist_path.append((t,nei_t))
                    exist_path.append((nei_t,t))
                    tri = (t, graph[t][nei_t]['relation'], nei_t)
                    temp.append(tri)
                    new_path.append(temp)
                    # print("add",t,nei_t)
                # continue
            nei_nei_t_list = get_neigbors(graph,nei_t)
            # print(nei_t,"nei_nei_t_list",nei_nei_t_list)
            for nei_nei_t in nei_nei_t_list[1]:
                # print("nei_nei_t",nei_nei_t)
                if nei_nei_t != t and nei_nei_t in a_entity:
                    if (t,nei_t) not in exist_path or (nei_t,nei_nei_t) not in exist_path:
                        if (t,nei_t) not in exist_path:
                            exist_path.append((t,nei_t))
                            exist_path.append((nei_t,t))
                        if (nei_t,nei_nei_t) not in exist_path:
                            exist_path.append((nei_nei_t,nei_t))
                            exist_path.append((nei_t,nei_nei_t))
                        temp =[]
                        tri = (t, graph[t][nei_t]['relation'], nei_t)
                        temp.append(tri)
                        tri = (nei_t, graph[nei_t][nei_nei_t]['relation'], nei_nei_t)
                        temp.append(tri)
                        new_path.append(temp)
                        print("2",t,nei_t,nei_nei_t)
            # print(nei_t)
        # break
    print(new_path)
    return new_path
def get_truth_paths2(q_entity: list, a_entity: list, graph: nx.Graph,has_exist_edges) -> list:
    '''
    Get shortest paths connecting question and answer entities.
    '''
    # Select paths
    paths = []
    for h in q_entity:
        if h not in graph:
            continue
        for t in a_entity:
            if t not in graph:
                continue
            try:
                for p in nx.all_shortest_paths(graph, h, t):
                    paths.append(p)
            except:
                pass
    # Add relation to paths
    result_paths = []
    for p in paths:
        tmp = []
        for i in range(len(p)-1):
            u = p[i]
            v = p[i+1]
            tri = (u, graph[u][v]['relation'], v)
            tmp.append(tri)
            if (u,v) not in has_exist_edges:
                has_exist_edges.append((u,v))
                has_exist_edges.append((v,u))
        result_paths.append(tmp)
    return result_paths
def get_truth_paths(q_entity: list, a_entity: list, graph: nx.Graph) -> list:
    '''
    Get shortest paths connecting question and answer entities.
    '''
    # Select paths
    paths = []
    for h in q_entity:
        if h not in graph:
            continue
        for t in a_entity:
            if t not in graph:
                continue
            try:
                for p in nx.all_shortest_paths(graph, h, t):
                    paths.append(p)
            except:
                pass
    # Add relation to paths
    result_paths = []
    for p in paths:
        tmp = []
        for i in range(len(p)-1):
            u = p[i]
            v = p[i+1]
            tmp.append((u, graph[u][v]['relation'], v))
        result_paths.append(tmp)
    return result_paths

    
def get_simple_paths(q_entity: list, a_entity: list, graph: nx.Graph, hop=2) -> list:
    '''
    Get all simple paths connecting question and answer entities within given hop
    '''
    # Select paths
    paths = []
    for h in q_entity:
        if h not in graph:
            continue
        for t in a_entity:
            if t not in graph:
                continue
            try:
                for p in nx.all_simple_edge_paths(graph, h, t, cutoff=hop):
                    paths.append(p)
            except:
                pass
    # Add relation to paths
    result_paths = []
    for p in paths:
        result_paths.append([(e[0], graph[e[0]][e[1]]['relation'], e[1]) for e in p])
    return result_paths

def get_negative_paths(q_entity: list, a_entity: list, graph: nx.Graph, n_neg: int, hop=2) -> list:
    '''
    Get negative paths for question witin hop
    '''
    # sample paths
    start_nodes = []
    end_nodes = []
    node_idx = list(graph.nodes())
    for h in q_entity:
        if h in graph:
            start_nodes.append(node_idx.index(h))
    for t in a_entity:
        if t in graph:
            end_nodes.append(node_idx.index(t))
    paths = walker.random_walks(graph, n_walks=n_neg, walk_len=hop, start_nodes=start_nodes, verbose=False)
    # Add relation to paths
    result_paths = []
    for p in paths:
        tmp = []
        # remove paths that end with answer entity
        if p[-1] in end_nodes:
            continue
        for i in range(len(p)-1):
            u = node_idx[p[i]]
            v = node_idx[p[i+1]]
            tmp.append((u, graph[u][v]['relation'], v))
        result_paths.append(tmp)
    return result_paths

def get_random_paths(q_entity: list, graph: nx.Graph, n=3, hop=2):# -> tuple [list, list]:
    '''
    Get negative paths for question witin hop
    '''
    # sample paths
    start_nodes = []
    node_idx = list(graph.nodes())
    for h in q_entity:
        if h in graph:
            start_nodes.append(node_idx.index(h))
    paths = walker.random_walks(graph, n_walks=n, walk_len=hop, start_nodes=start_nodes, verbose=False)
    # Add relation to paths
    result_paths = []
    rules = []
    for p in paths:
        tmp = []
        tmp_rule = []
        for i in range(len(p)-1):
            u = node_idx[p[i]]
            v = node_idx[p[i+1]]
            tmp.append((u, graph[u][v]['relation'], v))
            tmp_rule.append(graph[u][v]['relation'])
        result_paths.append(tmp)
        rules.append(tmp_rule)
    return result_paths, rules