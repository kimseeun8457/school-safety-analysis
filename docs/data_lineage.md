# Data Lineage

# 초등학교 안전사고 데이터 분석 프로젝트

---

# 목적

본 문서는 프로젝트에서 데이터가 어떻게 생성되고 가공되며 최종 결과물로 이어지는지를 기록한다.

데이터의 흐름(Data Lineage)을 문서화하여

- 데이터 추적성 확보
- 분석 재현성 향상
- 프로젝트 유지보수
- 협업 효율성

을 높이는 것을 목적으로 한다.

---

# 전체 데이터 흐름

```text
사고 원본 데이터
        │
        ▼
01_preprocessing.py
        │
        ▼
accident_clean.csv
        │
        ├──────────────┐
        ▼              ▼
02_eda.py       03_statistical_analysis.py
        │              │
        ▼              ▼
EDA 결과      통계검정 결과
        │              │
        └──────┬───────┘
               ▼
04_feature_engineering.py
               │
               ▼
model_dataset.csv
               │
               ▼
05_model_training.py
               │
               ▼
trained_model.pkl
               │
               ▼
06_model_evaluation.py
               │
               ▼
평가지표
               │
               ▼
07_shap_analysis.py
               │
               ▼
SHAP 결과

────────────────────────────

보상 원본 데이터
        │
        ▼
01_preprocessing.py
        │
        ▼
compensation_clean.csv
        │
        ▼
08_compensation_analysis.py
        │
        ▼
Severity Score

────────────────────────────

사고빈도
        │

Risk Score
        │

Severity Score
        │
        ▼
09_pps_calculation.py
        │
        ▼
PPS Ranking
        │
        ▼
10_sensitivity_analysis.py
        │
        ▼
Final Policy Recommendation
```

---

# 데이터 흐름 상세

## STEP 1

### Input

```
data/raw/accident/
```

↓

### Script

```
01_preprocessing.py
```

↓

### Output

```
accident_clean.csv
```

↓

다음 단계

- EDA
- Statistical Analysis
- Feature Engineering

---

## STEP 2

### Input

```
accident_clean.csv
```

↓

### Script

```
02_eda.py
```

↓

### Output

```
eda_summary.csv

accident_distribution.png

grade_distribution.png

place_distribution.png

activity_distribution.png
```

---

## STEP 3

### Input

```
accident_clean.csv
```

↓

### Script

```
03_statistical_analysis.py
```

↓

### Output

```
chi_square_result.csv

cramers_v_result.csv

cross_table.csv
```

---

## STEP 4

### Input

```
accident_clean.csv
```

↓

### Script

```
04_feature_engineering.py
```

↓

### Output

```
model_dataset.csv
```

---

## STEP 5

### Input

```
model_dataset.csv
```

↓

### Script

```
05_model_training.py
```

↓

### Output

```
decision_tree.pkl

random_forest.pkl

xgboost.pkl
```

---

## STEP 6

### Input

```
xgboost.pkl
```

↓

### Script

```
06_model_evaluation.py
```

↓

### Output

```
metrics.csv

confusion_matrix.png

roc_curve.png

feature_importance.csv
```

---

## STEP 7

### Input

```
xgboost.pkl

model_dataset.csv
```

↓

### Script

```
07_shap_analysis.py
```

↓

### Output

```
shap_summary.png

shap_bar.png

shap_dependence.png

local_explanation.csv
```

---

## STEP 8

### Input

```
compensation_clean.csv
```

↓

### Script

```
08_compensation_analysis.py
```

↓

### Output

```
severity_score.csv

boxplot.png

compensation_summary.csv
```

---

## STEP 9

### Input

```
frequency_score.csv

risk_score.csv

severity_score.csv
```

↓

### Script

```
09_pps_calculation.py
```

↓

### Output

```
pps_result.csv

pps_ranking.csv
```

---

## STEP 10

### Input

```
pps_result.csv
```

↓

### Script

```
10_sensitivity_analysis.py
```

↓

### Output

```
sensitivity_analysis.csv

ranking_comparison.csv

sensitivity_plot.png
```

---

# 최종 산출물

최종적으로 생성되는 주요 결과물은 다음과 같다.

## Tables

- eda_summary.csv
- statistical_test.csv
- metrics.csv
- severity_score.csv
- pps_result.csv
- sensitivity_analysis.csv

---

## Figures

- 사고 발생 분포
- Heatmap
- Feature Importance
- SHAP Summary Plot
- SHAP Dependence Plot
- Confusion Matrix
- Boxplot
- PPS Ranking
- Sensitivity Analysis Plot

---

## Models

- Decision Tree
- Random Forest
- XGBoost

---

## Final Outputs

- 위험요인 분석
- PPS 우선순위
- 정책 제안
- GitHub README
- 최종 보고서