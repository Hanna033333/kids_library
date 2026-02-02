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
};

module.exports = nextConfig;
