'use client'

// This page depends on runtime URL params and auth callbacks.
// Prevent Next.js from attempting to statically prerender it at build time.
export const dynamic = 'force-dynamic'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Eye, EyeOff } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { supabase } from '@/lib/supabase'

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [emailForVerify, setEmailForVerify] = useState('')
  const [needsEmailForVerify, setNeedsEmailForVerify] = useState(false)
  const [ready, setReady] = useState(false)
  const router = useRouter()
  const { toast } = useToast()
  const searchParams = useSearchParams()
  const errorDescription = useMemo(() => searchParams?.get('error_description') ?? '', [searchParams])
  const recoveryToken = useMemo(() => searchParams?.get('token') ?? '', [searchParams])
  const recoveryType = useMemo(() => searchParams?.get('type') ?? '', [searchParams])
  const recoveryEmail = useMemo(() => searchParams?.get('email') ?? '', [searchParams])

  // Helper to read auth params from both query and hash
  const readAuthParams = () => {
    const q = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '')
    const h = new URLSearchParams(typeof window !== 'undefined' ? (window.location.hash || '').replace(/^#/, '') : '')
    const first = (key: string) => q.get(key) || h.get(key) || ''
    return {
      code: first('code'),
      access_token: first('access_token'),
      refresh_token: first('refresh_token'),
      token: first('token'),
      type: first('type'),
      email: first('email'),
      error: first('error'),
      error_description: first('error_description')
    }
  }

  // Ensure the recovery session is established when arriving from the email link
  useEffect(() => {
    let mounted = true
    const init = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) {
          const params = readAuthParams()
          // 1) PKCE style
          if (params.code) {
            await supabase.auth.exchangeCodeForSession(params.code)
          }
          // 2) Token hash/session tokens style
          else if (params.access_token && params.refresh_token) {
            await supabase.auth.setSession({ access_token: params.access_token, refresh_token: params.refresh_token })
          }
          // 3) OTP style (token + type=recovery)
          else if (params.token && (params.type === 'recovery' || params.type === 'email_change')) {
            const email = (params.email || emailForVerify || '').trim().toLowerCase()
            if (email) {
              const { data: verifyData, error: verifyError } = await supabase.auth.verifyOtp({
                email,
                token: params.token,
                type: (params.type as 'recovery' | 'email_change')
              })
              if (verifyError) setError(verifyError.message)
              // Ensure session is established for updateUser
              if (verifyData?.session?.access_token && verifyData?.session?.refresh_token) {
                await supabase.auth.setSession({
                  access_token: verifyData.session.access_token,
                  refresh_token: verifyData.session.refresh_token,
                })
              }
            } else {
              setNeedsEmailForVerify(true)
            }
          }
        }
      } catch (e) {
        // non-fatal; user can still try updating and get a clear error
      } finally {
        if (mounted) setReady(true)
      }
    }
    init()
    return () => { mounted = false }
  }, [searchParams, recoveryToken, recoveryType, recoveryEmail, emailForVerify])

  const handleVerifyWithEmail = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    try {
      if (!recoveryToken) {
        setError('Lien de vérification manquant ou invalide')
        return
      }
      const { data: verifyData, error: verifyError } = await supabase.auth.verifyOtp({
        email: emailForVerify.trim().toLowerCase(),
        token: recoveryToken,
        type: 'recovery'
      })
      if (verifyError) {
        setError(verifyError.message)
      } else {
        if (verifyData?.session?.access_token && verifyData?.session?.refresh_token) {
          await supabase.auth.setSession({
            access_token: verifyData.session.access_token,
            refresh_token: verifyData.session.refresh_token,
          })
        }
        setNeedsEmailForVerify(false)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      setIsLoading(false)
      return
    }
    if (password !== confirm) {
      setError('Les mots de passe ne correspondent pas')
      setIsLoading(false)
      return
    }

    try {
      const { error: updateError } = await supabase.auth.updateUser({ password })
      if (updateError) throw updateError

      toast({
        title: 'Mot de passe mis à jour',
        description: 'Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.',
      })
      router.push('/login')
    } catch (err) {
      setError((err as Error).message || 'Impossible de mettre à jour le mot de passe')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center">Réinitialiser le mot de passe</CardTitle>
        <CardDescription className="text-center">
          Choisissez un nouveau mot de passe pour votre compte
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {errorDescription && (
            <Alert variant="destructive">
              <AlertDescription>{errorDescription}</AlertDescription>
            </Alert>
          )}
          {!ready && (
            <div className="flex items-center justify-center py-4 text-sm text-muted-foreground">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Préparation…
            </div>
          )}

          {needsEmailForVerify && (
            <div className="space-y-2">
              <Label htmlFor="verifyEmail">Confirmez votre email</Label>
              <Input
                id="verifyEmail"
                type="email"
                placeholder="votre@email.fr"
                value={emailForVerify}
                onChange={(e) => setEmailForVerify(e.target.value)}
                required
                autoComplete="email"
              />
              <Button onClick={handleVerifyWithEmail} disabled={isLoading} className="mt-2">
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Vérifier le lien
              </Button>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="password">Nouveau mot de passe</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm">Confirmer le mot de passe</Label>
            <Input
              id="confirm"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <Button type="submit" className="w-full" disabled={isLoading || !ready}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Mettre à jour le mot de passe
          </Button>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">Vous vous souvenez de votre mot de passe ? </span>
            <Link href="/login" className="text-primary hover:underline">
              Se connecter
            </Link>
          </div>
        </CardFooter>
      </form>
    </Card>
  )
}
