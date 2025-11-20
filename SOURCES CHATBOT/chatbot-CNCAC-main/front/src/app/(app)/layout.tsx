import AppSidebar from '@/components/app-sidebar';
import { AuthGuard } from '@/components/auth-guard';
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  // eslint-disable-next-line no-console
  console.debug('[AppLayout] rendering (app) layout');
  return (
    <AuthGuard>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>{children}</SidebarInset>
      </SidebarProvider>
    </AuthGuard>
  );
}
