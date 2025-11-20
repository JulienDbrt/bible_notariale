# **App Name**: ChatDocAI

## Core Features:

- Chat Interface: Real-time chat interface with message history, markdown support, and formatted AI responses.
- Document Management: Display of uploaded documents with name, size, date, and embedding status; drag & drop file upload; download/delete actions; knowledge graph link; and embedding process initiation.
- Document Upload: Upload documents to Docker volume via the /upload endpoint.
- Document Listing: List documents via the /documents endpoint.
- Document Deletion: Delete documents via the /documents/{id} endpoint.
- Document Download: Download documents via the /documents/{id}/download endpoint.
- AI Conversation Title: Automatically set the title of a newly created conversation using AI summarization tool.

## Style Guidelines:

- Primary color: Soft blue (#A0C4FF) to create a calm and trustworthy atmosphere for document interaction.
- Background color: Light gray (#F0F4F8), nearly the same hue as the primary, but highly desaturated for a clean interface.
- Accent color: Lavender (#BDB2FF), a slightly different but analogous hue, bright and saturated, to highlight key interactive elements.
- Font pairing: 'Space Grotesk' (sans-serif) for headlines and short amounts of text, and 'Inter' (sans-serif) for body text to maintain a techy yet readable aesthetic.
- Code font: 'Source Code Pro' for displaying code snippets.
- Use clean, line-based icons to represent document actions and conversation options.
- Maintain a clear and structured layout with a sidebar for navigation and a main content area for the chat interface and document management.
