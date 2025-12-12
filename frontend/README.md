# Kids Library Frontend

모바일 우선의 아동 도서 검색 UI

## 시작하기

### 의존성 설치
```bash
npm install
```

### 개발 서버 실행
```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 확인하세요.

## 환경 변수

`.env.local` 파일에 다음을 설정하세요:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 기능

- 검색: 제목, 저자, 키워드로 검색
- 필터: 연령대 필터링
- 리스트: pangyo_callno가 있는 책만 표시
- 반응형: 모바일 우선, PC에서도 최적화된 레이아웃

