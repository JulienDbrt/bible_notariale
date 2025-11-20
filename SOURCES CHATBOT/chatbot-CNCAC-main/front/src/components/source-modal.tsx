'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileText } from 'lucide-react';
import type { Citation } from '@/lib/types';

interface SourceModalProps {
  citation: Citation;
  index: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const SourceModal: React.FC<SourceModalProps> = ({
  citation,
  index,
  open,
  onOpenChange,
}) => {
  const getDisplayName = (path: string): string => {
    if (!path) return 'Document inconnu';
    if (path.includes('/')) {
      return path.split('/').pop() || path;
    }
    return path;
  };

  const getFileExtension = (path: string): string => {
    if (!path) return '';
    const parts = path.split('.');
    return parts.length > 1 ? parts[parts.length - 1].toUpperCase() : '';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="text-sm">
              Passage {index + 1}
            </Badge>
            <DialogTitle className="flex-1 truncate" title={citation.documentPath}>
              {getDisplayName(citation.documentPath)}
            </DialogTitle>
            {getFileExtension(citation.documentPath) && (
              <Badge variant="outline" className="text-xs">
                {getFileExtension(citation.documentPath)}
              </Badge>
            )}
          </div>
          <DialogDescription className="text-xs text-muted-foreground">
            Passage extrait du document référencé dans la réponse
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Document Information */}
          <div className="flex items-start gap-3 p-4 bg-muted rounded-lg">
            <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium mb-1">Chemin du document</div>
              <div className="text-xs text-muted-foreground font-mono truncate" title={citation.documentPath}>
                {citation.documentPath}
              </div>
              {citation.documentId && (
                <div className="text-xs text-muted-foreground mt-2">
                  ID: <span className="font-mono">{citation.documentId}</span>
                </div>
              )}
            </div>
          </div>

          {/* Source Text */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold">Contenu du passage</h4>
              <Badge variant="outline" className="text-xs">
                {citation.text.length} caractères
              </Badge>
            </div>
            <ScrollArea className="h-[300px] w-full rounded-md border">
              <div className="p-4">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {citation.text}
                </p>
              </div>
            </ScrollArea>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2 border-t">
            <p className="text-xs text-muted-foreground">
              Ce passage a été utilisé pour générer la réponse
            </p>
            {/* Future: Add button to open full document */}
            {/*
            <Button variant="outline" size="sm" className="gap-2">
              <ExternalLink className="h-3 w-3" />
              Ouvrir le document
            </Button>
            */}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
