'use client';

import { useState, useEffect } from 'react';
import { documentsApi, adminApi } from '@/lib/api';
import DocumentManagement from '@/components/document-management';
import { FileText, BrainCircuit, Activity, ChevronDown, ChevronUp, RefreshCw, Sparkles, Shield, AlertCircle, CheckCircle2, XCircle, AlertTriangle, Clock, ChevronRight } from 'lucide-react';
import { Document } from '@/lib/types';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import { CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { KnowledgeGraphModal } from '@/components/graph/KnowledgeGraphModal';

interface FeedbackItem {
  id: string;
  question_text: string;
  response_text: string;
  comment: string;
  user_rating: number;
  created_at: string;
  conversation_id: string;
  analysis?: {
    error_type: string;
    confidence: number;
    affected_entities: string[];
    correction_suggestion: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
  sources?: {
    content: string;
    score: number;
  }[];
}

const severityConfig = {
  low: { color: 'bg-blue-100 text-blue-800', icon: Shield },
  medium: { color: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle },
  high: { color: 'bg-orange-100 text-orange-800', icon: AlertCircle },
  critical: { color: 'bg-red-100 text-red-800', icon: XCircle }
};

const errorTypeLabels: Record<string, string> = {
  factual: 'Erreur Factuelle',
  relational: 'Erreur Relationnelle',
  contextual: 'Erreur Contextuelle',
  incomplete: 'Réponse Incomplète',
  ambiguous: 'Ambiguïté',
  other: 'Autre'
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showStatus, setShowStatus] = useState(false);
  const [ingestionStatus, setIngestionStatus] = useState<{
    total_documents: number;
    document_status: Record<string, number>;
    indexing_status: Record<string, number>;
    ingestion_tracking: Record<string, number>;
    is_processing: boolean;
    last_updated: string;
  } | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [enrichmentLoading, setEnrichmentLoading] = useState(false);
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);
  const [adminComment, setAdminComment] = useState('');
  const [processingFeedback, setProcessingFeedback] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [knowledgeGraphOpen, setKnowledgeGraphOpen] = useState(false);
  const { user } = useCurrentUser();
  const { toast } = useToast();

  const handleStartEmbedding = async () => {
    try {
      toast({
        title: 'Starting Embedding',
        description: 'Initiating document embedding process...',
      });

      const result = await documentsApi.startEmbedding();
      
      if (result.success) {
        toast({
          title: 'Ingestion Started',
          description: `Started processing ${result.documents_found} documents.`,
        });
        
        // Reload documents to show updated status
        loadDocuments();
        // Also refresh status if it's visible
        if (showStatus) {
          fetchIngestionStatus();
        }
      } else {
        toast({
          title: 'Ingestion Failed',
          description: 'Failed to start ingestion process.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Embedding error:', error);
      toast({
        title: 'Embedding Failed',
        description: 'Failed to start embedding process.',
        variant: 'destructive',
      });
    }
  };

  const fetchIngestionStatus = async () => {
    setStatusLoading(true);
    try {
      const status = await documentsApi.getIngestionStatus();
      setIngestionStatus(status);
    } catch (error) {
      console.error('Failed to fetch ingestion status:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch ingestion status',
        variant: 'destructive',
      });
    } finally {
      setStatusLoading(false);
    }
  };

  const handleSyncIndexingStatus = async () => {
    setSyncLoading(true);
    try {
      toast({
        title: 'Syncing Status',
        description: 'Synchronizing indexing status between systems...',
      });

      const result = await documentsApi.syncIndexingStatus();
      
      if (result.success) {
        toast({
          title: 'Sync Completed',
          description: `Updated ${result.updated_count} documents to indexed status.`,
        });
        
        // Refresh status and documents after sync
        await fetchIngestionStatus();
        loadDocuments();
      } else {
        toast({
          title: 'Sync Failed',
          description: 'Failed to sync indexing status.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Sync error:', error);
      toast({
        title: 'Sync Failed',
        description: 'Failed to sync indexing status.',
        variant: 'destructive',
      });
    } finally {
      setSyncLoading(false);
    }
  };

  const handleStartEnrichment = async () => {
    setEnrichmentLoading(true);
    try {
      toast({
        title: 'Starting Enrichment',
        description: 'Starting semantic enrichment process...',
      });

      const result = await documentsApi.startEnrichment();
      
      if (result.success) {
        toast({
          title: 'Enrichment Started',
          description: 'Semantic enrichment process started in background.',
        });
      } else {
        toast({
          title: 'Enrichment Failed',
          description: 'Failed to start enrichment process.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Enrichment error:', error);
      toast({
        title: 'Enrichment Failed',
        description: 'Failed to start enrichment process.',
        variant: 'destructive',
      });
    } finally {
      setEnrichmentLoading(false);
    }
  };

  const toggleStatusDisplay = () => {
    setShowStatus(!showStatus);
    if (!showStatus && !ingestionStatus) {
      fetchIngestionStatus();
    }
  };

  const handleKnowledgeGraphClick = () => {
    setKnowledgeGraphOpen(true);
  };

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedDocuments = await documentsApi.list();
      setDocuments(fetchedDocuments);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadDocuments();
      // Check if user is admin based on is_admin flag
      setIsAdmin(user.is_admin === true);
    }
  }, [user]);

  const fetchPendingFeedbacks = async () => {
    try {
      const evaluations = await adminApi.getPendingEvaluations();
      // Map backend evaluation rows to UI FeedbackItem shape
      const mapped: FeedbackItem[] = (evaluations || []).map((e: any) => ({
        id: e.id,
        question_text: e.question || '',
        response_text: e.response || '',
        comment: e.comment || '',
        user_rating: e.feedback === 'negative' ? 0 : 1,
        created_at: e.created_at,
        conversation_id: e.conversation_id,
        sources: Array.isArray(e.sources)
          ? e.sources.map((s: any) => ({ content: s?.content || '', score: s?.score ?? 0 }))
          : [],
        analysis: undefined,
      }));
      setFeedbacks(mapped);
      if (mapped.length > 0 && !selectedFeedback) {
        setSelectedFeedback(mapped[0]);
      }
    } catch (error) {
      console.error('Erreur:', error);
      toast({
        title: 'Erreur',
        description: 'Impossible de charger les feedbacks',
        variant: 'destructive'
      });
    }
  };

  const handleApproveFeedback = async () => {
    if (!selectedFeedback) return;
    
    setProcessingFeedback(true);
    try {
      await adminApi.approve(selectedFeedback.id);
      
      toast({
        title: 'Correction approuvée',
        description: 'Les modifications seront appliquées au graphe de connaissances'
      });
      
      const newFeedbacks = feedbacks.filter(f => f.id !== selectedFeedback.id);
      setFeedbacks(newFeedbacks);
      setSelectedFeedback(newFeedbacks[0] || null);
      setAdminComment('');
      
    } catch (error) {
      console.error('Erreur:', error);
      toast({
        title: 'Erreur',
        description: 'Erreur lors de l\'approbation',
        variant: 'destructive'
      });
    } finally {
      setProcessingFeedback(false);
    }
  };

  const handleRejectFeedback = async () => {
    if (!selectedFeedback) return;
    
    setProcessingFeedback(true);
    try {
      await adminApi.reject(selectedFeedback.id, adminComment);
      
      toast({
        title: 'Correction rejetée',
        description: 'Aucune modification ne sera appliquée'
      });
      
      const newFeedbacks = feedbacks.filter(f => f.id !== selectedFeedback.id);
      setFeedbacks(newFeedbacks);
      setSelectedFeedback(newFeedbacks[0] || null);
      setAdminComment('');
      
    } catch (error) {
      console.error('Erreur:', error);
      toast({
        title: 'Erreur',
        description: 'Erreur lors du rejet',
        variant: 'destructive'
      });
    } finally {
      setProcessingFeedback(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <header className="mb-6">
          <div className="flex items-center gap-3">
            <FileText className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-headline font-bold">Document Management</h1>
          </div>
          <p className="text-muted-foreground mt-1">
            Upload, manage, and process your documents to build your knowledge base.
          </p>
        </header>
        <div className="flex items-center justify-center py-8">
          <p>Loading documents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full">
        <header className="mb-6">
          <div className="flex items-center gap-3">
            <FileText className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-headline font-bold">Document Management</h1>
          </div>
          <p className="text-muted-foreground mt-1">
            Upload, manage, and process your documents to build your knowledge base.
          </p>
        </header>
        <div className="flex items-center justify-center py-8">
          <p className="text-red-500">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-6">
      <header className="mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-primary" />
              <h1 className="text-3xl font-headline font-bold">Document Management</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Upload, manage, and process your documents to build your knowledge base.
            </p>
          </div>
        </div>
      </header>
      
      <Tabs defaultValue="documents" className="flex-1">
        <div className="flex justify-between items-center mb-4">
          <TabsList>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="tribunal" onClick={() => feedbacks.length === 0 && fetchPendingFeedbacks()}>
                <Shield className="mr-2 h-4 w-4" />
                Le Tribunal
                {feedbacks.length > 0 && (
                  <Badge className="ml-2" variant="destructive">{feedbacks.length}</Badge>
                )}
              </TabsTrigger>
            )}
          </TabsList>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleKnowledgeGraphClick}>
              <BrainCircuit className="mr-2 h-4 w-4" />
              Knowledge Graph
            </Button>
            <Button 
              onClick={handleStartEmbedding}
              disabled={ingestionStatus?.is_processing}
            >
              {ingestionStatus?.is_processing ? 'Processing...' : 'Lancer l\'indexation'}
            </Button>
            <Button 
              variant="outline"
              onClick={handleStartEnrichment}
              disabled={enrichmentLoading || ingestionStatus?.is_processing}
            >
              <Sparkles className={`mr-2 h-4 w-4 ${enrichmentLoading ? 'animate-pulse' : ''}`} />
              {enrichmentLoading ? 'Enriching...' : 'Enrichissement'}
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={toggleStatusDisplay}
              className="self-start"
            >
              <Activity className="mr-2 h-4 w-4" />
              Status
              {showStatus ? <ChevronUp className="ml-2 h-4 w-4" /> : <ChevronDown className="ml-2 h-4 w-4" />}
            </Button>
          </div>
        </div>
        
        <TabsContent value="documents" className="flex-1">
          {/* Status Display */}
          {showStatus && (
            <Card className="mb-6">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Ingestion Status</h3>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleSyncIndexingStatus}
                      disabled={syncLoading || statusLoading}
                    >
                      <RefreshCw className={`mr-2 h-4 w-4 ${syncLoading ? 'animate-spin' : ''}`} />
                      {syncLoading ? 'Syncing...' : 'Sync Status'}
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={fetchIngestionStatus}
                      disabled={statusLoading || syncLoading}
                    >
                      {statusLoading ? 'Loading...' : 'Refresh'}
                    </Button>
                  </div>
                </div>
                
                {ingestionStatus && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Document Status */}
                    <div>
                      <h4 className="text-sm font-medium mb-2 text-muted-foreground">Document Status</h4>
                      <div className="space-y-1">
                        {Object.entries(ingestionStatus.document_status).map(([status, count]) => (
                          <div key={status} className="flex justify-between items-center">
                            <Badge variant={
                              status === 'complete' ? 'default' : 
                              status === 'embedding' ? 'secondary' : 
                              status === 'failed' ? 'destructive' : 'outline'
                            }>
                              {status}
                            </Badge>
                            <span className="text-sm">{count as React.ReactNode}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Indexing Status */}
                    <div>
                      <h4 className="text-sm font-medium mb-2 text-muted-foreground">Indexing Status</h4>
                      <div className="space-y-1">
                        {Object.entries(ingestionStatus.indexing_status).map(([status, count]) => (
                          <div key={status} className="flex justify-between items-center">
                            <Badge variant={
                              status === 'indexed' ? 'default' : 
                              status === 'indexing' ? 'secondary' : 
                              status === 'failed' ? 'destructive' : 'outline'
                            }>
                              {status}
                            </Badge>
                            <span className="text-sm">{count as React.ReactNode}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Processing Status */}
                    <div>
                      <h4 className="text-sm font-medium mb-2 text-muted-foreground">Processing Info</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Total Documents</span>
                          <span className="font-medium">{ingestionStatus.total_documents}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Is Processing</span>
                          <Badge variant={ingestionStatus.is_processing ? 'secondary' : 'outline'}>
                            {ingestionStatus.is_processing ? 'Yes' : 'No'}
                          </Badge>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Last updated: {new Date(ingestionStatus.last_updated).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {!ingestionStatus && !statusLoading && (
                  <p className="text-muted-foreground">Click refresh to load status information</p>
                )}
              </CardContent>
            </Card>
          )}
          
          <DocumentManagement 
            initialDocuments={documents} 
            onDocumentsChange={setDocuments}
          />
        </TabsContent>
        
        {/* Le Tribunal Tab */}
        {isAdmin && (
          <TabsContent value="tribunal" className="flex-1">
            <div className="flex h-full -m-6">
              {/* Panneau Gauche - La File d'Attente */}
              <div className="w-1/3 border-r border-border bg-background">
                <div className="p-4 border-b border-border">
                  <h2 className="text-lg font-semibold">File d'Attente</h2>
                  <p className="text-sm text-muted-foreground mt-1">
                    {feedbacks.length} feedback{feedbacks.length > 1 ? 's' : ''} en attente
                  </p>
                </div>
                
                <ScrollArea className="h-[calc(100vh-200px)]">
                  {feedbacks.length === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">
                      <CheckCircle2 className="h-12 w-12 mx-auto mb-4 text-green-500" />
                      <p>Aucun feedback en attente</p>
                      <p className="text-sm mt-2">Tous les feedbacks ont été traités</p>
                    </div>
                  ) : (
                    <div className="p-2">
                      {feedbacks.map((feedback) => {
                        const isSelected = selectedFeedback?.id === feedback.id;
                        const severity = feedback.analysis?.severity || 'medium';
                        const SeverityIcon = severityConfig[severity].icon;
                        
                        return (
                          <Card
                            key={feedback.id}
                            className={`mb-2 cursor-pointer transition-all ${
                              isSelected ? 'ring-2 ring-primary' : 'hover:bg-accent'
                            }`}
                            onClick={() => setSelectedFeedback(feedback)}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between mb-2">
                                <Badge 
                                  variant="outline" 
                                  className={severityConfig[severity].color}
                                >
                                  <SeverityIcon className="h-3 w-3 mr-1" />
                                  {severity}
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  {format(new Date(feedback.created_at), 'dd MMM HH:mm', { locale: fr })}
                                </span>
                              </div>
                              <p className="text-sm font-medium line-clamp-2">
                                {feedback.question_text}
                              </p>
                              <div className="flex items-center mt-2 text-xs text-muted-foreground">
                                <Clock className="h-3 w-3 mr-1" />
                                ID: {feedback.id.slice(0, 8)}...
                              </div>
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  )}
                </ScrollArea>
              </div>

              {/* Panneau Droit - La Salle d'Audience */}
              <div className="flex-1 overflow-auto p-6">
                {selectedFeedback ? (
                  <div className="space-y-6">
                    {/* Bloc 1: LE DOSSIER - L'Incident */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <AlertCircle className="h-5 w-5 mr-2" />
                          L'INCIDENT
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                            Question de l'utilisateur
                          </h4>
                          <p className="text-sm bg-muted p-3 rounded">
                            {selectedFeedback.question_text}
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                            Réponse de l'IA (erronée)
                          </h4>
                          <p className="text-sm bg-muted p-3 rounded">
                            {selectedFeedback.response_text}
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                            Commentaire du Notaire
                          </h4>
                          <p className="text-sm bg-destructive/10 text-[#7B1E1E] p-3 rounded">
                            {selectedFeedback.comment}
                          </p>
                        </div>

                        {selectedFeedback.sources && selectedFeedback.sources.length > 0 && (
                          <div>
                            <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                              Sources utilisées
                            </h4>
                            <div className="space-y-2">
                              {selectedFeedback.sources.map((source, idx) => (
                                <div key={idx} className="text-xs bg-muted p-2 rounded">
                                  <span className="font-mono">Score: {source.score.toFixed(3)}</span>
                                  <p className="mt-1 line-clamp-2">{source.content}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Bloc 2: L'ANALYSE - L'Autopsie de l'IA */}
                    {selectedFeedback.analysis && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center">
                            <Shield className="h-5 w-5 mr-2" />
                            L'AUTOPSIE DE L'IA
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                                Type d'erreur détecté
                              </h4>
                              <Badge variant="secondary">
                                {errorTypeLabels[selectedFeedback.analysis.error_type] || selectedFeedback.analysis.error_type}
                              </Badge>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                                Confiance de l'analyse
                              </h4>
                              <div className="flex items-center">
                                <div className="flex-1 bg-muted rounded-full h-2 mr-2">
                                  <div 
                                    className="bg-primary rounded-full h-2"
                                    style={{ width: `${selectedFeedback.analysis.confidence * 100}%` }}
                                  />
                                </div>
                                <span className="text-sm font-medium">
                                  {(selectedFeedback.analysis.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                              Entités affectées
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {selectedFeedback.analysis.affected_entities.map((entity, idx) => (
                                <Badge key={idx} variant="outline">
                                  {entity}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                              Suggestion de correction
                            </h4>
                            <p className="text-sm bg-primary/10 p-3 rounded">
                              {selectedFeedback.analysis.correction_suggestion}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Bloc 3: LA DÉCISION - Le Verdict */}
                    <Card className="border-primary">
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <ChevronRight className="h-5 w-5 mr-2" />
                          LE VERDICT
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <label className="text-sm font-medium mb-2 block">
                            Commentaire de l'administrateur (optionnel)
                          </label>
                          <Textarea
                            placeholder="Raison de la décision..."
                            value={adminComment}
                            onChange={(e) => setAdminComment(e.target.value)}
                            className="min-h-[100px]"
                          />
                        </div>
                        
                        <div className="flex gap-4">
                          <Button
                            onClick={handleApproveFeedback}
                            disabled={processingFeedback}
                            className="flex-1"
                            variant="default"
                          >
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Approuver la Correction
                          </Button>
                          
                          <Button
                            onClick={handleRejectFeedback}
                            disabled={processingFeedback}
                            className="flex-1"
                            variant="destructive"
                          >
                            <XCircle className="h-4 w-4 mr-2" />
                            Rejeter la Correction
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <div className="text-center">
                      <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-green-500" />
                      <h2 className="text-xl font-semibold">Aucun feedback sélectionné</h2>
                      <p className="text-muted-foreground mt-2">
                        Sélectionnez un feedback dans la file d'attente pour commencer
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>
        )}
      </Tabs>

      {/* Knowledge Graph Modal */}
      <KnowledgeGraphModal
        open={knowledgeGraphOpen}
        onOpenChange={setKnowledgeGraphOpen}
      />
    </div>
  );
}
