# ARCHITECTURE - 아키텍처 문서

이 폴더는 Dudaji Dashboard 프로젝트의 아키텍처 결정 문서(ADRs)를 포함합니다.

## 📚 문서 목록

### ADRs (Architecture Decision Records)

- **[ADR-001: 데이터베이스 Foreign Key 제약 조건 미사용](./ADR_001-No_Foreign_Keys.md)**
  - 결정: DB 레벨 FK 제약 조건 미사용, 애플리케이션 코드에서 관리
  - 이유: 마이크로서비스 분리 대비, 수평 확장성, 성능
  - 영향: 데이터 무결성은 서비스 레이어에서 트랜잭션으로 보장

## 📖 ADR이란?

Architecture Decision Record는 프로젝트의 중요한 아키텍처 결정을 문서화한 것입니다.

**ADR 구조:**
- **컨텍스트 (Context):** 결정이 필요했던 배경
- **결정 (Decision):** 내린 결정 내용
- **근거 (Rationale):** 결정의 이유와 고려 사항
- **결과 (Consequences):** 긍정적/부정적 영향 및 대응 방안

## 🎯 언제 ADR을 작성하나?

다음과 같은 경우 ADR 작성을 고려하세요:

1. 기술 스택 선택 (DB, Framework, Library)
2. 설계 패턴 선택 (아키텍처 스타일, 데이터 모델링)
3. Dudaji 표준과 다른 정책 적용
4. 향후 유지보수에 영향을 주는 중요한 결정

## 💡 Tip

새로운 기능을 구현하거나 기존 구조를 변경할 때, 먼저 이 폴더의 ADR을 확인하세요. 프로젝트의 설계 철학을 이해하는 데 도움이 됩니다.

---

**상위 문서:** 00_PROJECT.md
