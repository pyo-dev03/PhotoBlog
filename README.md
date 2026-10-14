# PhotoBlog - 모바일/웹서비스 프로젝트 공통평가 01

- 학번 / 이름 : 2022105757 / 표정수
- 강의자료(1) ch05 *모바일 앱으로 사용하는 기본 포토 블로그*, 강의자료(2) ch04 *테스트 주도 개발(TDD)*

```
ROOT
 ├─ PhotoBlogServer/   Django 서버 (REST API, 웹, API 검증 엔진, 자동 테스트, Socket Server)
 ├─ PhotoViewer/       Android 클라이언트 (Java)
 └─ 모바일/웹서비스 프로젝트 공통평가 01_수행 결과 보고서.docx
```

| 서버 | 주소 |
|---|---|
| 로컬 (브라우저 / telnet) | http://127.0.0.1:8000/ , API : http://127.0.0.1:8000/api_root/Post/ |
| 로컬 (Android 에뮬레이터) | http://10.0.2.2:8000 |
| 클라우드 (PythonAnywhere) | https://vyjsjs.pythonanywhere.com/ |

## 구현 항목

| # | 항목 | 구현 위치 |
|---|---|---|
| 1 | 포토 블로그 API (GET/POST/HEAD/OPTIONS, JSON Array, multipart 업로드) | `PhotoBlogServer/blog/views.py` `BlogImages`, `blog/urls.py` |
| 2-3 | API 검증 (telnet, codebeautify) | 보고서 그림 4, 5 |
| 4 | Server API 자동 테스트 + 검증 엔진 + Code Coverage | `PhotoBlogServer/blog/tests/`, `PhotoBlogServer/api_engine/` |
| 5-7 | Server/Client 연동 (브라우저, 앱 시작, 동기화) | `PhotoViewer/.../MainActivity.java` `CloadImage` |
| 8 | MainActivity Upload - **Post 에 따른 UI 제공(상)** | `MainActivity.onClickUpload`, `PutPost`, `res/layout/dialog_upload.xml` |
| 9 | PythonAnywhere 배포 | 아래 배포 절차 |
| 10 | 편의 기능 5개 | 아래 표 |

## 편의 기능 (소프트웨어 품질 요소별)

| # | 구분 | 기능 | 품질 요소 |
|---|---|---|---|
| ① | Server | 썸네일 자동 생성, ETag/304 조건부 GET, `?since=` 증분 조회, `?search=` 검색 | 효율성 |
| ② | Client | 썸네일 목록 + 원본은 상세 화면에서만, If-None-Match, 메모리·디스크 이미지 캐시, 동기화 성능 수치 표시, 핀치 줌 | 효율성 |
| ③ | Server | 작성자 위조 차단(토큰 사용자로 지정), 업로드 이미지 실검사(형식·크기·화소), 본인 글만 수정/삭제 | 보안 |
| ④ | Client | 로그인 화면(ID/PW → 토큰 발급), 토큰 Keystore 암호화 저장, 로컬↔클라우드 서버 전환 | 보안·유지보수 |
| ⑤ | Client | 업로드 전 리사이즈·JPEG 압축·EXIF 회전 보정, 업로드 진행률, 실패 시 지수 백오프 자동 재시도 | 신뢰성 |

각 폴더의 README.md 에 실행 방법이 있습니다.
