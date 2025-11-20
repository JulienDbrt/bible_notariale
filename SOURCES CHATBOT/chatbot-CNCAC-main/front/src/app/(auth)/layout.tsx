import { BotMessageSquare } from 'lucide-react';

// Force dynamic rendering for all auth pages to avoid prerender errors
export const dynamic = 'force-dynamic'
export const revalidate = 0

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-primary/10 rounded-xl">
              <BotMessageSquare className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h1 className="text-2xl font-headline font-bold text-foreground">
            MarIAnne
          </h1>
          <p className="text-muted-foreground mt-2">
            Assistant IA pour l'analyse de documents
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
