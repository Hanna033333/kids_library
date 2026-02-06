'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useState, useEffect } from 'react'

interface Banner {
  id: string
  bgImage: string
  title: string
  highlight?: string
  subtitle: string
  link: string
  bgColor: string
  textColor: string
}

const BANNERS: Banner[] = [
  {
    id: 'winter-2026-3d',
    bgImage: '/banners/winter_3d_bg.png', // Generated 3D background
    title: '서울시 교육청 어린이 도서관',
    highlight: '겨울방학 추천도서',
    subtitle: '이것만 읽으면 신학기 준비 끝!',
    link: '/books?curation=winter-vacation',
    bgColor: '#D1F5EA', // Matches the image background
    textColor: '#1F2937'
  }
]

export default function MainBanner() {
  const [currentSlide, setCurrentSlide] = useState(0)
  const banner = BANNERS[currentSlide]

  return (
    <div className="w-full" style={{ backgroundColor: banner.bgColor }}>
      <div className="max-w-[1200px] mx-auto relative group">
        <Link href={banner.link} className="block relative w-full aspect-[2/1] sm:aspect-[3/1] md:aspect-[1200/400] overflow-hidden">
          
          {/* Background Image (Right aligned for mobile, cover for PC) */}
          <div className="absolute inset-0 w-full h-full">
            <Image
              src={banner.bgImage}
              alt={banner.highlight || "배너"}
              fill
              className="object-cover object-right sm:object-center"
              priority
            />
          </div>

          {/* Text Overlay (Left aligned) */}
          <div className="absolute inset-0 flex flex-col justify-center px-6 sm:px-12 md:px-20 max-w-[600px]">
            <span className="text-sm sm:text-base font-bold text-emerald-700 mb-1 sm:mb-2 opacity-90">
              {banner.title}
            </span>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-gray-900 leading-tight mb-2 sm:mb-4 tracking-tight drop-shadow-sm">
              <span className="block text-emerald-950">{banner.highlight}</span>
            </h2>
            <div className="inline-flex items-center gap-2">
              <p className="text-sm sm:text-lg text-emerald-800 font-medium bg-white/40 backdrop-blur-sm px-3 py-1 rounded-full">
                {banner.subtitle}
              </p>
            </div>
            
            {/* CTA Button imitation */}
            <div className="mt-4 sm:mt-6">
               <span className="inline-block bg-emerald-600 text-white text-xs sm:text-sm font-bold px-4 py-2 rounded-lg shadow-sm hover:bg-emerald-700 transition-colors">
                 보러가기
               </span>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}
