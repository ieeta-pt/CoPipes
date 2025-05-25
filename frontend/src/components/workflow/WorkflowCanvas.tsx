"use client";

import { useCallback, useMemo, useEffect, useRef } from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  OnNodesDelete,
  NodeChange,
  EdgeChange,
  applyNodeChanges,
  applyEdgeChanges,
  useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";
import dagre from "@dagrejs/dagre";

import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { Settings } from "lucide-react";
import { WorkflowNode } from "@/components/workflow/WorkflowNode";

// Custom node types
const nodeTypes = {
  workflowNode: WorkflowNode,
};

type WorkflowNodeData = {
  item: WorkflowComponent;
  onRemove: (id: string) => void;
  onUpdate: (config: WorkflowComponent["config"]) => void;
  onDependenciesChange: (dependencies: string[]) => void;
};

// Function to get layouted nodes and edges
const getLayoutedNodes = (nodes: Node[], edges: Edge[], direction = "TB") => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction, nodesep: 100, ranksep: 100 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 100, height: 100 }); // Adjust these values based on your node size
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  return nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 125, // Center the node (width/2)
        y: nodeWithPosition.y - 50, // Center the node (height/2)
      },
    };
  });
};

export function WorkflowCanvas({
  workflowItems,
  setWorkflowItems,
  onCompile,
}: {
  workflowItems: WorkflowComponent[];
  setWorkflowItems: (
    items:
      | WorkflowComponent[]
      | ((prev: WorkflowComponent[]) => WorkflowComponent[])
  ) => void;
  onCompile: () => void;
}) {
  // Keep track of existing nodes to maintain their positions
  const existingNodesRef = useRef<Map<string, Node>>(new Map());

  // Memoize the node creation to prevent unnecessary recalculations
  const initialNodes = useMemo(
    () =>
      workflowItems.map((item) => {
        // If node already exists, use its position
        const existingNode = existingNodesRef.current.get(item.id);
        const position = existingNode?.position || {
          x: 250,
          y: Math.random() * 500,
        };

        const node: Node = {
          id: item.id,
          type: "workflowNode",
          position,
          data: {
            item,
            onRemove: (id: string) => {
              setWorkflowItems((currentItems: WorkflowComponent[]) =>
                currentItems.filter((i: WorkflowComponent) => i.id !== id)
              );
            },
            onUpdate: (newConfig: WorkflowComponent["config"]) => {
              setWorkflowItems((currentItems: WorkflowComponent[]) => {
                const updated = [...currentItems];
                const index = updated.findIndex((i) => i.id === item.id);
                if (index !== -1) {
                  updated[index].config = newConfig;
                }
                return updated;
              });
            },
            onDependenciesChange: (dependencies: string[]) => {
              setWorkflowItems((currentItems: WorkflowComponent[]) => {
                const updated = [...currentItems];
                const index = updated.findIndex((i) => i.id === item.id);
                if (index !== -1) {
                  updated[index].dependencies = dependencies;
                }
                return updated;
              });
            },
          },
        };

        existingNodesRef.current.set(item.id, node);
        return node;
      }),
    [workflowItems, setWorkflowItems]
  );

  // Create initial edges from dependencies
  const initialEdges = useMemo(() => {
    const edges: Edge[] = [];
    workflowItems.forEach((item) => {
      if (item.dependencies) {
        item.dependencies.forEach((depId) => {
          edges.push({
            id: `${depId}-${item.id}`,
            source: depId,
            target: item.id,
            type: "smoothstep",
          });
        });
      }
    });
    return edges;
  }, [workflowItems]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Apply layout when workflowItems or edges change
  useEffect(() => {
    const layoutedNodes = getLayoutedNodes(initialNodes, edges);
    setNodes(layoutedNodes);
    // eslint-disable-next-line
  }, [workflowItems, edges]);

  // Handle edge changes (including deletions)
  const onEdgesChangeHandler = useCallback(
    (changes: EdgeChange[]) => {
      setEdges((eds) => {
        const updatedEdges = applyEdgeChanges(changes, eds);

        // Update dependencies in workflow items
        const newDependencies = new Map<string, string[]>();
        updatedEdges.forEach((edge) => {
          const targetDeps = newDependencies.get(edge.target) || [];
          targetDeps.push(edge.source);
          newDependencies.set(edge.target, targetDeps);
        });

        // Update workflow items with new dependencies
        // setWorkflowItems((currentItems) => {
        //   return currentItems.map((item) => {
        //     const deps = newDependencies.get(item.id) || [];
        //     return { ...item, dependencies: deps };
        //   });
        // });

        return updatedEdges;
      });
    },
    [setEdges]
  );

  // Update dependencies in workflowItems when a new edge is created
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Add this effect to sync dependencies when edges change
  useEffect(() => {
    // Build dependencies from edges
    const newDependencies = new Map<string, string[]>();
    edges.forEach((edge) => {
      const targetDeps = newDependencies.get(edge.target) || [];
      targetDeps.push(edge.source);
      newDependencies.set(edge.target, targetDeps);
    });

    setWorkflowItems((currentItems) =>
      currentItems.map((item) => {
        const deps = newDependencies.get(item.id) || [];
        return { ...item, dependencies: deps };
      })
    );
    // eslint-disable-next-line
  }, [edges]);

  // Handle node deletion
  const onNodesDelete: OnNodesDelete = useCallback((deleted) => {
    deleted.forEach((node) => {
      existingNodesRef.current.delete(node.id);
    });
  }, []);

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChangeHandler}
        onConnect={onConnect}
        onNodesDelete={onNodesDelete}
        nodeTypes={nodeTypes}
        deleteKeyCode={["Backspace", "Delete"]}
        nodesDraggable={true}
        edgesFocusable={true}
        elementsSelectable={true}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
