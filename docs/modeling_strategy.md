# Association Rule Strategy

## 목적

본 프로젝트의 목적은 개별 사고를 예측하는 것이 아니라, 학교가 우선 관리해야 할 반복적 위험상황을 식별하는 것이다. 따라서 지도학습 모델 대신 Apriori 연관규칙 분석을 핵심 기법으로 사용한다.

## 거래 정의

사고 한 건을 다음 다섯 항목으로 구성된 거래(transaction)로 정의한다.

- 사고장소
- 원본 사고시간
- 사고형태
- 사고당시활동
- 학년

각 항목은 `변수=값` 형식으로 변환되어 한 거래 안의 아이템이 된다.

## Apriori 지표

- **Support**: 전체 사고 중 항목집합이 발생한 비율
- **Confidence**: 선행항목 발생 시 후행항목이 함께 발생하는 조건부 비율
- **Lift**: 두 항목의 동시 발생이 독립 기대치보다 강한 정도

최소 support는 1%, confidence는 30%, lift는 1.0으로 두며, 모든 기준은 `config/config.yaml`에서 관리한다.

## 결과 해석

규칙은 support, confidence, lift를 함께 제시한다. 높은 support는 반복성을, 높은 confidence는 결합 가능성을, lift가 1보다 큰 값은 양의 연관성을 의미한다. 규칙은 인과관계가 아니라 동시 발생 패턴으로 해석한다.

## PPS 연계

완전한 위험상황(장소·사고당시활동·사고형태)을 포함한 규칙만 PPS에 연결한다. Association Score는 규칙별 `0.5 × normalized(confidence) - 0.5 × normalized(lift)`를 계산한 뒤 같은 위험상황에서 평균한다. Support는 Frequency에 이미 반영되므로 사용하지 않는다.

Severity는 동일 위험상황의 중앙 보상금을 정규화해 산출한다. 최종 PPS는 `0.40 × Frequency - 0.30 × Association - 0.30 × Severity`를 적용한다.

## 한계

- 연관규칙은 인과관계를 증명하지 않는다.
- 최소 support와 confidence 설정에 따라 규칙 수가 달라질 수 있다.
- 보상 데이터는 사고 데이터와 직접 매칭되지 않으므로 독립적으로 Severity를 산출한다.
