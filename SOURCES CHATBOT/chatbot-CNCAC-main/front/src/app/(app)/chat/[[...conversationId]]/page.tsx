'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowRight, Bot, User, LoaderCircle } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { type Message, type Conversation } from '@/lib/types';
import { conversationsApi, chatApi } from '@/lib/api';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { useToast } from '@/hooks/use-toast';
import { CitationBadges } from '@/components/citation-badges';
import EvaluationComponent from '@/components/evaluation-component';

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const { user, loading: userLoading } = useCurrentUser();
  const conversationId = Array.isArray(params.conversationId) ? params.conversationId[0] : undefined;

  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<React.ElementRef<typeof ScrollArea>>(null);

  useEffect(() => {
    const loadConversation = async () => {
      if (conversationId && user) {
        try {
          const [conversationData, messagesData] = await Promise.all([
            conversationsApi.get(conversationId),
            conversationsApi.getMessages(conversationId)
          ]);
          setConversation(conversationData);
          setMessages(messagesData);
        } catch (error) {
          console.error('Failed to load conversation:', error);
          toast({
            variant: "destructive",
            title: "Error",
            description: "Failed to load conversation.",
          });
          router.push('/chat');
        }
      } else {
        setConversation(null);
        setMessages([]);
      }
    };

    if (!userLoading) {
      loadConversation();
    }
  }, [conversationId, user, userLoading, toast, router]);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !user) return;

    const userInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // Call the real chat API
      const requestData: { message: string; conversation_id?: string } = {
        message: userInput,
      };

      // Only include conversation_id if it exists
      if (conversationId) {
        requestData.conversation_id = conversationId;
      }

      const response = await chatApi.sendMessage(requestData);

      // Create the AI message object with citations (unused variable removed)

      // If it's a new conversation, redirect to it
      if (!conversationId && response.conversation_id) {
        // notifier la sidebar qu'une nouvelle conversation a été créée après le premier message
        try {
          window.dispatchEvent(new CustomEvent('conversations:changed'));
        } catch {}
        router.push(`/chat/${response.conversation_id}`);
      } else {
        // For existing conversations, add the new message with citations
        const updatedMessages = await conversationsApi.getMessages(conversationId || response.conversation_id);
        // Update the last message (AI response) with citations
        const messagesWithCitations = updatedMessages.map((msg, index) => {
          if (index === updatedMessages.length - 1 && !msg.is_user) {
            return { ...msg, citations: response.citations };
          }
          return msg;
        });
        setMessages(messagesWithCitations);
        // notifier la sidebar qu'une conversation existante a été mise à jour (ordre "Recent")
        try {
          window.dispatchEvent(new CustomEvent('conversations:changed'));
        } catch {}
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to send message. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-card rounded-xl shadow-sm">
      <header className="p-4 border-b">
        <h2 className="text-xl font-headline font-semibold">
          {conversation ? conversation.title : 'New Chat'}
        </h2>
      </header>

      <ScrollArea className="flex-grow p-4" ref={scrollAreaRef}>
        <div className="space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex flex-col gap-2',
                message.is_user && 'items-end'
              )}
            >
              <div className={cn(
                'flex items-start gap-4',
                message.is_user && 'justify-end'
              )}>
              {!message.is_user && (
                <Avatar className="h-9 w-9 border">
                  <AvatarFallback><Bot /></AvatarFallback>
                </Avatar>
              )}
              <div className={cn(
                  'max-w-xl rounded-lg p-3 relative',
                  message.is_user
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                )}>
                <pre className="font-body text-sm whitespace-pre-wrap">{message.content}</pre>

                {/* Citations - Displayed prominently below the message */}
                {!message.is_user && message.citations && message.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <CitationBadges citations={message.citations} />
                  </div>
                )}

                {/* Timestamp */}
                <div className="flex items-center justify-end mt-2">
                  <p className="text-xs opacity-70">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              {message.is_user && (
                <Avatar className="h-9 w-9 border">
                   <AvatarFallback><User /></AvatarFallback>
                </Avatar>
              )}
              </div>
              {/* Evaluation component below the message for better layout */}
              {!message.is_user && conversation && (
                <div className="ml-13 -mt-1">
                  <EvaluationComponent
                    messageId={message.id}
                    conversationId={conversation.id}
                    compact={true}
                  />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
             <div className="flex items-start gap-4">
                <Avatar className="h-9 w-9 border">
                  <AvatarFallback><Bot /></AvatarFallback>
                </Avatar>
                <div className="max-w-xl rounded-lg p-3 bg-muted flex items-center">
                    <LoaderCircle className="animate-spin h-5 w-5" />
                </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <footer className="p-4 border-t">
        <form onSubmit={handleSendMessage} className="flex items-center gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about your documents..."
            className="flex-grow"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <LoaderCircle className="animate-spin" />
            ) : (
              <ArrowRight />
            )}
            <span className="sr-only">Send</span>
          </Button>
        </form>
      </footer>
    </div>
  );
}
