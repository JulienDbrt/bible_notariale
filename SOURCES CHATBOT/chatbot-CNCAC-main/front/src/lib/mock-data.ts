import { Conversation, Message, Document } from './types';

export const mockConversations: Conversation[] = [
  { id: '1', user_id: 'user-1', title: 'First Chat about Documents', created_date: '2023-10-27T10:00:00Z' },
  { id: '2', user_id: 'user-1', title: 'Analysis of Q3 Report', created_date: '2023-10-26T14:30:00Z' },
  { id: '3', user_id: 'user-1', title: 'Brainstorming new features', created_date: '2023-10-25T09:00:00Z' },
];

export const mockMessages: { [key: string]: Message[] } = {
  '1': [
    { id: '1-1', content: 'Hello! What can you tell me about the uploaded documents?', is_user: true, timestamp: '2023-10-27T10:00:10Z' },
    { id: '1-2', content: 'Certainly! I have analyzed the documents. The quarterly report shows a 15% increase in revenue. The project proposal outlines a new initiative to expand into the European market.', is_user: false, timestamp: '2023-10-27T10:00:25Z' },
    { id: '1-3', content: '```javascript\nconsole.log("Can you show me some code?");\n```', is_user: true, timestamp: '2023-10-27T10:01:00Z' },
    { id: '1-4', content: 'Of course. Here is a Python code snippet for data analysis from the technical guide:\n\n```python\nimport pandas as pd\n\ndf = pd.read_csv("data.csv")\nprint(df.describe())\n```', is_user: false, timestamp: '2023-10-27T10:01:20Z' },
  ],
  '2': [
    { id: '2-1', content: 'Let\'s analyze the Q3 report.', is_user: true, timestamp: '2023-10-26T14:30:00Z' },
  ],
  '3': [],
};

export const mockDocuments: Document[] = [
  { 
    id: 'doc-1', 
    user_id: 'user-1',
    filename: 'quarterly_report_q3.pdf', 
    file_extension: 'pdf',
    file_path: '/docs/quarterly_report_q3.pdf',
    minio_path: 'documents/quarterly_report_q3.pdf',
    upload_date: '2023-10-27T09:00:00Z', 
    file_size: 2.5 * 1024 * 1024, 
    indexing_status: 'indexed',
    status: 'complete' 
  },
  { 
    id: 'doc-2', 
    user_id: 'user-1',
    filename: 'project_proposal_v2.docx', 
    file_extension: 'docx',
    file_path: '/docs/project_proposal_v2.docx',
    minio_path: 'documents/project_proposal_v2.docx',
    upload_date: '2023-10-26T11:45:00Z', 
    file_size: 1.2 * 1024 * 1024, 
    indexing_status: 'indexed',
    status: 'complete' 
  },
  { 
    id: 'doc-3', 
    user_id: 'user-1',
    filename: 'technical_guide.md', 
    file_extension: 'md',
    file_path: '/docs/technical_guide.md',
    minio_path: 'documents/technical_guide.md',
    upload_date: '2023-10-25T16:20:00Z', 
    file_size: 0.8 * 1024 * 1024, 
    indexing_status: 'indexing',
    status: 'embedding' 
  },
  { 
    id: 'doc-4', 
    user_id: 'user-1',
    filename: 'marketing_assets.zip', 
    file_extension: 'zip',
    file_path: '/docs/marketing_assets.zip',
    minio_path: 'documents/marketing_assets.zip',
    upload_date: '2023-10-24T10:10:00Z', 
    file_size: 15.7 * 1024 * 1024, 
    indexing_status: 'pending',
    status: 'pending' 
  },
  { 
    id: 'doc-5', 
    user_id: 'user-1',
    filename: 'competitor_analysis.xlsx', 
    file_extension: 'xlsx',
    file_path: '/docs/competitor_analysis.xlsx',
    minio_path: 'documents/competitor_analysis.xlsx',
    upload_date: '2023-10-23T13:00:00Z', 
    file_size: 3.1 * 1024 * 1024, 
    indexing_status: 'failed',
    status: 'failed' 
  },
];
