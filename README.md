*This project has been created as part of the 42 curriculum by hgawhari*

# Fly-In

## Description

Fly-In is a drone routing and simulation project built around a graph of hubs connected by routes with capacity constraints and special zone rules. Each drone must follow a route from a start hub to an end hub while respecting hub occupancy, link capacity, restricted-zone delays, and priority-routing decisions.

The goal of the project is to compute valid drone paths and simulate their movement over time in a clear and visual way. The application reads a map file, builds a graph, computes optimized paths, schedules drones, and renders the full state in a graphical interface.

The project models several constraints:
- hub capacity limits
- connection capacity limits
- blocked and restricted zones
- priority zones that should be favored when possible
- synchronized turn-based movement

## Instructions

### Requirements

- Python 3.10+
- pygame
- pydantic

Install the dependencies with:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the project

```bash
python3 -m src.main ./maps/easy/01_linear_path.txt
```

You can replace the map path with any valid map in the maps folder.

## Algorithm and implementation strategy

The project follows a graph-based approach:

1. Parse the map file into a structured model of hubs and connections.
2. Build a graph that stores all hub relationships and connection capacities.
3. Compute routes from the starting hub to the destination hub using a pathfinding strategy adapted to the project rules.
4. Schedule drones so that they are assigned valid routes.
5. Simulate movement turn by turn while checking hub usage, connection usage, lane capacity, and restricted-zone costs.
6. Resolve conflicts according to route priority and dynamic constraints.
7. Render the simulation in a live visual interface for inspection and debugging.

The simulation tracks:
- current drone positions
- remaining move costs
- reserved hubs during active travel
- connection usage per turn
- overall time elapsed in the simulation

This allows the system to behave like a constrained traffic simulation rather than a simple static routing solver.

## Visual representation

The visual layer is designed to make the simulation easier to understand.

It includes:
- colored hub nodes for different zone types and roles
- connection lines between hubs
- labels for hub names and current capacity usage
- live drone movement animation across the graph
- simulation state and control information positioned in the interface
- keyboard shortcuts such as pause, speed adjustment, reset, and information toggling

These visual elements help the user understand both the graph topology and the dynamic runtime behavior of the drones.

## Resources

### References
- Graph search and shortest-path theory
- Capacity-aware routing and traffic scheduling
- Pygame documentation for rendering and user interaction
- General algorithmic references for constrained pathfinding and graph traversal

### AI usage

AI tools were used to help with:
- debugging the graph and simulation logic
- implementing the visualization and event loop
- accelerating project documentation and explanation writing
- improving readability and maintainability of the codebase

AI was especially useful for clarifying route scheduling logic and polishing the user-facing documentation.

## Example input and expected output

### Example execution

```bash
python3 -m src.main ./maps/easy/01_linear_path.txt
```

### Example output

```text
1: start -> hubA -> hubB -> end
2: start -> hubC -> hubD -> end
...
SIMULATION SOLUTION
==================================================
Total turns: 12
Total drones: 3
```

The exact turn count depends on the selected map and the computed route assignment, but the program always prints the total number of simulation turns after the visualization is closed.

## Project structure

```text
.
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── exception.py
│   ├── models/
│   ├── parser/
│   ├── routing/
│   ├── simulation/
│   └── visualization/
├── maps/
│   ├── easy/
│   ├── medium/
│   ├── hard/
│   └── challenger/
└── tests/
```

## Summary

Fly-In combines route planning, capacity management, and live visualization into a single project. It is designed to demonstrate how a drone fleet can be coordinated through a constrained graph while remaining readable, interactive, and useful for debugging.
