'use client';

import {
  BotMessageSquare,
  FileText,
  Plus,
  MessageSquare,
  LogOut,
  Trash2,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  useSidebar,
  SidebarGroup,
  SidebarGroupLabel,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { conversationsApi } from '@/lib/api';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { Conversation } from '@/lib/types';
import { ScrollArea } from './ui/scroll-area';
import { useState, useEffect, useCallback } from 'react';

export default function AppSidebar() {
  const pathname = usePathname();
  const { state } = useSidebar();
  const { user, loading, signOut } = useCurrentUser();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [deletingConversationId, setDeletingConversationId] = useState<string | null>(null);

  const isActive = (path: string) => {
    return pathname === path || pathname.startsWith(`${path}/`);
  };

  const loadConversations = useCallback(async () => {
    if (!user) return;
    try {
      const conversationsData = await conversationsApi.list();
      setConversations(conversationsData);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  }, [user]);

  useEffect(() => {
    if (!loading) {
      loadConversations();
    }
  }, [user, loading, loadConversations]);

  // Rafraîchir quand l'utilisateur revient sur l'onglet (focus)
  useEffect(() => {
    const onFocus = () => {
      // eslint-disable-next-line no-console
      console.debug('[AppSidebar] window focus -> refresh conversations');
      loadConversations();
    };
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [loadConversations]);

  // Rafraîchir sur événement personnalisé après création/suppression/modif
  useEffect(() => {
    const onChanged = () => {
      // eslint-disable-next-line no-console
      console.debug('[AppSidebar] conversations:changed -> refresh conversations');
      loadConversations();
    };
    window.addEventListener('conversations:changed', onChanged as EventListener);
    return () => window.removeEventListener('conversations:changed', onChanged as EventListener);
  }, [loadConversations]);

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('[DEBUG] Delete conversation clicked:', conversationId);
    
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette conversation ? Cette action est irréversible.')) {
      console.log('[DEBUG] User cancelled deletion');
      return;
    }

    setDeletingConversationId(conversationId);
    console.log('[DEBUG] Starting deletion for:', conversationId);
    
    try {
      console.log('[DEBUG] Calling conversationsApi.delete');
      const result = await conversationsApi.delete(conversationId);
      console.log('[DEBUG] Delete API response:', result);
      
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      
      // If we're currently viewing the deleted conversation, redirect to main chat
      if (pathname.includes(conversationId)) {
        window.location.href = '/chat';
      }
      
      // Trigger conversation list refresh event
      window.dispatchEvent(new CustomEvent('conversations:changed'));
      
      console.log('[DEBUG] Conversation deleted successfully');
    } catch (error) {
      console.error('[DEBUG] Failed to delete conversation:', error);
      alert('Erreur lors de la suppression de la conversation. Veuillez réessayer.');
    } finally {
      setDeletingConversationId(null);
    }
  };

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="h-10 w-10 text-primary hover:bg-primary/10">
            <BotMessageSquare size={28} />
          </Button>
          {state === 'expanded' && <h1 className="text-xl font-headline font-semibold">MarIAnne</h1>}
        </div>
      </SidebarHeader>

      <SidebarContent className="p-4 pt-0">
        <div className="flex flex-col h-full">
          <Button asChild>
            <Link href="/chat" className="flex items-center gap-2">
              <Plus size={18} />
              {state === 'expanded' && 'New Chat'}
            </Link>
          </Button>

          <SidebarMenu className="mt-8">
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={isActive('/chat')}>
                <Link href="/chat">
                  <MessageSquare />
                  {state === 'expanded' && <span>Chat</span>}
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={isActive('/documents')}>
                <Link href="/documents">
                  <FileText />
                  {state === 'expanded' && <span>Documents</span>}
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>

          <div className="flex-grow mt-8">
            <SidebarGroup>
              <SidebarGroupLabel>Recent</SidebarGroupLabel>
              <ScrollArea className="h-full">
                <SidebarMenu>
                  {conversations.map((convo) => (
                    <SidebarMenuItem key={convo.id}>
                      <div className="relative group">
                        <SidebarMenuButton
                          asChild
                          isActive={pathname.includes(convo.id)}
                          size="sm"
                          className="truncate pr-8"
                        >
                          <Link href={`/chat/${convo.id}`} title={convo.title}>
                            {state === 'expanded' && <span className="truncate">{convo.title}</span>}
                          </Link>
                        </SidebarMenuButton>
                        {state === 'expanded' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 bg-red-100 text-red-600 hover:bg-red-200"
                            onClick={(e) => {
                              console.log('🔥 DELETE BUTTON CLICKED!', convo.id);
                              alert('Delete button clicked for: ' + convo.title);
                              handleDeleteConversation(convo.id, e);
                            }}
                            disabled={deletingConversationId === convo.id}
                            title="Supprimer la conversation"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </ScrollArea>
            </SidebarGroup>
          </div>
        </div>
      </SidebarContent>

      <SidebarFooter className="p-4">
        <div className="flex items-center gap-2">
          <Avatar className="h-9 w-9">
            <AvatarImage src="https://placehold.co/100x100" alt="User Avatar" />
            <AvatarFallback>{user?.full_name?.charAt(0) || 'U'}</AvatarFallback>
          </Avatar>
          {state === 'expanded' && (
            <div className="flex flex-col flex-1">
              <span className="text-sm font-semibold">{user?.full_name || 'User'}</span>
              <span className="text-xs text-muted-foreground">{user?.email || 'user@email.com'}</span>
            </div>
          )}
          {state === 'expanded' && (
            <Button
              variant="outline"
              size="sm"
              onClick={signOut}
              className="h-8 w-8 p-0"
              title="Se déconnecter"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          )}
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
