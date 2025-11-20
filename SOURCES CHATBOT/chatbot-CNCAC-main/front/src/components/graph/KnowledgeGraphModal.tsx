'use client';

import React, { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { KnowledgeGraphCanvas, GraphData } from './KnowledgeGraphCanvas';
import { Loader2 } from 'lucide-react';
import { documentsApi } from '@/lib/api';

interface KnowledgeGraphModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const KnowledgeGraphModal: React.FC<KnowledgeGraphModalProps> = ({
  open,
  onOpenChange,
}) => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && !graphData) {
      loadGraphData();
    }
  }, [open]);

  const loadGraphData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await documentsApi.getKnowledgeGraph();
      setGraphData(data);
    } catch (err) {
      console.error('Failed to load knowledge graph:', err);
      setError(err instanceof Error ? err.message : 'Failed to load knowledge graph');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Knowledge Graph Visualization</DialogTitle>
          <DialogDescription>
            Interactive visualization of entities and relationships in your document corpus
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Loading knowledge graph...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-red-500">
                <p className="font-semibold mb-2">Error loading graph</p>
                <p className="text-sm">{error}</p>
                <button
                  onClick={loadGraphData}
                  className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {!loading && !error && graphData && (
            <div className="h-full flex items-center justify-center">
              <KnowledgeGraphCanvas data={graphData} width={1200} height={700} />
            </div>
          )}

          {!loading && !error && !graphData && (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">No graph data available</p>
            </div>
          )}
        </div>

        <div className="border-t pt-4">
          <p className="text-xs text-muted-foreground">
            💡 Use mouse wheel to zoom, drag to pan, click on nodes to focus
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};
