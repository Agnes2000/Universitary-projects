# Planning and Reasoning
# Domain description

The proposed project focuses on optimizing public transport route planning using PDDL and Situation Calculus. The problem involves finding the best route for a person traveling from a starting location to a destination using buses, metro, or trams while considering schedules, transfers, and possible delays.

Problem overview: 

A user needs to move from location A to location B using available public transport. The goal is to find the optimal path based on various factors:
- Minimizing travel time
- Reducing the number of transfers
- Handling unexpected delays
- Accommodating user preferences (e.g., avoiding metro)

# Problem instances
We define three levels of difficulty:
# 1. Instance 1 (basic route planning)
The user has to travel between two locations using a single mode of transport.
There are no delays, and all vehicles run on schedule.

# 2. Instance 2 (multi-modal route planning)
The user needs to change at least one transport mode.
Schedules must be considered to ensure feasible transfers.

# 3. Instance 3 (realistic transport planning with delays)
Some transport options are delayed or unavailable.
The system must dynamically adjust the route to accommodate disruptions.
Additional constraints such as user preferences (e.g., avoiding specific transport types) may apply.

# Planners to be used
We will experiment with different PDDL planners, including:
- Fast Downward (a widely used PDDL planner with support for various heuristics)
- ENHSP (a numeric and hybrid planner suitable for handling time-based planning problems)
- Planning.Domains (a web-based planner useful for quick testing and validation)

# Heuristics to be used
To optimize route planning, we tested multiple heuristic search strategies:
- Additive Heuristic (hadd): Estimates the cost of achieving a set of goals by summing the costs of individual subgoals, assuming independence.
- Max Heuristic (hmax): Uses the maximum cost among all subgoals, providing an admissible and fast estimate.
- Refined Additive Heuristic (hradd): A variation of hadd that considers additional structure in the problem for improved guidance.
- Refined Max Heuristic (hrmax): An enhancement of hmax that incorporates more detailed dependency information between actions.

These heuristics were selected to explore different trade-offs between informativeness and computational efficiency during planning. Blind search and landmark-based heuristics were not included in the final evaluation.

# Reasoning tasks in IndiGolog (SWI-Prolog)
To enhance the project, we will implement reasoning tasks in IndiGolog using SWI-Prolog. These tasks simulate real-world decision-making in public transport.
# 1. Reasoning task 1: optimal route calculation
Question: What is the fastest way to travel from location A to B?
Execution: The system finds the optimal route based on current schedules and conditions.

# 2. Reasoning task 2: handling unexpected delays
Question: If transport X is delayed, what alternative routes are available?
Execution: The system dynamically recomputes an alternative plan considering real-time updates.

# 3. Reasoning task 3: route planning with user preferences
Question: Can a user reach their destination while avoiding the metro?
Execution: The system finds a valid route that respects the user’s constraints.

# Expected challenges and considerations
Handling realistic time-based planning in PDDL.
Implementing effective heuristics for large-scale route planning.
Ensuring smooth integration of PDDL planning with IndiGolog for reasoning.

# Conclusion
This project aims to create an intelligent travel assistant capable of generating optimal public transport routes under various constraints. By leveraging PDDL planning and logic-based reasoning in IndiGolog, the system will provide realistic and flexible travel solutions.
