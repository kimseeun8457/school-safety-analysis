# P4-SAFE: 학교안전 예방관리 우선순위체계

> **Predict · Profile · Prioritize · Prove**

학교안전 사고 데이터를 바탕으로 제한된 인력·시간·예산을 어떤 위험상황에 먼저 배치해야 하는지 제안하는 재현 가능한 정책 데이터과학 프로젝트입니다.

## 연구 목표

- 사고 이후의 귀책 판단이 아닌 **사전 예방관리 기준**을 설계합니다.
- 사고 빈도, 심각도, 반복성, 예방가능성, 개입비용을 통합한 `Preventive Priority Score (PPS)`를 개발합니다.
- 결과를 학교·교육청이 실행 가능한 `Top 3 예방관리 과제`로 변환합니다.

## 핵심 질문

1. 어떤 `학교급 × 시기 × 장소 × 활동` 조합을 우선 관리해야 하는가?
2. 동일한 예방자원으로 예상 손실을 가장 크게 줄일 수 있는 개입은 무엇인가?
3. 제안한 우선순위가 실제 사고·피해 부담을 줄이는가?

## 빠른 시작

```bash
git clone <repository-url>
cd school-safety-p4-safe
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

원자료는 `data/raw/`에만 보관하며 Git에 커밋하지 않습니다. `config/config.yaml`에서 실행 환경을 설정합니다.

## 디렉터리 안내

| 경로 | 용도 |
|---|---|
| `data/` | 원본, 외부, 중간, 정제 데이터 및 메타데이터 |
| `docs/` | 연구 설계, 분석계획, 변수사전, 의사결정·실험 기록 |
| `notebooks/` | 탐색·검증용 분석 노트북 |
| `src/` | 재사용 가능한 데이터·모델·점수화 코드 |
| `outputs/` | 표, 그림, 학습모델, 대시보드 산출물 |
| `tests/` | 데이터 품질 및 코드 테스트 |

## 재현성과 윤리

- 개인·학교 식별정보를 커밋하거나 공개하지 않습니다.
- 위험점수는 교원·학교의 징계, 책임판단, 성과평가에 사용하지 않습니다.
- 모든 모델은 시간 기준 검증, 불확실성, 공정성 점검을 포함합니다.
- 중요한 선택은 `docs/decision_log.md`에 기록합니다.

## 개발 명령어

```bash
ruff check src tests
pytest -q
jupyter lab
```

## 라이선스

코드와 문서는 [MIT License](LICENSE)를 따릅니다. 데이터 이용 조건은 각 제공기관의 정책을 따릅니다.
