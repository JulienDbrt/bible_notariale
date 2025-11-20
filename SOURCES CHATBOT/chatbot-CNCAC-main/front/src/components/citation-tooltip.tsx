'use client';

import React from 'react';
import { Info, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Badge } from '@/components/ui/badge';
import { Citation } from '@/lib/types';
import { cn } from '@/lib/utils';

interface CitationTooltipProps {
  citations: Citation[];
  className?: string;
}

const CitationTooltip: React.FC<CitationTooltipProps> = ({ citations, className }) => {
  if (!citations || citations.length === 0) {
    return null;
  }

  // Extract filename from document path for display
  const getDisplayName = (path: string) => {
    if (path.includes('/')) {
      return path.split('/').pop() || path;
    }
    return path;
  };

  // Truncate text for preview
  const getPreviewText = (text: string, maxLength: number = 120) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <TooltipProvider delayDuration={300}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-6 w-6 p-0 rounded-full opacity-60 hover:opacity-100 transition-opacity",
              "bg-primary/10 hover:bg-primary/20",
              className
            )}
          >
            <Info className="h-3 w-3" />
            <span className="sr-only">
              Voir les passages sources ({citations.length})
            </span>
          </Button>
        </TooltipTrigger>
        <TooltipContent
          side="top"
          align="start"
          className="max-w-md p-0 border-0 bg-transparent shadow-none"
        >
          <div className="bg-popover border rounded-lg shadow-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">
                Passages sources ({citations.length})
              </span>
            </div>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {citations.map((citation, index) => (
                <div
                  key={`${citation.documentId}-${index}`}
                  className="flex items-start gap-2"
                >
                  <Badge
                    variant="secondary"
                    className="text-xs shrink-0 mt-0.5"
                  >
                    {index + 1}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate mb-1"
                         title={citation.documentPath}>
                      {getDisplayName(citation.documentPath)}
                    </div>
                    <div className="text-xs text-muted-foreground leading-relaxed">
                      "{getPreviewText(citation.text)}"
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default CitationTooltip;
