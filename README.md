# 초등학교 안전사고 데이터 기반 위험요인 분석 및 PPS 산출

연관규칙 분석 기반 초등학교 안전사고 위험상황 도출 및 PPS 기반 예방 우선순위 제안

## 프로젝트 목표

- 초등학교 안전사고가 언제, 어디서, 어떤 활동 중 발생하는지 분석합니다.
- 사고 발생과 관련된 위험요인을 머신러닝으로 분류하고 해석합니다.
- 사고 빈도, 모델 기반 위험도, 보상 기반 피해 규모를 함께 고려한 Preventive Priority Score(PPS)를 산출합니다.
- 학교 현장에서 우선적으로 관리할 위험상황을 제안합니다.

## 분석 대상과 데이터 활용 원칙

- 분석 대상은 2023~2025년 초등학교 안전사고 데이터입니다.
- 사고 데이터는 전처리, EDA, 통계분석, 피처 엔지니어링 및 모델링에 사용합니다.
- 보상 데이터는 사고 데이터와 행 단위로 결합하지 않습니다. 두 데이터에는 동일 사고를 식별할 수 있는 공통 키가 없으므로, 보상 데이터는 사고 유형별 피해 규모(Severity)를 산출하는 독립 자료로 사용합니다.

## 폴더 구조

```text
.
├── data/
│   ├── raw/
│   │   ├── accident/       # 원본 사고 데이터
│   │   └── compensation/   # 원본 보상 데이터
│   ├── interim/            # 단계 간 임시 데이터
│   └── processed/          # 정제 데이터
├── notebooks/              # 탐색 및 검증용 노트북
├── scripts/                # 실행 순서가 명시된 분석 스크립트
├── outputs/
│   ├── figures/            # 시각화 결과
│   ├── tables/             # 분석 결과 표
│   ├── models/             # 학습 모델
│   ├── shap/               # SHAP 분석 결과
│   └── pps/                # PPS 및 민감도 분석 결과
├── docs/                   # 분석 설계 및 데이터 계보 문서
├── README.md
├── requirements.txt
└── .gitignore
```

원본 데이터와 실행 산출물은 Git에 커밋하지 않습니다.

## 실행 환경

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

원본 사고 CSV는 `data/raw/accident/`, 보상 CSV는 `data/raw/compensation/`에 저장합니다.

## 실행 순서

아래 스크립트는 번호 순서대로 실행합니다. 각 스크립트는 하나의 분석 역할만 수행합니다.

1. `python scripts/01_preprocessing.py` — 사고·보상 원본 데이터를 정제하여 `data/processed/accident_clean.csv`, `data/processed/compensation_clean.csv`를 생성합니다.
2. `python scripts/02_eda.py` — 사고 분포와 교차분석 결과를 `outputs/figures/`, `outputs/tables/`에 저장합니다.

본 스크립트는 (EDA)에서 생성된 탐색 결과와 교차표를 바탕으로 변수 간 통계적 유의성을 검정한다.

3. `python scripts/03_statistical_analysis.py` — 카이제곱 검정과 Cramer's V 결과를 생성합니다.
4. `python scripts/04_feature_engineering.py` — 모델 학습용 `model_dataset.csv`를 생성합니다.
5. `python scripts/05_model_training.py` — Decision Tree, Random Forest, XGBoost 모델을 학습합니다.
6. `python scripts/06_model_evaluation.py` — 모델 성능과 혼동행렬, ROC 곡선, 중요도를 평가합니다.
7. `python scripts/07_shap_analysis.py` — SHAP 기반 전역·국소 위험요인 해석을 수행합니다.
8. `python scripts/08_compensation_analysis.py` — 보상 데이터로 Severity Score를 산출합니다.
9. `python scripts/09_pps_calculation.py` — Frequency, Risk, Severity를 결합해 PPS 순위를 생성합니다.
10. `python scripts/10_sensitivity_analysis.py` — PPS 가중치 조합별 순위 안정성을 분석합니다.
11. `python scripts/11_visualization.py` — 최종 분석 결과를 시각화합니다.

## 분석 파이프라인

```text
사고 원본 데이터 → 전처리 → EDA / 통계분석 → 피처 엔지니어링
→ 모델 학습 → 모델 평가 → SHAP 위험요인 해석

보상 원본 데이터 → 전처리 → 보상 분석 → Severity Score

Frequency Score + Risk Score + Severity Score
→ PPS 산출 → 민감도 분석 → 예방관리 우선순위 제안
```

## 위험상황과 모델링

개별 사고를 예측하는 대신, 다음 조합을 하나의 위험상황(Risk Context)으로 정의합니다.

- 장소
- 사고형태
- 사고당시활동
- 시간대
- 학년

위험상황별 사고 빈도를 기준으로 위험수준을 High, Medium, Low로 구분합니다. 모델 입력 변수는 지역, 학년, 성별, 요일, 시간대, 장소, 사고형태, 활동, 월, 계절입니다.

## Preventive Priority Score (PPS)

PPS는 학교가 우선적으로 관리할 위험상황을 정량화하는 지표입니다. 각 위험상황에 대해 다음 요소를 0~1 범위로 정규화하고 가중합합니다.

- **Frequency**: 위험상황별 사고 발생 빈도
- **Risk**: XGBoost가 예측한 위험수준 또는 예측 확률
- **Severity**: 보상 데이터로 산출한 피해 규모

기본 PPS 예시는 `0.4 × Frequency + 0.3 × Risk + 0.3 × Severity`이며, 민감도 분석에서 여러 가중치 조합을 비교해 결과의 안정성을 평가합니다.

## 주요 산출물

- 정제 데이터: `data/processed/accident_clean.csv`, `data/processed/compensation_clean.csv`
- 분석 표와 시각화: `outputs/tables/`, `outputs/figures/`
- 모델: `outputs/models/`
- SHAP 결과: `outputs/shap/`
- PPS 결과와 민감도 분석: `outputs/pps/`

## 참고 문서

- [분석 계획](docs/analysis_plan.md)
- [프로젝트 파이프라인](docs/project_pipeline.md)
- [데이터 계보](docs/data_lineage.md)
- [모델링 전략](docs/modeling_strategy.md)
