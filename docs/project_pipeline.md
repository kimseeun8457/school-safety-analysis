# Project Pipeline

## 전체 파이프라인

```text
Raw Data
  ↓
01_preprocessing.py
  ↓
accident_clean.csv / compensation_clean.csv
  ├─ 02_eda.py → outputs/figures, outputs/tables
  ├─ 03_statistical_analysis.py → 카이제곱, Cramér's V
  └─ 04_association_rules.py → 빈발항목집합, 연관규칙

compensation_clean.csv
  ↓
05_compensation_analysis.py → Severity

Frequency + Association + Severity
  ↓
06_pps_calculation.py
  ↓
07_visualization.py → 예방관리 우선순위 및 정책 제안
```

## 실행 단계

| 순서 | 스크립트 | 목적 | 주요 산출물 |
|---:|---|---|---|
| 1 | `01_preprocessing.py` | 사고·보상 데이터 정제 | `accident_clean.csv`, `compensation_clean.csv` |
| 2 | `02_eda.py` | 사고 특성 및 교차분석 탐색 | `eda_summary.csv`, 분포도, 히트맵 |
| 3 | `03_statistical_analysis.py` | 범주형 변수 관계 검정 | 카이제곱, Cramér's V, 교차표 |
| 4 | `04_association_rules.py` | Apriori 연관규칙 분석 | 빈발항목집합, 연관규칙 |
| 5 | `05_compensation_analysis.py` | 피해 규모 분석 | Severity 요약 |
| 6 | `06_pps_calculation.py` | PPS 산출 | PPS 결과와 순위 |
| 7 | `07_visualization.py` | 최종 시각화 및 정책 제안 | PPS 차트와 정책 결과 |

## 폴더 구조

```text
data/raw/accident/        원본 사고 데이터
data/raw/compensation/    원본 보상 데이터
data/processed/           정제 데이터
outputs/figures/          EDA 및 최종 그림
outputs/tables/           EDA·통계분석 표
outputs/association_rules/ Apriori 결과
outputs/pps/              PPS 결과
```

## 사용 라이브러리

- 데이터 처리: pandas, numpy
- 시각화: matplotlib, seaborn
- 통계분석: scipy
- 연관규칙 분석: mlxtend
- 원본 Excel 읽기: openpyxl
