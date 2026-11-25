// zzHeartPlus 운동 형태 분류기: 존별 시간 분포 → TID 모델 (Riduck 심박분석의 8가지 모델 기준).
// 방식: 지금까지의 Z1~Z5 비율을 각 모델의 기준 분포와 비교해 가장 닮은 모델을 고른다.
//   겹침(overlap) = Σ min(내 비율, 모델 비율)  → 0~100%, 두 분포가 겹치는 넓이
//   거리(euclid)  = √Σ (내 비율 - 모델 비율)²  → 작을수록 닮음 (점수는 100 - 거리)
// 기기(Monkey C)에는 정수 배열 8개와 반복문 하나면 되므로 그대로 옮길 수 있다.

const MODELS = [
  { key: "HVLI",   ko: "HVLI · 저강도 고볼륨", desc: "저강도 비중 최대화, 기초 베이스 구축",   dist: [35, 55, 5, 2, 3] },
  { key: "HIT",    ko: "HIT · 고강도 인터벌", desc: "고강도 인터벌 집중, 단기 성과 위주",     dist: [20, 20, 5, 5, 50] },
  { key: "PRMD",   ko: "피라미드",           desc: "계단식 하향 분포, 가장 안정적인 모델",   dist: [20, 55, 15, 5, 5] },
  { key: "R.PRMD", ko: "역피라미드",          desc: "고강도 중심 하향, 근지구력·파워 강조",   dist: [3, 7, 10, 30, 50] },
  { key: "THRD",   ko: "역치",              desc: "중강도(Z3~4) 집중, 경기 페이스 적응",   dist: [10, 35, 25, 25, 5] },
  { key: "POL",    ko: "양극화",             desc: "중간(Z3~4) 배제, 양극단 강도 최적화",   dist: [25, 55, 2, 3, 15] },
  { key: "R.POL",  ko: "역양극화",            desc: "극단적 고강도 모델, 특정 시즌용",       dist: [10, 10, 5, 15, 60] },
  { key: "EVEN",   ko: "균등",              desc: "전 구역 균등 배분, 무작위 훈련 형태",    dist: [20, 20, 20, 20, 20] }
];

const DEFAULTS = {
  method: "overlap",   // "overlap" | "euclid"
  minMinutes: 10,      // 이보다 짧으면 "분석 중"
  closeGap: 5          // 1위와 2위 점수 차가 이보다 작으면 "비슷함" 표시
};

function percents(min) {
  const total = min.reduce((a, b) => a + b, 0);
  return { total, pct: min.map(m => (total > 0 ? (m / total) * 100 : 0)) };
}

function score(pct, dist, method) {
  if (method === "euclid") {
    let s = 0;
    for (let i = 0; i < 5; i++) s += (pct[i] - dist[i]) ** 2;
    return 100 - Math.sqrt(s);
  }
  let s = 0;
  for (let i = 0; i < 5; i++) s += Math.min(pct[i], dist[i]);
  return s;
}

function classify(min, t = DEFAULTS) {
  const { total, pct } = percents(min);
  const ranking = MODELS.map(m => ({ ...m, score: score(pct, m.dist, t.method) }))
    .sort((a, b) => b.score - a.score);
  const ready = total >= t.minMinutes;
  const best = ranking[0];
  const close = ranking[1] && best.score - ranking[1].score < t.closeGap;
  return { ready, total, pct, best, ranking, close };
}

// 대표 라이딩 예시 (존별 분). expect 는 사람이 보기에 그럴듯한 답.
const PRESETS = [
  { name: "LSD 3시간",                min: [55, 110, 12, 3, 0],   expect: "HVLI" },
  { name: "회복 라이딩 45분",           min: [30, 14, 1, 0, 0],     expect: "HVLI" },
  { name: "Z2 + 짧은 고강도 5x4분",     min: [30, 66, 2, 4, 18],    expect: "POL" },
  { name: "긴 그룹 라이딩",              min: [30, 80, 22, 8, 4],    expect: "PRMD" },
  { name: "템포 / 스윗스팟 90분",        min: [10, 30, 28, 20, 2],   expect: "THRD" },
  { name: "역치 인터벌 2x20분",          min: [12, 30, 18, 25, 5],   expect: "THRD" },
  { name: "VO2max 인터벌 (짧은 세션)",    min: [12, 12, 3, 4, 29],    expect: "HIT" },
  { name: "힐클라임 레이스",             min: [1, 3, 5, 18, 33],     expect: "R.PRMD" },
  { name: "크리테리움",                 min: [5, 5, 3, 9, 38],      expect: "R.POL" },
  { name: "출퇴근 (신호 많음)",           min: [6, 6, 6, 5, 5],       expect: "EVEN" },
  { name: "막 출발 (6분)",              min: [3, 3, 0, 0, 0],       expect: "-" }
];

if (typeof module !== "undefined") {
  module.exports = { MODELS, DEFAULTS, classify, PRESETS };
}
