'use client'

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  error: string | null
  signOut: () => Promise<void>
  refreshSession: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize auth state
  useEffect(() => {
    let mounted = true

    const initializeAuth = async () => {
      try {
        // Get initial session
        const { data: { session: initialSession }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Error fetching session:', sessionError)
          setError(sessionError.message)
        } else if (mounted) {
          setSession(initialSession)
          setUser(initialSession?.user ?? null)
        }
      } catch (err) {
        console.error('Unexpected error during auth initialization:', err)
        setError('Failed to initialize authentication')
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    // Set up auth state change listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event: string, newSession: Session | null) => {
      console.log('Auth state changed:', event)
      
      if (mounted) {
        setSession(newSession)
        setUser(newSession?.user ?? null)
        setError(null)

        // Handle specific events
        switch (event) {
          case 'SIGNED_IN':
            console.log('User signed in')
            break
          case 'SIGNED_OUT':
            console.log('User signed out')
            break
          case 'TOKEN_REFRESHED':
            console.log('Token refreshed')
            break
          case 'USER_UPDATED':
            console.log('User updated')
            break
          default:
            break
        }
      }
    })

    initializeAuth()

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  const signOut = useCallback(async () => {
    try {
      setLoading(true)
      const { error } = await supabase.auth.signOut()
      if (error) {
        console.error('Error signing out:', error)
        setError(error.message)
      }
    } catch (err) {
      console.error('Unexpected error during sign out:', err)
      setError('Failed to sign out')
    } finally {
      setLoading(false)
    }
  }, [])

  const refreshSession = useCallback(async () => {
    try {
      setLoading(true)
      const { data: { session: refreshedSession }, error } = await supabase.auth.refreshSession()
      if (error) {
        console.error('Error refreshing session:', error)
        setError(error.message)
      } else {
        setSession(refreshedSession)
        setUser(refreshedSession?.user ?? null)
      }
    } catch (err) {
      console.error('Unexpected error during session refresh:', err)
      setError('Failed to refresh session')
    } finally {
      setLoading(false)
    }
  }, [])

  const value: AuthContextType = {
    user,
    session,
    loading,
    error,
    signOut,
    refreshSession
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}