# Project Pipeline

# 초등학교 안전사고 데이터 기반 위험요인 분석 및 예방관리 우선순위(PPS) 산출

---

# 프로젝트 목표

본 프로젝트는 초등학교 안전사고 데이터를 활용하여 사고 발생 특성을 분석하고, Explainable AI(XGBoost + SHAP)를 이용해 위험요인을 해석한다.

또한 보상데이터를 함께 활용하여 사고 발생 빈도와 피해 규모를 종합적으로 고려한 Preventive Priority Score(PPS)를 산출하고, 학교 안전관리 우선순위를 제안하는 것을 목표로 한다.

---

# 전체 Pipeline

```text
Raw Data
    │
    ▼
Data Preprocessing
    │
    ▼
Exploratory Data Analysis (EDA)
    │
    ▼
Statistical Analysis
(Chi-square, Cramer's V)
    │
    ▼
Feature Engineering
    │
    ▼
Machine Learning
(Baseline → Final Model)
    │
    ▼
Model Evaluation
    │
    ▼
Explainable AI (SHAP)
    │
    ▼
Compensation Analysis
    │
    ▼
PPS Calculation
    │
    ▼
Sensitivity Analysis
    │
    ▼
Visualization
    │
    ▼
Policy Recommendation
```

---

# 프로젝트 폴더 구조

```text
school-safety-risk-analysis/

│
├── data/
│   ├── raw/
│   │   ├── accident/
│   │   └── compensation/
│   │
│   ├── interim/
│   │
│   └── processed/
│
├── notebooks/
│
├── scripts/
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── models/
│   ├── shap/
│   └── pps/
│
├── docs/
│
├── README.md
│
├── requirements.txt
│
└── .gitignore
```

---

# 실행 Pipeline

---

# STEP 01. Data Preprocessing

## 목적

원시 데이터를 분석 가능한 형태로 정제한다.

---

### 입력

```
data/raw/accident/

data/raw/compensation/
```

---

### 수행 작업

- 결측치 처리
- 중복 제거
- 이상치 확인
- 변수명 통일
- 데이터 타입 변환
- 범주 통합

---

### 출력

```
data/processed/

accident_clean.csv

compensation_clean.csv
```

---

### 실행 Script

```
scripts/01_preprocessing.py
```

---

# STEP 02. Exploratory Data Analysis

## 목적

사고 발생 특성을 파악하고 데이터 구조를 이해한다.

---

### 입력

```
accident_clean.csv
```

---

### 수행 작업

- 사고건수 분석
- 학년별 분석
- 성별 분석
- 장소 분석
- 시간 분석
- 사고형태 분석
- 활동 분석

---

### 생성 시각화

- Count Plot
- Bar Plot
- Pie Chart
- Heatmap

---

### 출력

```
outputs/figures/

outputs/tables/
```

---

### 실행 Script

```
scripts/02_eda.py
```

---

# STEP 03. Statistical Analysis

## 목적

변수 간 관계가 통계적으로 유의한지 검정한다.

---

### 입력

```
accident_clean.csv
```

---

### 수행 작업

- Cross Table
- Chi-square Test
- Cramer's V

---

### 분석 대상

- 장소 × 사고형태
- 장소 × 활동
- 활동 × 사고형태
- 학년 × 장소
- 시간대 × 장소

---

### 출력

```
outputs/tables/statistical_test.csv
```

---

### 실행 Script

```
scripts/03_statistical_analysis.py
```

---

# STEP 04. Feature Engineering

## 목적

머신러닝 학습용 데이터를 생성한다.

---

### 수행 작업

- 시간대 생성
- 계절 생성
- 희소 범주 통합
- Encoding
- Target 생성

---

### 출력

```
model_dataset.csv
```

---

### 실행 Script

```
scripts/04_feature_engineering.py
```

---

# STEP 05. Machine Learning

## 목적

위험수준을 예측하는 모델을 구축한다.

---

### 모델

Baseline

- Decision Tree

- Random Forest

Final

- XGBoost

---

### 수행 작업

- Train/Test Split
- Cross Validation
- Hyperparameter Tuning
- Model Training

---

### 출력

```
outputs/models/
```

---

### 실행 Script

```
scripts/05_model_training.py
```

---

# STEP 06. Model Evaluation

## 목적

모델 성능을 비교하고 최종 모델을 선정한다.

---

### 평가지표

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

---

### 생성

- Confusion Matrix
- ROC Curve
- Feature Importance

---

### 출력

```
outputs/figures/

outputs/tables/
```

---

### 실행 Script

```
scripts/06_model_evaluation.py
```

---

# STEP 07. Explainable AI

## 목적

모델의 예측 결과를 해석한다.

---

### 수행 작업

- SHAP Summary Plot
- SHAP Bar Plot
- SHAP Dependence Plot
- Local Explanation

---

### 출력

```
outputs/shap/
```

---

### 실행 Script

```
scripts/07_shap_analysis.py
```

---

# STEP 08. Compensation Analysis

## 목적

피해 규모를 정량적으로 분석한다.

---

### 입력

```
compensation_clean.csv
```

---

### 수행 작업

- 평균 보상금
- 중앙값
- 최대 보상금
- IQR
- Boxplot

---

### 출력

```
outputs/tables/

outputs/figures/
```

---

### 실행 Script

```
scripts/08_compensation_analysis.py
```

---

# STEP 09. PPS Calculation

## 목적

예방관리 우선순위를 산출한다.

---

### 입력

- 사고 빈도
- 위험도
- 피해 규모

---

### 수행 작업

- Min-Max Scaling
- PPS 계산
- PPS Ranking 생성

---

### 출력

```
outputs/pps/

pps_result.csv

pps_ranking.csv
```

---

### 실행 Script

```
scripts/09_pps_calculation.py
```

---

# STEP 10. Sensitivity Analysis

## 목적

가중치 변화에 따른 PPS의 안정성을 평가한다.

---

### 수행 작업

다양한 가중치 조합을 적용하여 PPS를 재산출한다.

예시

Case 1

Frequency : Risk : Severity

= 0.33 : 0.33 : 0.34

Case 2

0.50 : 0.25 : 0.25

Case 3

0.25 : 0.50 : 0.25

Case 4

0.25 : 0.25 : 0.50

---

### 분석 내용

- 순위 변화
- 상위 위험상황 유지 여부
- 정책 적용 시나리오 비교

---

### 출력

```
outputs/pps/

sensitivity_analysis.csv
```

---

### 실행 Script

```
scripts/10_sensitivity_analysis.py
```

---

# STEP 11. Visualization

## 목적

최종 분석 결과를 시각화한다.

---

### 생성

- EDA Figure
- Heatmap
- Feature Importance
- SHAP Plot
- Confusion Matrix
- PPS Ranking
- Sensitivity Analysis Plot

---

### 출력

```
outputs/figures/
```

---

### 실행 Script

```
scripts/11_visualization.py
```

---

# STEP 12. Final Report

최종적으로 다음 결과물을 생성한다.

## Tables

- 사고 통계
- 통계검정 결과
- 모델 성능 비교
- SHAP 결과
- 보상 분석
- PPS 순위

---

## Figures

- EDA
- Heatmap
- SHAP
- Feature Importance
- PPS Ranking

---

## Models

- Decision Tree
- Random Forest
- XGBoost

---

## Final Deliverables

- GitHub Repository
- Analysis Report
- PPT
- README
- PPS Dashboard (Optional)

---

# 사용 라이브러리

## Data Processing

- pandas
- numpy

---

## Visualization

- matplotlib
- seaborn
---

## Statistical Analysis

- scipy
- statsmodels
---

## Machine Learning

- scikit-learn
- xgboost
---

## Explainable AI

- shap
---

## Utility

- joblib
- tqdm