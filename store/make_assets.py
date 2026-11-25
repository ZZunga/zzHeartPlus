"""
make_assets.py - Connect IQ 스토어용 이미지 생성 (zzHeartPlus)

    python store/make_assets.py            -> store/images/*.png

  cover.png              앱 아이콘(대표 이미지) 500x500, 둘레 10px 여백, 투명 배경
  hero_ko.png / _en.png  히어로 1440x720 (한국어·영어)
  screen{1..5}.png       화면 이미지 500x500 (영어) (업로드 한도 150KB 이하로 저장)

화면 안의 데이터 필드는 tools/preview.py 렌더러로 그린다
(= 앱과 같은 비트맵 폰트·같은 배치 계산). Pillow 필요. zzWeatherPlus/store/make_assets.py 와 같은 틀.
"""
import io, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import preview as pv  # noqa: E402

OUT = os.path.join(HERE, "images")
os.makedirs(OUT, exist_ok=True)

# ---- 글꼴 -------------------------------------------------------------------
def _find_font(cands, want="KR"):
    for path in cands:
        if not os.path.exists(path):
            continue
        if path.endswith(".ttc"):
            for i in range(10):
                try:
                    f = ImageFont.truetype(path, 20, index=i)
                    if want in " ".join(f.getname()):
                        return path, i
                except OSError:
                    break
        else:
            return path, 0
    raise SystemExit("한글 글꼴을 찾을 수 없음: " + ", ".join(cands))

KR_BOLD = _find_font(["/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
                      "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                      "C:/Windows/Fonts/malgunbd.ttf"])
KR_REG = _find_font(["/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
                     "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                     "C:/Windows/Fonts/malgun.ttf"])
TITILLIUM = os.path.join(ROOT, "tools", "ttf", "TitilliumWeb-Bold.ttf")

def kb(size): return ImageFont.truetype(KR_BOLD[0], size, index=KR_BOLD[1])
def kr(size): return ImageFont.truetype(KR_REG[0], size, index=KR_REG[1])
def ti(size): return ImageFont.truetype(TITILLIUM, size)

RED = (226, 0, 0)
BLUE_LINE = (0, 120, 215)

def device(screen, side=16, top=22, bottom=30, radius=26):
    """화면 둘레에 무광 검정 사이클 컴퓨터 본체를 그린다 (로고 없음)."""
    sw, sh = screen.size
    W, H = sw + side * 2, sh + top + bottom
    ss = 3
    body = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, W * ss - 1, H * ss - 1], radius=radius * ss, fill=(28, 30, 34, 255))
    d.rounded_rectangle([3 * ss, 3 * ss, W * ss - 3 * ss, H * ss - 3 * ss], radius=(radius - 3) * ss,
                        outline=(58, 62, 70, 255), width=2 * ss)
    d.rounded_rectangle([(side - 4) * ss, (top - 4) * ss, (side + sw + 4) * ss, (top + sh + 4) * ss],
                        radius=6 * ss, fill=(8, 9, 11, 255))
    body = body.resize((W, H), Image.LANCZOS)
    body.paste(screen, (side, top))
    # 유리 반사 한 줄
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.polygon([(side, top), (side + sw * 0.55, top), (side + sw * 0.25, top + sh), (side, top + sh)],
               fill=(255, 255, 255, 14))
    body.alpha_composite(gl)
    return body


def shadowed(img, blur=18, offset=(0, 14), alpha=110):
    pad = blur * 3
    W, H = img.size
    out = Image.new("RGBA", (W + pad * 2, H + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    mask = img.split()[3].point(lambda a: a * alpha // 255)
    sh.paste(Image.new("RGBA", img.size, (0, 0, 0, 255)), (pad + offset[0], pad + offset[1]), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh)
    out.alpha_composite(img, (pad, pad))
    return out, pad


def gradient(W, H, top, bottom):
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / max(1, H - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g.resize((W, H)).convert("RGBA")


def save_png(img, name, limit_kb):
    path = os.path.join(OUT, name)
    rgb = img
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    if limit_kb and buf.tell() > limit_kb * 1024:
        has_alpha = img.mode == "RGBA"
        for colors in (256, 192, 128):
            q = img.convert("RGBA").quantize(colors=colors, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
            buf = io.BytesIO()
            q.save(buf, "PNG", optimize=True)
            if buf.tell() <= limit_kb * 1024:
                break
    with open(path, "wb") as f:
        f.write(buf.getvalue())
    print("  %-18s %4dx%-4d %6.1f KB" % (name, img.size[0], img.size[1], buf.tell() / 1024))



# ---- 화면 합성 ------------------------------------------------------------------
def page(rows, sw, sh, dark, solid=False, zone_color=False):
    """rows: [ (h, [ cell, ... ]), ... ]  cell = (w, hr, zone, avg, ratios[, analyzing]) -> 기기 화면"""
    pv.SCREEN_W[0] = sw
    bg = (23, 24, 29) if (dark and sw >= 480) else ((0, 0, 0) if dark else (255, 255, 255))
    img = Image.new("RGB", (sw, sh), bg)
    dr = ImageDraw.Draw(img)
    lw = 2 if sw >= 480 else 1
    y = 0
    for ri, (h, cells) in enumerate(rows):
        x = 0
        for ci, c in enumerate(cells):
            w, hr, zone, avg, ratios = c[:5]
            an = c[5] if len(c) > 5 else False
            tile = pv.render(w, h, hr, zone, avg, ratios, dark=dark, solid=solid, zone_color=zone_color, analyzing=an)
            img.paste(tile, (x, y))
            x += w
            if ci < len(cells) - 1:
                dr.line([x, y, x, y + h - 1], fill=BLUE_LINE, width=lw)
                x += lw
        y += h
        if ri < len(rows) - 1:
            dr.line([0, y, sw, y], fill=BLUE_LINE, width=lw)
            y += lw
    return img


# 존별 시간 비율 예시
R_LSD  = [0.31, 0.58, 0.06, 0.03, 0.02]   # HVLI
R_POL  = [0.24, 0.55, 0.03, 0.04, 0.14]   # POL
R_THRD = [0.12, 0.34, 0.24, 0.24, 0.06]   # THRD
R_PRMD = [0.18, 0.54, 0.17, 0.07, 0.04]   # PRMD
R_HIT  = [0.20, 0.22, 0.06, 0.07, 0.45]   # HIT


# 10분할 (5줄 x 2칸) 칸 값 예시: (심박, 존, 평균)
VALS10 = [(98, 1.8, 141), (132, 2.4, 128), (149, 2.9, 140), (162, 3.5, 148),
          (171, 4.2, 152), (176, 4.6, 158), (185, 5.3, 160), (121, 1.6, 120),
          (155, 3.1, 146), (140, 2.6, 138)]


def ten(sw, sh, ratios, vals=VALS10):
    """Garmin 10필드 레이아웃: 5줄 x 2칸, 칸 사이 구분선 포함해 화면을 꽉 채움"""
    lw = 2 if sw >= 480 else 1
    hs = [(sh - 4 * lw) // 5] * 5
    hs[-1] += (sh - 4 * lw) - sum(hs)
    w1 = (sw - lw) // 2
    w2 = sw - lw - w1
    rows = []
    for i, h in enumerate(hs):
        a, b = vals[2 * i], vals[2 * i + 1]
        rows.append((h, [(w1, a[0], a[1], a[2], ratios), (w2, b[0], b[1], b[2], ratios)]))
    return rows


def page_overview_840(dark=False):          # 246x322: 10분할
    return page(ten(246, 322, R_PRMD), 246, 322, dark)


def page_ten_850(dark=True):                # 420x600: 10분할 (검정 배경, 채움 막대)
    return page(ten(420, 600, R_HIT), 420, 600, dark, solid=True)


def page_ten_1050(dark=False):              # 480x800: 10분할
    return page(ten(480, 800, R_THRD), 480, 800, dark)


def page_tid_540(dark=False):               # 246x322: 넓고 높은 칸 운동 형태
    return page([
        (160, [(246, 152, 2.6, 141, R_LSD)]),
        (80, [(122, 138, 2.3, 141, R_LSD), (123, 164, 3.4, 152, R_LSD)]),
        (80, [(246, 145, 2.9, 140, R_LSD)]),
    ], 246, 322, dark)


def page_tid_1050(dark=True):               # 480x800: 운동 형태 + 넓은 칸 + 10필드 칸
    return page([
        (399, [(480, 158, 2.7, 146, R_POL)]),
        (199, [(480, 171, 3.6, 152, R_THRD)]),
        (198, [(239, 132, 2.2, 128, R_POL), (239, 185, 5.3, 160, R_POL)]),
    ], 480, 800, dark)


def page_cells_1040(dark=False):            # 282x470: 10분할, 심박존 색
    return page(ten(282, 470, R_THRD), 282, 470, dark, zone_color=True)


def page_wide_850(dark=True):               # 420x600: 넓은 칸 4개
    return page([
        (149, [(420, 162, 2.4, 148, R_HIT)]),
        (149, [(420, 176, 4.2, 158, R_HIT)]),
        (149, [(420, 191, 5.4, 165, R_HIT)]),
        (150, [(420, 145, 2.9, 140, R_HIT)]),
    ], 420, 600, dark, solid=True)


# ---- 1) 대표 이미지 500x500 --------------------------------------------------------
def make_cover():
    S = 4
    W = 500 * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    p = 10 * S
    d.rounded_rectangle([p, p, W - p - 1, W - p - 1], radius=34 * S, fill=(26, 30, 39, 255))
    sx0, sy0, sx1, sy1 = 58 * S, 50 * S, 442 * S, 318 * S
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=22 * S, fill=(244, 244, 244, 255))
    ink = (20, 20, 20, 255)
    zc = [(85, 85, 85), (0, 0, 255), (0, 170, 0), (255, 85, 0), (170, 0, 0)]

    # 아래: 존별 시간 히스토그램 (줄무늬) + 존 띠
    bx0, bx1, base = sx0 + 22 * S, sx1 - 22 * S, sy1 - 30 * S
    ratios = [0.20, 0.52, 0.16, 0.08, 0.04]
    cw = (bx1 - bx0) / 5
    for i, r in enumerate(ratios):
        x0, x1 = bx0 + cw * i + 3 * S, bx0 + cw * (i + 1) - 3 * S
        d.rectangle([x0 - 3 * S, base, x1 + 3 * S, base + 9 * S], fill=zc[i] + (255,))
        top = base - r * 150 * S
        y = base - 6 * S
        while y >= top:
            d.rectangle([x0, y, x1, y + 2 * S], fill=zc[i] + (255,))
            y -= 7 * S
    # 위: 하트 + 존 번호, 큰 심박 + 2단 단위
    # 하트 + 존 번호는 왼쪽 위 작게, 큰 심박은 그 아래 오른쪽 (앱의 10필드 칸 배치)
    k = 46 * S / 1000
    hx, hy = sx0 + 24 * S, sy0 + 22 * S
    d.polygon([(hx + px * k, hy + py * k) for px, py in pv.HEART], fill=(200, 0, 0, 255))
    d.text((hx + 54 * S, hy + 20 * S), "2.4", font=ti(46 * S), fill=zc[1] + (255,), anchor="lm")
    big = ti(132 * S)
    unit = ti(40 * S)
    ux = sx1 - 22 * S
    vy = sy0 + 196 * S
    d.text((ux, vy - 58 * S), "bp", font=unit, fill=ink, anchor="rs")
    d.text((ux, vy), "m", font=unit, fill=ink, anchor="rs")
    uw = d.textlength("bp", font=unit)
    d.text((ux - uw - 10 * S, vy), "162", font=big, fill=ink, anchor="rs")

    d.text((W / 2, 384 * S), "zzHeartPlus", font=ti(64 * S), fill=(255, 255, 255, 255), anchor="mm")
    cap = "HEART RATE  /  ZONE  /  TID"
    cf = ti(19 * S)
    spacing = 1.6 * S
    total = sum(d.textlength(ch, font=cf) + spacing for ch in cap) - spacing
    cxp = W / 2 - total / 2
    for ch in cap:
        d.text((cxp, 446 * S), ch, font=cf, fill=(232, 96, 96, 255), anchor="lm")
        cxp += d.textlength(ch, font=cf) + spacing
    img = img.resize((500, 500), Image.LANCZOS)
    save_png(img, "cover.png", 300)


# ---- 2) 히어로 1440x720 ------------------------------------------------------------
HERO_TXT = {
    "ko": dict(kicker="Garmin Edge 데이터 필드",
               title="zz심박수", tag="심박수 · 심박존 · 존별 시간 · 운동 형태",
               bullets=[((234, 64, 44), "존별 시간 비율을 히스토그램으로"),
                        ((0, 170, 255), "TID 8가지 모델로 운동 형태 분석"),
                        ((255, 170, 0), "큰 Titillium 숫자로 라이딩 중에도 또렷하게")],
               devices="Edge 540 · 550 · 840 · 850 · 1040 · 1050 · 1060"),
    "en": dict(kicker="Garmin Edge Data Field",
               title="zzHeart", tag="Heart Rate · Zone · Time in Zone · Training Type",
               bullets=[((234, 64, 44), "Time in each zone as a live histogram"),
                        ((0, 170, 255), "Training type from 8 TID models"),
                        ((255, 170, 0), "Big Titillium digits, readable at speed")],
               devices="Edge 540 · 550 · 840 · 850 · 1040 · 1050 · 1060"),
}


def pulse_line(img, color):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    W, H = img.size
    y0 = 560
    pts, x = [], -20
    while x < W + 40:
        pts += [(x, y0), (x + 60, y0), (x + 75, y0 - 50), (x + 90, y0 + 40), (x + 105, y0 - 120),
                (x + 122, y0 + 70), (x + 138, y0), (x + 230, y0)]
        x += 230
    d.line(pts, fill=color + (36,), width=4, joint="curve")
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1)))


def make_hero(lang):
    pv.LANG[0] = lang
    t = HERO_TXT[lang]
    W, H = 1440, 720
    img = gradient(W, H, (34, 14, 22), (12, 8, 14))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([820, -120, 1620, 700], fill=(200, 30, 60, 60))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    pulse_line(img, (255, 90, 110))

    big = device(page_tid_1050(dark=True), side=22, top=30, bottom=40, radius=34)
    big = big.resize((int(big.width * 0.70), int(big.height * 0.70)), Image.LANCZOS)
    small = device(page_overview_840(dark=False), side=16, top=22, bottom=30, radius=26)
    small = small.resize((int(small.width * 1.12), int(small.height * 1.12)), Image.LANCZOS)
    b, bp = shadowed(big, blur=22, offset=(0, 18), alpha=150)
    s_, sp = shadowed(small, blur=18, offset=(0, 14), alpha=170)
    img.alpha_composite(b, (1040 - bp, 52 - bp))
    img.alpha_composite(s_, (800 - sp, 222 - sp))

    d = ImageDraw.Draw(img)
    x = 96
    d.text((x, 150), t["kicker"], font=kr(30), fill=(235, 170, 180))
    if lang == "ko":
        f = kb(104)
        d.text((x - 4, 186), t["title"], font=f, fill=(255, 255, 255))
    else:
        f = ti(118)
        d.text((x - 4, 168), t["title"], font=f, fill=(255, 255, 255))
    tw_ = d.textlength(t["title"], font=f)
    d.text((x + tw_ + 2, 168 if lang == "ko" else 160), "+", font=ti(128), fill=RED)
    tag_f = kb(34) if lang == "ko" else ti(38)
    while d.textlength(t["tag"], font=tag_f) > 680:
        tag_f = kb(tag_f.size - 1) if lang == "ko" else ti(tag_f.size - 1)
    d.text((x, 336), t["tag"], font=tag_f, fill=(248, 226, 230))
    y = 418
    for color, line in t["bullets"]:
        d.ellipse([x, y + 12, x + 14, y + 26], fill=color)
        d.text((x + 30, y), line, font=kr(27) if lang == "ko" else ti(30), fill=(245, 232, 235))
        y += 52
    d.text((x, 610), t["devices"], font=kr(22) if lang == "ko" else ti(24), fill=(190, 140, 150))
    save_png(img.convert("RGB"), "hero_%s.png" % lang, 0)


# ---- 3) 화면 이미지 500x500 ----------------------------------------------------------
SCREENS = [
    ("screen1", page_overview_840, False,
     ("심박수 · 심박존 · 존별 시간을 한 칸에", "10분할 한 칸에서도 또렷하게"),
     ("Heart rate, zone and time in zone", "Clear even in one slot of a 10-field layout")),
    ("screen2", page_tid_1050, True,
     ("넓고 높은 칸에서 운동 형태 분석", "존별 시간 분포를 TID 8가지 모델과 비교"),
     ("Training type in large wide fields", "Your zone distribution vs 8 TID models")),
    ("screen3", page_tid_540, False,
     ("심박 바로 아래에 운동 형태", "괄호 안 숫자는 모델과 겹치는 정도, 기록 10분부터"),
     ("Training type under your heart rate", "Bracket = overlap with the model, after 10 minutes")),
    ("screen4", page_cells_1040, False,
     ("심박존 색과 위치 화살표", "평균 대비 높고 낮음 색상 설정 가능"),
     ("Zone colors and position arrow", "Colors for above or below your average")),
    ("screen5", page_ten_850, True,
     ("10분할 화면도 큰 숫자로", "줄무늬 또는 채움 히스토그램 선택"),
     ("Big digits even in 10-field layouts", "Striped or solid histogram bars")),
]


def make_screen(name, page_fn, dark, cap, lang):
    pv.LANG[0] = lang
    W = 500
    img = gradient(W, W, (242, 245, 250), (222, 229, 240)) if not dark else gradient(W, W, (36, 20, 28), (12, 10, 16))
    d = ImageDraw.Draw(img)
    title_c = (20, 30, 48) if not dark else (255, 255, 255)
    sub_c = (80, 92, 112) if not dark else (205, 175, 185)

    def fit(make, size, text, maxw=468):
        while size > 12 and d.textlength(text, font=make(size)) > maxw:
            size -= 1
        return make(size)
    tf = fit(kb, 25, cap[0]) if lang == "ko" else fit(ti, 28, cap[0])
    sf = fit(kr, 16, cap[1]) if lang == "ko" else fit(ti, 19, cap[1])
    d.text((W / 2, 30), cap[0], font=tf, fill=title_c, anchor="mm")
    d.text((W / 2, 62), cap[1], font=sf, fill=sub_c, anchor="mm")

    scr = page_fn(dark)
    if scr.height > 340:   # 1040/850/1050: 축소
        dev = device(scr, side=22, top=30, bottom=40, radius=34)
        k = 400 / dev.height
        dev = dev.resize((int(dev.width * k), int(dev.height * k)), Image.LANCZOS)
    else:                  # 540/840: 실제 픽셀 그대로 (비트맵 폰트 선명)
        dev = device(scr)
    sh, sp = shadowed(dev, blur=12, offset=(0, 8), alpha=120)
    img.alpha_composite(sh, ((W - dev.width) // 2 - sp, 88 - sp))
    save_png(img.convert("RGB"), "%s.png" % name, 150)


def main():
    print("store/images:")
    make_cover()
    # 히어로는 한국어·영어 두 장, 화면 5장은 영어만
    make_hero("ko")
    make_hero("en")
    for name, fn, dark, cko, cen in SCREENS:
        make_screen(name, fn, dark, cen, "en")


if __name__ == "__main__":
    main()
