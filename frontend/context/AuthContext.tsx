'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { User, Session } from '@supabase/supabase-js'

const VALID_CHILD_AGES = ['0-3', '4-7', '8-12', '13+'] as const

const normalizeChildAge = (age: string | null | undefined): string | null => {
    if (!age) return null
    return (VALID_CHILD_AGES as readonly string[]).includes(age) ? age : null
}

type AuthContextType = {
    user: User | null
    session: Session | null
    isLoading: boolean
    preferredChildAge: string | null
    updatePreferredChildAge: (age: string | null) => Promise<boolean>
    signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType>({
    user: null,
    session: null,
    isLoading: true,
    preferredChildAge: null,
    updatePreferredChildAge: async () => false,
    signOut: async () => { },
})

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null)
    const [session, setSession] = useState<Session | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [preferredChildAge, setPreferredChildAge] = useState<string | null>(null)

    const syncLocalPreferredAge = (age: string | null) => {
        if (typeof window === 'undefined') return
        if (age) {
            localStorage.setItem('preferred_child_age', age)
        } else {
            localStorage.removeItem('preferred_child_age')
        }
    }

    const fetchPreferredChildAge = async (userId: string): Promise<string | null> => {
        try {
            const queryPromise = supabase
                .from('members')
                .select('preferred_child_age')
                .eq('id', userId)
                .single()

            const result = await Promise.race([
                queryPromise,
                new Promise<{ data: null; error: Error }>((resolve) =>
                    setTimeout(() => resolve({ data: null, error: new Error('timeout') }), 3000)
                ),
            ])

            if (result.error) {
                console.warn('preferred_child_age fetch skipped:', result.error.message)
                return null
            }
            const age = normalizeChildAge((result.data as { preferred_child_age?: string | null } | null)?.preferred_child_age)
            syncLocalPreferredAge(age)
            return age
        } catch (err) {
            console.warn('preferred_child_age fetch error:', err)
            return null
        }
    }

    useEffect(() => {
        const setData = async () => {
            // Check for QA Mock Token first
            const isQaMode = typeof window !== 'undefined' && localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN';
            
            if (isQaMode) {
                const mockUser = {
                    id: '00000000-0000-0000-0000-000000000000',
                    email: 'qa-tester@checkjari.com',
                    app_metadata: { provider: 'kakao' },
                    user_metadata: { provider_id: 'qa-tester-001' }
                } as any;
                setUser(mockUser);
                setSession({ user: mockUser, access_token: 'TEST_QA_TOKEN' } as any);
                const qaAge = normalizeChildAge(sessionStorage.getItem('qa_preferred_child_age'))
                setPreferredChildAge(qaAge)
                syncLocalPreferredAge(qaAge)
                setIsLoading(false);
                return;
            }

            try {
                const { data: { session }, error } = await supabase.auth.getSession()
                if (error) {
                    console.error("Session fetch error:", error);
                    setPreferredChildAge(null)
                    setIsLoading(false);
                    return;
                }
                setSession(session)
                setUser(session?.user ?? null)
                if (session?.user) {
                    const age = await fetchPreferredChildAge(session.user.id)
                    setPreferredChildAge(age)
                } else {
                    setPreferredChildAge(null)
                    syncLocalPreferredAge(null)
                }
            } catch (err) {
                console.error("Unexpected auth error:", err);
                setPreferredChildAge(null)
            } finally {
                setIsLoading(false)
            }
        }

        setData()

        // Also check periodically or on storage events for the mock token in dev
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'supabase.auth.token') {
                setData();
            }
        };
        window.addEventListener('storage', handleStorageChange);

        const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
            // If we are in QA mode, don't let Supabase override the mock user
            const isQaMode = typeof window !== 'undefined' && localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN';
            if (isQaMode) return;

            setSession(session)
            setUser(session?.user ?? null)
            if (session?.user) {
                const age = await fetchPreferredChildAge(session.user.id)
                setPreferredChildAge(age)
            } else {
                setPreferredChildAge(null)
                syncLocalPreferredAge(null)
            }
            setIsLoading(false)
        })

        return () => {
            subscription.unsubscribe()
            window.removeEventListener('storage', handleStorageChange);
        }
    }, [supabase.auth])

    const updatePreferredChildAge = async (age: string | null): Promise<boolean> => {
        const normalized = normalizeChildAge(age)
        setPreferredChildAge(normalized)
        syncLocalPreferredAge(normalized)

        const isQaMode = typeof window !== 'undefined' && (
            sessionStorage.getItem('qa_mode') === 'true' ||
            localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'
        )
        if (isQaMode) {
            if (normalized) {
                sessionStorage.setItem('qa_preferred_child_age', normalized)
            } else {
                sessionStorage.removeItem('qa_preferred_child_age')
            }
            return true
        }

        if (!user) return false

        try {
            const { error } = await supabase
                .from('members')
                .update({ preferred_child_age: normalized })
                .eq('id', user.id)
            if (error) {
                console.error('preferred_child_age update failed:', error)
                return false
            }
            return true
        } catch (err) {
            console.error('preferred_child_age update error:', err)
            return false
        }
    }

    const signOut = async () => {
        await supabase.auth.signOut()
        localStorage.removeItem('supabase.auth.token') // Clear mock token too
        localStorage.removeItem('preferred_child_age')
        sessionStorage.removeItem('qa_mode')
        sessionStorage.removeItem('qa_member_state')
        sessionStorage.removeItem('qa_saved_nickname')
        sessionStorage.removeItem('qa_preferred_child_age')
        sessionStorage.removeItem('generatedNickname')
        sessionStorage.removeItem('showSignupComplete')
        setUser(null)
        setSession(null)
        setPreferredChildAge(null)
    }

    return (
        <AuthContext.Provider value={{ user, session, isLoading, preferredChildAge, updatePreferredChildAge, signOut }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
