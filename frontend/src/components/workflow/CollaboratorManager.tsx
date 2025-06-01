"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Users } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface Collaborator {
  email: string;
}

interface CollaboratorManagerProps {
  workflowName: string;
  collaborators: string[];
  canManageCollaborators: boolean;
  onCollaboratorsChange?: (collaborators: string[]) => void;
}

export default function CollaboratorManager({
  workflowName,
  collaborators,
  canManageCollaborators,
  onCollaboratorsChange,
}: CollaboratorManagerProps) {
  const { token } = useAuth();
  const [localCollaborators, setLocalCollaborators] = useState<string[]>(
    Array.isArray(collaborators) ? collaborators : []
  );
  const [newCollaboratorEmail, setNewCollaboratorEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLocalCollaborators(Array.isArray(collaborators) ? collaborators : []);
  }, [collaborators]);

  const addCollaborator = async () => {
    if (!newCollaboratorEmail.trim()) return;
    
    // Check if user is authenticated
    if (!token) {
      setError("You must be logged in to manage collaborators");
      return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newCollaboratorEmail.trim())) {
      setError("Please enter a valid email address");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/workflows/${workflowName.replace(/ /g, "_")}/collaborators`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`, // Use token from auth context
        },
        body: JSON.stringify({ email: newCollaboratorEmail.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to add collaborator");
      }

      const updatedCollaborators = [...localCollaborators, newCollaboratorEmail.trim()];
      setLocalCollaborators(updatedCollaborators);
      setNewCollaboratorEmail("");
      onCollaboratorsChange?.(updatedCollaborators);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add collaborator");
    } finally {
      setIsLoading(false);
    }
  };

  const removeCollaborator = async (email: string) => {
    // Check if user is authenticated
    if (!token) {
      setError("You must be logged in to manage collaborators");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `/api/workflows/${workflowName.replace(/ /g, "_")}/collaborators/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
          headers: {
            "Authorization": `Bearer ${token}`, // Use token from auth context
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to remove collaborator");
      }

      const updatedCollaborators = localCollaborators.filter(c => c !== email);
      setLocalCollaborators(updatedCollaborators);
      onCollaboratorsChange?.(updatedCollaborators);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove collaborator");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      addCollaborator();
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200  p-4">
      <div className="flex items-center gap-2 mb-4">
        <Users className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Collaborators</h3>
      </div>

      {error && (
        <div className={`alert mb-4 ${
          error.includes("not registered") ? "alert-info" : "alert-error"
        }`}>
          <div className="flex flex-col">
            <span className="font-medium">
              {error.includes("not registered") ? "User Not Found" : "Error"}
            </span>
            <span className="text-sm mt-1">{error}</span>
          </div>
        </div>
      )}

      {/* Add new collaborator */}
      {canManageCollaborators && (
        <div className="mb-4">
          <div className="flex gap-2">
            <input
              type="email"
              placeholder="Enter collaborator email"
              className="input input-bordered flex-1"
              value={newCollaboratorEmail}
              onChange={(e) => setNewCollaboratorEmail(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              className="btn btn-primary"
              onClick={addCollaborator}
              disabled={isLoading || !newCollaboratorEmail.trim()}
            >
              {isLoading ? (
                <span className="loading loading-spinner loading-sm"></span>
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Add
            </button>
          </div>
        </div>
      )}

      {/* Collaborators list */}
      <div className="space-y-2">
        {localCollaborators.length === 0 ? (
          <p className="text-base-content/50 text-center py-4">
            No collaborators added yet.
          </p>
        ) : (
          localCollaborators.map((email) => (
            <div
              key={email}
              className="flex items-center justify-between p-3 bg-base-200 rounded-lg"
            >
              <span className="text-sm font-medium">{email}</span>
              {canManageCollaborators && (
                <button
                  className="btn btn-ghost btn-sm text-error hover:bg-error hover:text-error-content"
                  onClick={() => removeCollaborator(email)}
                  disabled={isLoading}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {!canManageCollaborators && (
        <p className="text-sm text-base-content/60 mt-2">
          Only the workflow owner can manage collaborators.
        </p>
      )}
    </div>
  );
}