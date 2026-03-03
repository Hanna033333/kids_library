import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
        // 책자리 브랜드 컬러 팔레트
        brand: {
          primary: {
            DEFAULT: '#F59E0B',      // 메인 오렌지 (Amber-500)
            hover: '#F59E0B',         // 호버 상태 (변화 없음)
            active: '#B45309',        // 클릭 상태 (Amber-700)
          },
          accent: {
            DEFAULT: '#FF4D00',       // 강조 레드-오렌지
            hover: '#FF4D00',         // 호버 상태 (변화 없음)
          },
          kakao: {
            DEFAULT: '#FEE500',       // 카카오 브랜드 컬러
            hover: '#FEE500',         // 호버 상태 (변화 없음)
            active: '#FCC419',
            text: '#191919',          // 카카오 텍스트 컬러
          },
          intro: {
            DEFAULT: '#FFB300',       // 인트로 페이지 전용 (Amber-400)
            hover: '#FFB300',         // 호버 상태 (변화 없음)
          },
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};
export default config;

