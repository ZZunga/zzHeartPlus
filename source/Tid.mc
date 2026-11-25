using Toybox.Lang;
using Toybox.WatchUi;

// 운동 형태 분석 (TID, Training Intensity Distribution).
// 지금까지의 존별 시간 비율을 Riduck 심박분석의 8가지 TID 모델 기준 분포와 비교해
// 가장 닮은 모델을 고른다. 닮은 정도 = 겹침 % (각 존에서 작은 쪽 비율의 합, 0~100).
// tools/tid/index.html (분석 도구) 와 같은 계산.
//
// 넓고 높은 칸 + 설정 "운동 형태 분석" 이 켜진 경우에만 10초마다 계산한다.
module Tid {

    const N = 8;
    const KEYS = [ "HVLI", "HIT", "PRMD", "R.PRMD", "THRD", "POL", "R.POL", "EVEN" ];
    // Z1..Z5 %
    const DIST = [
        [ 35, 55,  5,  2,  3 ],   // HVLI    저강도 고볼륨
        [ 20, 20,  5,  5, 50 ],   // HIT     고강도 인터벌
        [ 20, 55, 15,  5,  5 ],   // PRMD    피라미드
        [  3,  7, 10, 30, 50 ],   // R.PRMD  역피라미드
        [ 10, 35, 25, 25,  5 ],   // THRD    역치
        [ 25, 55,  2,  3, 15 ],   // POL     양극화
        [ 10, 10,  5, 15, 60 ],   // R.POL   역양극화
        [ 20, 20, 20, 20, 20 ]    // EVEN    균등
    ];
    const MIN_MS = 600000;         // 기록 10분 미만이면 "분석 중"

    var best = -1;                 // 모델 인덱스, 분석 전 -1
    var score = 0;                 // 겹침 % (0~100)
    var ready = false;
    var _names = null;

    function reset() {
        best = -1;
        score = 0;
        ready = false;
    }

    // Zones.ms 로 다시 계산
    function update() {
        var total = Zones.total();
        ready = (total >= MIN_MS);
        if (!ready) {
            best = -1;
            return;
        }
        // 비율 (0~100, 소수 한 자리까지 쓰기 위해 x10 정수)
        var pct = new [5];
        for (var i = 0; i < 5; i++) {
            pct[i] = (Zones.ms[i].toLong() * 1000 / total).toNumber();
        }
        var bi = 0;
        var bs = -1;
        for (var m = 0; m < N; m++) {
            var d = DIST[m];
            var s = 0;
            for (var z = 0; z < 5; z++) {
                var dz = d[z] * 10;
                s += (pct[z] < dz) ? pct[z] : dz;
            }
            if (s > bs) {
                bs = s;
                bi = m;
            }
        }
        best = bi;
        score = (bs + 5) / 10;
    }

    // 모델 이름 (기기 언어: 한국어면 한글, 그 외 영문). 처음 쓸 때 한 번 읽는다.
    function name(i) {
        if (_names == null) {
            _names = [
                WatchUi.loadResource(Rez.Strings.tidHVLI),
                WatchUi.loadResource(Rez.Strings.tidHIT),
                WatchUi.loadResource(Rez.Strings.tidPRMD),
                WatchUi.loadResource(Rez.Strings.tidRPRMD),
                WatchUi.loadResource(Rez.Strings.tidTHRD),
                WatchUi.loadResource(Rez.Strings.tidPOL),
                WatchUi.loadResource(Rez.Strings.tidRPOL),
                WatchUi.loadResource(Rez.Strings.tidEVEN)
            ];
        }
        return _names[i];
    }

    // "HVLI(92%)"
    function head() {
        return KEYS[best] + "(" + score.format("%d") + "%)";
    }
}
