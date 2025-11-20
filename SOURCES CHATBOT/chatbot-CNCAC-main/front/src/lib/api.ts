import { Conversation, Message, Document, User, Citation } from './types';
import { supabase } from './supabase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  console.log('[API DEBUG] Starting fetchApi call:', { endpoint, method: options.method || 'GET' });
  
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('[API DEBUG] Full URL:', url);
  
  const makeRequest = async (retryCount = 0): Promise<T> => {
    try {
      // Get auth token from Supabase
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError) {
        console.error('[API DEBUG] Session error:', sessionError);
        throw new Error(`Session error: ${sessionError.message}`);
      }
      
      const token = session?.access_token;
      console.log('[API DEBUG] Token exists:', !!token);
      
      const requestConfig = {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      };
      
      console.log('[API DEBUG] Making fetch request with config:', requestConfig);
      
      const response = await fetch(url, requestConfig);
      console.log('[API DEBUG] Response received:', { status: response.status, ok: response.ok });
      
      // If token is expired (401) and we haven't retried yet, try to refresh
      if (response.status === 401 && retryCount === 0) {
        console.log('[API DEBUG] Token expired, attempting to refresh...');
        
        const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
        
        if (refreshError) {
          console.error('[API DEBUG] Token refresh failed:', refreshError);
          // Redirect to login (correct app route)
          window.location.href = '/login';
          throw new Error('Authentication required');
        }
        
        if (refreshData.session) {
          console.log('[API DEBUG] Token refreshed successfully, retrying request...');
          return makeRequest(1); // Retry with new token
        }
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('[API DEBUG] Response not ok:', { status: response.status, errorText });
        
        // If still unauthorized after retry, redirect to login
        if (response.status === 401) {
          window.location.href = '/login';
          throw new Error('Authentication required');
        }
        
        throw new ApiError(response.status, errorText || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('[API DEBUG] Response parsed successfully:', result);
      return result;
    } catch (error) {
      console.error('[API DEBUG] fetchApi error:', error);
      throw error;
    }
  };

  return makeRequest();
}

// Conversations API
export const conversationsApi = {
  async list(): Promise<Conversation[]> {
    return fetchApi<Conversation[]>('/api/conversations');
  },

  async get(id: string): Promise<Conversation> {
    return fetchApi<Conversation>(`/api/conversations/${id}`);
  },

  async create(data: { title: string; user_id: string }): Promise<Conversation> {
    return fetchApi<Conversation>('/api/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async delete(id: string): Promise<{ success: boolean; message: string }> {
    console.log('[DEBUG] conversationsApi.delete called with id:', id);
    const result = await fetchApi<{ success: boolean; message: string }>(`/api/conversations/${id}`, {
      method: 'DELETE',
    });
    console.log('[DEBUG] conversationsApi.delete result:', result);
    return result;
  },

  async getMessages(conversationId: string): Promise<Message[]> {
    return fetchApi<Message[]>(`/api/conversations/${conversationId}/messages`);
  },
};

// Documents API
export const documentsApi = {
  async list(): Promise<Document[]> {
    return fetchApi<Document[]>('/api/documents/');
  },

  async get(id: string): Promise<Document> {
    return fetchApi<Document>(`/api/documents/${id}`);
  },

  async upload(file: File, userId: string, folderPath: string = '/'): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('folder_path', folderPath);

    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || `Upload failed: ${response.status}`);
    }

    return response.json();
  },

  async delete(id: string): Promise<{ success: boolean; message: string }> {
    return fetchApi(`/api/documents/${id}`, {
      method: 'DELETE',
    });
  },

  async move(documentId: string, folderPath: string): Promise<{ message: string; folder_path: string }> {
    return fetchApi(`/api/documents/${documentId}/move?folder_path=${encodeURIComponent(folderPath)}`, {
      method: 'PATCH',
    });
  },

  async listFolders(): Promise<string[]> {
    const res = await fetchApi<any>('/api/documents/folders/list');
    // Backend returns { folders: string[] }. Support both shapes for robustness.
    if (Array.isArray(res)) return res as string[];
    if (res && Array.isArray(res.folders)) return res.folders as string[];
    return ['/'];
  },

  async startEmbedding(): Promise<{ success: boolean; message: string; documents_found: number; status: string }> {
    return fetchApi('/api/documents/start_ingestion', {
      method: 'POST',
    });
  },

  async getIngestionStatus(): Promise<{
    total_documents: number;
    document_status: Record<string, number>;
    indexing_status: Record<string, number>;
    ingestion_tracking: Record<string, number>;
    is_processing: boolean;
    last_updated: string;
  }> {
    return fetchApi('/api/documents/ingestion/status', {
      method: 'GET',
    });
  },

  async getEmbeddingStatus(): Promise<{ 
    total_documents: number;
    status_counts: { pending: number; embedding: number; complete: number; failed: number };
    is_processing: boolean;
  }> {
    return fetchApi('/api/documents/embedding/status');
  },

  async getKnowledgeGraph(): Promise<{
    nodes: Array<{ id: string; label: string; type: string; size: number; color: string; degree: number }>;
    edges: Array<{ id: string; source: string; target: string; type: string; weight: number }>;
    total_nodes: number;
    total_edges: number;
    statistics?: {
      nodes: number;
      chunks: number;
      documents: number;
      relations: number;
    };
    last_updated: string;
  }> {
    return fetchApi('/api/documents/graph/knowledge');
  },

  async syncIndexingStatus(): Promise<{
    success: boolean;
    message: string;
    updated_count: number;
    total_neo4j_indexed: number;
    sync_timestamp: string;
  }> {
    return fetchApi('/api/documents/sync-indexing-status', {
      method: 'POST',
    });
  },

  async startEnrichment(): Promise<{
    success: boolean;
    message: string;
    status: string;
  }> {
    return fetchApi('/api/documents/start-enrichment', {
      method: 'POST',
    });
  },
};

// Chat API  
export const chatApi = {
  async sendMessage(data: {
    message: string;
    conversation_id?: string;
  }): Promise<{
    response: string;
    conversation_id: string;
    message_id: string;
    citations: Citation[];
  }> {
    return fetchApi('/api/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// Embedding API
export const embeddingApi = {
  async getJobs(): Promise<Array<{
    id: string;
    document_id: string;
    status: string;
    created_at: string;
  }>> {
    return fetchApi('/api/embedding/jobs');
  },

  async startJob(documentId: string): Promise<{
    id: string;
    document_id: string;
    status: string;
  }> {
    return fetchApi('/api/embedding/start', {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId }),
    });
  },
};

// Auth API (using backend endpoints for additional functionality)
export const authApi = {
  async signUp(email: string, password: string, fullName?: string) {
    return fetchApi('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });
  },

  async signIn(email: string, password: string) {
    return fetchApi('/api/auth/signin', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
      }),
    });
  },

  async getCurrentUser(): Promise<User> {
    return fetchApi('/api/auth/me');
  },

  async signOut() {
    return fetchApi('/api/auth/signout', {
      method: 'POST',
    });
  },

  async forgotPassword(email: string) {
    return fetchApi('/api/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },
};

// Evaluations API
export const evaluationsApi = {
  async create(evaluation: {
    conversation_id: string;
    message_id: string;
    evaluation_type: 'positive' | 'negative';
    comment?: string | null;
  }) {
    return fetchApi<{
      id: string;
      conversation_id: string;
      message_id: string;
      evaluation_type: 'positive' | 'negative';
      comment?: string | null;
    }>('/api/evaluations/', {
      method: 'POST',
      body: JSON.stringify(evaluation),
    });
  },

  async update(evaluationId: string, evaluation: {
    evaluation_type: 'positive' | 'negative';
    comment?: string | null;
  }) {
    return fetchApi<{
      id: string;
      conversation_id: string;
      message_id: string;
      evaluation_type: 'positive' | 'negative';
      comment?: string | null;
    }>(`/api/evaluations/${evaluationId}`, {
      method: 'PUT',
      body: JSON.stringify(evaluation),
    });
  },

  async getForMessage(messageId: string) {
    return fetchApi<{
      id: string;
      conversation_id: string;
      message_id: string;
      evaluation_type: 'positive' | 'negative';
      comment?: string | null;
    } | null>(`/api/evaluations/message/${messageId}`);
  },

  async getForConversation(conversationId: string) {
    return fetchApi<Array<{
      id: string;
      conversation_id: string;
      message_id: string;
      evaluation_type: 'positive' | 'negative';
      comment?: string | null;
    }>>(`/api/evaluations/conversation/${conversationId}`);
  },

  async delete(evaluationId: string) {
    return fetchApi(`/api/evaluations/${evaluationId}`, {
      method: 'DELETE',
    });
  },

  async getStats() {
    return fetchApi('/api/evaluations/stats/summary');
  },
};

// Admin API
export const adminApi = {
  async getPendingEvaluations(): Promise<any[]> {
    const res = await fetchApi<any>(`/api/admin/evaluations/pending`);
    // Backend returns { evaluations: [...] }
    if (Array.isArray(res)) return res as any[];
    if (res && Array.isArray(res.evaluations)) return res.evaluations as any[];
    return [];
  },

  async approve(evaluationId: string): Promise<{ status: string; message: string }> {
    return fetchApi(`/api/admin/evaluations/${evaluationId}/approve`, {
      method: 'POST',
    });
  },

  async reject(evaluationId: string, reason?: string): Promise<{ status: string; message: string }> {
    const qp = reason ? `?rejection_reason=${encodeURIComponent(reason)}` : '';
    return fetchApi(`/api/admin/evaluations/${evaluationId}/reject${qp}`, {
      method: 'POST',
    });
  },
};
