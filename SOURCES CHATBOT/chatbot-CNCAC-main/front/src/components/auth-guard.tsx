'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { Loader2 } from 'lucide-react';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { user, loading } = useCurrentUser();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Logs de diagnostic temporaires
    // eslint-disable-next-line no-console
    console.debug('[AuthGuard] pathname=%s loading=%s user=%s', pathname, loading, !!user);

    if (!loading && !user) {
      // eslint-disable-next-line no-console
      console.debug('[AuthGuard] redirecting to /login');
      router.push('/login');
    }
  }, [user, loading, router, pathname]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    // Fallback explicite pendant la redirection
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Redirection vers la page de connexion…</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
