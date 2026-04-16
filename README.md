# 🚚 DeliverIQ — Delivery Route Optimization System

A full-stack web application implementing three core algorithms for intelligent delivery route planning.

---

## Algorithms Implemented

| Algorithm | Complexity | Purpose |
|-----------|-----------|---------|
| **0/1 Knapsack** (DP) | O(n × W) | Select best orders within weight capacity |
| **Greedy Nearest Neighbor** | O(n²) | Fast route planning (approximation) |
| **Dijkstra's Shortest Path** | O((V+E) log V) | Optimal shortest-path routing |

---

## Project Structure

```
delivery-route-optimizer/
├── index.html      ← Frontend (standalone, works without backend)
├── app.py          ← Python Flask backend (optional REST API)
├── README.md       ← This file
```

---

## Option A — Run Frontend Only (Recommended for Quick Start)

No installation required. All algorithms run in the browser.

```bash
# Simply open in your browser:
open index.html
# or double-click index.html in your file manager
```

---

## Option B — Run with Flask Backend

### 1. Install dependencies

```bash
pip install flask flask-cors
```

### 2. Start the backend

```bash
python app.py
```

Backend runs at: `http://localhost:5000`

### 3. Open the frontend

```bash
open index.html
```

---

## API Endpoints (Flask Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/health`   | Health check |
| POST | `/api/knapsack` | Run 0/1 Knapsack order selection |
| POST | `/api/greedy`   | Run Greedy route algorithm |
| POST | `/api/dijkstra` | Run Dijkstra route algorithm |
| POST | `/api/compare`  | Run both and compare |

### Example: POST /api/compare

```json
{
  "nodes": ["Depot", "Karol Bagh", "Lajpat Nagar", "Saket"],
  "edges": [
    {"from": "Depot", "to": "Karol Bagh", "dist": 5},
    {"from": "Karol Bagh", "to": "Lajpat Nagar", "dist": 10},
    {"from": "Lajpat Nagar", "to": "Saket", "dist": 5},
    {"from": "Depot", "to": "Saket", "dist": 12}
  ],
  "depot": "Depot",
  "selected_orders": [
    {"id": "ORD-001", "loc": "Karol Bagh", "weight": 3, "profit": 150, "priority": "vip"},
    {"id": "ORD-002", "loc": "Lajpat Nagar", "weight": 8, "profit": 300, "priority": "normal"},
    {"id": "ORD-003", "loc": "Saket", "weight": 7, "profit": 350, "priority": "normal"}
  ]
}
```

---

## Sample Test Dataset

The built-in sample data (click **🚀 Load Sample Dataset**) includes:

### Locations (8 nodes)
- Depot (Hub), Karol Bagh, Lajpat Nagar, Connaught Place
- Dwarka, Rohini, Saket, Noida Sector 18

### Routes (12 edges)
```
Depot ↔ Karol Bagh       : 5 km
Depot ↔ Connaught Place  : 7 km
Depot ↔ Rohini           : 12 km
Karol Bagh ↔ CP          : 4 km
Karol Bagh ↔ Lajpat      : 10 km
CP ↔ Lajpat Nagar        : 8 km
CP ↔ Dwarka              : 15 km
CP ↔ Saket               : 9 km
Lajpat ↔ Saket           : 5 km
Lajpat ↔ Noida 18        : 13 km
Rohini ↔ Dwarka          : 18 km
Saket ↔ Noida 18         : 14 km
```

### Orders (6)
| Order | Location | Weight | Profit | Priority |
|-------|----------|--------|--------|----------|
| ORD-001 | Karol Bagh | 3 kg | ₹150 | ⭐ VIP |
| ORD-002 | Lajpat Nagar | 8 kg | ₹300 | Normal |
| ORD-003 | Connaught Place | 2 kg | ₹200 | ⭐ VIP |
| ORD-004 | Dwarka | 12 kg | ₹500 | Normal |
| ORD-005 | Rohini | 5 kg | ₹180 | Normal |
| ORD-006 | Saket | 7 kg | ₹350 | Normal |

**Knapsack capacity**: 25 kg  
**Expected selection**: ORD-001 (VIP), ORD-003 (VIP), ORD-006, ORD-002, ORD-005 ≈ 25 kg

---

## How to Use

1. **Load Sample Data** or manually add locations, routes, and orders
2. **Run Knapsack** — set max weight capacity and select depot
3. **Run Greedy / Dijkstra / Compare Both** — view routes and logs
4. **Check Performance Graphs** — compare execution times

---

## Features

- ⭐ **VIP Priority**: VIP orders always delivered first
- 📊 **Performance Charts**: Bar chart (comparison) + Line chart (run history)
- 🎒 **Knapsack Selection**: Optimal order selection with DP
- 🗺️ **Route Visualization**: Color-coded nodes (depot / VIP / normal)
- 📋 **Execution Logs**: Step-by-step algorithm trace
- 🔍 **Algorithm Comparison Summary**: Winner analysis

---

## Time Complexity Reference

```
Knapsack DP    : O(n × W) — n orders, W = scaled capacity
Greedy Route   : O(n²)   — n delivery nodes, n nearest lookups
Dijkstra       : O((V+E) log V) — V nodes, E edges, log V for heap
```
