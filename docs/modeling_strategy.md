# Modeling Strategy

# Explainable AI 기반 초등학교 안전사고 위험도 분석 모델 설계

---

# 문서 목적

본 문서는 프로젝트에서 사용한 머신러닝 모델의 설계 의도와 모델 선택 이유를 기록한다.

단순히 모델을 구현하는 것이 아니라,

- 왜 해당 모델을 선택했는가
- 왜 이러한 Target을 정의했는가
- 모델 결과를 어떻게 활용하는가

를 명확히 설명하여 프로젝트의 재현성과 해석 가능성을 높이는 것을 목적으로 한다.

---

# 모델링 목표

본 프로젝트의 목표는

> "사고를 예측하는 것"

이 아니라

> "학교가 우선적으로 관리해야 할 위험상황을 식별하는 것"

이다.

따라서 모델의 예측 성능뿐만 아니라 결과를 설명할 수 있는 해석 가능성(Interpretability)을 중요하게 고려하였다.

---

# 문제 정의

## 문제 유형

Classification

---

## 선정 이유

사고 데이터를 이용하여 위험상황(Context)의 위험수준을

- High
- Medium
- Low

세 단계로 분류하는 것이 프로젝트 목적에 가장 적합하다고 판단하였다.

---

# Target 정의

## 위험상황(Context)

하나의 사고가 아니라

다음 변수의 조합을 하나의 위험상황으로 정의한다.

- 장소
- 사고형태
- 사고당시활동
- 시간대
- 학년

예시

```
운동장

+

쉬는시간

+

넘어짐

+

6학년
```

↓

하나의 Risk Context

---

## Risk Level 생성

각 Risk Context별 사고 발생 빈도를 집계한 후

빈도 분포를 기준으로

- High
- Medium
- Low

위험수준을 생성한다.

이 방식은 개별 사고를 예측하는 것이 아니라 반복적으로 발생하는 위험상황을 학습하는 데 목적이 있다.

---

# 입력 변수(Features)

모델 입력 변수는 다음과 같다.

| Feature | 설명 |
|---------|------|
| Region | 사고 발생 지역 |
| Grade | 학년 |
| Gender | 성별 |
| Weekday | 요일 |
| Time Zone | 시간대 |
| Place | 장소 |
| Accident Type | 사고형태 |
| Activity | 사고 당시 활동 |
| Month | 월 |
| Season | 계절 |

---

# Feature Engineering 전략

모델 성능과 해석력을 높이기 위해 다음 과정을 수행한다.

## 범주 통합

희소 범주는 상위 범주로 통합하여 데이터 불균형을 완화한다.

---

## 파생변수 생성

생성 변수

- 계절
- 시간대

---

## Encoding

범주형 변수는 모델 특성에 따라

- One-Hot Encoding
- Label Encoding

중 적절한 방법을 선택한다.

---

# Baseline Model 선정

최종 모델의 성능을 객관적으로 평가하기 위해 Baseline 모델을 구축한다.

## Decision Tree

선정 이유

- 구조가 단순
- 해석이 쉬움
- 기준 성능 확인

---

## Random Forest

선정 이유

- 앙상블 모델
- 과적합 감소
- Feature Importance 제공

---

# Final Model

## XGBoost

최종 모델로 XGBoost를 선정하였다.

선정 이유는 다음과 같다.

- 높은 예측 성능
- 범주형 데이터에 적합
- 결측치 처리에 강함
- 과적합 방지 기능
- Feature Importance 제공
- SHAP과 높은 호환성

---

# 모델 학습 전략

## Train/Test Split

기본적으로

- Train : 80%
- Test : 20%

비율을 사용한다.

---

## Cross Validation

K-Fold Cross Validation을 수행하여 모델의 일반화 성능을 평가한다.

---

## Hyperparameter Tuning

Grid Search 또는 Random Search를 이용하여

다음 주요 하이퍼파라미터를 최적화한다.

- max_depth
- learning_rate
- n_estimators
- subsample
- colsample_bytree

---

# 모델 평가 전략

다음 평가지표를 함께 활용한다.

| Metric | 목적 |
|---------|------|
| Accuracy | 전체 정확도 |
| Precision | 오탐 최소화 |
| Recall | 위험상황 탐지 |
| F1-score | Precision과 Recall 균형 |
| ROC-AUC | 분류 성능 평가 |

Confusion Matrix를 함께 분석하여 클래스별 예측 성능을 확인한다.

---

# Explainable AI 전략

본 프로젝트는 예측보다 설명 가능성을 중요하게 고려한다.

따라서 SHAP(SHapley Additive Explanations)을 활용하여

- 어떤 변수가 위험도를 높이는가
- 위험도가 왜 높게 예측되었는가

를 설명한다.

---

## Global Interpretation

전체 데이터 기준

- Feature Importance
- SHAP Summary Plot

---

## Local Interpretation

개별 사례 기준

예시

```
운동장

↓

쉬는시간

↓

6학년

↓

넘어짐

↓

High Risk
```

각 변수의 기여도를 시각적으로 분석한다.

---

# Error Analysis

Confusion Matrix를 기반으로 오분류 사례를 분석한다.

주요 분석 내용

- High → Medium 오분류
- Medium → Low 오분류
- 반복적으로 발생하는 오분류 패턴

Error Analysis 결과는 Feature Engineering 개선에 활용한다.

---

# PPS 연계 전략

머신러닝 모델의 최종 목적은 위험도 예측 자체가 아니다.

예측 결과는 PPS(Preventive Priority Score)의 Risk Score로 활용된다.

최종 PPS는

- Frequency
- Risk
- Severity

를 종합하여 계산한다.

---

# PPS 민감도 분석

가중치 설정의 영향을 평가하기 위해 민감도 분석을 수행한다.

다양한 가중치 조합에서 PPS를 계산하여

- 순위 변화
- 상위 위험상황 유지 여부
- 정책 우선순위 변화

를 비교 분석한다.

민감도 분석을 통해 PPS가 특정 가중치에 과도하게 의존하지 않는지 확인하고, 정책 목적에 따라 가중치를 유연하게 조정할 수 있는 근거를 제시한다.

---

# 모델링 한계

본 프로젝트는 다음과 같은 한계를 가진다.

- 과거 사고 데이터를 기반으로 분석한다.
- Risk Level은 빈도 기반으로 정의되므로 새로운 위험상황에는 한계가 있다.
- 보상데이터는 사고데이터와 직접 매칭되지 않아 독립적으로 활용된다.
- 학교별 시설, 학생 수, 기상 등 외부 요인은 포함하지 않는다.

---

# 향후 개선 방향

향후에는 다음과 같은 확장을 고려할 수 있다.

- 학교 시설 정보 연계
- 기상 데이터 활용
- 학생 수 및 학급 규모 반영
- LightGBM, CatBoost 등 모델 비교
- 웹 기반 PPS Dashboard 구축
- 실시간 학교 안전관리 의사결정 지원 시스템 개발