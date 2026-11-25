using Toybox.Application.Storage;
using Toybox.Lang;
using Toybox.UserProfile;

// 심박존 계산 + 존별 누적 시간.
//
// UserProfile.getHeartRateZones() 는 6개 값을 준다:
//   [Z1 최소, Z1 최대, Z2 최대, Z3 최대, Z4 최대, Z5 최대]
// 존 번호는 가민 기기와 같은 소수 표기: Z2 구간의 40% 지점이면 2.4.
// Z1 최소보다 낮은 심박(0.x)은 히스토그램에서 Z1 에 합친다.
module Zones {

    const N = 5;
    const STORE_KEY = "hz";

    var bounds = null;               // 6개 경계값 or null
    var ms = [0, 0, 0, 0, 0];        // 존별 누적 시간 (ms, 타이머가 도는 동안만)

    // 최대심박 기준 계산 방식 (calcTypeHZ, zzHeartChart 와 같은 값).
    // 0 기본 / 1 Joe Friel / 2 Andrew Coggan / 3 USA Cycling / 4 British Cycling / 5 Strava / 6 Garmin
    // (Friel·Coggan 은 원래 젖산역치심박(LTHR) 기준 비율이다)
    const CALC = [
        [0.65, 0.80, 0.89, 0.95,  1.00, 1.07],
        [0.65, 0.82, 0.89, 0.94,  1.00, 1.06],
        [0.50, 0.69, 0.84, 0.95,  1.06, 1.10],
        [0.50, 0.66, 0.73, 0.84,  0.91, 1.10],
        [0.50, 0.65, 0.75, 0.82,  0.89, 0.94],
        [0.50, 0.59, 0.78, 0.875, 0.97, 1.10],
        [0.50, 0.60, 0.70, 0.80,  0.90, 1.00]
    ];

    // 존 경계 읽기: 직접 입력 > 최대심박 계산 > 기기 사용자 프로필(현재 스포츠)
    function loadBounds() {
        bounds = null;
        var cfg = Config.read();
        if (cfg.manualZone && valid(cfg.manualBounds)) {
            bounds = cfg.manualBounds;
            return;
        }
        if (cfg.calcZone) {
            var pct = CALC[cfg.calcType];
            var b = new [6];
            for (var i = 0; i < 6; i++) {
                b[i] = (cfg.maxHr * pct[i]).toNumber();
            }
            if (valid(b)) {
                bounds = b;
                return;
            }
        }
        try {
            var z = UserProfile.getHeartRateZones(UserProfile.getCurrentSport());
            if (valid(z)) {
                bounds = z;
            }
        } catch (ex) {
            bounds = null;
        }
    }

    // 6개, 모두 숫자, 오름차순일 때만 사용
    function valid(b) {
        if (b == null || !(b instanceof Lang.Array) || b.size() < 6) {
            return false;
        }
        for (var i = 0; i < 6; i++) {
            if (b[i] == null || b[i] <= 0) {
                return false;
            }
            if (i > 0 && b[i] <= b[i - 1]) {
                return false;
            }
        }
        return true;
    }

    // 소수 존 (예: 2.4). 심박 없으면 null
    function zoneOf(hr) {
        if (hr == null) {
            return null;
        }
        if (bounds == null) {
            loadBounds();
            if (bounds == null) {
                return null;
            }
        }
        var b = bounds;
        if (hr < b[0]) {
            return (b[0] > 0) ? hr.toFloat() / b[0] : 0.0;
        }
        for (var i = 0; i < N; i++) {
            var lo = b[i];
            var hi = b[i + 1];
            if (hr < hi || i == N - 1) {
                var span = hi - lo;
                var frac = (span > 0) ? (hr - lo).toFloat() / span : 0.0;
                if (frac > 0.99) { frac = 0.99; }
                if (frac < 0.0)  { frac = 0.0; }
                return (i + 1) + frac;
            }
        }
        return 5.99;
    }

    // 소수 존 -> 히스토그램 칸 0..4 (Z1..Z5)
    function bucketOf(zone) {
        if (zone == null) {
            return -1;
        }
        var i = zone.toNumber() - 1;
        if (i < 0) { i = 0; }
        if (i > N - 1) { i = N - 1; }
        return i;
    }

    function add(bucket, deltaMs) {
        if (bucket >= 0 && bucket < N) {
            ms[bucket] += deltaMs;
        }
    }

    function total() {
        var t = 0;
        for (var i = 0; i < N; i++) {
            t += ms[i];
        }
        return t;
    }

    // 존별 비율 0.0 ~ 1.0
    function ratio(i) {
        var t = total();
        return (t > 0) ? ms[i].toFloat() / t : 0.0;
    }

    function reset() {
        ms = [0, 0, 0, 0, 0];
        try {
            Storage.deleteValue(STORE_KEY);
        } catch (ex) {
        }
    }

    // 앱이 중간에 다시 켜져도(프로필 전환 등) 누적값을 잃지 않게 저장.
    // [타이머 ms, z1..z5 ms]
    function save(timerMs) {
        try {
            Storage.setValue(STORE_KEY, [timerMs, ms[0], ms[1], ms[2], ms[3], ms[4]]);
        } catch (ex) {
        }
    }

    // 지금 타이머 시각과 맞는 저장값이면 복원. 저장된 타이머가 지금보다 크면
    // 이전 라이딩 값이므로 버린다. 복원했으면 저장된 타이머 ms, 아니면 null.
    function restore(timerMs) {
        try {
            var v = Storage.getValue(STORE_KEY);
            if (v instanceof Lang.Array && v.size() == 6 && v[0] != null
                    && v[0] > 0 && v[0] <= timerMs + 2000) {
                ms = [v[1], v[2], v[3], v[4], v[5]];
                return v[0];
            }
        } catch (ex) {
        }
        return null;
    }
}
