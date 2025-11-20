'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { Viewport } from 'pixi-viewport';

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  size: number;
  color: string;
  degree: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics?: {
    nodes: number;
    chunks: number;
    documents: number;
    relations: number;
  };
}

interface KnowledgeGraphCanvasProps {
  data: GraphData;
  width?: number;
  height?: number;
}

interface NodeGraphics {
  circle: PIXI.Graphics;
  text: PIXI.Text;
  data: GraphNode;
  x: number;
  y: number;
}

export const KnowledgeGraphCanvas: React.FC<KnowledgeGraphCanvasProps> = ({
  data,
  width = 1200,
  height = 800,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const viewportRef = useRef<Viewport | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize PixiJS Application
    const app = new PIXI.Application();

    // Initialize the application
    (async () => {
      await app.init({
        width,
        height,
        backgroundColor: 0x1a1a1a,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
      });

      if (!containerRef.current) return;

      containerRef.current.innerHTML = '';
      containerRef.current.appendChild(app.canvas);

      // Create viewport for pan/zoom
      const viewport = new Viewport({
        screenWidth: width,
        screenHeight: height,
        worldWidth: width * 10,
        worldHeight: height * 10,
        events: app.renderer.events,
      });

      app.stage.addChild(viewport);

      // Activate plugins
      viewport
        .drag()
        .pinch()
        .wheel()
        .decelerate();

      viewportRef.current = viewport;
      appRef.current = app;

      // Render the graph
      renderGraph(viewport, data);
    })();

    // Cleanup
    return () => {
      if (appRef.current) {
        appRef.current.destroy(true, { children: true });
        appRef.current = null;
      }
    };
  }, [data, width, height]);

  // Force-directed layout algorithm
  const calculateForceDirectedLayout = (
    nodes: GraphNode[],
    edges: GraphEdge[],
    iterations: number = 200  // Augmenté pour meilleure convergence
  ): Map<string, { x: number; y: number }> => {
    const positions = new Map<string, { x: number; y: number }>();
    const velocities = new Map<string, { vx: number; vy: number }>();

    // Initialize positions randomly with massive spread
    const centerX = width * 5;  // Centre du monde 10x
    const centerY = height * 5;
    const spreadRadius = Math.min(width, height) * 3;  // Distribution initiale MASSIVE

    nodes.forEach((node) => {
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.random() * spreadRadius;
      positions.set(node.id, {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
      });
      velocities.set(node.id, { vx: 0, vy: 0 });
    });

    // Build adjacency map for faster edge lookups
    const adjacency = new Map<string, Set<string>>();
    edges.forEach((edge) => {
      if (!adjacency.has(edge.source)) adjacency.set(edge.source, new Set());
      if (!adjacency.has(edge.target)) adjacency.set(edge.target, new Set());
      adjacency.get(edge.source)!.add(edge.target);
      adjacency.get(edge.target)!.add(edge.source);
    });

    // Physics parameters - Équilibre entre répulsion et stabilité
    const repulsionStrength = 50000;  // Force de répulsion modérée mais efficace
    const attractionStrength = 0.01;  // Attraction légèrement augmentée pour cohésion
    const damping = 0.85;  // Damping pour convergence stable

    // Simulation iterations
    for (let iter = 0; iter < iterations; iter++) {
      const forces = new Map<string, { fx: number; fy: number }>();

      // Initialize forces
      nodes.forEach((node) => {
        forces.set(node.id, { fx: 0, fy: 0 });
      });

      // Repulsion between all nodes - appliquée à TOUS les nœuds
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const node1 = nodes[i];
          const node2 = nodes[j];

          const pos1 = positions.get(node1.id)!;
          const pos2 = positions.get(node2.id)!;

          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          // Force de répulsion inversement proportionnelle au carré de la distance
          // Plus forte pour les nœuds proches, mais pas de condition spéciale
          const force = repulsionStrength / Math.max(distance * distance, 100);

          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;

          forces.get(node1.id)!.fx -= fx;
          forces.get(node1.id)!.fy -= fy;
          forces.get(node2.id)!.fx += fx;
          forces.get(node2.id)!.fy += fy;
        }
      }

      // Attraction along edges
      edges.forEach((edge) => {
        const pos1 = positions.get(edge.source);
        const pos2 = positions.get(edge.target);

        if (!pos1 || !pos2) return;

        const dx = pos2.x - pos1.x;
        const dy = pos2.y - pos1.y;
        const distance = Math.sqrt(dx * dx + dy * dy) || 1;

        const force = distance * attractionStrength;
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;

        forces.get(edge.source)!.fx += fx;
        forces.get(edge.source)!.fy += fy;
        forces.get(edge.target)!.fx -= fx;
        forces.get(edge.target)!.fy -= fy;
      });

      // Update velocities and positions
      nodes.forEach((node) => {
        const force = forces.get(node.id)!;
        const vel = velocities.get(node.id)!;
        const pos = positions.get(node.id)!;

        vel.vx = (vel.vx + force.fx) * damping;
        vel.vy = (vel.vy + force.fy) * damping;

        pos.x += vel.vx;
        pos.y += vel.vy;

        // Keep nodes within bounds (monde 10x plus grand)
        const margin = 50;
        pos.x = Math.max(margin, Math.min(width * 10 - margin, pos.x));
        pos.y = Math.max(margin, Math.min(height * 10 - margin, pos.y));
      });
    }

    return positions;
  };

  const renderGraph = (viewport: Viewport, graphData: GraphData) => {
    const { nodes, edges } = graphData;

    // Calculate positions using force-directed layout
    const nodeMap = new Map<string, NodeGraphics>();
    const positions = calculateForceDirectedLayout(nodes, edges);

    // Create node graphics
    nodes.forEach((node) => {
      const pos = positions.get(node.id)!;
      const x = pos.x;
      const y = pos.y;

      // Create circle
      const circle = new PIXI.Graphics();
      const nodeColor = parseInt(node.color.replace('#', ''), 16);

      circle.circle(0, 0, node.size);
      circle.fill({ color: nodeColor, alpha: 0.8 });
      circle.stroke({ color: 0xffffff, width: 2 });

      circle.x = x;
      circle.y = y;
      circle.eventMode = 'static';
      circle.cursor = 'pointer';

      // Create label
      const text = new PIXI.Text({
        text: node.label.length > 20 ? node.label.substring(0, 17) + '...' : node.label,
        style: {
          fontSize: 12,
          fill: 0xffffff,
          align: 'center',
        },
      });

      text.x = x;
      text.y = y + node.size + 10;
      text.anchor.set(0.5, 0);

      // Event handlers
      circle.on('pointerover', () => {
        circle.scale.set(1.2);
        circle.alpha = 1;
        setSelectedNode(node);
      });

      circle.on('pointerout', () => {
        circle.scale.set(1);
        circle.alpha = 0.8;
        setSelectedNode(null);
      });

      circle.on('click', () => {
        console.log('Node clicked:', node);
        // Center viewport on clicked node
        viewport.animate({
          position: { x, y },
          scale: 1.5,
          time: 500,
        });
      });

      viewport.addChild(circle);
      viewport.addChild(text);

      nodeMap.set(node.id, { circle, text, data: node, x, y });
    });

    // Draw edges
    edges.forEach((edge) => {
      const sourceNode = nodeMap.get(edge.source);
      const targetNode = nodeMap.get(edge.target);

      if (sourceNode && targetNode) {
        const line = new PIXI.Graphics();

        line.moveTo(sourceNode.x, sourceNode.y);
        line.lineTo(targetNode.x, targetNode.y);
        line.stroke({ color: 0x555555, width: 2, alpha: 0.3 });

        // Add edge to viewport (behind nodes)
        viewport.addChildAt(line, 0);
      }
    });

    // Center viewport on graph
    if (nodes.length > 0) {
      // Calculate bounding box
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      nodes.forEach((node) => {
        const pos = positions.get(node.id)!;
        minX = Math.min(minX, pos.x);
        minY = Math.min(minY, pos.y);
        maxX = Math.max(maxX, pos.x);
        maxY = Math.max(maxY, pos.y);
      });

      const centerX = (minX + maxX) / 2;
      const centerY = (minY + maxY) / 2;

      viewport.fit();
      viewport.moveCenter(centerX, centerY);
    }
  };

  return (
    <div className="relative">
      <div ref={containerRef} className="rounded-lg overflow-hidden border border-gray-700" />

      {selectedNode && (
        <div className="absolute top-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg max-w-xs">
          <h3 className="font-semibold text-lg mb-2">{selectedNode.label}</h3>
          <div className="space-y-1 text-sm">
            <p><span className="text-gray-400">Type:</span> {selectedNode.type}</p>
            <p><span className="text-gray-400">Connections:</span> {selectedNode.degree}</p>
          </div>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-400">
        <p>Nodes: {data.nodes.length} | Edges: {data.edges.length}</p>
        {data.statistics && (
          <p>
            Total Entities: {data.statistics.nodes} |
            Documents: {data.statistics.documents} |
            Relations: {data.statistics.relations}
          </p>
        )}
      </div>
    </div>
  );
};
