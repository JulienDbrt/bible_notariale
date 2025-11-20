'use client';

import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { FileText } from 'lucide-react';
import type { Citation } from '@/lib/types';
import { SourceModal } from './source-modal';

interface CitationBadgesProps {
  citations: Citation[];
  className?: string;
}

export const CitationBadges: React.FC<CitationBadgesProps> = ({ citations, className }) => {
  const [selectedCitation, setSelectedCitation] = useState<{ citation: Citation; index: number } | null>(null);

  if (!citations || citations.length === 0) {
    return null;
  }

  const getDisplayName = (path: string): string => {
    if (!path) return 'Source';
    if (path.includes('/')) {
      const fileName = path.split('/').pop() || path;
      // Tronquer si trop long
      return fileName.length > 20 ? fileName.substring(0, 17) + '...' : fileName;
    }
    return path.length > 20 ? path.substring(0, 17) + '...' : path;
  };

  // Compter le nombre de documents uniques
  const uniqueDocuments = new Set(citations.map(c => c.documentPath)).size;
  const totalPassages = citations.length;

  return (
    <div className={`flex items-center gap-2 flex-wrap ${className || ''}`}>
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <FileText className="h-3 w-3" />
        <span className="font-medium">
          {totalPassages} passage{totalPassages > 1 ? 's' : ''} source{totalPassages > 1 ? 's' : ''} • {uniqueDocuments} document{uniqueDocuments > 1 ? 's' : ''}:
        </span>
      </div>

      {citations.map((citation, index) => (
        <Badge
          key={`${citation.documentId}-${index}`}
          variant="secondary"
          className="cursor-pointer hover:bg-secondary/80 transition-colors gap-1.5"
          onClick={() => setSelectedCitation({ citation, index })}
          title={`Cliquer pour voir le passage extrait de: ${citation.documentPath}`}
        >
          <span className="font-mono text-xs">{index + 1}</span>
          <span className="text-xs">{getDisplayName(citation.documentPath)}</span>
        </Badge>
      ))}

      {selectedCitation && (
        <SourceModal
          citation={selectedCitation.citation}
          index={selectedCitation.index}
          open={!!selectedCitation}
          onOpenChange={(open) => !open && setSelectedCitation(null)}
        />
      )}
    </div>
  );
};
