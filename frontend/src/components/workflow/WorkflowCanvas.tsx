"use client";

import { useCallback, useMemo, useEffect, useRef } from "react";
import ReactFlow, {
  Node,
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
} from "reactflow";
import "reactflow/dist/style.css";

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
};

export function WorkflowCanvas({
  workflowItems,
  setWorkflowItems,
  onCompile,
}: {
  workflowItems: WorkflowComponent[];
  setWorkflowItems: (items: WorkflowComponent[] | ((prev: WorkflowComponent[]) => WorkflowComponent[])) => void;
  onCompile: () => void;
}) {
  // Keep track of existing nodes to maintain their positions
  const existingNodesRef = useRef<Map<string, Node>>(new Map());
  
  // Memoize the node creation to prevent unnecessary recalculations
  const initialNodes = useMemo(() => 
    workflowItems.map((item) => {
      // If node already exists, use its position
      const existingNode = existingNodesRef.current.get(item.id);
      const position = existingNode?.position || { x: 250, y: Math.random() * 500 }; // Random y position for new nodes
      
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
        },
      };
      
      // Store the node for future reference
      existingNodesRef.current.set(item.id, node);
      return node;
    }), [workflowItems, setWorkflowItems]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Update nodes when workflowItems change, preserving positions
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  // Handle node changes (including position updates)
  const onNodesChangeHandler = useCallback(
    (changes: NodeChange[]) => {
      setNodes((nds) => {
        const updatedNodes = applyNodeChanges(changes, nds);
        // Update our reference with new positions
        updatedNodes.forEach((node) => {
          existingNodesRef.current.set(node.id, node);
        });
        return updatedNodes;
      });
    },
    [setNodes]
  );

  // Handle edge changes (including deletions)
  const onEdgesChangeHandler = useCallback(
    (changes: EdgeChange[]) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
    },
    [setEdges]
  );

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Handle node deletion
  const onNodesDelete: OnNodesDelete = useCallback(
    (deleted) => {
      deleted.forEach((node) => {
        existingNodesRef.current.delete(node.id);
      });
    },
    []
  );

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeHandler}
        onEdgesChange={onEdgesChangeHandler}
        onConnect={onConnect}
        onNodesDelete={onNodesDelete}
        nodeTypes={nodeTypes}
        deleteKeyCode={['Backspace', 'Delete']}
        nodesDraggable={true}
        edgesFocusable={true}
        elementsSelectable={true}
      >
        <Background />
        <Controls />
      </ReactFlow>
      {/* <div className="flex justify-center gap-2 mt-4">
        <button
          disabled={workflowItems.length === 0}
          className="btn btn-wide btn-primary"
          onClick={onCompile}
        >
          <Settings className="h-4 w-4 mr-2" /> Compile
        </button>
      </div> */}
    </div>
  );
}