"""
Eternal Heart ❤️ — Specially made for Muskan
A heart within a heart, written in words.

Features:
- Golden comet traces the heart outline.
- Crimson love messages fly into the heart.
- A golden inner heart appears with personal messages.
- "I LOVE YOU MUSKAN" appears in the centre.
- Glowing rings, heartbeat, glitter and floating embers.

Controls:
Click = Replay animation
Esc   = Close window

Requirements:
Python 3.8+
Uses only Python standard libraries.
"""

import math as m
import random as r
import tkinter as tk
import tkinter.font as tkf
import turtle as t


# ======================== PERSONALISE ========================

NAME = "I LOVE YOU MUSKAN"
SIGNATURE = "Forever yours,Muskan❤️"

PERSONAL = (
    "You are my home",
    "My favourite person",
    "Always yours",
    "Still choosing you",
    "You mean everything",
    "You are my happiness",
    "My beautiful Muskan",
    "Forever in my heart",
)

SEED = 11

# =============================================================


# Heart dimensions and animation settings
SC, OY = 20, 14

WIN_W, WIN_H = 820, 860

TICK = 16
ANIM = 46

INNER_K = 0.58
BAND_PAD = 13

SIZES = (10, 11, 12, 13)
INNER_SIZES = (9, 10)

BG = "#060208"


# Animation timeline
OUT_FRAMES = 150

BAND_START, BAND_FRAMES = 50, 430

INNER_START, INNER_FRAMES = 400, 200

NAME_START = INNER_START + INNER_FRAMES + 10

SIG_START = NAME_START + 80

ALL_IN = SIG_START + 90

BEAT = 100


# Romantic messages displayed around the outer heart
OUTER_TEXTS = [
    "I love you",
    "Seni seviyorum",
    "Te amo",
    "Je t'aime",
    "Ich liebe dich",
    "Ti amo",
    "Eu te amo",
    "Я тебя люблю",
    "사랑해",
    "愛してる",
    "我爱你",
    "Σ' αγαπώ",
    "Ik hou van jou",
    "Jag älskar dig",
    "Kocham cię",
    "ฉันรักเธอ",
    "Anh yêu em",
    "Aku cinta kamu",
    "நான் உன்னை காதலிக்கிறேன்",
    "Eres mi hogar",
    "Tu es ma lumière",
    "Sei la mia luce",
    "Du bist mein Zuhause",
]


SHORT_TEXTS = [
    "I love you",
    "Te amo",
    "Je t'aime",
    "Ti amo",
    "愛してる",
    "사랑해",
    "我爱你",
    "Seni seviyorum",
    "Ich liebe dich",
]


# Colour palette
WINE = (0.58, 0.0, 0.09)

CRIMSON = (0.90, 0.05, 0.14)

BLOOD = (0.98, 0.10, 0.16)

GOLD = (0.80, 0.58, 0.26)

GOLD_HI = (1.0, 0.86, 0.55)

IVORY = (1.0, 0.94, 0.78)

FLASH_RED = (1.0, 0.78, 0.78)

FLASH_GOLD = (1.0, 0.95, 0.80)

BGC = tuple(
    int(BG[i:i + 2], 16) / 255
    for i in (1, 3, 5)
)


# ======================== HELPER FUNCTIONS ========================

def clamp(v):
    return max(0.0, min(1.0, v))


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def mix(a, b, k):
    return tuple(
        p + (q - p) * k
        for p, q in zip(a, b)
    )


def dim(c, k):
    return tuple(v * k for v in c)


def hx(c):
    return "#%02x%02x%02x" % tuple(
        int(clamp(v) * 255)
        for v in c
    )


# Heart-shaped mathematical curve
def heart(a):
    x = 16 * m.sin(a) ** 3

    y = (
        13 * m.cos(a)
        - 5 * m.cos(2 * a)
        - 2 * m.cos(3 * a)
        - m.cos(4 * a)
    )

    return x * SC, y * SC + OY


POLY = [
    heart(2 * m.pi * i / 720)
    for i in range(720)
]

YMAX = max(p[1] for p in POLY)

YMIN = min(p[1] for p in POLY)

CY = (YMAX + YMIN) / 2


def scale_pt(x, y, k):
    """Scale a point around the centre of the heart."""

    return x * k, CY + (y - CY) * k


IPOLY = [
    scale_pt(x, y, INNER_K)
    for x, y in POLY
]


def edges_of(poly):
    return list(zip(poly, poly[1:] + poly[:1]))


EDGES = edges_of(POLY)

IEDGES = edges_of(IPOLY)


def spans(y, edges):
    xs = []

    for (x1, y1), (x2, y2) in edges:

        if (y1 <= y < y2) or (y2 <= y < y1):

            xs.append(
                x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            )

    xs.sort()

    return list(zip(xs[0::2], xs[1::2]))


def intersect(A, B, min_len):
    out = []

    for a in A:
        for b in B:

            lo = max(a[0], b[0])
            hi = min(a[1], b[1])

            if hi - lo > min_len:
                out.append((lo, hi))

    return out


def cut(seg, a, b, min_len):
    lo, hi = seg

    out = []

    if lo < a:
        out.append((lo, min(hi, a)))

    if hi > b:
        out.append((max(lo, b), hi))

    return [
        s for s in out
        if s[1] - s[0] > min_len
    ]


def radial(x, y):
    """Returns approximate distance from the heart's centre."""

    return m.hypot(
        x / (16 * SC),
        (y - CY) / (14.5 * SC)
    )


def beat_amp(age):
    """Creates the double-pulse heartbeat effect."""

    return (
        m.exp(-((age - 4) / 5.0) ** 2)
        + 0.6 * m.exp(-((age - 24) / 6.0) ** 2)
    )


# ======================== ANIMATION CLASS ========================

class EternalHeart:

    def __init__(self):

        self.screen = t.Screen()

        self.screen.setup(WIN_W, WIN_H)

        self.screen.bgcolor(BG)

        self.screen.title("For Muskan ❤️")

        self.screen.tracer(0)

        self.cv = self.screen.getcanvas()

        self.rng = r.Random(SEED)

        self._fonts = {}

        avail = set(
            tkf.families(root=self.cv)
        )

        def pick(opts, default):
            return next(
                (f for f in opts if f in avail),
                default
            )

        self.sans = pick(
            ("Arial", "Helvetica Neue", "Segoe UI", "DejaVu Sans"),
            "Arial"
        )

        self.serif = pick(
            (
                "Georgia",
                "Palatino Linotype",
                "Book Antiqua",
                "Times New Roman",
                "Times"
            ),
            "Times New Roman"
        )

        self._measure_name()

        self.templates = self._layout()

        self.frame = 0

        self._build_scene()

        top = self.cv.winfo_toplevel()

        top.bind(
            "<Button-1>",
            lambda _e: self._build_scene()
        )

        top.bind(
            "<Escape>",
            lambda _e: top.destroy()
        )

    # ======================== FONTS ========================

    def font(self, family, size, style):

        key = (family, size, style)

        if key not in self._fonts:

            self._fonts[key] = tkf.Font(
                root=self.cv,
                family=family,
                size=size,
                weight="bold" if style == "bold" else "normal",
                slant="italic" if style == "italic" else "roman"
            )

        return self._fonts[key]

    def _measure_name(self):

        limit = 32 * SC * INNER_K * 0.46

        size = 32

        while True:

            f = self.font(
                self.serif,
                size,
                "italic"
            )

            if f.measure(NAME) <= limit or size <= 14:
                break

            size -= 2

        self.name_size = size

        self.name_hw = f.measure(NAME) / 2 + 20

        self.name_hh = f.metrics("linespace") / 2 + 8

        self.name_cy = CY + 6

    # ======================== TEXT LAYOUT ========================

    def _cycle(self, texts):

        while True:

            order = list(texts)

            self.rng.shuffle(order)

            yield from order

    def _fill(
        self,
        segs_fn,
        family,
        style,
        sizes,
        texts,
        row_extra,
        pad
    ):

        rng = self.rng

        cycle = self._cycle(texts)

        row_h = max(
            self.font(family, z, style).metrics("linespace")
            for z in sizes
        ) + row_extra

        half = row_h / 2

        placed = []

        y = YMAX - half

        while y > YMIN + half:

            for lo, hi in segs_fn(y, half):

                lo, hi = lo + pad, hi - pad

                cur = lo + rng.uniform(0, 6)

                line = []

                while True:

                    fit = None

                    for _ in range(10):

                        text = next(cycle)

                        size = rng.choice(sizes)

                        w = self.font(
                            family,
                            size,
                            style
                        ).measure(text)

                        if cur + w <= hi:

                            fit = (text, size, w)

                            break

                    if not fit:
                        break

                    text, size, w = fit

                    line.append([
                        cur + w / 2,
                        text,
                        size,
                        w
                    ])

                    cur += w + 7

                if not line:
                    continue

                if len(line) > 1:

                    left = hi - (
                        line[-1][0] + line[-1][3] / 2
                    )

                    for i, it in enumerate(line):

                        it[0] += (
                            left * i / (len(line) - 1)
                        )

                else:

                    line[0][0] = (lo + hi) / 2

                for i, (x, text, size, _w) in enumerate(line):

                    placed.append(
                        dict(
                            x=x,
                            y=y,
                            text=text,
                            size=size,
                            edge=(
                                i == 0
                                or i == len(line) - 1
                            )
                        )
                    )

            y -= row_h

        return placed
    def _layout(self):
        rng = self.rng

        def band_segs(y, half):
            segs = intersect(
                spans(y + half, EDGES),
                spans(y - half, EDGES),
                14
            )

            for yy in (y + half, y, y - half):
                for a, b in spans(yy, IEDGES):
                    segs = [
                        p
                        for s in segs
                        for p in cut(
                            s,
                            a - BAND_PAD,
                            b + BAND_PAD,
                            24
                        )
                    ]

            return segs

        def inner_segs(y, half):
            segs = intersect(
                spans(y + half, IEDGES),
                spans(y - half, IEDGES),
                24
            )

            if abs(y - self.name_cy) < self.name_hh + half:
                segs = [
                    p
                    for s in segs
                    for p in cut(
                        s,
                        -self.name_hw,
                        self.name_hw,
                        24
                    )
                ]

            return segs

        band = self._fill(
            band_segs,
            self.sans,
            "bold",
            SIZES,
            OUTER_TEXTS,
            2,
            4
        )

        inner = self._fill(
            inner_segs,
            self.serif,
            "italic",
            INNER_SIZES,
            list(PERSONAL) * 3 + SHORT_TEXTS,
            4,
            6
        )

        out = []

        # Outer heart: red words
        for p in band:
            rad = min(1.0, radial(p["x"], p["y"]))

            c = mix(
                WINE,
                CRIMSON,
                0.25 + 0.75 * rad
            )

            c = mix(
                c,
                BLOOD,
                rng.uniform(0, 0.35)
                + (0.3 if p["edge"] else 0)
            )

            p.update(
                color=tuple(min(1, v) for v in c),
                rad=rad,
                mode="out",
                family=self.sans,
                style="bold",
                flashc=FLASH_RED,
                kind="word",
                ang=m.atan2(
                    p["x"],
                    p["y"] - CY
                ) % (2 * m.pi)
            )

        band.sort(key=lambda p: p["ang"])

        for k, p in enumerate(band):
            p["start"] = (
                BAND_START
                + BAND_FRAMES * k / len(band)
            )

        out += band

        # Inner heart: golden words
        for p in inner:
            v = clamp(
                (p["y"] - (CY - 150)) / 300
            )

            c = mix(GOLD, GOLD_HI, v)

            if p["text"] in PERSONAL:
                c = mix(c, IVORY, 0.45)

            p.update(
                color=c,
                rad=min(1.0, radial(p["x"], p["y"])),
                mode="in",
                family=self.serif,
                style="italic",
                flashc=FLASH_GOLD,
                kind="word"
            )

        inner.sort(
            key=lambda p: p["rad"] + rng.uniform(0, 0.1)
        )

        for k, p in enumerate(inner):
            p["start"] = (
                INNER_START
                + INNER_FRAMES * k / max(1, len(inner))
            )

        out += inner

        # Center message
        out.append(
            dict(
                x=0,
                y=self.name_cy,
                text=NAME,
                size=self.name_size,
                family=self.serif,
                style="italic",
                color=IVORY,
                rad=0.0,
                mode="rise",
                flashc=FLASH_GOLD,
                kind="name",
                start=NAME_START
            )
        )

        # Signature below the heart
        if SIGNATURE:
            out.append(
                dict(
                    x=0,
                    y=YMIN - 48,
                    text=SIGNATURE,
                    size=15,
                    family=self.serif,
                    style="italic",
                    color=mix(IVORY, GOLD, 0.35),
                    rad=0.0,
                    mode="rise",
                    flashc=FLASH_GOLD,
                    kind="sig",
                    start=SIG_START
                )
            )

        out.sort(key=lambda p: p["start"])

        return out

    # Scene objects
    def _build_scene(self):
        cv, rng = self.cv, self.rng

        cv.delete("all")

        self.frame = 0
        self.items = [
            dict(p) for p in self.templates
        ]

        self.next_i = 0
        self.flying = []
        self.landed = []
        self.rings = []

        # Heart glow layers
        self.glow = []

        for k, s in (
            (1.22, 0.012),
            (1.15, 0.022),
            (1.09, 0.036),
            (1.05, 0.052),
            (1.02, 0.070)
        ):
            pts = []

            for x, y in POLY[::3]:
                px, py = scale_pt(x, y, k)
                pts += [px, -py]

            self.glow.append(
                (
                    cv.create_polygon(
                        pts,
                        fill=BG,
                        outline=""
                    ),
                    s
                )
            )

        # Inner heart outline
        ipts = []

        for x, y in IPOLY[::2]:
            ipts += [x, -y]

        self.inner_line = cv.create_polygon(
            ipts,
            fill="",
            outline=BG,
            width=1.4
        )

        # Animated outline lines
        self.r_line = cv.create_line(
            0, 0, 0, 1,
            fill=BG,
            width=2,
            capstyle="round"
        )

        self.l_line = cv.create_line(
            0, 0, 0, 1,
            fill=BG,
            width=2,
            capstyle="round"
        )

        # Glowing tips
        self.heads = [
            (
                cv.create_oval(
                    0, 0, 0, 0,
                    fill=BG,
                    outline=""
                ),
                cv.create_oval(
                    0, 0, 0, 0,
                    fill=BG,
                    outline=""
                )
            )
            for _ in range(2)
        ]

        # Floating glowing particles
        self.embers = []

        for _ in range(30):
            e = dict(
                id=cv.create_oval(
                    0, 0, 0, 0,
                    fill=BG,
                    outline=""
                )
            )

            self._respawn_ember(e, True)
            self.embers.append(e)

    def _respawn_ember(self, e, initial=False):
        rng = self.rng

        for _ in range(60):
            y = rng.uniform(YMIN, YMAX)
            segs = spans(y, EDGES)

            if segs:
                lo, hi = rng.choice(segs)

                e["x"] = rng.uniform(lo, hi)
                e["y"] = y
                break

        e["life"] = rng.randint(140, 300)

        e["age"] = (
            rng.randint(0, e["life"])
            if initial
            else 0
        )

        e["vy"] = rng.uniform(0.35, 0.9)
        e["ph"] = rng.uniform(0, 6.28)
        e["r"] = rng.uniform(0.9, 2.2)
        e["gold"] = rng.random() < 0.55

    # Heart outline points
    def _outline_pts(self, a0, a1, n, k=1.04):
        pts = []

        for i in range(n + 1):
            x, y = heart(
                a0 + (a1 - a0) * i / n
            )

            px, py = scale_pt(x, y, k)
            pts += [px, -py]

        return pts

    def _draw_outline(self, p):
        n = max(2, int(130 * p))

        right = self._outline_pts(
            m.pi,
            m.pi - m.pi * p,
            n
        )

        left = self._outline_pts(
            m.pi,
            m.pi + m.pi * p,
            n
        )

        self.cv.coords(self.r_line, *right)
        self.cv.coords(self.l_line, *left)

        for (halo, core), pts in zip(
            self.heads,
            (right, left)
        ):
            x, y = pts[-2], pts[-1]

            self.cv.coords(
                halo,
                x - 9, y - 9,
                x + 9, y + 9
            )

            self.cv.coords(
                core,
                x - 3, y - 3,
                x + 3, y + 3
            )

            self.cv.itemconfig(
                halo,
                fill=hx(mix(BGC, GOLD, 0.35))
            )

            self.cv.itemconfig(
                core,
                fill=hx(mix(GOLD_HI, IVORY, 0.7))
            )

    def _hide_heads(self):
        for halo, core in self.heads:
            self.cv.coords(halo, 0, 0, 0, 0)
            self.cv.coords(core, 0, 0, 0, 0)

    # Animate words flying into the heart
    def _spawn(self, it):
        cv, rng = self.cv, self.rng

        tx, ty = it["x"], -it["y"]

        if it["mode"] == "out":
            a = rng.uniform(0, 2 * m.pi)
            rr = rng.uniform(520, 620)

            sx = rr * m.cos(a)
            sy = rr * m.sin(a)
            curve = rng.uniform(-110, 110)

        elif it["mode"] == "in":
            sx = 0.0
            sy = -CY
            curve = rng.uniform(-45, 45)

        else:
            sx = tx
            sy = ty + 18
            curve = 0.0

        dx, dy = tx - sx, ty - sy
        d = m.hypot(dx, dy) or 1

        it.update(
            sx=sx,
            sy=sy,
            curve=curve,
            nx=-dy / d,
            ny=dx / d,
            f=0,
            dur=ANIM if it["kind"] == "word" else 72,
            flash=0.0,
            last=""
        )

        fnt = (
            it["family"],
            it["size"],
            it["style"]
        )

        big = (
            it["family"],
            it["size"] + 1,
            it["style"]
        )

        it["shadow"] = cv.create_text(
            sx + 2,
            sy + 3,
            text=it["text"],
            font=fnt,
            fill=BG
        )

        it["halo"] = cv.create_text(
            sx,
            sy,
            text=it["text"],
            font=big,
            fill=BG
        )

        it["main"] = cv.create_text(
            sx,
            sy,
            text=it["text"],
            font=fnt,
            fill=BG
        )

        self.flying.append(it)
    def _fly(self, it):
        cv = self.cv

        it["f"] += 1
        u = clamp(it["f"] / it["dur"])
        e = 1 - (1 - u) ** 3

        tx, ty = it["x"], -it["y"]

        bend = it["curve"] * m.sin(m.pi * u)

        px = (
            it["sx"]
            + (tx - it["sx"]) * e
            + it["nx"] * bend
        )

        py = (
            it["sy"]
            + (ty - it["sy"]) * e
            + it["ny"] * bend
        )

        c = it["color"]

        cv.coords(
            it["shadow"],
            px + 2 * e,
            py + 3 * e
        )

        cv.coords(it["halo"], px, py)
        cv.coords(it["main"], px, py)

        cv.itemconfig(
            it["shadow"],
            fill=hx(mix(BGC, dim(c, 0.30), e))
        )

        cv.itemconfig(
            it["halo"],
            fill=hx(mix(BGC, dim(c, 0.20), e * e))
        )

        flash = 0.75 * m.sin(
            m.pi * clamp((u - 0.55) / 0.45)
        )

        cv.itemconfig(
            it["main"],
            fill=hx(
                mix(
                    mix(BGC, c, e ** 1.5),
                    it["flashc"],
                    flash
                )
            )
        )

        if u >= 1:
            cv.coords(
                it["shadow"],
                tx + 2,
                ty + 3
            )

            cv.coords(it["halo"], tx, ty)
            cv.coords(it["main"], tx, ty)

            it["last"] = ""

            if it["kind"] == "name":
                self._add_ring(0)
                self._add_ring(16)

            return False

        return True

    def _add_ring(self, delay):
        self.rings.append(
            dict(
                f=-delay,
                id=self.cv.create_oval(
                    0, 0, 0, 0,
                    outline=BG,
                    width=2
                )
            )
        )

    # Main animation loop
    def step(self):
        try:
            self._render()
            self.cv.after(TICK, self.step)

        except tk.TclError:
            return

    def _render(self):
        self.frame += 1

        f = self.frame
        cv = self.cv
        rng = self.rng

        started = f >= ALL_IN

        age = (
            (f - ALL_IN) % BEAT
            if started
            else 0
        )

        pulse = beat_amp(age) if started else 0.0

        # Draw the heart outline
        if f <= OUT_FRAMES + 1:
            self._draw_outline(
                max(smooth(f / OUT_FRAMES), 0.01)
            )

        elif f == OUT_FRAMES + 2:
            self._hide_heads()

        line_c = hx(
            mix(
                BGC,
                dim(GOLD, 0.85 + 0.25 * pulse),
                smooth(f / 40)
            )
        )

        cv.itemconfig(self.r_line, fill=line_c)
        cv.itemconfig(self.l_line, fill=line_c)

        cv.itemconfig(
            self.inner_line,
            fill="",
            outline=hx(
                mix(
                    BGC,
                    dim(GOLD, 0.8 + 0.3 * pulse),
                    smooth(
                        (f - INNER_START + 30) / 60
                    )
                )
            )
        )

        # Heart glow
        gi = smooth((f - 30) / 150)

        for gid, s in self.glow:
            cv.itemconfig(
                gid,
                fill=hx(
                    mix(
                        BGC,
                        CRIMSON,
                        s * gi * (0.8 + 0.9 * pulse)
                    )
                )
            )

        # Start word animations according to schedule
        while (
            self.next_i < len(self.items)
            and self.items[self.next_i]["start"] <= f
        ):
            self._spawn(self.items[self.next_i])
            self.next_i += 1

        # Animate flying words
        still = []

        for it in self.flying:
            if self._fly(it):
                still.append(it)
            else:
                self.landed.append(it)

        self.flying = still

        # Heartbeat glow and glitter
        lum = (
            0.93
            + 0.07 * m.sin(f * 0.05)
            + 0.08 * pulse
        )

        rip = []

        if started:
            for off, amp in (
                (0, 0.6),
                (20, 0.35)
            ):
                a = age - off

                if 0 <= a < 60:
                    rip.append(
                        (
                            a / 48.0,
                            amp * (1 - a / 60.0)
                        )
                    )

        if self.landed and rng.random() < 0.3:
            rng.choice(self.landed)["flash"] = 0.8

        for it in self.landed:
            g = 0.0

            for rr, amp in rip:
                g = max(
                    g,
                    amp * m.exp(
                        -((it["rad"] - rr) / 0.13) ** 2
                    )
                )

            fl = it["flash"]

            it["flash"] = (
                fl * 0.9
                if fl > 0.02
                else 0.0
            )

            col = mix(
                dim(it["color"], lum),
                it["flashc"],
                max(g, fl)
            )

            c = hx(col)

            if c != it["last"]:
                cv.itemconfig(it["main"], fill=c)
                it["last"] = c

        # Expanding golden rings
        for rg in self.rings[:]:
            rg["f"] += 1

            if rg["f"] <= 0:
                continue

            u = rg["f"] / 70.0

            if u >= 1:
                cv.delete(rg["id"])
                self.rings.remove(rg)
                continue

            rad = 20 + 420 * (1 - (1 - u) ** 2)

            cv.coords(
                rg["id"],
                -rad,
                -CY - rad * 0.92,
                rad,
                -CY + rad * 0.92
            )

            cv.itemconfig(
                rg["id"],
                outline=hx(
                    mix(
                        BGC,
                        GOLD_HI,
                        0.9 * (1 - u) ** 1.6
                    )
                )
            )

        # Floating golden and red particles
        ei = smooth((f - INNER_START) / 120)

        for e in self.embers:
            e["age"] += 1

            if e["age"] >= e["life"]:
                self._respawn_ember(e)

            a = m.sin(
                m.pi * e["age"] / e["life"]
            ) ** 2

            tw = (
                0.6
                + 0.4 * m.sin(
                    e["age"] * 0.25 + e["ph"]
                )
            )

            x = (
                e["x"]
                + 7 * m.sin(
                    e["age"] * 0.04 + e["ph"]
                )
            )

            y = -(e["y"] + e["vy"] * e["age"])
            rr = e["r"]

            cv.coords(
                e["id"],
                x - rr,
                y - rr,
                x + rr,
                y + rr
            )

            base = GOLD_HI if e["gold"] else BLOOD

            cv.itemconfig(
                e["id"],
                fill=hx(
                    mix(
                        BGC,
                        base,
                        0.9 * a * tw * ei
                    )
                )
            )

    # Start animation
    def run(self):
        self.cv.after(200, self.step)
        t.done()


# Application entry point
def main():
    try:
        EternalHeart().run()

    except (t.Terminator, tk.TclError):
        pass


if __name__ == "__main__":
    main()