# zzHeartPlus (zz심박수+)

Garmin Edge **데이터 필드**. 현재 심박을 Titillium Web 비트맵 폰트로 크게 보여주고,
심박존과 **존별 시간 비율 히스토그램**(기록 중 전체 시간 대비 각 존 %)을 배경에 그린다.
기존 **zzHeartChart (v1.1.2)** 를 다시 짠 버전. zzCadence 와 같은 폰트 크기 표와 칸 배치를 쓰고,
설정 키 이름은 zzHeartChart 와 같다.

## 대상 기기

| 기기 | 화면 | 런처 아이콘 |
|---|---|---|
| Edge 540 / 840 | 246 x 322 | 35 (기본 `resources/`) |
| Edge 550 / 850 | 420 x 600 | 56 |
| Edge 1040 | 282 x 470 | 40 |
| Edge 1050 / 1060 | 480 x 800 | 68 |

`minApiLevel` = **4.1.0**. `edge1060` 이 설치된 SDK 기기 목록에 없으면 SDK Manager 에서
받거나 `manifest.xml` 에서 그 줄을 지우고 빌드한다.

## 화면 (Plus 시리즈 zzSpeedPlus / zzCadencePlus 와 같은 규칙)

칸 폭이 화면 폭의 75% 를 넘으면 **넓은 칸**, 아니면 **좁은 칸**. 여백 가로/세로 5%.

**좁은 칸** (10필드 칸 등)
```
 ♥ 2            148 bp      ← 하트 + 현재 존(존 색) / 보조값 + 2단 단위 (같은 크기)
                    m
          162 bp            ← 현재 심박 (오른쪽 아래)
              m
 ■■■■■■▼■■■■■■■■■■■■■■      ← 존 색 띠 + 현재 위치 화살표 (+ 배경 히스토그램)
```
| 기기 | 메인 숫자 | 보조값·존 | 단위 (40%) |
|---|---|---|---|
| 540 / 840 | 33 | 20 | 13 / 8 |
| 1040 | 37 | 24 | 15 / 10 |
| 550 / 850 | 56 | 36 | 22 / 14 |
| 1050 / 1060 | 65 | 41 | 26 / 16 |

- Plus 시리즈(zzSpeedPlus / zzCadencePlus) 10필드 칸과 같은 크기 (기기별 `C10*` 폰트).
  칸이 이보다 작으면 Num 폰트 중 들어가는 가장 큰 크기로 줄인다.
- 존 번호: 소수(2.4)가 안 들어가면 정수(2), 그것도 안 되면 숨김 (10필드 칸은 정수).
- 단위: 2단 `bp` / `m`. 윗줄은 숫자 윗선, 아랫줄은 숫자 바닥선에 맞춤. 숫자-단위 간격 칸 폭의 2%.

**넓은 칸**, 아니면 **좁은 칸**. 여백 가로/세로 5%.

**좁은 칸** (10필드 칸 등)
```
 ♥ 2.4          148 bp      ← 하트 + 현재 존(존 색) / 보조값 + 2단 단위
                    m
          162 bp            ← 현재 심박 (오른쪽 아래, "188" + 단위가 들어가는 가장 큰 크기)
              m
 ■■■■■■▼■■■■■■■■■■■■■■      ← 존 색 띠 + 현재 위치 화살표 (+ 배경 히스토그램)
```
- 숫자: Num18..Num190 (zzCadence 크기 표).
- 단위: 숫자 높이 40% 의 2단 `bp` / `m` (Unit* 폰트). 윗줄은 숫자 윗선, 아랫줄은 숫자 바닥선에 맞춤.
  숫자와 단위 사이 칸 폭의 2%. 세 자리 값에도 항상 표시.

**넓은 칸**
```
 ♥ 2.4 zzHeartPlus          AVG bpm   ← 타이틀 줄 (SemiBold), 라벨 회색
      162      |      148              ← 두 값 같은 크기로 나란히 (보조값 없음이면 가운데 하나)
 ■■■■■■▼■■■■■■■■■■■■■■■■■■■■■■■■■■■
```
| 기기 | 값 숫자 높이 | 타이틀 | 라벨 |
|---|---|---|---|
| 540 / 840 | 35 | 13 | 10 |
| 1040 | 42 | 15 | 12 |
| 550 / 850 | 63 | 23 | 18 |
| 1050 / 1060 | 72 | 26 | 21 |

- 칸 폭 300px 미만은 짧은 타이틀 `zzHeart+`.
- 높은 넓은 칸은 숫자 줄을 남는 높이의 가운데에. 낮아서 타이틀이 안 들어가면(550/850 420x60 등)
  타이틀을 빼고 Num 폰트로 숫자만 (넓은 칸 값 크기를 넘지 않음).
- 존 띠는 아래 여백 안에 들어가서 타이틀이 들어가는 높이 조건이 zzCadencePlus 와 같다.

**운동 형태 분석** (설정 `tidAnalysis` 켬 + 넓고 높은 칸, 높이 >= 폭의 60%)
```
 ♥ 2.4 zzHeartPlus          AVG bpm
      158      |      146              ← 위쪽 절반: 값은 타이틀 바로 아래
 POL(98%) - 양극화                     ← 심박 숫자 왼쪽 끝에 맞춰 한 줄 (라벨 크기)
 ─────────── 히스토그램 (% 숫자) ──────  ← 아래쪽 절반
```
- `Tid.mc`: 존별 시간 비율을 Riduck 심박분석의 TID 8가지 모델과 비교, 겹침 %(각 존에서 작은 쪽 합)가 가장 큰 모델.
  HVLI 35/55/5/2/3, HIT 20/20/5/5/50, PRMD 20/55/15/5/5, R.PRMD 3/7/10/30/50,
  THRD 10/35/25/25/5, POL 25/55/2/3/15, R.POL 10/10/5/15/60, EVEN 20/20/20/20/20
- 이 화면일 때만 10초마다 계산 (다른 칸에서는 계산 안 함). 기록 10분 미만은 "분석 중".
- 이름은 기기 언어를 따름 (한국어 = 한글, 그 외 영문). 줄이 길면 칸 왼쪽 여백부터, 그래도 길면 이름 생략.
- 폰트 `TidLabel`: 영문·숫자 Titillium SemiBold + 한글 23자 Noto Sans KR (`tools/TidFont.py`).
- 분석 도구: `tools/tid/index.html` (존별 시간 입력 → 판정, Monkey C 상수 복사).

**공통**
- 존 번호: 가민 기기와 같은 소수 표기(2.4 = 2존의 40% 지점). 2.99 가 3.0 으로 올라가지 않게 버림.
- 히스토그램: 막대 높이 = 그 존의 시간 비율(100% 면 칸 맨 위까지). 막대 위 `%` 숫자는
  **넓고 높은 칸(높이 >= 폭의 60%, 1~2필드 칸)에서만** 표시하고, 숫자·하트·타이틀과 겹치면 생략. 줄무늬(기본) / 채움(옅은 색).
- 하트는 `tools/heart.svg`(Font Awesome heart, CC BY 4.0) 꼭짓점을 벡터로 그림. 1초마다 살짝 뛴다.
- 배경색은 기기 설정(흰/검정)을 따른다.

## 시간 누적 (`Zones.mc`)

- `UserProfile.getHeartRateZones(현재 스포츠)` 의 6개 경계값으로 존 계산. 타이머 시작 때 다시 읽음.
- `info.timerTime` 이 늘어난 만큼 현재 존에 더한다 → 일시정지·자동 일시정지 시간은 자연히 빠짐.
- Z1 최소 미만 심박은 Z1 에 합친다 (5개 막대 합 = 100%).
- 60초마다·일시정지·정지 때 `Application.Storage` 에 저장 → 라이딩 중 앱이 다시 켜져도 이어서 누적.
  타이머 리셋(저장/삭제) 때 지움.

## FIT 기록 (Garmin Connect)

| id | 이름 | 종류 |
|---|---|---|
| 0 | `hr_zone` | 레코드: 현재 존 (그래프) |
| 1~5 | `z1_pct` ~ `z5_pct` | 세션 요약: 존별 시간 % |

## 설정 (키 이름은 zzHeartChart 그대로)

| 키 | 내용 |
|---|---|
| `dataMode` | 오른쪽 위: 0 평균 / 1 최대 / 2 랩평균 / 3 없음 |
| `HeartZoneBar` | 하단 존 띠 + 현재 심박 위치 화살표 (존 안 소수 위치까지) |
| `HeartZoneHistory` | 존별 시간 % 히스토그램 |
| `histStyle`, `showPct` | 막대 모양(줄무늬/채움), 막대 위 % *(새로 추가)* |
| `showIcon`, `zoneDecimal` | 하트+존 번호, 존 소수 표시 *(새로 추가)* |
| `manualHeartZone` + `Zone1minValue`..`Zone5maxValue` | 심박존 직접 입력 (1순위) |
| `calcHeartZone` + `calcTypeHZ` + `maxHeartRate` | 최대심박으로 계산 (2순위): 기본 / Joe Friel / Andrew Coggan / USA / British / Strava / Garmin |
| (둘 다 끔) | 기기 사용자 프로필의 현재 스포츠 심박존 (3순위, **기본값**) |
| `threshold`, `colorHigh`, `colorLow` | 보조값 대비 threshold% 넘게 높/낮으면 메인 숫자 색 변경. "심박존 색"이면 항상 존 색 |

존 색 팔레트, 하트 색, 1050/1060 배경(0x17181D)·글자(0x313152) 색도 zzHeartChart 와 같다.

## zzHeartChart 대비 바뀐 점

| 기존 | zzHeartPlus |
|---|---|
| 히스토그램을 compute 호출 횟수로 셈, 일시정지 중에도 증가 | `timerTime` 증가분(ms)으로 누적 → 일시정지·자동정지 제외 |
| 막대 = 가장 많은 존 기준 정규화(줄 수) | 막대 = **전체 기록 시간 대비 %** (+ % 숫자) |
| 심박이 정확히 Z1 최소값이면 존 계산이 안 됨(경계 누락) | 경계 포함 처리, Z1 미만은 0.x 로 표시하고 시간은 Z1 에 합산 |
| `Properties.getValue` 그대로 사용 (값 없으면 크래시) | `Config.mc` 에서 try/catch + 기본값 + 범위 검사, 직접 입력 존은 오름차순일 때만 사용 |
| 존 프로필 항상 `HR_ZONE_SPORT_BIKING` | 현재 스포츠 프로필, 타이머 시작 때 다시 읽음 |
| 기기 폭으로 모델·칸 판정 (`switch(width)`) | 칸 크기만으로 폰트·배치 계산 (550/850/1060 포함 어느 기기든) |
| 레이아웃 XML + 폰트 2개 | 코드로 그림 + Titillium Web 11단계 |
| 앱 재시작 시 기록 초기화 | `Application.Storage` 로 복원 |
| `calcTypeHZ` 주석의 Friel/Coggan 이름이 서로 바뀌어 있음 (값은 설정 목록과 맞음) | 값 그대로, 주석 정리 |

## 폰트 다시 만들기

PNG 는 R=G=B=A 회색조 (zzWeatherPlus 에서 고친 형식, 가장자리 계단 현상 없음).

```
# 숫자 (공통)
java tools/FntGen.java tools/ttf/TitilliumWeb-Bold.ttf resources/fonts num " %-./0123456789:abeglmnopvxz" - 18 24 30 38 48 60 76 96 120 150 190
# 2단 단위 (공통, 숫자 높이 40%)
java tools/FntGen.java tools/ttf/TitilliumWeb-Bold.ttf resources/fonts unit "0bpm" - 9 12 14 19 23 29 38 47 59 75
# 10필드 칸 (기기별 폴더): c10main / c10sub / c10unitmain / c10unitsub  Bold
#   resources/ (540·840) 33/20/13/8, edge1040 37/24/15/10, edge550·850 56/36/22/14, edge1050·1060 65/41/26/16
# 운동 형태 줄 (기기별): python tools/TidFont.py <폴더>/fonts <라벨 높이 10/12/18/21>
# 넓은 칸 (기기별 폴더, 숫자 높이를 맞춰 px 를 고름)
#   wideval   Bold     "0123456789- "
#   widetitle SemiBold "zHeartPlus+0123456789.- "
#   widelabel SemiBold "0AVGMXLP bpm"
#   resources/ (540·840) 50/17/13px, resources-edge1040 60/20/16, edge550·850 90/32/25, edge1050·1060 103/37/29
```

출력의 `px adv cap` 을 `source/Layout.mc` 와 `tools/preview.py` 표에 맞춘다.

## 스토어

- 소개글: `store/description_ko.txt`, `store/description_en.txt`
- 이미지: `python store/make_assets.py` → `store/images/` (cover 500x500, hero 1440x720, screen1~5 500x500)
- 등록 체크리스트: `store/RELEASE.md`

## 빌드

```
powershell -File tools\build-all.ps1     # 기기별 .prg
powershell -File tools\export-iq.ps1     # 스토어 업로드용 .iq
python tools\preview.py                  # 레이아웃 미리보기 -> tools/preview.png
```
