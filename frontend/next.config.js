/** @type {import('next').NextConfig} */
const nextConfig = {
    async redirects() {
        return [
            // Redirect /collections/winter-vacation to correct URL
            {
                source: '/collections/winter-vacation',
                destination: '/books?curation=winter-vacation',
                permanent: true,
            },
            // Redirect old 13+ age category to new 'teen' slug
            {
                source: '/collections/age/13\\+',
                destination: '/collections/age/teen',
                permanent: true,
            },
        ]
    },
    async headers() {
        return [
            {
                source: '/:path*',
                headers: [
                    {
                        key: 'X-DNS-Prefetch-Control',
                        value: 'on'
                    },
                    {
                        key: 'Strict-Transport-Security',
                        value: 'max-age=63072000; includeSubDomains; preload'
                    },
                    {
                        key: 'X-Frame-Options',
                        value: 'SAMEORIGIN'
                    },
                    {
                        key: 'X-Content-Type-Options',
                        value: 'nosniff'
                    },
                    {
                        key: 'X-XSS-Protection',
                        value: '1; mode=block'
                    },
                    {
                        key: 'Referrer-Policy',
                        value: 'origin-when-cross-origin'
                    },
                    {
                        key: 'Permissions-Policy',
                        value: 'camera=(), microphone=(), geolocation=()'
                    },
                ],
            },
        ]
    },
    images: {
        // 알라딘 등 외부 이미지는 Next.js Image Optimizer 프록시 시 서버 IP 차단(Hotlink Protection) 문제로
        // unoptimized: true 설정하여 브라우저가 직접 원본 URL을 로드하도록 우회
        unoptimized: true,
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'image.aladin.co.kr',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'shopping-phinf.pstatic.net',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'bookthumb-phinf.pstatic.net',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'image.yes24.com',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'image.kyobobook.co.kr',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'contents.kyobobook.co.kr',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'images.unsplash.com',
                port: '',
                pathname: '/**',
            },
        ],
    },
};

module.exports = nextConfig;
