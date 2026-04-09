'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { User, Session } from '@supabase/supabase-js'

type AuthContextType = {
    user: User | null
    session: Session | null
    isLoading: boolean
    signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    session: null,
    isLoading: true,
    signOut: async () => { },
})

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null)
    const [session, setSession] = useState<Session | null>(null)
    const [isLoading, setIsLoading] = useState(true)

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
                setIsLoading(false);
                return;
            }

            try {
                const { data: { session }, error } = await supabase.auth.getSession()
                if (error) {
                    console.error("Session fetch error:", error);
                    setIsLoading(false);
                    return;
                }
                setSession(session)
                setUser(session?.user ?? null)
            } catch (err) {
                console.error("Unexpected auth error:", err);
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

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            // If we are in QA mode, don't let Supabase override the mock user
            const isQaMode = typeof window !== 'undefined' && localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN';
            if (isQaMode) return;

            setSession(session)
            setUser(session?.user ?? null)
            setIsLoading(false)
        })

        return () => {
            subscription.unsubscribe()
            window.removeEventListener('storage', handleStorageChange);
        }
    }, [supabase.auth])

    const signOut = async () => {
        await supabase.auth.signOut()
        localStorage.removeItem('supabase.auth.token') // Clear mock token too
        setUser(null)
        setSession(null)
    }

    return (
        <AuthContext.Provider value={{ user, session, isLoading, signOut }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
