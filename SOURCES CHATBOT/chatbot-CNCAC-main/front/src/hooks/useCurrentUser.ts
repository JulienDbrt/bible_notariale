import { useAuth } from '@/contexts/AuthContext';
import { useEffect, useState } from 'react';
import { User } from '@/lib/types';
import { supabase } from '@/lib/supabase';

export function useCurrentUser() {
  const { user: authUser, session, loading: authLoading, signOut, error } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadUserData = async () => {
      if (!authUser) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const { data, error } = await supabase
          .from('users')
          .select('*')
          .eq('id', authUser.id)
          .single();

        if (error) {
          console.error('[useCurrentUser] Error loading user data:', error);
          if (mounted) setUser(null);
        } else if (mounted) {
          setUser(data as User);
        }
      } catch (err) {
        console.error('[useCurrentUser] Unexpected error:', err);
        if (mounted) setUser(null);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    if (!authLoading) {
      loadUserData();
    }

    return () => {
      mounted = false;
    };
  }, [authUser, authLoading]);

  return {
    user,
    loading: authLoading || loading,
    isAuthenticated: !!user && !!session,
    signOut,
    error
  };
}