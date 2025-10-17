"""
Quantum Optimization System for Ultimate Launch Planning System
Provides quantum-inspired optimization algorithms for complex launch planning problems
"""

import numpy as np
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum
import uuid
import random
from scipy.optimize import minimize, differential_evolution
from scipy.spatial.distance import pdist, squareform
import networkx as nx

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    RESOURCE_ALLOCATION = "resource_allocation"
    TIMELINE_OPTIMIZATION = "timeline_optimization"
    BUDGET_OPTIMIZATION = "budget_optimization"
    TEAM_ASSIGNMENT = "team_assignment"
    RISK_MINIMIZATION = "risk_minimization"
    SUCCESS_MAXIMIZATION = "success_maximization"

class QuantumAlgorithm(Enum):
    QUANTUM_ANNEALING = "quantum_annealing"
    QAOA = "qaoa"  # Quantum Approximate Optimization Algorithm
    VQE = "vqe"    # Variational Quantum Eigensolver
    QUANTUM_GENETIC = "quantum_genetic"
    QUANTUM_PARTICLE_SWARM = "quantum_particle_swarm"

@dataclass
class OptimizationResult:
    id: str
    optimization_type: OptimizationType
    algorithm: QuantumAlgorithm
    objective_value: float
    solution: Dict[str, Any]
    execution_time: float
    iterations: int
    convergence_rate: float
    confidence: float
    metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "optimization_type": self.optimization_type.value,
            "algorithm": self.algorithm.value,
            "objective_value": self.objective_value,
            "solution": self.solution,
            "execution_time": self.execution_time,
            "iterations": self.iterations,
            "convergence_rate": self.convergence_rate,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class QuantumState:
    amplitude: complex
    probability: float
    state_vector: np.ndarray
    energy: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "amplitude": str(self.amplitude),
            "probability": self.probability,
            "state_vector": self.state_vector.tolist(),
            "energy": self.energy
        }

class QuantumOptimizer:
    """Quantum-inspired optimization algorithms"""
    
    def __init__(self):
        self.optimization_history: deque = deque(maxlen=1000)
        self.quantum_states: Dict[str, QuantumState] = {}
        self.optimization_cache: Dict[str, OptimizationResult] = {}
        self.lock = threading.RLock()
        
        # Quantum parameters
        self.quantum_parameters = {
            "annealing_time": 1.0,
            "temperature": 1.0,
            "coupling_strength": 1.0,
            "tunneling_rate": 0.1,
            "decoherence_time": 10.0
        }
        
        logger.info("Quantum Optimizer initialized")
    
    def optimize_resource_allocation(self, resources: Dict[str, float], 
                                   constraints: Dict[str, Any], 
                                   objective: str = "maximize_efficiency") -> OptimizationResult:
        """Optimize resource allocation using quantum algorithms"""
        start_time = time.time()
        
        # Prepare optimization problem
        problem_data = {
            "resources": resources,
            "constraints": constraints,
            "objective": objective
        }
        
        # Use quantum annealing for resource allocation
        solution = self._quantum_annealing_optimization(problem_data)
        
        execution_time = time.time() - start_time
        
        result = OptimizationResult(
            id=str(uuid.uuid4()),
            optimization_type=OptimizationType.RESOURCE_ALLOCATION,
            algorithm=QuantumAlgorithm.QUANTUM_ANNEALING,
            objective_value=solution["objective_value"],
            solution=solution["allocation"],
            execution_time=execution_time,
            iterations=solution["iterations"],
            convergence_rate=solution["convergence_rate"],
            confidence=solution["confidence"],
            metadata=problem_data,
            created_at=datetime.now()
        )
        
        with self.lock:
            self.optimization_history.append(result)
            self.optimization_cache[result.id] = result
        
        return result
    
    def optimize_timeline(self, tasks: List[Dict[str, Any]], 
                         dependencies: List[Tuple[str, str]], 
                         resources: Dict[str, float]) -> OptimizationResult:
        """Optimize project timeline using quantum algorithms"""
        start_time = time.time()
        
        # Create task graph
        task_graph = self._create_task_graph(tasks, dependencies)
        
        # Use QAOA for timeline optimization
        solution = self._qaoa_timeline_optimization(task_graph, resources)
        
        execution_time = time.time() - start_time
        
        result = OptimizationResult(
            id=str(uuid.uuid4()),
            optimization_type=OptimizationType.TIMELINE_OPTIMIZATION,
            algorithm=QuantumAlgorithm.QAOA,
            objective_value=solution["objective_value"],
            solution=solution["schedule"],
            execution_time=execution_time,
            iterations=solution["iterations"],
            convergence_rate=solution["convergence_rate"],
            confidence=solution["confidence"],
            metadata={"tasks": tasks, "dependencies": dependencies, "resources": resources},
            created_at=datetime.now()
        )
        
        with self.lock:
            self.optimization_history.append(result)
            self.optimization_cache[result.id] = result
        
        return result
    
    def optimize_budget(self, budget_categories: Dict[str, float], 
                       expected_returns: Dict[str, float], 
                       risk_factors: Dict[str, float]) -> OptimizationResult:
        """Optimize budget allocation using quantum algorithms"""
        start_time = time.time()
        
        # Use VQE for budget optimization
        solution = self._vqe_budget_optimization(budget_categories, expected_returns, risk_factors)
        
        execution_time = time.time() - start_time
        
        result = OptimizationResult(
            id=str(uuid.uuid4()),
            optimization_type=OptimizationType.BUDGET_OPTIMIZATION,
            algorithm=QuantumAlgorithm.VQE,
            objective_value=solution["objective_value"],
            solution=solution["allocation"],
            execution_time=execution_time,
            iterations=solution["iterations"],
            convergence_rate=solution["convergence_rate"],
            confidence=solution["confidence"],
            metadata={"categories": budget_categories, "returns": expected_returns, "risks": risk_factors},
            created_at=datetime.now()
        )
        
        with self.lock:
            self.optimization_history.append(result)
            self.optimization_cache[result.id] = result
        
        return result
    
    def optimize_team_assignment(self, team_members: List[Dict[str, Any]], 
                                tasks: List[Dict[str, Any]], 
                                skill_requirements: Dict[str, List[str]]) -> OptimizationResult:
        """Optimize team assignment using quantum algorithms"""
        start_time = time.time()
        
        # Use quantum genetic algorithm for team assignment
        solution = self._quantum_genetic_assignment(team_members, tasks, skill_requirements)
        
        execution_time = time.time() - start_time
        
        result = OptimizationResult(
            id=str(uuid.uuid4()),
            optimization_type=OptimizationType.TEAM_ASSIGNMENT,
            algorithm=QuantumAlgorithm.QUANTUM_GENETIC,
            objective_value=solution["objective_value"],
            solution=solution["assignments"],
            execution_time=execution_time,
            iterations=solution["iterations"],
            convergence_rate=solution["convergence_rate"],
            confidence=solution["confidence"],
            metadata={"team_members": team_members, "tasks": tasks, "requirements": skill_requirements},
            created_at=datetime.now()
        )
        
        with self.lock:
            self.optimization_history.append(result)
            self.optimization_cache[result.id] = result
        
        return result
    
    def _quantum_annealing_optimization(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Quantum annealing optimization implementation"""
        resources = problem_data["resources"]
        constraints = problem_data["constraints"]
        
        # Simulate quantum annealing process
        num_resources = len(resources)
        num_iterations = 1000
        
        # Initialize quantum state
        quantum_state = np.ones(num_resources) / np.sqrt(num_resources)
        
        # Annealing schedule
        initial_temp = 10.0
        final_temp = 0.1
        temp_schedule = np.linspace(initial_temp, final_temp, num_iterations)
        
        best_solution = None
        best_energy = float('inf')
        convergence_history = []
        
        for iteration in range(num_iterations):
            # Quantum tunneling effect
            tunneling_prob = np.exp(-temp_schedule[iteration] / self.quantum_parameters["temperature"])
            
            # Update quantum state
            quantum_state = self._update_quantum_state(quantum_state, tunneling_prob)
            
            # Measure quantum state (collapse to classical state)
            classical_state = self._measure_quantum_state(quantum_state)
            
            # Calculate energy (objective function)
            energy = self._calculate_resource_energy(classical_state, resources, constraints)
            
            # Update best solution
            if energy < best_energy:
                best_energy = energy
                best_solution = classical_state.copy()
            
            convergence_history.append(energy)
        
        # Calculate convergence rate
        convergence_rate = self._calculate_convergence_rate(convergence_history)
        
        # Convert solution to allocation
        allocation = {}
        resource_names = list(resources.keys())
        for i, value in enumerate(best_solution):
            if i < len(resource_names):
                allocation[resource_names[i]] = float(value)
        
        return {
            "objective_value": best_energy,
            "allocation": allocation,
            "iterations": num_iterations,
            "convergence_rate": convergence_rate,
            "confidence": min(1.0, 1.0 - best_energy / 100.0)
        }
    
    def _qaoa_timeline_optimization(self, task_graph: nx.DiGraph, resources: Dict[str, float]) -> Dict[str, Any]:
        """QAOA (Quantum Approximate Optimization Algorithm) for timeline optimization"""
        num_tasks = len(task_graph.nodes())
        num_layers = 3  # QAOA layers
        
        # Initialize QAOA parameters
        gamma_params = np.random.uniform(0, 2*np.pi, num_layers)
        beta_params = np.random.uniform(0, np.pi, num_layers)
        
        best_solution = None
        best_energy = float('inf')
        convergence_history = []
        
        # QAOA optimization loop
        for iteration in range(500):
            # Apply QAOA circuit
            quantum_state = self._apply_qaoa_circuit(gamma_params, beta_params, task_graph)
            
            # Measure quantum state
            classical_state = self._measure_quantum_state(quantum_state)
            
            # Calculate energy (makespan)
            energy = self._calculate_timeline_energy(classical_state, task_graph, resources)
            
            # Update best solution
            if energy < best_energy:
                best_energy = energy
                best_solution = classical_state.copy()
            
            convergence_history.append(energy)
            
            # Update QAOA parameters using gradient descent
            gamma_params, beta_params = self._update_qaoa_parameters(
                gamma_params, beta_params, energy, task_graph
            )
        
        # Generate schedule from solution
        schedule = self._generate_schedule_from_solution(best_solution, task_graph)
        
        convergence_rate = self._calculate_convergence_rate(convergence_history)
        
        return {
            "objective_value": best_energy,
            "schedule": schedule,
            "iterations": 500,
            "convergence_rate": convergence_rate,
            "confidence": min(1.0, 1.0 - best_energy / 1000.0)
        }
    
    def _vqe_budget_optimization(self, categories: Dict[str, float], 
                                returns: Dict[str, float], 
                                risks: Dict[str, float]) -> Dict[str, Any]:
        """VQE (Variational Quantum Eigensolver) for budget optimization"""
        num_categories = len(categories)
        
        # Initialize VQE parameters
        theta_params = np.random.uniform(0, 2*np.pi, num_categories)
        
        best_solution = None
        best_energy = float('inf')
        convergence_history = []
        
        # VQE optimization loop
        for iteration in range(300):
            # Apply VQE circuit
            quantum_state = self._apply_vqe_circuit(theta_params, categories, returns, risks)
            
            # Measure quantum state
            classical_state = self._measure_quantum_state(quantum_state)
            
            # Calculate energy (risk-adjusted return)
            energy = self._calculate_budget_energy(classical_state, categories, returns, risks)
            
            # Update best solution
            if energy < best_energy:
                best_energy = energy
                best_solution = classical_state.copy()
            
            convergence_history.append(energy)
            
            # Update VQE parameters
            theta_params = self._update_vqe_parameters(theta_params, energy, categories, returns, risks)
        
        # Convert solution to allocation
        allocation = {}
        category_names = list(categories.keys())
        total_budget = sum(categories.values())
        
        for i, value in enumerate(best_solution):
            if i < len(category_names):
                allocation[category_names[i]] = float(value * total_budget)
        
        convergence_rate = self._calculate_convergence_rate(convergence_history)
        
        return {
            "objective_value": best_energy,
            "allocation": allocation,
            "iterations": 300,
            "convergence_rate": convergence_rate,
            "confidence": min(1.0, 1.0 - best_energy / 100.0)
        }
    
    def _quantum_genetic_assignment(self, team_members: List[Dict[str, Any]], 
                                   tasks: List[Dict[str, Any]], 
                                   requirements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Quantum genetic algorithm for team assignment"""
        population_size = 50
        num_generations = 200
        
        # Initialize quantum population
        quantum_population = []
        for _ in range(population_size):
            individual = np.random.uniform(0, 1, (len(tasks), len(team_members)))
            quantum_population.append(individual)
        
        best_solution = None
        best_fitness = float('inf')
        convergence_history = []
        
        for generation in range(num_generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in quantum_population:
                fitness = self._calculate_assignment_fitness(individual, team_members, tasks, requirements)
                fitness_scores.append(fitness)
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = individual.copy()
            
            convergence_history.append(best_fitness)
            
            # Quantum selection
            selected_population = self._quantum_selection(quantum_population, fitness_scores)
            
            # Quantum crossover
            quantum_population = self._quantum_crossover(selected_population)
            
            # Quantum mutation
            quantum_population = self._quantum_mutation(quantum_population)
        
        # Convert solution to assignments
        assignments = self._convert_to_assignments(best_solution, team_members, tasks)
        
        convergence_rate = self._calculate_convergence_rate(convergence_history)
        
        return {
            "objective_value": best_fitness,
            "assignments": assignments,
            "iterations": num_generations,
            "convergence_rate": convergence_rate,
            "confidence": min(1.0, 1.0 - best_fitness / 100.0)
        }
    
    def _update_quantum_state(self, state: np.ndarray, tunneling_prob: float) -> np.ndarray:
        """Update quantum state with tunneling effect"""
        # Simulate quantum tunneling
        if random.random() < tunneling_prob:
            # Random quantum jump
            jump_index = random.randint(0, len(state) - 1)
            state[jump_index] *= np.exp(1j * random.uniform(0, 2*np.pi))
        
        # Normalize quantum state
        state = state / np.linalg.norm(state)
        return state
    
    def _measure_quantum_state(self, quantum_state: np.ndarray) -> np.ndarray:
        """Measure quantum state to get classical state"""
        # Calculate probabilities
        probabilities = np.abs(quantum_state) ** 2
        
        # Sample from probability distribution
        classical_state = np.random.binomial(1, probabilities)
        return classical_state.astype(float)
    
    def _calculate_resource_energy(self, state: np.ndarray, resources: Dict[str, float], 
                                 constraints: Dict[str, Any]) -> float:
        """Calculate energy for resource allocation"""
        # Simple energy function (can be made more complex)
        total_allocation = np.sum(state)
        target_allocation = constraints.get("total_budget", 1.0)
        
        # Energy based on deviation from target
        energy = abs(total_allocation - target_allocation) * 10
        
        # Add constraint penalties
        if total_allocation > constraints.get("max_budget", 1.0):
            energy += (total_allocation - constraints["max_budget"]) * 100
        
        return energy
    
    def _calculate_timeline_energy(self, state: np.ndarray, task_graph: nx.DiGraph, 
                                 resources: Dict[str, float]) -> float:
        """Calculate energy for timeline optimization"""
        # Calculate makespan (total project duration)
        makespan = 0
        
        for node in task_graph.nodes():
            task_duration = task_graph.nodes[node].get("duration", 1.0)
            makespan += task_duration * state[node] if node < len(state) else task_duration
        
        return makespan
    
    def _calculate_budget_energy(self, state: np.ndarray, categories: Dict[str, float], 
                               returns: Dict[str, float], risks: Dict[str, float]) -> float:
        """Calculate energy for budget optimization"""
        # Risk-adjusted return optimization
        total_return = 0
        total_risk = 0
        
        category_names = list(categories.keys())
        for i, value in enumerate(state):
            if i < len(category_names):
                category = category_names[i]
                total_return += value * returns.get(category, 0.1)
                total_risk += value * risks.get(category, 0.1)
        
        # Minimize risk-adjusted return (negative of Sharpe ratio)
        if total_risk > 0:
            energy = -total_return / total_risk
        else:
            energy = -total_return
        
        return energy
    
    def _calculate_assignment_fitness(self, individual: np.ndarray, team_members: List[Dict[str, Any]], 
                                    tasks: List[Dict[str, Any]], requirements: Dict[str, List[str]]) -> float:
        """Calculate fitness for team assignment"""
        fitness = 0
        
        # Check skill requirements
        for task_idx, task in enumerate(tasks):
            if task_idx < individual.shape[0]:
                task_requirements = requirements.get(task["id"], [])
                assigned_members = individual[task_idx]
                
                for member_idx, assignment_prob in enumerate(assigned_members):
                    if member_idx < len(team_members) and assignment_prob > 0.5:
                        member_skills = team_members[member_idx].get("skills", [])
                        skill_match = len(set(task_requirements) & set(member_skills))
                        fitness += skill_match / len(task_requirements) if task_requirements else 0
        
        # Penalize over-assignment
        total_assignments = np.sum(individual > 0.5)
        if total_assignments > len(tasks):
            fitness += (total_assignments - len(tasks)) * 0.1
        
        return -fitness  # Minimize (negative fitness)
    
    def _calculate_convergence_rate(self, history: List[float]) -> float:
        """Calculate convergence rate from optimization history"""
        if len(history) < 10:
            return 0.0
        
        # Calculate improvement over last 10% of iterations
        last_10_percent = int(len(history) * 0.1)
        if last_10_percent < 2:
            return 0.0
        
        recent_history = history[-last_10_percent:]
        improvement = (recent_history[0] - recent_history[-1]) / recent_history[0]
        
        return max(0.0, min(1.0, improvement))
    
    def _create_task_graph(self, tasks: List[Dict[str, Any]], 
                          dependencies: List[Tuple[str, str]]) -> nx.DiGraph:
        """Create task dependency graph"""
        G = nx.DiGraph()
        
        # Add tasks as nodes
        for task in tasks:
            G.add_node(task["id"], **task)
        
        # Add dependencies as edges
        for dep_from, dep_to in dependencies:
            G.add_edge(dep_from, dep_to)
        
        return G
    
    def _apply_qaoa_circuit(self, gamma_params: np.ndarray, beta_params: np.ndarray, 
                           task_graph: nx.DiGraph) -> np.ndarray:
        """Apply QAOA circuit (simplified simulation)"""
        num_qubits = len(task_graph.nodes())
        quantum_state = np.ones(2**num_qubits) / np.sqrt(2**num_qubits)
        
        # Simulate QAOA layers
        for gamma, beta in zip(gamma_params, beta_params):
            # Cost Hamiltonian (simplified)
            cost_hamiltonian = np.diag(np.random.uniform(-1, 1, 2**num_qubits))
            quantum_state = np.exp(-1j * gamma * cost_hamiltonian) @ quantum_state
            
            # Mixer Hamiltonian (simplified)
            mixer_hamiltonian = np.diag(np.random.uniform(-1, 1, 2**num_qubits))
            quantum_state = np.exp(-1j * beta * mixer_hamiltonian) @ quantum_state
        
        return quantum_state
    
    def _apply_vqe_circuit(self, theta_params: np.ndarray, categories: Dict[str, float], 
                          returns: Dict[str, float], risks: Dict[str, float]) -> np.ndarray:
        """Apply VQE circuit (simplified simulation)"""
        num_qubits = len(categories)
        quantum_state = np.ones(2**num_qubits) / np.sqrt(2**num_qubits)
        
        # Simulate VQE ansatz
        for theta in theta_params:
            # Parameterized quantum circuit (simplified)
            rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                      [np.sin(theta), np.cos(theta)]])
            quantum_state = np.kron(rotation_matrix, np.eye(2**(num_qubits-1))) @ quantum_state
        
        return quantum_state
    
    def _update_qaoa_parameters(self, gamma_params: np.ndarray, beta_params: np.ndarray, 
                               energy: float, task_graph: nx.DiGraph) -> Tuple[np.ndarray, np.ndarray]:
        """Update QAOA parameters using gradient descent"""
        learning_rate = 0.01
        
        # Simplified gradient update
        gamma_grad = np.random.uniform(-0.1, 0.1, len(gamma_params))
        beta_grad = np.random.uniform(-0.1, 0.1, len(beta_params))
        
        new_gamma = gamma_params - learning_rate * gamma_grad
        new_beta = beta_params - learning_rate * beta_grad
        
        return new_gamma, new_beta
    
    def _update_vqe_parameters(self, theta_params: np.ndarray, energy: float, 
                              categories: Dict[str, float], returns: Dict[str, float], 
                              risks: Dict[str, float]) -> np.ndarray:
        """Update VQE parameters using gradient descent"""
        learning_rate = 0.01
        
        # Simplified gradient update
        theta_grad = np.random.uniform(-0.1, 0.1, len(theta_params))
        new_theta = theta_params - learning_rate * theta_grad
        
        return new_theta
    
    def _generate_schedule_from_solution(self, solution: np.ndarray, task_graph: nx.DiGraph) -> Dict[str, Any]:
        """Generate schedule from optimization solution"""
        schedule = {}
        
        for i, node in enumerate(task_graph.nodes()):
            if i < len(solution):
                schedule[node] = {
                    "start_time": float(solution[i] * 100),  # Scale to realistic time
                    "duration": task_graph.nodes[node].get("duration", 1.0),
                    "assigned": solution[i] > 0.5
                }
        
        return schedule
    
    def _quantum_selection(self, population: List[np.ndarray], fitness_scores: List[float]) -> List[np.ndarray]:
        """Quantum selection operator"""
        # Tournament selection with quantum interference
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            # Select tournament participants
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Quantum interference in selection
            winner_index = tournament_indices[np.argmin(tournament_fitness)]
            selected.append(population[winner_index].copy())
        
        return selected
    
    def _quantum_crossover(self, population: List[np.ndarray]) -> List[np.ndarray]:
        """Quantum crossover operator"""
        offspring = []
        
        for i in range(0, len(population), 2):
            if i + 1 < len(population):
                parent1 = population[i]
                parent2 = population[i + 1]
                
                # Quantum crossover (superposition of parents)
                alpha = random.uniform(0, 1)
                child1 = alpha * parent1 + (1 - alpha) * parent2
                child2 = (1 - alpha) * parent1 + alpha * parent2
                
                offspring.extend([child1, child2])
            else:
                offspring.append(population[i])
        
        return offspring
    
    def _quantum_mutation(self, population: List[np.ndarray]) -> List[np.ndarray]:
        """Quantum mutation operator"""
        mutated = []
        mutation_rate = 0.1
        
        for individual in population:
            mutated_individual = individual.copy()
            
            for i in range(len(individual)):
                if random.random() < mutation_rate:
                    # Quantum mutation (phase shift)
                    mutated_individual[i] *= np.exp(1j * random.uniform(0, 2*np.pi))
            
            mutated.append(mutated_individual)
        
        return mutated
    
    def _convert_to_assignments(self, solution: np.ndarray, team_members: List[Dict[str, Any]], 
                              tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert optimization solution to team assignments"""
        assignments = {}
        
        for task_idx, task in enumerate(tasks):
            if task_idx < solution.shape[0]:
                task_assignments = []
                for member_idx, assignment_prob in enumerate(solution[task_idx]):
                    if member_idx < len(team_members) and assignment_prob > 0.5:
                        task_assignments.append({
                            "member_id": team_members[member_idx]["id"],
                            "name": team_members[member_idx]["name"],
                            "assignment_probability": float(assignment_prob)
                        })
                
                assignments[task["id"]] = {
                    "task_name": task["name"],
                    "assigned_members": task_assignments
                }
        
        return assignments
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        with self.lock:
            total_optimizations = len(self.optimization_history)
            
            if total_optimizations == 0:
                return {"total_optimizations": 0}
            
            # Statistics by optimization type
            type_stats = defaultdict(int)
            algorithm_stats = defaultdict(int)
            
            for result in self.optimization_history:
                type_stats[result.optimization_type.value] += 1
                algorithm_stats[result.algorithm.value] += 1
            
            # Average performance metrics
            avg_execution_time = sum(r.execution_time for r in self.optimization_history) / total_optimizations
            avg_iterations = sum(r.iterations for r in self.optimization_history) / total_optimizations
            avg_convergence_rate = sum(r.convergence_rate for r in self.optimization_history) / total_optimizations
            avg_confidence = sum(r.confidence for r in self.optimization_history) / total_optimizations
            
            return {
                "total_optimizations": total_optimizations,
                "optimization_types": dict(type_stats),
                "algorithms_used": dict(algorithm_stats),
                "average_execution_time": avg_execution_time,
                "average_iterations": avg_iterations,
                "average_convergence_rate": avg_convergence_rate,
                "average_confidence": avg_confidence,
                "quantum_parameters": self.quantum_parameters
            }

# Global quantum optimizer instance
_quantum_optimizer = None

def get_quantum_optimizer() -> QuantumOptimizer:
    """Get global quantum optimizer instance"""
    global _quantum_optimizer
    if _quantum_optimizer is None:
        _quantum_optimizer = QuantumOptimizer()
    return _quantum_optimizer

# Example usage
if __name__ == "__main__":
    # Initialize quantum optimizer
    quantum_opt = get_quantum_optimizer()
    
    # Test resource allocation optimization
    resources = {
        "marketing": 100000,
        "development": 150000,
        "operations": 75000,
        "contingency": 25000
    }
    
    constraints = {
        "total_budget": 350000,
        "max_budget": 400000,
        "min_marketing": 50000
    }
    
    result = quantum_opt.optimize_resource_allocation(resources, constraints)
    print("Resource Allocation Optimization:")
    print(f"Objective Value: {result.objective_value:.2f}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Confidence: {result.confidence:.2f}")
    print("Solution:", json.dumps(result.solution, indent=2))
    
    # Test timeline optimization
    tasks = [
        {"id": "task1", "name": "Market Research", "duration": 10},
        {"id": "task2", "name": "Product Development", "duration": 30},
        {"id": "task3", "name": "Testing", "duration": 15},
        {"id": "task4", "name": "Launch", "duration": 5}
    ]
    
    dependencies = [("task1", "task2"), ("task2", "task3"), ("task3", "task4")]
    resources = {"team_size": 10, "budget": 200000}
    
    timeline_result = quantum_opt.optimize_timeline(tasks, dependencies, resources)
    print(f"\nTimeline Optimization:")
    print(f"Objective Value: {timeline_result.objective_value:.2f}")
    print(f"Execution Time: {timeline_result.execution_time:.2f}s")
    print("Schedule:", json.dumps(timeline_result.solution, indent=2))
    
    # Get statistics
    stats = quantum_opt.get_optimization_statistics()
    print(f"\nOptimization Statistics:")
    print(json.dumps(stats, indent=2))








