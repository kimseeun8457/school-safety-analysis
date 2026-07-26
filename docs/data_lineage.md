# Data Lineage

## 데이터 흐름

```text
data/raw/accident/
  ↓ 01_preprocessing.py
data/processed/accident_clean.csv
  ├─ 02_eda.py → outputs/tables/eda_summary.csv, outputs/figures/*.png
  ├─ 03_statistical_analysis.py → chi_square_result.csv, cramers_v_result.csv
  └─ 04_association_rules.py → frequent_itemsets.csv, association_rules.csv

data/raw/compensation/
  ↓ 01_preprocessing.py
data/processed/compensation_clean.csv
  ↓ 05_compensation_analysis.py
severity_summary.csv, compensation_overview.csv

Frequency + Association + Severity
  ↓ 06_pps_calculation.py
outputs/pps/pps_result.csv
  ↓ 07_visualization.py
pps_top_contexts.png, pps_component_comparison.png, policy_recommendations.csv
```

## 단계별 입출력

| 단계 | 입력 | 출력 | 용도 |
|---|---|---|---|
| 전처리 | 원본 사고·보상 데이터 | `accident_clean.csv`, `compensation_clean.csv` | 분석 가능한 초등학교 데이터 생성 |
| EDA | `accident_clean.csv` | `eda_summary.csv`, `eda_cross_table.csv`, 그림 | 분포와 위험상황 탐색 |
| 통계분석 | `accident_clean.csv` | 카이제곱, Cramér's V, 교차표 | 변수 연관성 검정 |
| 연관규칙 | `accident_clean.csv` | 빈발항목집합, 연관규칙 | 반복 조합 식별 |
| 보상분석 | `compensation_clean.csv` | `severity_summary.csv`, `compensation_overview.csv` | 피해 규모 정량화 |
| PPS | Frequency, Association, Severity | PPS 결과와 순위 | 예방 우선순위 산출 |

사고 데이터와 보상 데이터는 동일 사고를 식별할 공통 키가 없으므로 행 단위로 결합하지 않는다.
