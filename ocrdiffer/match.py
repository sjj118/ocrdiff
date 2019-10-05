import networkx as nx


def match_box(ocr1, ocr2):
    graph = nx.Graph()
    n1 = len(ocr1)
    n2 = len(ocr2)
    graph.add_nodes_from(range(n1 + n2))
    for i, box1 in enumerate(ocr1):
        for j, box2 in enumerate(ocr2):
            graph.add_edge(i, n1 + j, weight=get_sim(box1, box2))
    s = nx.algorithms.max_weight_matching(graph, maxcardinality=True)
    mat1 = []
    mat2 = []
    for i, j in s:
        if i >= n1: i, j = j, i
        mat1.append(i)
        mat2.append(j - n1)
    mat = [(ocr1[i], ocr2[j]) for i, j in zip(mat1, mat2)]
    unmat1 = [ocr1[i] for i in range(n1) if i not in mat1]
    unmat2 = [ocr2[i] for i in range(n2) if i not in mat2]
    return mat, unmat1, unmat2


def get_sim(box1, box2):
    nx = min(box1.right, box2.right) - max(box1.left, box2.left)
    ny = min(box1.bottom, box2.bottom) - max(box1.top, box2.top)
    ux = box1.width + box2.width - max(0, nx)
    uy = box1.height + box2.height - max(0, ny)
    return nx / ux + ny / uy
