"""
Análisis de Mercado con Grafos

Análisis de relaciones y conexiones en el mercado usando teoría de grafos:
- Análisis de relaciones entre entidades
- Detección de comunidades
- Análisis de centralidad
- Identificación de nodos clave
- Análisis de caminos y conexiones
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MarketNode:
    """Nodo en el grafo de mercado."""
    node_id: str
    node_type: str  # 'company', 'product', 'trend', 'market'
    name: str
    attributes: Dict[str, Any]
    connections: Set[str]  # IDs de nodos conectados


@dataclass
class MarketGraph:
    """Grafo de mercado."""
    nodes: Dict[str, MarketNode]
    edges: List[Tuple[str, str, float]]  # (source, target, weight)
    communities: Dict[str, List[str]]  # community_id -> node_ids
    central_nodes: List[str]


class MarketGraphAnalyzer:
    """Analizador de grafos de mercado."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def build_market_graph(
        self,
        market_data: Dict[str, Any],
        industry: str
    ) -> MarketGraph:
        """
        Construye grafo de mercado.
        
        Args:
            market_data: Datos de mercado
            industry: Industria
            
        Returns:
            Grafo de mercado
        """
        logger.info(f"Building market graph for {industry}")
        
        nodes = {}
        edges = []
        
        # Crear nodos para empresas/competidores
        competitors = market_data.get("competitors", [])
        for comp in competitors:
            node_id = f"comp_{comp}"
            nodes[node_id] = MarketNode(
                node_id=node_id,
                node_type="company",
                name=comp,
                attributes={"industry": industry},
                connections=set()
            )
        
        # Crear nodos para tendencias
        trends = market_data.get("trends", [])
        for trend in trends:
            trend_name = trend.get("trend_name", "unknown")
            node_id = f"trend_{trend_name.replace(' ', '_')}"
            nodes[node_id] = MarketNode(
                node_id=node_id,
                node_type="trend",
                name=trend_name,
                attributes=trend,
                connections=set()
            )
        
        # Crear edges (conexiones)
        for i, comp1 in enumerate(competitors):
            for comp2 in competitors[i+1:]:
                # Competidores están conectados
                weight = 0.5  # Peso de competencia
                edges.append((f"comp_{comp1}", f"comp_{comp2}", weight))
                nodes[f"comp_{comp1}"].connections.add(f"comp_{comp2}")
                nodes[f"comp_{comp2}"].connections.add(f"comp_{comp1}")
        
        # Conectar tendencias con empresas
        for trend_node in [n for n in nodes.values() if n.node_type == "trend"]:
            for comp_node in [n for n in nodes.values() if n.node_type == "company"]:
                weight = 0.3  # Peso de relación
                edges.append((trend_node.node_id, comp_node.node_id, weight))
                trend_node.connections.add(comp_node.node_id)
                comp_node.connections.add(trend_node.node_id)
        
        # Detectar comunidades
        communities = self._detect_communities(nodes, edges)
        
        # Identificar nodos centrales
        central_nodes = self._identify_central_nodes(nodes, edges)
        
        return MarketGraph(
            nodes=nodes,
            edges=edges,
            communities=communities,
            central_nodes=central_nodes
        )
    
    def _detect_communities(
        self,
        nodes: Dict[str, MarketNode],
        edges: List[Tuple[str, str, float]]
    ) -> Dict[str, List[str]]:
        """Detecta comunidades en el grafo."""
        # Algoritmo simplificado de detección de comunidades
        communities = {}
        visited = set()
        community_id = 0
        
        for node_id, node in nodes.items():
            if node_id in visited:
                continue
            
            # BFS para encontrar comunidad
            community = []
            queue = [node_id]
            visited.add(node_id)
            
            while queue:
                current = queue.pop(0)
                community.append(current)
                
                for neighbor in nodes[current].connections:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            communities[f"community_{community_id}"] = community
            community_id += 1
        
        return communities
    
    def _identify_central_nodes(
        self,
        nodes: Dict[str, MarketNode],
        edges: List[Tuple[str, str, float]]
    ) -> List[str]:
        """Identifica nodos centrales usando grado."""
        # Calcular grado (número de conexiones)
        degrees = {
            node_id: len(node.connections)
            for node_id, node in nodes.items()
        }
        
        # Ordenar por grado
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        
        # Top 5 nodos más centrales
        return [node_id for node_id, _ in sorted_nodes[:5]]
    
    def analyze_graph_structure(
        self,
        graph: MarketGraph
    ) -> Dict[str, Any]:
        """Analiza estructura del grafo."""
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        
        # Calcular densidad
        max_edges = total_nodes * (total_nodes - 1) / 2
        density = total_edges / max_edges if max_edges > 0 else 0
        
        # Análisis de comunidades
        community_sizes = [len(nodes) for nodes in graph.communities.values()]
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "graph_density": density,
            "communities_count": len(graph.communities),
            "average_community_size": sum(community_sizes) / len(community_sizes) if community_sizes else 0,
            "central_nodes": [
                {
                    "node_id": node_id,
                    "name": graph.nodes[node_id].name,
                    "type": graph.nodes[node_id].node_type,
                    "connections": len(graph.nodes[node_id].connections)
                }
                for node_id in graph.central_nodes
            ]
        }






