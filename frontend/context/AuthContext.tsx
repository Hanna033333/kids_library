'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
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
    const supabase = createClient()

    useEffect(() => {
        const setData = async () => {
            const { data: { session }, error } = await supabase.auth.getSession()
            if (error) throw error
            setSession(session)
            setUser(session?.user ?? null)
            setIsLoading(false)
        }

        setData()

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
            setUser(session?.user ?? null)
            setIsLoading(false)
        })

        return () => {
            subscription.unsubscribe()
        }
    }, [supabase.auth])

    const signOut = async () => {
        await supabase.auth.signOut()
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
