'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Download, MoreVertical, Trash2, UploadCloud, Folder, FolderPlus, FileText } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { type Document } from '@/lib/types';
import { cn } from '@/lib/utils';
import { documentsApi } from '@/lib/api';
import { useCurrentUser } from '@/hooks/useCurrentUser';

interface DocumentManagementProps {
  initialDocuments: Document[];
  onDocumentsChange?: (documents: Document[]) => void;
  onStartEmbedding?: () => void;
}

export default function DocumentManagement({ initialDocuments, onDocumentsChange, onStartEmbedding }: DocumentManagementProps) {
  const [documents, setDocuments] = useState<Document[]>(initialDocuments);
  const [folders, setFolders] = useState<string[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string>('/');
  const [isDragging, setIsDragging] = useState(false);
  const [dragOverFolder, setDragOverFolder] = useState<string | null>(null);
  const [embeddingProgress] = useState(0); // Progress display - managed by parent
  const [isEmbedding] = useState(false); // Embedding state - managed by parent
  const [uploading, setUploading] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [showNewFolderInput, setShowNewFolderInput] = useState(false);
  const { toast } = useToast();
  const { user } = useCurrentUser();

  // Sync with initial documents when they change
  useEffect(() => {
    setDocuments(initialDocuments);
  }, [initialDocuments]);

  // Notify parent when documents change (but not during render)
  useEffect(() => {
    onDocumentsChange?.(documents);
  }, [documents, onDocumentsChange]);

  // Update documents function (now only updates local state)
  const updateDocuments = useCallback((newDocuments: Document[] | ((prev: Document[]) => Document[])) => {
    if (typeof newDocuments === 'function') {
      setDocuments(prev => newDocuments(prev));
    } else {
      setDocuments(newDocuments);
    }
  }, []);

  // Load folders from API
  useEffect(() => {
    const loadFolders = async () => {
      try {
        const folderList = await documentsApi.listFolders();
        setFolders(folderList);
      } catch (error) {
        console.error('Error loading folders:', error);
      }
    };
    
    if (user) {
      loadFolders();
    }
  }, [user]); // Only reload folders when user changes, not when documents change

  // Filter documents by current folder
  const currentDocuments = documents.filter(doc => 
    (doc.folder_path || '/') === currentFolder
  );

  // Get folder name from path
  const getFolderName = (path: string) => {
    if (path === '/') return 'Root';
    return path.split('/').filter(Boolean).pop() || 'Root';
  };

  // Get folder breadcrumbs
  const getBreadcrumbs = (path: string) => {
    if (path === '/') return [{ name: 'Root', path: '/' }];
    const parts = path.split('/').filter(Boolean);
    const breadcrumbs = [{ name: 'Root', path: '/' }];
    let currentPath = '';
    
    parts.forEach(part => {
      currentPath += '/' + part;
      breadcrumbs.push({ name: part, path: currentPath + '/' });
    });
    
    return breadcrumbs;
  };

  // Call parent's embedding handler when needed
  useEffect(() => {
    if (onStartEmbedding) {
      // We'll trigger this from the parent component
    }
  }, [onStartEmbedding]);

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const uploadFiles = useCallback(async (files: FileList) => {
    if (!user?.id) {
      toast({
        title: 'Error',
        description: 'You must be logged in to upload files.',
        variant: 'destructive',
      });
      return;
    }

    setUploading(true);
    const fileArray = Array.from(files);
    let successCount = 0;
    let errorCount = 0;

    for (const file of fileArray) {
      try {
        const uploadedDoc = await documentsApi.upload(file, user.id, currentFolder);
        updateDocuments(prev => [uploadedDoc, ...prev]);
        successCount++;
      } catch (error) {
        console.error('Upload error:', error);
        errorCount++;
      }
    }

    setUploading(false);

    if (successCount > 0) {
      toast({
        title: 'Upload Success',
        description: `${successCount} file(s) uploaded successfully${errorCount > 0 ? `, ${errorCount} failed` : ''}.`,
      });
    }

    if (errorCount > 0 && successCount === 0) {
      toast({
        title: 'Upload Failed',
        description: `Failed to upload ${errorCount} file(s).`,
        variant: 'destructive',
      });
    }
  }, [user?.id, toast, currentFolder, updateDocuments]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      uploadFiles(files);
    }
  }, [uploadFiles]);

  // Unused function - embedding is triggered from parent component
  // const startEmbedding = useCallback(async () => {
  //   try {
  //     setIsEmbedding(true);
  //     setEmbeddingProgress(0);
  //     
  //     const result = await documentsApi.startEmbedding();
  //     
  //     if (result.success) {
  //       toast({
  //         title: 'Embedding Started',
  //         description: `Started processing ${(result as { documents_processed?: number; documents_found?: number }).documents_processed || (result as { documents_found?: number }).documents_found || 0} documents.`,
  //       });
  //       
  //       // Simulate progress
  //       const interval = setInterval(() => {
  //         setEmbeddingProgress((prev) => {
  //           if (prev >= 100) {
  //             clearInterval(interval);
  //             setIsEmbedding(false);
  //             toast({
  //               title: 'Embedding Complete',
  //               description: 'All documents have been processed.',
  //             });
  //             // Update documents to embedding status
  //             updateDocuments(docs => docs.map(d => 
  //               d.status === 'pending' ? {...d, status: 'embedding'} : d
  //             ));
  //             return 100;
  //           }
  //           return prev + 10;
  //         });
  //       }, 500);
  //     } else {
  //       setIsEmbedding(false);
  //       toast({
  //         title: 'Embedding Failed',
  //         description: 'Failed to start embedding process.',
  //         variant: 'destructive',
  //       });
  //     }
  //   } catch (error) {
  //     console.error('Embedding error:', error);
  //     setIsEmbedding(false);
  //     toast({
  //       title: 'Embedding Failed', 
  //       description: 'Failed to start embedding process.',
  //       variant: 'destructive',
  //     });
  //   }
  // }, [toast, updateDocuments]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      uploadFiles(files);
    }
    // Reset input value to allow re-uploading the same file
    e.target.value = '';
  };

  const handleDeleteDocument = async (docId: string) => {
    try {
      await documentsApi.delete(docId);
      updateDocuments(docs => docs.filter(d => d.id !== docId));
      toast({
        title: 'Document Deleted',
        description: 'Document has been successfully deleted.',
      });
    } catch (error) {
      console.error('Delete error:', error);
      toast({
        title: 'Delete Failed',
        description: 'Failed to delete document.',
        variant: 'destructive',
      });
    }
  };

  const handleCreateFolder = () => {
    if (!newFolderName.trim()) return;
    
    const newFolderPath = currentFolder === '/' 
      ? `/${newFolderName.trim()}/` 
      : `${currentFolder}${newFolderName.trim()}/`;
    
    setFolders(prev => Array.from(new Set([...prev, newFolderPath])));
    setNewFolderName('');
    setShowNewFolderInput(false);
    
    toast({
      title: 'Folder Created',
      description: `Created folder: ${getFolderName(newFolderPath)}`,
    });
  };

  const handleMoveDocument = async (documentId: string, targetFolder: string) => {
    try {
      await documentsApi.move(documentId, targetFolder);
      updateDocuments(docs => 
        docs.map(doc => 
          doc.id === documentId 
            ? { ...doc, folder_path: targetFolder }
            : doc
        )
      );
      
      toast({
        title: 'Document Moved',
        description: `Moved to ${getFolderName(targetFolder)}`,
      });
    } catch (error) {
      console.error('Move error:', error);
      toast({
        title: 'Move Failed',
        description: 'Failed to move document.',
        variant: 'destructive',
      });
    }
  };

  const handleDocumentDragStart = (e: React.DragEvent, docId: string) => {
    e.dataTransfer.setData('text/plain', docId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleFolderDragOver = (e: React.DragEvent, folderPath: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverFolder(folderPath);
  };

  const handleFolderDragLeave = () => {
    setDragOverFolder(null);
  };

  const handleFolderDrop = async (e: React.DragEvent, targetFolder: string) => {
    e.preventDefault();
    const docId = e.dataTransfer.getData('text/plain');
    setDragOverFolder(null);
    
    if (docId) {
      await handleMoveDocument(docId, targetFolder);
    }
  };

  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const getStatusBadge = (status: Document['status']) => {
    switch (status) {
      case 'complete':
        return <Badge variant="default" className="bg-green-500 hover:bg-green-600">Complete</Badge>;
      case 'embedding':
        return <Badge variant="secondary" className="bg-blue-200 text-blue-800">Embedding</Badge>;
      case 'pending':
        return <Badge variant="outline">Pending</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={cn("border-2 border-dashed transition-colors cursor-pointer", isDragging && "border-primary bg-primary/10")}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <CardContent className="p-6">
          <div className="flex flex-col items-center justify-center text-center space-y-2">
            <UploadCloud className="h-12 w-12 text-muted-foreground" />
            <p className="font-semibold">
              {uploading ? 'Uploading files...' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-muted-foreground">
              {uploading ? `Please wait... (uploading to ${getFolderName(currentFolder)})` : `or click to browse (uploads to ${getFolderName(currentFolder)})`}
            </p>
          </div>
          <input
            id="file-input"
            type="file"
            multiple
            className="hidden"
            onChange={handleFileInputChange}
            accept=".pdf,.docx,.txt,.md,.pptx,.xlsx"
          />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Folders Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Folder className="h-5 w-5" />
                  Folders
                </CardTitle>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => setShowNewFolderInput(true)}
                >
                  <FolderPlus className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {showNewFolderInput && (
                <div className="mb-4 space-y-2">
                  <input
                    type="text"
                    placeholder="Folder name"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleCreateFolder();
                      if (e.key === 'Escape') {
                        setShowNewFolderInput(false);
                        setNewFolderName('');
                      }
                    }}
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleCreateFolder}>
                      Create
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => {
                        setShowNewFolderInput(false);
                        setNewFolderName('');
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
              
              <div className="space-y-1">
                {folders.map(folderPath => (
                  <div
                    key={folderPath}
                    className={cn(
                      "flex items-center gap-2 p-2 rounded-md cursor-pointer transition-colors hover:bg-gray-100",
                      currentFolder === folderPath && "bg-primary/10 text-primary",
                      dragOverFolder === folderPath && "bg-primary/20 border-2 border-primary border-dashed"
                    )}
                    onClick={() => setCurrentFolder(folderPath)}
                    onDragOver={(e) => handleFolderDragOver(e, folderPath)}
                    onDragLeave={handleFolderDragLeave}
                    onDrop={(e) => handleFolderDrop(e, folderPath)}
                  >
                    <Folder className="h-4 w-4 text-blue-500" />
                    <span className="text-sm truncate">{getFolderName(folderPath)}</span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {documents.filter(doc => (doc.folder_path || '/') === folderPath).length}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Documents Area */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {getBreadcrumbs(currentFolder).map((crumb, index, arr) => (
                      <React.Fragment key={crumb.path}>
                        <button
                          onClick={() => setCurrentFolder(crumb.path)}
                          className="text-sm hover:text-primary transition-colors"
                        >
                          {crumb.name}
                        </button>
                        {index < arr.length - 1 && <span className="text-muted-foreground">/</span>}
                      </React.Fragment>
                    ))}
                  </div>
                  <CardTitle>Documents in {getFolderName(currentFolder)}</CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {currentDocuments.length} document{currentDocuments.length !== 1 ? 's' : ''} in this folder
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Embedding progress display - currently managed by parent component */}
              {isEmbedding && (
                <div className="mb-4 space-y-2">
                  <p className="text-sm font-medium">Embedding progress...</p>
                  <Progress value={embeddingProgress} />
                </div>
              )}
              
              {currentDocuments.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No documents in this folder</p>
                  <p className="text-sm">Drag files here or use the upload area above</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead className="hidden sm:table-cell">Size</TableHead>
                      <TableHead className="hidden md:table-cell">Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentDocuments.map((doc) => (
                      <TableRow 
                        key={doc.id}
                        draggable
                        onDragStart={(e) => handleDocumentDragStart(e, doc.id)}
                        className="cursor-move hover:bg-gray-50"
                      >
                        <TableCell className="font-medium flex items-center gap-2">
                          <FileText className="h-4 w-4 text-blue-500" />
                          {doc.filename}
                        </TableCell>
                        <TableCell className="hidden sm:table-cell">{formatBytes(doc.file_size)}</TableCell>
                        <TableCell className="hidden md:table-cell">{new Date(doc.upload_date).toLocaleDateString()}</TableCell>
                        <TableCell>{getStatusBadge(doc.status)}</TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>
                                <Download className="mr-2 h-4 w-4" />
                                Download
                              </DropdownMenuItem>
                              <DropdownMenuItem 
                                className="text-destructive" 
                                onClick={() => handleDeleteDocument(doc.id)}
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
