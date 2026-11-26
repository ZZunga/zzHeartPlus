using Toybox.Application.Properties;
using Toybox.Lang;

// 설정 스냅샷 + 캐싱. onUpdate 는 1Hz 이므로 매번 Properties 를 읽지 않고
// 캐시를 쓰고 onSettingsChanged 에서 invalidate() 한다.
// 설정 키는 기존 zzHeartChart 와 같은 이름을 쓴다.
module Config {

    // 배경색 (bgMode)
    enum {
        BG_AUTO  = 0,   // 기기 화면과 같은 색으로 칠함 (1050/1060 은 #17181D / 남색 글씨)
        BG_PLAIN = 1,   // 기기가 알려준 검정 / 흰색 그대로
        BG_CLEAR = 2    // 칠하지 않음 (기기 배경이 그대로 비침)
    }

    // 우측 상단 보조값 (dataMode) - zzHeartChart 와 같은 번호
    enum {
        SEC_AVG     = 0,
        SEC_MAX     = 1,
        SEC_LAP_AVG = 2,
        SEC_NONE    = 3
    }

    // 히스토그램 막대 모양
    enum {
        HIST_STRIPE = 0,   // 가로 줄무늬 (숫자가 잘 보임)
        HIST_SOLID  = 1    // 꽉 채움
    }

    // 색 테마 (colorHigh / colorLow) - zzHeartChart 와 같은 번호
    enum {
        COLOR_DEFAULT      = 0,
        COLOR_RED          = 1,
        COLOR_ORANGE       = 2,
        COLOR_YELLOW       = 3,
        COLOR_YELLOWORANGE = 4,
        COLOR_GREEN        = 5,
        COLOR_BLUE         = 6,
        COLOR_PURPLE       = 7,
        COLOR_PINK         = 8,
        COLOR_PINKRED      = 9,
        COLOR_GRAY         = 10,
        COLOR_ZONE         = 11
    }

    class Snapshot {
        var bgMode     = BG_AUTO;  // 배경색
        var secondary   = SEC_AVG;
        var showIcon    = true;     // 하트 + 존 번호
        var zoneDecimal = true;     // 존 번호 2.4 처럼 소수 한 자리
        var showBar     = true;     // 하단 존 띠 + 현재 위치 화살표 (HeartZoneBar)
        var showHist    = true;     // 존별 시간 % 막대 (HeartZoneHistory)
        var histStyle   = HIST_STRIPE;
        var showPct     = true;     // 막대 위 % 숫자
        var tidAnalysis = true;     // 넓고 높은 칸에서 운동 형태 분석 화면

        // 심박존 출처: 직접 입력 > 최대심박 계산 > 기기 프로필
        var manualZone  = false;
        var manualBounds = null;    // [Z1최소, Z1최대, Z2최대, Z3최대, Z4최대, Z5최대]
        var calcZone    = false;
        var calcType    = 0;
        var maxHr       = 180;

        // 색 테마: 보조값(평균 등) 대비 threshold% 이상 높으면 colorHigh, 낮으면 colorLow
        var threshold   = 5;
        var colorHigh   = COLOR_DEFAULT;
        var colorLow    = COLOR_DEFAULT;
    }

    var _cache = null;

    function invalidate() {
        _cache = null;
    }

    function _get(key, dflt) {
        try {
            var v = Properties.getValue(key);
            if (v != null) {
                return v;
            }
        } catch (ex) {
        }
        return dflt;
    }

    function _num(key, dflt, lo, hi) {
        var v = _get(key, dflt);
        if (v instanceof Lang.Float || v instanceof Lang.Double || v instanceof Lang.Long) {
            v = v.toNumber();
        }
        if (!(v instanceof Lang.Number)) {
            return dflt;
        }
        if (v < lo) { return lo; }
        if (v > hi) { return hi; }
        return v;
    }

    function _bool(key, dflt) {
        var v = _get(key, dflt);
        return (v instanceof Lang.Boolean) ? v : dflt;
    }

    function read() {
        if (_cache != null) {
            return _cache;
        }
        var s = new Snapshot();
        s.secondary   = _num("dataMode", SEC_AVG, 0, 3);
        s.showIcon    = _bool("showIcon", true);
        s.zoneDecimal = _bool("zoneDecimal", true);
        s.showBar     = _bool("HeartZoneBar", true);
        s.showHist    = _bool("HeartZoneHistory", true);
        s.histStyle   = _num("histStyle", HIST_STRIPE, 0, 1);
        s.showPct     = _bool("showPct", true);
        s.tidAnalysis = _bool("tidAnalysis", true);

        s.manualZone  = _bool("manualHeartZone", false);
        if (s.manualZone) {
            s.manualBounds = [
                _num("Zone1minValue", 130, 30, 250),
                _num("Zone1maxValue", 160, 30, 250),
                _num("Zone2maxValue", 178, 30, 250),
                _num("Zone3maxValue", 190, 30, 250),
                _num("Zone4maxValue", 200, 30, 250),
                _num("Zone5maxValue", 214, 30, 250)
            ];
        }
        s.calcZone    = _bool("calcHeartZone", false);
        s.calcType    = _num("calcTypeHZ", 0, 0, 6);
        s.maxHr       = _num("maxHeartRate", 180, 50, 250);

        s.threshold   = _num("threshold", 5, 0, 100);
        s.colorHigh   = _num("colorHigh", COLOR_DEFAULT, 0, 11);
        s.colorLow    = _num("colorLow", COLOR_DEFAULT, 0, 11);
        s.bgMode      = _num("bgMode", BG_AUTO, 0, 2);
        _cache = s;
        return s;
    }
}
