export type User = {
  id: string;
  email: string;
  full_name?: string;
  created_date: string;
  last_login?: string;
  is_active: boolean;
  is_admin: boolean;
};

export type Document = {
  id: string;
  user_id?: string;
  filename: string;
  file_extension: string;
  file_path: string;
  minio_path: string;
  folder_path?: string;
  upload_date: string;
  file_size: number;
  indexing_status: 'pending' | 'indexing' | 'indexed' | 'failed';
  status: 'pending' | 'embedding' | 'complete' | 'failed';
};

export type Folder = {
  path: string;
  name: string;
  documents: Document[];
};

export type Conversation = {
  id: string;
  user_id: string;
  title: string;
  created_date: string;
};

export type Message = {
  id: string;
  content: string;
  is_user: boolean;
  timestamp: string;
  citations?: Citation[];
};

export type Citation = {
  documentId: string;
  documentPath: string;
  text: string;
};

export type EmbeddingJob = {
  id: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  created_date: string;
};
