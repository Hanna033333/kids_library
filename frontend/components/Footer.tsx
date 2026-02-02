'use client'

import Link from "next/link";

export default function Footer() {
    return (
        <footer className="bg-gray-900 text-gray-400 py-10 px-6 mt-auto">
            <div className="max-w-6xl mx-auto text-center">
                <div className="flex flex-col items-center">
                    {/* Copyright */}
                    <p className="text-sm text-gray-500 mb-2">© 2026 책자리. All rights reserved.</p>

                    {/* Links */}
                    <div className="text-sm flex items-center justify-center gap-3 flex-wrap">
                        <Link
                            href="/intro"
                            className="hover:text-white transition-colors"
                        >
                            서비스 소개
                        </Link>

                        <span className="text-gray-700">|</span>

                        <a
                            href="https://docs.google.com/forms/d/e/1FAIpQLSdz7vpG3dj7RVHUEFWoxjdkEIyALYIry-3J-79bfowT2_82mQ/viewform?usp=publish-editor"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-white transition-colors"
                        >
                            우리 동네 도서관도 추가해주세요
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    )
}
