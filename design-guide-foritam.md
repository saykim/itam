# IT 자산 관리 시스템(ITAM) 디자인 가이드

> **버전**: 1.0
> **최종 수정**: 2026-02-15
> **목적**: IT 자산 관리 시스템의 일관된 사용자 경험과 상용 수준의 디자인 품질 보장

---

## 목차

1. [디자인 원칙](#디자인-원칙)
2. [디자인 시스템](#디자인-시스템)
3. [컴포넌트 가이드](#컴포넌트-가이드)
4. [Web Interface Guidelines 준수](#web-interface-guidelines-준수)
5. [접근성 요구사항](#접근성-요구사항)
6. [반응형 디자인](#반응형-디자인)
7. [구현 체크리스트](#구현-체크리스트)

---

## 디자인 원칙

### 1. 최소 변경, 최대 효과
- 기존 구조와 레이아웃을 최대한 유지하면서 시각적 품질 향상
- 사용자가 학습 곡선 없이 바로 사용할 수 있는 개선
- "큰 변화"보다 "배치, 디테일, 구성" 개선에 집중

### 2. 상용 수준의 품질
- 인터랙티브한 호버 효과와 트랜지션
- 섬세한 그림자와 테두리로 깊이감 표현
- 타이포그래피와 간격의 정교한 조정

### 3. 접근성 우선
- 스크린 리더 지원
- 키보드 네비게이션
- 모션 감소 옵션 제공

### 4. Web Interface Guidelines 준수
- Vercel의 Web Interface Guidelines 기준 적용
- 현대적인 웹 표준과 모범 사례 준수

---

## 디자인 시스템

### 색상 팔레트

#### 그레이 스케일
```css
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-400: #9CA3AF;
--gray-500: #6B7280;
--gray-600: #4B5563;
--gray-700: #374151;
--gray-800: #1F2937;
--gray-900: #111827;
```

#### 상태별 색상
```css
/* 성공/정상 - 초록 */
--success: #10B981;
--success-bg: #D1FAE5;
--success-text: #065F46;

/* 경고 - 주황 */
--warning: #F59E0B;
--warning-bg: #FEF3C7;
--warning-text: #92400E;

/* 위험/오류 - 빨강 */
--danger: #EF4444;
--danger-bg: #FEE2E2;
--danger-text: #991B1B;

/* 정보 - 파랑 */
--info: #3B82F6;
--info-bg: #DBEAFE;
--info-text: #1E40AF;
```

#### 사용 예시
```css
/* 사용중 자산 */
.card-value.success { color: var(--success); }

/* 수리중, 라이선스 만료 임박 */
.card-value.warning { color: var(--warning); }

/* 폐기예정, 라이선스 만료 */
.card-value.danger { color: var(--danger); }
```

### 타이포그래피

#### 폰트 스택
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif;
```

#### 폰트 크기 스케일
```css
/* 카드 타이틀 */
--text-xs: 0.8125rem;  /* 13px */

/* 본문 */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */

/* 강조 */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */

/* 대형 숫자 (카드 값) */
--text-2xl: 1.5rem;    /* 24px - Mobile */
--text-3xl: 1.875rem;  /* 30px - Tablet */
--text-4xl: 2.25rem;   /* 36px - Desktop */
```

#### 폰트 두께
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### 핵심 원칙: Tabular Nums
**모든 숫자 표시에는 `font-variant-numeric: tabular-nums` 필수 적용**

```css
.card-value {
    font-variant-numeric: tabular-nums;  /* 숫자 폭 일정하게 유지 */
}
```

**이유**:
- 숫자가 업데이트될 때 레이아웃 이동 방지
- 정렬된 느낌으로 전문성 향상
- Web Interface Guidelines 핵심 규칙

### 간격(Spacing)

#### 간격 스케일
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
```

#### 카드 간격
```css
/* 카드 간 간격 */
.cards {
    gap: 16px;  /* var(--space-4) */
}

/* 카드 내부 패딩 */
.card {
    padding: 20px;  /* var(--space-5) */
}

/* 카드 타이틀과 값 사이 */
.card-title {
    margin-bottom: 12px;  /* var(--space-3) */
}
```

### 그림자(Shadows)

#### 그림자 레벨
```css
/* 레벨 1: 기본 카드 */
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08),
             0 1px 2px rgba(0, 0, 0, 0.05);

/* 레벨 2: 호버 카드 */
--shadow-md: 0 10px 20px rgba(0, 0, 0, 0.12),
             0 4px 8px rgba(0, 0, 0, 0.08);

/* 레벨 3: 모달/드롭다운 */
--shadow-lg: 0 20px 25px rgba(0, 0, 0, 0.15),
             0 10px 10px rgba(0, 0, 0, 0.04);
```

#### 이중 그림자 원칙
**항상 이중 그림자를 사용하여 깊이감과 섬세함 표현**

```css
.card {
    /* ❌ 잘못된 예 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    /* ✅ 올바른 예 */
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08),
                0 1px 2px rgba(0, 0, 0, 0.05);
}
```

### 모서리(Border Radius)

```css
--radius-sm: 8px;   /* 작은 요소 */
--radius-md: 12px;  /* 카드 (기본) */
--radius-lg: 16px;  /* 큰 패널 */
--radius-xl: 24px;  /* 모달 */
```

### 트랜지션(Transitions)

#### Easing 함수
```css
/* 기본 - 대부분의 인터랙션 */
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);

/* 가속 - 요소가 사라질 때 */
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* 감속 - 요소가 나타날 때 */
--ease-out: cubic-bezier(0, 0, 0.2, 1);
```

#### 지속 시간
```css
--duration-fast: 150ms;    /* 버튼 클릭 등 */
--duration-base: 200ms;    /* 대부분의 호버 */
--duration-slow: 250ms;    /* 카드 호버 */
--duration-slower: 300ms;  /* 페이지 전환 */
```

#### 카드 트랜지션 예시
```css
.card {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 컴포넌트 가이드

### 대시보드 카드

#### 구조
```html
<div class="card" role="article" aria-labelledby="card-id">
    <div class="card-title" id="card-id">
        <span aria-hidden="true">🎯</span> 카드 제목
    </div>
    <div class="card-value" aria-label="123개">1,234</div>
</div>
```

#### 카드 컨테이너 CSS
```css
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}
```

**핵심 설정 설명**:
- `minmax(240px, 1fr)`: 카드 최소 너비 240px, 여유 공간은 균등 분배
- `auto-fit`: 화면 너비에 맞춰 자동으로 열 개수 조정
- `gap: 16px`: 카드 간 일정한 간격 유지

#### 카드 기본 스타일
```css
.card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08),
                0 1px 2px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--gray-200);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
```

**각 속성의 역할**:
- `border-radius: 12px`: 부드러운 모서리로 현대적인 느낌
- 이중 `box-shadow`: 깊이감과 섬세함
- `border`: 카드 경계 명확화
- `transition`: 부드러운 호버 효과

#### 카드 호버 효과
```css
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12),
                0 4px 8px rgba(0, 0, 0, 0.08);
    border-color: var(--gray-300);
}
```

**효과 설명**:
- `translateY(-2px)`: 카드가 살짝 위로 올라오는 느낌
- 강화된 그림자: 더 깊은 입체감
- 테두리 색상 변화: 미묘한 강조

#### 접근성: 모션 감소 지원
```css
@media (prefers-reduced-motion: reduce) {
    .card {
        transition: box-shadow 0.2s ease;
    }
    .card:hover {
        transform: none;  /* 움직임 제거 */
    }
}
```

**중요**: 전정 기능 장애가 있는 사용자를 위해 **반드시 포함**해야 함

#### 카드 타이틀
```css
.card-title {
    font-size: 0.8125rem;  /* 13px */
    color: var(--gray-600);
    margin-bottom: 12px;
    font-weight: 500;
    letter-spacing: 0.01em;
    text-wrap: balance;  /* 멀티라인 시 균형 배치 */
    line-height: 1.3;
    display: flex;
    align-items: center;
    gap: 6px;
}
```

**핵심 포인트**:
- 작은 폰트(13px): 값(36px)과의 명확한 계층 구조
- `text-wrap: balance`: 줄바꿈 시 시각적 균형
- `flex` 레이아웃: 아이콘과 텍스트 정렬

#### 카드 값 (숫자)
```css
.card-value {
    font-size: 2.25rem;  /* 36px */
    font-weight: 700;
    color: var(--gray-800);
    line-height: 1.1;
    font-variant-numeric: tabular-nums;  /* 🔥 핵심 */
    letter-spacing: -0.02em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

**필수 설정**:
- `font-variant-numeric: tabular-nums`: 숫자 정렬 (Web Interface Guidelines)
- `overflow` 처리: 큰 숫자도 안전하게 표시
- 큰 폰트와 굵은 두께: 가독성과 강조

#### 상태별 색상
```css
.card-value.success { color: var(--success); }   /* 사용중 */
.card-value.warning { color: var(--warning); }   /* 수리중, 만료 임박 */
.card-value.danger { color: var(--danger); }     /* 폐기예정, 만료 */
```

#### 아이콘 가이드

**IT 자산 관리 시스템 표준 아이콘**:
```html
📦 총 자산
✅ 사용중
💤 여유
🔧 수리중
⚠️ 폐기예정
🗑️ 폐기완료
⏰ 라이선스 만료 임박
❌ 라이선스 만료
```

**사용 예시**:
```html
<div class="card-title" id="card-total">
    <span aria-hidden="true">📦</span> 총 자산
</div>
```

**주의사항**:
- 아이콘에 **반드시** `aria-hidden="true"` 추가 (장식용, 스크린 리더 제외)
- 아이콘만으로 의미 전달 금지 (텍스트와 함께 사용)

### 반응형 디자인

#### 데스크톱 (기본)
```css
.cards {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
}

.card-value {
    font-size: 2.25rem;  /* 36px */
}
```

#### 태블릿 (768px 이하)
```css
@media (max-width: 768px) {
    .cards {
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
    }

    .card-value {
        font-size: 1.875rem;  /* 30px */
    }
}
```

#### 모바일 (480px 이하)
```css
@media (max-width: 480px) {
    .cards {
        grid-template-columns: repeat(2, 1fr);  /* 2열 고정 */
        gap: 10px;
    }

    .card {
        padding: 16px;
    }

    .card-value {
        font-size: 1.5rem;  /* 24px */
    }
}
```

**반응형 전략**:
1. **240px → 160px → 2열 고정**: 단계적 축소
2. **폰트 크기 조정**: 36px → 30px → 24px
3. **간격 축소**: 16px → 12px → 10px
4. **패딩 최적화**: 카드 내부 여백 조정

---

## Web Interface Guidelines 준수

### 핵심 규칙 체크리스트

#### ✅ 1. 애니메이션
- **규칙**: `transform`과 `opacity`만 애니메이션, `prefers-reduced-motion` 지원
- **적용**:
  ```css
  .card:hover {
      transform: translateY(-2px);  /* ✅ transform 사용 */
  }

  @media (prefers-reduced-motion: reduce) {
      .card:hover {
          transform: none;  /* ✅ 모션 감소 지원 */
      }
  }
  ```

#### ✅ 2. 타이포그래피
- **규칙**: 숫자에 `font-variant-numeric: tabular-nums`, 텍스트에 `text-wrap: balance`
- **적용**:
  ```css
  .card-value {
      font-variant-numeric: tabular-nums;  /* ✅ 숫자 정렬 */
  }

  .card-title {
      text-wrap: balance;  /* ✅ 균형 잡힌 줄바꿈 */
  }
  ```

#### ✅ 3. 호버 상태
- **규칙**: 인터랙티브 요소에 명확한 호버 상태 제공
- **적용**:
  ```css
  .card:hover {
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12),
                  0 4px 8px rgba(0, 0, 0, 0.08);
  }
  ```

#### ✅ 4. 접근성
- **규칙**: `role`, `aria-label`, `aria-labelledby` 사용
- **적용**:
  ```html
  <div class="card" role="article" aria-labelledby="card-total">
      <div class="card-title" id="card-total">총 자산</div>
      <div class="card-value" aria-label="1234개">1,234</div>
  </div>
  ```

#### ✅ 5. 로케일
- **규칙**: `Intl.NumberFormat` 사용하여 숫자/통화 포맷팅
- **적용**:
  ```javascript
  function formatNumber(num) {
      return new Intl.NumberFormat('ko-KR').format(num);
  }
  ```

#### ✅ 6. 콘텐츠 오버플로우
- **규칙**: 긴 콘텐츠에 `text-overflow: ellipsis` 처리
- **적용**:
  ```css
  .card-value {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
  }
  ```

---

## 접근성 요구사항

### ARIA 속성

#### 카드 컴포넌트
```html
<div class="card" role="article" aria-labelledby="card-id">
    <div class="card-title" id="card-id">카드 제목</div>
    <div class="card-value" aria-label="숫자 + 단위">포맷된 숫자</div>
</div>
```

**ARIA 속성 설명**:
- `role="article"`: 카드를 독립적인 콘텐츠 단위로 표시
- `aria-labelledby`: 카드 타이틀과 연결
- `aria-label`: 스크린 리더에 원본 숫자 + 단위 제공 (예: "1234개")

#### 장식 요소
```html
<span aria-hidden="true">📦</span>
```

**규칙**: 장식용 아이콘/이미지는 **반드시** `aria-hidden="true"` 설정

### 키보드 네비게이션

카드가 클릭 가능한 경우:
```html
<div class="card" role="article" tabindex="0"
     onclick="..." onkeypress="...">
    ...
</div>
```

```css
.card:focus {
    outline: 2px solid var(--info);
    outline-offset: 2px;
}
```

### 색상 대비

**WCAG AA 기준 준수** (최소 4.5:1 대비):
- 텍스트: `var(--gray-800)` on white → 대비율 ~12:1 ✅
- 상태 색상: success/warning/danger 모두 충분한 대비 제공

---

## JavaScript 가이드

### 숫자 포맷팅

#### formatNumber() 함수
```javascript
/**
 * 숫자를 한국 로케일 형식으로 포맷팅
 * @param {number|null|undefined} num - 포맷팅할 숫자
 * @returns {string} 쉼표로 구분된 숫자 문자열
 * @example
 * formatNumber(1234) // "1,234"
 * formatNumber(null) // "0"
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return new Intl.NumberFormat('ko-KR').format(num);
}
```

**핵심 포인트**:
- `Intl.NumberFormat`: Web Interface Guidelines 권장 방식
- `'ko-KR'`: 한국어 로케일 (쉼표 구분)
- null/undefined 안전 처리

#### 대시보드 카드 생성 예시
```javascript
function loadDashboard() {
    fetch('/api/dashboard')
        .then(r => r.json())
        .then(data => {
            document.getElementById('summary-cards').innerHTML = `
                <div class="card" role="article" aria-labelledby="card-total">
                    <div class="card-title" id="card-total">
                        <span aria-hidden="true">📦</span> 총 자산
                    </div>
                    <div class="card-value" aria-label="${data.total}개">
                        ${formatNumber(data.total)}
                    </div>
                </div>
                <!-- 나머지 카드들... -->
            `;
        })
        .catch(err => {
            console.error('대시보드 로딩 실패:', err);
            // 에러 UI 표시
        });
}
```

**주의사항**:
1. `aria-label`에는 원본 숫자 사용 (`${data.total}개`)
2. 표시되는 값에는 포맷팅된 숫자 사용 (`${formatNumber(data.total)}`)
3. 에러 처리 필수

### 폴백 처리 (선택사항)

구형 브라우저 지원이 필요한 경우:
```javascript
function formatNumber(num) {
    if (num === null || num === undefined) return '0';

    // Intl API 미지원 브라우저용 폴백
    if (typeof Intl === 'undefined') {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    return new Intl.NumberFormat('ko-KR').format(num);
}
```

---

## 구현 체크리스트

### CSS 구현

#### 카드 컨테이너
- [ ] `display: grid` 사용
- [ ] `grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))`
- [ ] `gap: 16px`
- [ ] `margin-bottom: 32px`

#### 카드 기본 스타일
- [ ] `border-radius: 12px`
- [ ] `padding: 20px`
- [ ] 이중 그림자 (`box-shadow` 2개 값)
- [ ] `border: 1px solid var(--gray-200)`
- [ ] `transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1)`

#### 카드 호버 효과
- [ ] `transform: translateY(-2px)`
- [ ] 강화된 이중 그림자
- [ ] `border-color: var(--gray-300)`
- [ ] `@media (prefers-reduced-motion: reduce)` 지원

#### 카드 타이틀
- [ ] `font-size: 0.8125rem` (13px)
- [ ] `color: var(--gray-600)`
- [ ] `font-weight: 500`
- [ ] `text-wrap: balance`
- [ ] `display: flex; gap: 6px` (아이콘용)

#### 카드 값
- [ ] `font-size: 2.25rem` (36px)
- [ ] `font-weight: 700`
- [ ] `font-variant-numeric: tabular-nums` ⭐ **필수**
- [ ] `overflow: hidden; text-overflow: ellipsis`
- [ ] 반응형 폰트 크기 (768px, 480px 브레이크포인트)

#### 반응형
- [ ] 768px 이하: `minmax(160px, 1fr)`, 폰트 30px
- [ ] 480px 이하: `repeat(2, 1fr)`, 폰트 24px
- [ ] 간격 조정 (16px → 12px → 10px)

### HTML 구현

#### 카드 구조
- [ ] `<div class="card" role="article">`
- [ ] `aria-labelledby` 속성 추가
- [ ] 타이틀에 고유 `id` 부여
- [ ] 아이콘에 `aria-hidden="true"`
- [ ] 값에 `aria-label` 추가 (단위 포함)

#### 아이콘
- [ ] 각 카드 유형별 적절한 이모지 선택
- [ ] 아이콘을 `<span aria-hidden="true">` 안에 배치
- [ ] 카드 타이틀과 함께 표시

### JavaScript 구현

#### formatNumber() 함수
- [ ] `Intl.NumberFormat('ko-KR')` 사용
- [ ] null/undefined 처리
- [ ] (선택) 폴백 로직 추가

#### 카드 생성
- [ ] API 데이터에 `formatNumber()` 적용
- [ ] `aria-label`에 원본 숫자 + 단위
- [ ] 표시값에 포맷팅된 숫자
- [ ] 에러 처리

### 테스트

#### 시각적 테스트
- [ ] 호버 효과 작동 (살짝 위로 + 그림자)
- [ ] 숫자에 쉼표 구분 표시
- [ ] 아이콘이 타이틀 왼쪽에 표시
- [ ] 상태별 색상 정확히 적용

#### 반응형 테스트
- [ ] 1920px: 4열 이상
- [ ] 768px: 2-3열
- [ ] 375px: 2열 고정
- [ ] 폰트 크기 적절히 조정

#### 접근성 테스트
- [ ] 스크린 리더로 카드 내용 읽기
- [ ] 키보드 Tab 키로 네비게이션 (카드 클릭 가능한 경우)
- [ ] "움직임 줄이기" 설정 시 transform 제거 확인

#### 브라우저 테스트
- [ ] Chrome/Edge
- [ ] Safari
- [ ] Firefox
- [ ] 모바일 Safari/Chrome

---

## 추가 리소스

### Web Interface Guidelines
- **공식 문서**: https://github.com/vercel-labs/web-interface-guidelines
- **핵심 원칙**: 애니메이션, 타이포그래피, 접근성, 로케일

### 접근성
- **WCAG 2.1 AA 기준**: https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA 사용 가이드**: https://www.w3.org/WAI/ARIA/apg/

### MDN 참고 문서
- `Intl.NumberFormat`: https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat
- `font-variant-numeric`: https://developer.mozilla.org/ko/docs/Web/CSS/font-variant-numeric
- `prefers-reduced-motion`: https://developer.mozilla.org/ko/docs/Web/CSS/@media/prefers-reduced-motion

---

## 버전 히스토리

### v1.0 (2026-02-15)
- 초기 디자인 가이드 작성
- 대시보드 카드 컴포넌트 가이드
- Web Interface Guidelines 준수 사항
- 접근성 및 반응형 디자인 규칙

---

## 기여 및 피드백

이 가이드는 IT 자산 관리 시스템의 디자인 일관성을 유지하기 위한 **살아있는 문서**입니다.

**개선 제안이 있다면**:
1. 실제 사용 사례를 기반으로 제안
2. Web Interface Guidelines 원칙과의 정합성 확인
3. 접근성 요구사항 준수 여부 검토

**이 가이드를 사용하는 개발자/AI에게**:
- 단순히 복사-붙여넣기가 아닌, **원칙을 이해하고 적용**하세요
- 새로운 컴포넌트를 추가할 때는 **이 가이드를 확장**하세요
- 디자인 시스템의 **일관성을 최우선**으로 고려하세요

---

**© 2026 IT Asset Management System Design Team**
