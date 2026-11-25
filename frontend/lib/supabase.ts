import { createClient as createSupabaseClient, SupabaseClient } from '@supabase/supabase-js'

let browserClient: SupabaseClient | null = null

export const createClient = (): SupabaseClient => {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

    // 서버 사이드(SSR/SSG)에서는 세션 스토리지나 토큰 자동 갱신 타이머를 사용하지 않음
    if (typeof window === 'undefined') {
        return createSupabaseClient(supabaseUrl, supabaseAnonKey, {
            auth: {
                autoRefreshToken: false,
                persistSession: false,
                detectSessionInUrl: false,
            }
        })
    }

    // 브라우저에서는 단일 GoTrueClient 인스턴스를 재사용하여 navigator.locks 토큰 갱신 교착(deadlock) 방지
    if (!browserClient) {
        browserClient = createSupabaseClient(supabaseUrl, supabaseAnonKey, {
            auth: {
                autoRefreshToken: true,
                persistSession: true,
                detectSessionInUrl: true
            }
        })
    }

    return browserClient
}

export const supabase = createClient()
