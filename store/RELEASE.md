# zzHeartPlus 신규 앱 등록 체크리스트

## 0. 신규 앱으로 올라가는 이유
- `manifest.xml` 의 앱 ID가 새 값(`fa373009c1484baeb96078a6d4349403`)이라 스토어에서 **별도 앱**으로 등록된다.
  기존 zz심박수그래프(zzHeartChart)는 그대로 남는다.
- 기존 앱을 업데이트하는 방식으로 바꾸려면 ID를 기존 앱 값으로 바꾸면 된다. 설정 키는 zzHeartChart 와 같아서 사용자 설정이 유지된다.
- 개발자 키: 이후 업데이트도 **같은 키**로 서명해야 하니 `developer_key` 백업.

## 1. 빌드
```powershell
pwsh tools/build-all.ps1     # 기기별 .prg (시뮬레이터/사이드로드 테스트용)
pwsh tools/export-iq.ps1     # 업로드용 bin/zzHeartPlus.iq
```
- SDK 기기 목록에 `edge1060` 이 없으면 SDK Manager 에서 받거나 `manifest.xml` 에서 그 줄을 지운다.

## 2. 시뮬레이터 확인
- [ ] 기기마다(540/550/840/850/1040/1050/1060) `Simulation > Data Fields` 로 1·2·3·4·10필드, 전체화면
- [ ] 10필드 칸: 하트·존 번호·보조값·메인 심박·2단 단위가 겹치지 않는지
- [ ] 넓은 칸: 타이틀 줄과 두 값, 낮은 칸(550/850 420x60)은 타이틀 없이 숫자만
- [ ] 넓고 높은 칸: 운동 형태 화면. 10분 전 "분석 중", 10분 후 `HVLI(92%) - 저강도 고볼륨` 형식 (한국어/영어 기기 언어)
- [ ] 설정 "운동 형태 분석" 끔 → 넓은 칸 화면으로 바뀌는지
- [ ] 심박계 없음 → `--`, 크래시 없음
- [ ] 일시정지 중 히스토그램이 늘지 않는지, 타이머 리셋 후 초기화
- [ ] 심박존: 기기 프로필 / 최대심박 계산 / 직접 입력 (잘못된 값이면 기기 프로필로)
- [ ] 다크/라이트 배경, 색 테마(높을 때/낮을 때/심박존 색)
- [ ] 실기기 사이드로드: `bin/zzHeartPlus-<기기>.prg` → 기기 `GARMIN/APPS/`

## 3. 스토어 등록 (apps.garmin.com → 개발자 대시보드 → Upload an App)
| 항목 | 파일 / 내용 |
|---|---|
| 앱 패키지 | `bin/zzHeartPlus.iq` |
| 앱 이름 | `description_ko.txt` / `description_en.txt` 의 [앱 이름] |
| 설명 | 각 파일의 [설명] 부분 |
| 새로운 기능 | [새로운 기능 / 버전 기록] |
| 버전 | 1.0.0 (`resources/settings/properties.xml` 의 appVersion 과 맞춤) |
| 앱 유형 | Data Field |
| 대표 이미지(아이콘) | `images/cover.png` (500x500, 둘레 10px 여백) |
| 히어로 이미지 | `images/hero_ko.png`, `images/hero_en.png` (1440x720, 언어별) |
| 화면 이미지 | `images/screen1~5_ko.png` / `_en.png` (500x500, 150KB 이하) |
| 기부 링크 | https://paypal.me/zzungga (설명 안에 포함) |

- 이미지는 `python store/make_assets.py` 로 다시 만들 수 있다 (레이아웃을 바꾸면 같이 재생성).

## 4. 등록 후
- 기존 zz심박수그래프 설명 맨 위에 안내 추가 (예: "Edge 540/550/840/850/1040/1050/1060 사용자는 새 버전 zz심박수+를 받아주세요: 새 앱 링크")
- 버전 올릴 때: `properties.xml` 의 appVersion, `description_*.txt` 의 버전 기록 같이 수정
