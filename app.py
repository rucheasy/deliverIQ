
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import math
import heapq

app = Flask(__name__)
CORS(app)  # Allow frontend to call from any origin


#  UTILITY — Build adjacency dict from edge list

def build_adjacency(nodes: list, edges: list) -> dict:
    """Convert edge list to undirected weighted adjacency dictionary."""
    adj = {n: {} for n in nodes}
    for e in edges:
        adj[e["from"]][e["to"]] = e["dist"]
        adj[e["to"]][e["from"]] = e["dist"]
    return adj



#  ALGORITHM 1 — GREEDY NEAREST NEIGHBOR
#  ─ Always move to closest unvisited delivery node
#  ─ VIP orders are served first (forced priority phase)
#  ─ Time Complexity : O(n²)
#  ─ Space Complexity: O(n)

def greedy_route(depot: str, delivery_nodes: list, adj: dict, vip_locs: set):
    log = [f"[GREEDY] Depot: {depot}", f"[GREEDY] VIP-first enabled"]

    vip_nodes    = [n for n in delivery_nodes if n in vip_locs]
    normal_nodes = [n for n in delivery_nodes if n not in vip_locs]

    log.append(f"[VIP] Must serve first: {vip_nodes}")

    route = [depot]
    total_dist = 0
    current = depot

    def nearest(current, remaining):
        best, best_d = None, math.inf
        for n in remaining:
            d = adj.get(current, {}).get(n, math.inf)
            if d < best_d:
                best_d = d
                best = n
        return best, best_d

    # Phase 1 — VIP deliveries
    remaining_vip = list(vip_nodes)
    while remaining_vip:
        node, d = nearest(current, remaining_vip)
        if node is None or d == math.inf:
            log.append(f"[WARN] VIP node unreachable from {current}")
            break
        route.append(node)
        total_dist += d
        log.append(f"[VIP] {current} → {node} ({d} km)")
        remaining_vip.remove(node)
        current = node

    # Phase 2 — Normal deliveries
    remaining_norm = list(normal_nodes)
    while remaining_norm:
        node, d = nearest(current, remaining_norm)
        if node is None or d == math.inf:
            log.append(f"[WARN] Normal node unreachable from {current}")
            break
        route.append(node)
        total_dist += d
        log.append(f"[NORMAL] {current} → {node} ({d} km)")
        remaining_norm.remove(node)
        current = node

    # Return to depot
    return_d = adj.get(current, {}).get(depot, math.inf)
    if return_d != math.inf:
        total_dist += return_d
        route.append(depot)
        log.append(f"[DONE] Return to depot ({return_d} km)")

    log.append(f"[GREEDY] Total: {total_dist} km")
    return {"route": route, "total_dist": total_dist, "log": log}



#  ALGORITHM 2 — DIJKSTRA'S ALGORITHM
#  ─ Finds true shortest path between all node pairs
#  ─ Uses min-heap priority queue for efficiency
#  ─ Time Complexity : O((V + E) log V)
#  ─ Space Complexity: O(V)

def dijkstra(source: str, adj: dict, all_nodes: list):
    """Return shortest distances and predecessors from source."""
    dist = {n: math.inf for n in all_nodes}
    prev = {n: None for n in all_nodes}
    dist[source] = 0

    # Min-heap: (distance, node)
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue  # Stale entry — skip
        for v, w in adj.get(u, {}).items():
            new_d = d + w
            if new_d < dist[v]:
                dist[v] = new_d
                prev[v] = u
                heapq.heappush(heap, (new_d, v))

    return dist, prev


def reconstruct_path(prev: dict, src: str, dst: str) -> list:
    """Backtrack predecessor map to get full path."""
    path = []
    cur = dst
    while cur is not None:
        path.append(cur)
        if cur == src:
            break
        cur = prev.get(cur)
    path.reverse()
    return path if path and path[0] == src else []


def dijkstra_route(depot: str, delivery_nodes: list, adj: dict,
                   vip_locs: set, all_nodes: list):
    log = [f"[DIJKSTRA] Computing shortest paths from all sources"]

    # Pre-compute Dijkstra from depot + all delivery nodes
    sources = [depot] + delivery_nodes
    sp = {}
    for src in sources:
        dist, prev = dijkstra(src, adj, all_nodes)
        sp[src] = {"dist": dist, "prev": prev}
        log.append(f"[DIJKSTRA] Processed source: {src}")

    vip_nodes    = [n for n in delivery_nodes if n in vip_locs]
    normal_nodes = [n for n in delivery_nodes if n not in vip_locs]
    log.append(f"[VIP] Priority queue: {vip_nodes}")

    route = [depot]
    total_dist = 0
    current = depot

    def visit_nearest(remaining):
        best, best_d = None, math.inf
        for n in remaining:
            d = sp[current]["dist"].get(n, math.inf)
            if d < best_d:
                best_d = d
                best = n
        return best, best_d

    # VIP phase
    vip_rem = list(vip_nodes)
    while vip_rem:
        node, d = visit_nearest(vip_rem)
        if node is None or d == math.inf:
            log.append(f"[WARN] VIP unreachable from {current}")
            break
        path = reconstruct_path(sp[current]["prev"], current, node)
        route.extend(path[1:])
        total_dist += d
        log.append(f"[VIP] {current} → {node} = {d} km (via {' → '.join(path)})")
        vip_rem.remove(node)
        current = node

    # Normal phase
    norm_rem = list(normal_nodes)
    while norm_rem:
        node, d = visit_nearest(norm_rem)
        if node is None or d == math.inf:
            log.append(f"[WARN] Node unreachable from {current}")
            break
        path = reconstruct_path(sp[current]["prev"], current, node)
        route.extend(path[1:])
        total_dist += d
        log.append(f"[NORMAL] {current} → {node} = {d} km")
        norm_rem.remove(node)
        current = node

    # Return to depot
    return_d = sp.get(current, {}).get("dist", {}).get(depot, math.inf)
    if return_d != math.inf:
        ret_path = reconstruct_path(sp[current]["prev"], current, depot)
        route.extend(ret_path[1:])
        total_dist += return_d
        log.append(f"[DONE] Return to depot: {return_d} km")

    log.append(f"[DIJKSTRA] Total: {total_dist} km")
    return {"route": route, "total_dist": total_dist, "log": log}

#  ALGORITHM 3 — 0/1 KNAPSACK (Dynamic Programming)
#  ─ VIP orders are mandatory (always selected)
#  ─ Normal orders selected to maximize profit within capacity
#  ─ Time Complexity : O(n × W)
#  ─ Space Complexity: O(n × W)

def knapsack_01(orders: list, capacity: float):
    """
    Solve 0/1 knapsack.
    VIP orders are pre-selected; remaining capacity allocated to normal orders.
    Returns list of selected orders.
    """
    vip_orders    = [o for o in orders if o["priority"] == "vip"]
    normal_orders = [o for o in orders if o["priority"] != "vip"]

    vip_weight = sum(o["weight"] for o in vip_orders)
    remaining  = capacity - vip_weight

    selected = list(vip_orders)  # VIP always included

    if remaining > 0 and normal_orders:
        n = len(normal_orders)
        # Scale weights by 10 to handle one decimal place
        W = int(remaining * 10)

        # Build DP table
        dp = [[0] * (W + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            wt = int(normal_orders[i - 1]["weight"] * 10)
            pr = normal_orders[i - 1]["profit"]
            for w in range(W + 1):
                dp[i][w] = dp[i - 1][w]          # Skip item
                if w >= wt:
                    dp[i][w] = max(dp[i][w],      # Take item
                                   dp[i - 1][w - wt] + pr)

        # Backtrack to find selected items
        w = W
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected.append(normal_orders[i - 1])
                w -= int(normal_orders[i - 1]["weight"] * 10)

    total_weight = sum(o["weight"] for o in selected)
    total_profit = sum(o["profit"] for o in selected)

    return {
        "selected": selected,
        "total_weight": round(total_weight, 2),
        "total_profit": total_profit,
        "capacity": capacity,
        "vip_count": len(vip_orders),
        "normal_selected": len(selected) - len(vip_orders),
        "total_orders": len(orders),
    }


#  API ROUTES

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "DeliverIQ API"})


@app.route("/api/knapsack", methods=["POST"])
def api_knapsack():
    """
    POST /api/knapsack
    Body: { orders: [...], capacity: float }
    """
    data     = request.json
    orders   = data.get("orders", [])
    capacity = float(data.get("capacity", 30))

    t0     = time.perf_counter()
    result = knapsack_01(orders, capacity)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 4)

    result["elapsed_ms"] = elapsed_ms
    result["complexity"] = "O(n × W)"
    return jsonify(result)


@app.route("/api/greedy", methods=["POST"])
def api_greedy():
    """
    POST /api/greedy
    Body: { nodes, edges, selected_orders, depot }
    """
    data     = request.json
    nodes    = data["nodes"]
    edges    = data["edges"]
    orders   = data["selected_orders"]
    depot    = data["depot"]

    adj      = build_adjacency(nodes, edges)
    vip_locs = {o["loc"] for o in orders if o["priority"] == "vip"}
    delivery = list({o["loc"] for o in orders if o["loc"] != depot})

    t0     = time.perf_counter()
    result = greedy_route(depot, delivery, adj, vip_locs)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 4)

    result["elapsed_ms"] = elapsed_ms
    result["complexity"] = "O(n²)"
    return jsonify(result)


@app.route("/api/dijkstra", methods=["POST"])
def api_dijkstra():
    """
    POST /api/dijkstra
    Body: { nodes, edges, selected_orders, depot }
    """
    data     = request.json
    nodes    = data["nodes"]
    edges    = data["edges"]
    orders   = data["selected_orders"]
    depot    = data["depot"]

    adj      = build_adjacency(nodes, edges)
    vip_locs = {o["loc"] for o in orders if o["priority"] == "vip"}
    delivery = list({o["loc"] for o in orders if o["loc"] != depot})

    t0     = time.perf_counter()
    result = dijkstra_route(depot, delivery, adj, vip_locs, nodes)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 4)

    result["elapsed_ms"] = elapsed_ms
    result["complexity"] = "O((V+E) log V)"
    return jsonify(result)


@app.route("/api/compare", methods=["POST"])
def api_compare():
    """
    POST /api/compare
    Runs both algorithms and returns a side-by-side comparison.
    Body: { nodes, edges, selected_orders, depot }
    """
    data     = request.json
    nodes    = data["nodes"]
    edges    = data["edges"]
    orders   = data["selected_orders"]
    depot    = data["depot"]

    adj      = build_adjacency(nodes, edges)
    vip_locs = {o["loc"] for o in orders if o["priority"] == "vip"}
    delivery = list({o["loc"] for o in orders if o["loc"] != depot})

    # Run Greedy
    t0 = time.perf_counter()
    g  = greedy_route(depot, delivery, adj, vip_locs)
    g["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 4)

    # Run Dijkstra
    t0 = time.perf_counter()
    d  = dijkstra_route(depot, delivery, adj, vip_locs, nodes)
    d["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 4)

    # Summary
    better_dist = "greedy" if g["total_dist"] <= d["total_dist"] else "dijkstra"
    faster      = "greedy" if g["elapsed_ms"] <= d["elapsed_ms"]  else "dijkstra"

    return jsonify({
        "greedy":   g,
        "dijkstra": d,
        "summary": {
            "better_distance": better_dist,
            "faster_execution": faster,
            "dist_diff_km": abs(g["total_dist"] - d["total_dist"]),
            "time_diff_ms": round(abs(g["elapsed_ms"] - d["elapsed_ms"]), 4),
        }
    })


if __name__ == "__main__":
    print("\n🚚 DeliverIQ API running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
