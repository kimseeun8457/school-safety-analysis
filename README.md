# 초등학교 안전사고 연관규칙 분석 및 PPS 산출

초등학교 안전사고의 반복 발생 조합을 Apriori 연관규칙으로 분석하고, 사고 빈도·연관 강도·보상 기반 피해 규모를 결합한 Preventive Priority Score(PPS)를 산출하는 프로젝트입니다.

## 프로젝트 목표

- 초등학교 안전사고의 시간·장소·활동·사고형태 분포를 탐색합니다.
- 카이제곱 검정과 Cramér's V로 주요 범주형 변수의 연관성을 확인합니다.
- Apriori로 함께 발생하는 위험상황 조합과 연관규칙을 식별합니다.
- 사고 빈도, 연관 강도, 피해 규모를 결합해 예방관리 우선순위를 제안합니다.

## 데이터 활용 원칙

- 분석 대상은 초등학교 안전사고 데이터입니다.
- 사고 데이터와 보상 데이터는 행 단위로 결합하지 않습니다.
- 보상 데이터는 사고 유형별 피해 규모(Severity)를 산출하는 독립 자료로 사용합니다.

## 폴더 구조

```text
.
├── data/
│   ├── raw/
│   │   ├── accident/
│   │   └── compensation/
│   ├── interim/
│   └── processed/
├── scripts/
│   ├── 01_preprocessing.py
│   ├── 02_eda.py
│   ├── 03_statistical_analysis.py
│   ├── 04_association_rules.py
│   ├── 05_compensation_analysis.py
│   ├── 06_pps_calculation.py
│   └── 07_visualization.py
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── association_rules/
│   └── pps/
├── docs/
├── config/
├── README.md
└── requirements.txt
```

## 실행 환경

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## 실행 순서

1. `python scripts/01_preprocessing.py` — 사고·보상 원본 데이터를 정제합니다.
2. `python scripts/02_eda.py` — 사고 분포와 교차분석 결과를 생성합니다.
3. `python scripts/03_statistical_analysis.py` — 카이제곱 검정과 Cramér's V를 산출합니다.
4. `python scripts/04_association_rules.py` — Apriori 기반 빈발항목집합과 연관규칙을 생성합니다.
5. `python scripts/05_compensation_analysis.py` — 보상 데이터의 피해 규모를 분석합니다.
6. `python scripts/06_pps_calculation.py` — Frequency·Association·Severity를 결합해 PPS를 산출합니다.
7. `python scripts/07_visualization.py` — 결과를 시각화하고 예방관리 우선순위를 제시합니다.

## 분석 파이프라인

```text
사고 원본 데이터 → 전처리 → EDA → 통계분석 → Apriori 연관규칙 분석
                                                    ↓
보상 원본 데이터 → 전처리 → 보상 분석 → Severity ─┤
                                                    ↓
Frequency + Association + Severity → PPS → 시각화 및 정책 제안
```

## Apriori 분석

각 사고는 다음 항목으로 구성된 거래(transaction)로 변환합니다.

- 사고장소
- 원본 사고시간
- 사고형태
- 사고당시활동
- 학년

빈발항목집합의 support와 연관규칙의 confidence·lift를 이용해 반복적으로 함께 나타나는 위험상황을 식별합니다. 기본 임계값은 최소 support 1%, confidence 30%, lift 1.0이며 `config/config.yaml`에서 관리합니다.

## Preventive Priority Score (PPS)

PPS는 다음 세 요소를 0~1 범위로 정규화한 가중합입니다.

- **Frequency**: 위험상황의 사고 발생 빈도
- **Association**: 연관규칙의 confidence와 lift로 측정한 결합 강도
- **Severity**: 보상 데이터로 산출한 피해 규모

기본 가중치는 Frequency 0.40, Association 0.30, Severity 0.30입니다.

## 참고 문서

- [분석 계획](docs/analysis_plan.md)
- [프로젝트 파이프라인](docs/project_pipeline.md)
- [데이터 계보](docs/data_lineage.md)
- [연관규칙 분석 전략](docs/modeling_strategy.md)
