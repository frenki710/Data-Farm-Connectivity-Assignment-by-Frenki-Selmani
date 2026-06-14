import sys
import heapq


INF = float("inf")


def format_number(value):
    """
    Prints numbers in a more mannerly format.
    For example: if the value is 3.0, it prints 3.
    If the value is 3.75, it just prints 3.75.
    """
    if value == INF:
        return "infinity"
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def read_input(filename):
    """
    Reads the input file.
    """

    with open(filename, "r") as file:
        lines = [line.strip() for line in file if line.strip()]

    n, e = map(int, lines[0].split())
    budget = int(lines[1])
    start = int(lines[2])

    graph = [[] for _ in range(n)]
    edges = []

    for i in range(3, 3 + e):
        from_host, to_host, weight = lines[i].split()
        from_host = int(from_host)
        to_host = int(to_host)
        weight = float(weight)

        graph[from_host].append((to_host, weight))
        edges.append((from_host, to_host, weight))

    return n, e, budget, start, graph, edges


def reconstruct_path(parent, start, target):
    """
    Reconstructs the path from start to target using the parent array.
    Used for Dijkstra's.
    """

    if target == start:
        return [start]

    if parent[target] is None:
        return None

    path = []
    current = target

    while current is not None:
        path.append(current)

        if current == start:
            break

        current = parent[current]

    path.reverse()

    if path[0] != start:
        return None

    return path


def dijkstra(n, graph, start):
    """
    Computes shortest paths from start to every other node.
    This is used for when budget = -1, meaning there is no limit on the number of links.
    Since all weights are non-negative, Dijkstra is more appropriate.
    """

    dist = [INF] * n
    parent = [None] * n

    dist[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)

        if current_dist > dist[current_node]:
            continue

        for neighbor, weight in graph[current_node]:
            new_dist = current_dist + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = current_node
                heapq.heappush(priority_queue, (new_dist, neighbor))

    paths = []

    for host in range(n):
        path = reconstruct_path(parent, start, host)
        paths.append(path)

    return dist, paths


def reconstruct_budget_path(parent_state, start, target, final_step):
    """
    Reconstructs a path for the budget-limited algorithm.
    If the best path to target used final_step links, we move backward:
    target at step final_step
    previous node at step final_step - 1
    previous node at step final_step - 2
    ...
    until we reach the starting host.
    """

    if target == start and final_step == 0:
        return [start]

    path = []
    current_node = target
    current_step = final_step

    while current_step > 0:
        path.append(current_node)

        key = (current_step, current_node)

        if key not in parent_state:
            return None

        current_node = parent_state[key]
        current_step -= 1

    path.append(current_node)
    path.reverse()

    if path[0] != start:
        return None

    return path


def budget_limited_shortest_paths(n, edges, start, budget):
    """
    Computes shortest paths from start to every host using at most 'budget' links.
-------------------------------------------------------------------------------------
    exact_prev[v] means:
    the minimum latency to reach v using exactly step - 1 links.
    exact_current[v] means:
    the minimum latency to reach v using exactly step links.
    best_dist[v] stores:
    the best latency found so far using at most 'budget' links.
    """

    if budget == 0:
        dist = [INF] * n
        paths = [None] * n

        dist[start] = 0
        paths[start] = [start]

        return dist, paths


    effective_budget = min(budget, n - 1)

    exact_prev = [INF] * n
    exact_prev[start] = 0

    best_dist = [INF] * n
    best_dist[start] = 0

    best_step = [None] * n
    best_step[start] = 0

    parent_state = {}

    for step in range(1, effective_budget + 1):
        exact_current = [INF] * n
        changed = False

        for u, v, weight in edges:
            if exact_prev[u] == INF:
                continue

            candidate = exact_prev[u] + weight

            if candidate < exact_current[v]:
                exact_current[v] = candidate
                parent_state[(step, v)] = u

        for host in range(n):
            if exact_current[host] < best_dist[host]:
                best_dist[host] = exact_current[host]
                best_step[host] = step
                changed = True

        exact_prev = exact_current

        # If no new better paths were found during this step, we can stop early.
        if not changed:
            break

    paths = []

    for host in range(n):
        if best_dist[host] == INF:
            paths.append(None)
        else:
            path = reconstruct_budget_path(parent_state, start, host, best_step[host])
            paths.append(path)

    return best_dist, paths



def topological_sort(n, graph):
    """
    Attempts to topologically sort the directed graph.

    If the graph is acyclic, it returns a valid topological order.
    If the graph contains at least one cycle, it returns None.
    """

    indegree = [0] * n

    for u in range(n):
        for v, weight in graph[u]:
            indegree[v] += 1

    queue = []

    for host in range(n):
        if indegree[host] == 0:
            queue.append(host)

    order = []

    while queue:
        current = queue.pop(0)
        order.append(current)

        for neighbor, weight in graph[current]:
            indegree[neighbor] -= 1

            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != n:
        return None

    return order


def reconstruct_longest_path(parent, start, target):
    """
    Reconstructs the longest simple chain from start to target
    using the parent array.
    """

    if target == start:
        return [start]

    if parent[target] is None:
        return None

    path = []
    current = target

    while current is not None:
        path.append(current)

        if current == start:
            break

        current = parent[current]

    path.reverse()

    if path[0] != start:
        return None

    return path


def longest_simple_chain_dag(n, graph, start):
    """
    Computes the longest simple chain from the starting host to every other host
    when the graph is a DAG.

    In a DAG, there are no cycles, so every path is automatically simple.
    The chain length is measured by number of links, not latency.
    """

    order = topological_sort(n, graph)

    if order is None:
        return None, None

    longest = [-INF] * n
    parent = [None] * n

    longest[start] = 0

    for u in order:
        if longest[u] == -INF:
            continue

        for v, weight in graph[u]:
            candidate = longest[u] + 1

            if candidate > longest[v]:
                longest[v] = candidate
                parent[v] = u

    paths = []

    for host in range(n):
        if longest[host] == -INF:
            paths.append(None)
        else:
            paths.append(reconstruct_longest_path(parent, start, host))

    return longest, paths


def longest_simple_chain_small_graph(n, graph, start):

    longest = [-INF] * n
    best_paths = [None] * n

    visited = [False] * n
    current_path = []

    def dfs(node):
        visited[node] = True
        current_path.append(node)

        chain_length = len(current_path) - 1

        if chain_length > longest[node]:
            longest[node] = chain_length
            best_paths[node] = current_path.copy()

        for neighbor, weight in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)

        current_path.pop()
        visited[node] = False

    dfs(start)

    return longest, best_paths


def print_bonus_results(start, longest, paths):
    """
    Prints the bonus result.
    """

    print()
    print("Bonus: Longest simple chains")
    print(f"Starting host: {start}")
    print()

    for host in range(len(longest)):
        if longest[host] == -INF:
            print(f"Host {host}: unreachable")
        else:
            path = " -> ".join(map(str, paths[host]))
            print(f"Host {host}: length = {int(longest[host])} links, path = {path}")


def run_bonus(n, graph, start):
    """
    Runs the bonus part.

    First, it tries the efficient DAG algorithm.
    If the graph has cycles and is small, it uses exact DFS/backtracking.
    For large cyclic graphs, it avoids running an exponential algorithm.
    """

    bonus_distances, bonus_paths = longest_simple_chain_dag(n, graph, start)

    if bonus_distances is not None:
        print_bonus_results(start, bonus_distances, bonus_paths)
        return

    print()
    print("Bonus note: The graph contains cycles, so the DAG-based algorithm cannot be used.")

    if n <= 20:
        print("Since the graph is small, exact DFS/backtracking is used.")
        bonus_distances, bonus_paths = longest_simple_chain_small_graph(n, graph, start)
        print_bonus_results(start, bonus_distances, bonus_paths)
    else:
        print("Bonus: Longest simple chains")
        print("The graph is too large for exact DFS/backtracking.")
        print("Exact longest simple path in a general directed graph can require exponential time.")


def print_results(start, budget, distances, paths):
    """
    Prints the final result in a clear format.
    """

    print(f"Starting host: {start}")

    if budget == -1:
        print("Budget: No limit")
    else:
        print(f"Budget: At most {budget} links")

    print()

    for host in range(len(distances)):
        if distances[host] == INF:
            print(f"Host {host}: unreachable")
        else:
            path = " -> ".join(map(str, paths[host]))
            latency = format_number(distances[host])
            print(f"Host {host}: latency = {latency}, path = {path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py input.txt")
        return

    filename = sys.argv[1]

    n, e, budget, start, graph, edges = read_input(filename)

    if budget == -1:
        distances, paths = dijkstra(n, graph, start)
    else:
        distances, paths = budget_limited_shortest_paths(n, edges, start, budget)

    print_results(start, budget, distances, paths)

    # Bonus part
    run_bonus(n, graph, start)


if __name__ == "__main__":
    main()
