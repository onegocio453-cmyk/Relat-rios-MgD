#!/usr/bin/env python3
# MGD8 - 05/10/2026 a 11/10/2026 (4 grupos: MGD8.1 a MGD8.4)
# Relatório reconstruído do zero para corresponder ao layout de referência

import math, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, KeepTogether)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# ── Paleta ──────────────────────────────────────────────────────────────────
GD_BLUE    = colors.HexColor('#0D2B4E')
GD_BLUE_DK = colors.HexColor('#071A30')
GD_BLUE_LT = colors.HexColor('#1A6FAA')
GD_GOLD    = colors.HexColor('#B07800')
GD_GOLD_LT = colors.HexColor('#F5C842')
GD_BG      = colors.HexColor('#F0F4F8')
GD_ROW1    = colors.HexColor('#FFFFFF')
GD_ROW2    = colors.HexColor('#EEF2F7')
GD_BORDER  = colors.HexColor('#C8D6E5')
GD_MUTED   = colors.HexColor('#5A5A5A')
GD_GREEN   = colors.HexColor('#1A7A4A')
GD_GREEN_BG= colors.HexColor('#E6F4ED')
GD_RED     = colors.HexColor('#B00020')
GD_RED_BG  = colors.HexColor('#FAE6EA')
GD_ORA     = colors.HexColor('#B05000')
GD_ORA_BG  = colors.HexColor('#FAEEE6')
GD_YEL_BG  = colors.HexColor('#FFF9E6')
GD_YEL     = colors.HexColor('#7A5A00')
WHITE      = colors.white
W, H       = A4
BODY_W     = W - 3.0*cm   # content width (1.5cm margins each side)

# ── Estilos ──────────────────────────────────────────────────────────────────
def S(name, **kw):
    base = {
        'fontName': 'Helvetica', 'fontSize': 9, 'leading': 13,
        'textColor': GD_BLUE, 'spaceAfter': 0, 'spaceBefore': 0,
    }
    base.update(kw)
    return ParagraphStyle(name, **base)

sNorm   = S('norm')
sBold   = S('bold', fontName='Helvetica-Bold')
sSmall  = S('small', fontSize=7.5, textColor=GD_MUTED)
sCenter = S('center', alignment=TA_CENTER)
sRight  = S('right',  alignment=TA_RIGHT)
sBoldC  = S('boldc',  fontName='Helvetica-Bold', alignment=TA_CENTER)
sBoldR  = S('boldr',  fontName='Helvetica-Bold', alignment=TA_RIGHT)
sWhite  = S('white',  textColor=WHITE)
sWhiteB = S('whiteb', fontName='Helvetica-Bold', textColor=WHITE)
sWhiteBC= S('whitebc',fontName='Helvetica-Bold', textColor=WHITE, alignment=TA_CENTER)
sMuted  = S('muted',  textColor=GD_MUTED, fontSize=8)
sMutedC = S('mutedc', textColor=GD_MUTED, fontSize=8, alignment=TA_CENTER)
sGold   = S('gold',   fontName='Helvetica-Bold', textColor=GD_GOLD)
sJust   = S('just',   alignment=TA_JUSTIFY)
sBoldGold = S('boldgold', fontName='Helvetica-Bold', textColor=GD_GOLD)

def P(txt, style=None):
    return Paragraph(str(txt), style or sNorm)

def c(txt):
    # Replace em dashes with comma
    return txt.replace(' - ', ', ').replace(' -- ', ', ').replace('—', ', ')

# ── Flowables utilitários ────────────────────────────────────────────────────
class BlueLine(Flowable):
    def __init__(self, w=None, h=2, color=GD_BLUE):
        super().__init__()
        self._w = w; self.height = h; self._color = color
    def wrap(self, aw, ah):
        self.width = self._w or aw
        return self.width, self.height
    def draw(self):
        self.canv.setFillColor(self._color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

class GoldLine(BlueLine):
    def __init__(self, w=None, h=1.5):
        super().__init__(w, h, GD_GOLD)

# ── Capa header/footer via onPage ─────────────────────────────────────────────
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_gd_cropped.png')

def first_page(canvas, doc):
    """Capa: com cabeçalho e rodapé iguais às demais páginas."""
    canvas.saveState()
    _draw_header(canvas, doc, page_num=1)
    _draw_footer(canvas, doc)
    canvas.restoreState()

def later_pages(canvas, doc):
    canvas.saveState()
    _draw_header(canvas, doc)
    _draw_footer(canvas, doc)
    canvas.restoreState()

def _draw_header(canvas, doc, page_num=None):
    # Faixa azul mais fina — só "RELATÓRIO SEMANAL" (sem data)
    BAR_H = 1.4*cm
    canvas.setFillColor(GD_BLUE)
    canvas.rect(0, H - BAR_H, W, BAR_H, fill=1, stroke=0)
    # Texto único centralizado
    canvas.setFont('Helvetica-Bold', 10)
    canvas.setFillColor(WHITE)
    canvas.drawCentredString(W/2, H - BAR_H/2 - 4, 'RELATÓRIO SEMANAL')
    # Número de página à direita
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#C8D6E5'))
    pg = page_num if page_num is not None else canvas.getPageNumber()
    canvas.drawRightString(W - 1.2*cm, H - BAR_H/2 - 4, f'Pág. {pg}')

def _draw_footer(canvas, doc):
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GD_MUTED)
    canvas.drawCentredString(W/2, 0.6*cm,
        'MGD8  ·  3.331 mensagens  ·  05 a 11/10/2026  ·  Relatório Semanal de Inteligência de Mercado  ·  Geração Dividendos  ·  out/2026')

# ── Seção header ──────────────────────────────────────────────────────────────
def sec_header(num, title, subtitle=None):
    """Cabeçalho de seção: fundo azul, número igual ao título, espaço explícito."""
    badge = f'0{num}' if num < 10 else str(num)
    line = f'<font size="11"><b>{badge}</b></font>    <font size="11"><b>{title.upper()}</b></font>'
    if subtitle:
        cell = [
            P(line, sWhite),
            P(subtitle, S('sub', fontSize=7.5, textColor=colors.HexColor('#C8D6E5'))),
        ]
        t = Table([[cell[0]], [cell[1]]], colWidths=[BODY_W])
    else:
        t = Table([[P(line, sWhiteB)]], colWidths=[BODY_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GD_BLUE),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

# ── Callout box ───────────────────────────────────────────────────────────────
def callout(text, color=GD_BG, border_color=GD_BLUE_LT, text_color=GD_BLUE):
    sty = S('cbox', textColor=text_color, fontSize=8.5, leading=13, alignment=TA_JUSTIFY)
    t = Table([[P(text, sty)]], colWidths=[BODY_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1.5, border_color),
        ('ROUNDEDCORNERS', [3,3,3,3]),
    ]))
    return t

# ── Tabela padrão ─────────────────────────────────────────────────────────────
def std_tbl(data, cols, extra=None):
    t = Table(data, colWidths=cols, repeatRows=1)
    style = [
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,-1), 8.5),
        ('BACKGROUND',     (0,0), (-1,0), GD_BLUE),
        ('TEXTCOLOR',      (0,0), (-1,0), WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [GD_ROW1, GD_ROW2]),
        ('GRID',           (0,0), (-1,-1), 0.3, GD_BORDER),
        ('TOPPADDING',     (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 5),
        ('LEFTPADDING',    (0,0), (-1,-1), 6),
        ('RIGHTPADDING',   (0,0), (-1,-1), 6),
        ('VALIGN',         (0,0), (-1,-1), 'TOP'),
    ]
    if extra:
        style += extra
    t.setStyle(TableStyle(style))
    return t

# ── Badge de sentimento ───────────────────────────────────────────────────────
def sentiment_badge(label, bg, fg=WHITE):
    sty = S('badge', fontName='Helvetica-Bold', fontSize=7.5, textColor=fg, alignment=TA_CENTER)
    # Sem colWidths fixo — o badge ocupa 100% da célula da tabela pai
    t = Table([[P(label, sty)]])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    return t

# ── Badge de intensidade ──────────────────────────────────────────────────────
def intensity_badge(label, bg, fg=WHITE):
    sty = S('ibadge', fontName='Helvetica-Bold', fontSize=7.5, textColor=fg, alignment=TA_CENTER)
    t = Table([[P(label, sty)]])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    return t

# ── Gauge semicircular ────────────────────────────────────────────────────────
class GaugeFlowable(Flowable):
    """Semicírculo profissional 0-100 com 3 zonas. Score e label abaixo do pivot."""
    def __init__(self, score, width=None, height=230):
        super().__init__()
        self.score = score
        self._w = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = self._w or aw
        return self.width, self.height

    def _arc_band(self, cx, cy, r1, r2, a0_deg, a1_deg, color):
        c = self.canv
        steps = 60
        a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
        da = (a1 - a0) / steps
        pts_out, pts_in = [], []
        for i in range(steps + 1):
            a = a0 + i * da
            pts_out.append((cx + r2*math.cos(a), cy + r2*math.sin(a)))
            pts_in.append ((cx + r1*math.cos(a), cy + r1*math.sin(a)))
        p = c.beginPath()
        p.moveTo(*pts_out[0])
        for pt in pts_out[1:]: p.lineTo(*pt)
        for pt in reversed(pts_in): p.lineTo(*pt)
        p.close()
        c.setFillColor(color)
        c.drawPath(p, fill=1, stroke=0)

    def draw(self):
        c = self.canv
        cx = self.width / 2
        # Legenda ocupa 28pt na base (bar_y=2, bar_h=26)
        # Score 40pt abaixo do pivot → precisa de ~55pt abaixo do cy
        # cy = 28 (legenda) + 55 (score+label) + 9 (hub) = ~92
        cy = 96
        R_OUT = 95; R_IN = 62

        zones = [
            (180, 120, colors.HexColor('#C0392B')),   # Negativo
            (120,  60, colors.HexColor('#D4880A')),   # Misto
            ( 60,   0, colors.HexColor('#1A7A4A')),   # Positivo
        ]
        for a0, a1, col in zones:
            self._arc_band(cx, cy, R_IN, R_OUT, a0, a1, col)

        # Divisórias brancas entre zonas
        c.setStrokeColor(WHITE)
        c.setLineWidth(2.5)
        for angle in [120, 60]:
            rad = math.radians(angle)
            c.line(cx + R_IN*math.cos(rad), cy + R_IN*math.sin(rad),
                   cx + R_OUT*math.cos(rad), cy + R_OUT*math.sin(rad))

        # Labels dentro dos arcos — ajustados por zona para não sair da borda
        zone_labels = [('NEGATIVO', '0–33'), ('MISTO', '34–66'), ('POSITIVO', '67–100')]
        # Offsets angulares por zona: empurra NEGATIVO e POSITIVO para dentro
        for (a0, a1, _), (lbl, rng) in zip(zones, zone_labels):
            mid = math.radians((a0 + a1) / 2)
            rm = (R_OUT + R_IN) / 2
            lx = cx + rm * math.cos(mid)
            ly = cy + rm * math.sin(mid)
            c.setFillColor(WHITE)
            c.setFont('Helvetica-Bold', 5.5)
            c.drawCentredString(lx, ly + 3, lbl)
            c.setFont('Helvetica', 5)
            c.drawCentredString(lx, ly - 5, rng)

        # Marcadores de tick nas extremidades (0, 50, 100)
        for val, lbl in [(0, '0'), (50, '50'), (100, '100')]:
            ang = math.radians(180 - val * 1.8)
            tx = cx + (R_OUT + 8) * math.cos(ang)
            ty = cy + (R_OUT + 8) * math.sin(ang)
            c.setFont('Helvetica', 6.5)
            c.setFillColor(GD_MUTED)
            c.drawCentredString(tx, ty - 3, lbl)

        # Agulha
        pct = self.score / 100.0
        needle_ang = math.radians(180 - pct * 180)
        # Sombra leve da agulha
        nx = cx + (R_IN - 4) * math.cos(needle_ang)
        ny = cy + (R_IN - 4) * math.sin(needle_ang)
        c.setStrokeColor(colors.HexColor('#00000033'))
        c.setLineWidth(5)
        c.line(cx + 1, cy - 1, nx + 1, ny - 1)
        # Agulha principal
        c.setStrokeColor(GD_BLUE)
        c.setLineWidth(3)
        c.line(cx, cy, nx, ny)
        # Contrapeso (pequena cauda)
        back_ang = needle_ang + math.pi
        bx = cx + 10 * math.cos(back_ang)
        by = cy + 10 * math.sin(back_ang)
        c.setLineWidth(2)
        c.line(cx, cy, bx, by)
        # Hub externo
        c.setFillColor(GD_BLUE)
        c.circle(cx, cy, 9, fill=1, stroke=0)
        # Hub interno branco
        c.setFillColor(WHITE)
        c.circle(cx, cy, 4.5, fill=1, stroke=0)

        # ── Score e label ABAIXO do pivot ──
        c.setFont('Helvetica-Bold', 40)
        c.setFillColor(GD_BLUE)
        c.drawCentredString(cx, cy - 46, str(self.score))

        zone_color = colors.HexColor('#1A7A4A')
        zone_text  = 'POSITIVO'
        if self.score <= 33:
            zone_color = colors.HexColor('#C0392B')
            zone_text  = 'NEGATIVO'
        elif self.score <= 66:
            zone_color = colors.HexColor('#D4880A')
            zone_text  = 'MISTO'
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(zone_color)
        c.drawCentredString(cx, cy - 60, zone_text)

        # ── Faixa de legenda integrada no fundo do box ──
        bar_y = 2          # y do fundo da faixa
        bar_h = 26         # altura da faixa
        W = self.width
        zone_defs = [
            (colors.HexColor('#C0392B'), 'NEGATIVO', '0–33'),
            (colors.HexColor('#D4880A'), 'MISTO',    '34–66'),
            (colors.HexColor('#1A7A4A'), 'POSITIVO', '67–100'),
        ]
        sw = 12            # largura do swatch colorido
        seg_w = W / 3
        for i, (zcol, zlbl, zrng) in enumerate(zone_defs):
            sx = i * seg_w
            # swatch colorido
            c.setFillColor(zcol)
            c.roundRect(sx + 8, bar_y + 5, sw, bar_h - 10, 2, fill=1, stroke=0)
            # texto label + intervalo
            c.setFillColor(GD_BLUE)
            c.setFont('Helvetica-Bold', 8)
            c.drawString(sx + sw + 14, bar_y + 13, zlbl)
            c.setFont('Helvetica', 7)
            c.setFillColor(GD_MUTED)
            c.drawString(sx + sw + 14, bar_y + 4, zrng)
            # separador vertical (exceto no último)
            if i < 2:
                c.setStrokeColor(GD_BORDER)
                c.setLineWidth(0.5)
                c.line(sx + seg_w, bar_y, sx + seg_w, bar_y + bar_h)
        # linha separadora acima da faixa
        c.setStrokeColor(GD_BORDER)
        c.setLineWidth(0.5)
        c.line(0, bar_y + bar_h, W, bar_y + bar_h)

# ── BarChart diário ──────────────────────────────────────────────────────────
class BarChart(Flowable):
    def __init__(self, labels, values, width=None, height=110, weekend_idxs=None, avg=None):
        super().__init__()
        self.labels = labels; self.values = values
        self._w = width; self.height = height
        self.weekend_idxs = weekend_idxs or []
        self.avg = avg

    def wrap(self, aw, ah):
        self.width = self._w or aw
        return self.width, self.height

    def draw(self):
        c = self.canv
        W, H = self.width, self.height
        pad_l, pad_r, pad_t, pad_b = 35, 15, 22, 30
        cw = W - pad_l - pad_r
        ch = H - pad_t - pad_b
        mx = max(self.values) if self.values else 1
        n = len(self.labels)
        gap = cw / n
        bw  = gap * 0.58

        # Grid lines
        for frac in [0, 0.25, 0.5, 0.75, 1.0]:
            val = mx * frac
            yy = pad_b + frac * ch
            c.setStrokeColor(colors.HexColor('#D8E4EF'))
            c.setLineWidth(0.4)
            c.line(pad_l, yy, W - pad_r, yy)
            c.setFont('Helvetica', 6)
            c.setFillColor(GD_MUTED)
            c.drawRightString(pad_l - 3, yy - 3, f'{int(val):,}'.replace(',','.'))

        # Bars
        for i, (lbl, val) in enumerate(zip(self.labels, self.values)):
            x = pad_l + i * gap + (gap - bw) / 2
            bh = max((val / mx) * ch, 2)
            y  = pad_b
            fc = colors.HexColor('#8AAEC8') if i in self.weekend_idxs else GD_BLUE
            c.setFillColor(fc)
            c.roundRect(x, y, bw, bh, 2, fill=1, stroke=0)
            # Value label on top of bar
            c.setFont('Helvetica-Bold', 6.5)
            c.setFillColor(GD_BLUE)
            c.drawCentredString(x + bw/2, y + bh + 3, f'{val:,}'.replace(',','.'))
            # X label below
            c.setFont('Helvetica', 7)
            c.setFillColor(GD_MUTED)
            c.drawCentredString(x + bw/2, pad_b - 12, lbl[:5])
            c.setFont('Helvetica', 5.5)
            c.drawCentredString(x + bw/2, pad_b - 20, lbl[5:].strip())

        # Avg line
        if self.avg:
            ay = pad_b + (self.avg / mx) * ch
            c.setStrokeColor(GD_GOLD)
            c.setLineWidth(1.5)
            c.setDash([5, 3])
            c.line(pad_l, ay, W - pad_r, ay)
            c.setDash([])
            c.setFont('Helvetica-Bold', 7)
            c.setFillColor(GD_GOLD)
            c.setFont('Helvetica-Bold', 7)
            c.setFillColor(GD_GOLD)
            avg_lbl = f'Média: {self.avg:,}'.replace(',', '.')
            c.drawRightString(W - pad_r - 2, ay + 5, avg_lbl)

# ── Monthly bar chart ─────────────────────────────────────────────────────────
class MonthlyBarChart(Flowable):
    def __init__(self, labels, values, partial_idx=None, width=None, height=110):
        super().__init__()
        self.labels = labels; self.values = values
        self.partial_idx = partial_idx  # index that is partial/lighter
        self._w = width; self.height = height

    def wrap(self, aw, ah):
        self.width = self._w or aw
        return self.width, self.height

    def draw(self):
        c = self.canv
        W, H = self.width, self.height
        pad_l, pad_r, pad_t, pad_b = 50, 20, 22, 30
        cw = W - pad_l - pad_r
        ch = H - pad_t - pad_b
        mx = max(self.values) if self.values else 1
        n = len(self.labels)
        gap = cw / n
        bw  = gap * 0.55

        # Grid
        for frac in [0, 0.25, 0.5, 0.75, 1.0]:
            val = mx * frac
            yy = pad_b + frac * ch
            c.setStrokeColor(colors.HexColor('#D8E4EF'))
            c.setLineWidth(0.4)
            c.line(pad_l, yy, W - pad_r, yy)
            c.setFont('Helvetica', 6.5)
            c.setFillColor(GD_MUTED)
            c.drawRightString(pad_l - 4, yy - 3, f'{int(val):,}'.replace(',','.'))

        for i, (lbl, val) in enumerate(zip(self.labels, self.values)):
            x = pad_l + i * gap + (gap - bw) / 2
            bh = max((val / mx) * ch, 2)
            y  = pad_b
            fc = GD_BLUE_LT if (self.partial_idx is not None and i == self.partial_idx) else GD_BLUE
            c.setFillColor(fc)
            c.roundRect(x, y, bw, bh, 2, fill=1, stroke=0)
            c.setFont('Helvetica-Bold', 7)
            c.setFillColor(GD_BLUE)
            c.drawCentredString(x + bw/2, y + bh + 4, f'{val:,}'.replace(',','.'))
            c.setFont('Helvetica', 8)
            c.setFillColor(GD_MUTED)
            c.drawCentredString(x + bw/2, pad_b - 14, lbl)

# ════════════════════════════════════════════════════════════════════════════════
# DADOS DO RELATÓRIO — MGD8 (MGD8.1, MGD8.2, MGD8.3, MGD8.4)
# Fonte: exportações WhatsApp dos 4 grupos, mensagens de 05/10 a 11/10/2026
# Menções = nº de mensagens que citam o ativo/tema (ticker, nome ou apelido)
# ════════════════════════════════════════════════════════════════════════════════

SEMANA_STR = '05 a 11 de outubro de 2026'
SEMANA_SHORT = '05-11/10/2026'
TOTAL_MSGS = 3331
N_GRUPOS = 4

ranking_raw = [
    ('05/10', 'Segunda', 1182),
    ('06/10', 'Terça',    501),
    ('07/10', 'Quarta',   549),
    ('08/10', 'Quinta',   310),
    ('09/10', 'Sexta',    577),
    ('10/10', 'Sábado',   117),
    ('11/10', 'Domingo',   95),
]
WEEKEND_IDXS = [5, 6]

# Volume por grupo (substitui o volume mensal: sem comparação com períodos anteriores)
grupos = [
    # (grupo, mensagens, participantes ativos, dia de pico, msgs no pico)
    ('MGD8.1', 858, 89, '05/10', 318),
    ('MGD8.2', 880, 93, '05/10', 327),
    ('MGD8.3', 614, 81, '05/10', 187),
    ('MGD8.4', 979, 54, '05/10', 350),
]

# FIIs
fiis = [
    (1, 'TRXF11', 'TRX Gestora de Recursos', 'Renda Urbana', 23, 'Negativo', GD_RED,
     'Único FII que não acompanhou o rally pós-eleição, virando piada recorrente nos grupos. Relatório mensal '
     'mostrou distribuição de R$0,93 apoiada em reserva acumulada, com guidance mantido entre R$0,90 e R$0,93. '
     'Parte dos alunos aproveitou para comprar perto de R$70.'),
    (2, 'RZTR11', 'Riza Asset', 'Agro / Terras', 13, 'Negativo', GD_RED,
     'Vídeo expôs disputa judicial envolvendo uma fazenda do fundo, ainda em 1ª instância. O receio de precedente '
     'para outros arrendatários levou vários alunos a zerar posição, alguns com prejuízo; outros mantêm aguardando o desfecho.'),
    (3, 'RBRR11', 'Pátria Investimentos', 'Recebíveis', 7, 'Misto', GD_ORA,
     'Ficou para trás no rally, efeito atribuído à arbitragem da incorporação via cotas da Pátria. Alunos notaram '
     'redução nos dividendos do mês e questionam se é reflexo da expectativa de queda de juros.'),
    (4, 'GARE11', 'Guardian Gestora', 'Híbrido', 6, 'Positivo', GD_GREEN,
     'Anunciou a compra de um complexo logístico frigorificado no RS por R$155,9 milhões, com yield-alvo de 13,5%. '
     'Queda pontual de 2,25% na quinta foi lida como ajuste após a alta.'),
    (5, 'LVBI11', 'Pátria - Vbi Asset', 'Logística', 6, 'Positivo', GD_GREEN,
     'Apontado como um dos poucos FIIs ainda descontados. O vídeo do Léo sobre HGLG11/LVBI11 (09/10) abriu o debate: '
     'vender ao atingir o valor patrimonial ou aguardar uma possível incorporação.'),
    (6, 'GGRC11', 'Zagros Capital', 'Logística', 6, 'Misto', GD_ORA,
     'Citado entre os fundos que seguiram "patinando" mesmo com o IFIX em alta. Entrou em compras de rebalanceamento '
     'junto de BTLG11, LVBI11 e XPLG11; alguns alunos o comparam com TRXF11 pela amortização via cotas.'),
]

# Ações
acoes = [
    (1, 'BBAS3', 'Banco do Brasil', 'Financeiro', 59, 'Misto', GD_ORA,
     'Disparou até cerca de 11% na segunda com o rally pós-1º turno e a especulação sobre privatização. Alunos com PM '
     'de R$19 a R$22 realizaram lucro entre R$25 e R$27,15. Na live, Léo avaliou que não fazia sentido BBAS3 naqueles '
     'preços; inadimplência segue como preocupação estrutural.'),
    (2, 'PETR4', 'Petrobras', 'Energia', 51, 'Misto', GD_ORA,
     'Tocou R$60 no pico e fechou perto de R$56. Alunos com PM de R$30 a R$32 acumulam 75% a 90% de valorização e se '
     'dividem entre realizar 25% a 30% da posição (trocando por WRLD11/IVVB11) e manter pela nova descoberta na Foz do '
     'Amazonas e Brent alto.'),
    (3, 'VALE3', 'Vale', 'Mineração', 27, 'Negativo', GD_RED,
     'Na contramão do rally, recuou para R$66 a R$68, pressionada pelo dólar em queda e pelo minério fraco após o '
     'feriado chinês. Vários alunos montam posição em escadinha (de R$68 a R$66,50); outros só entram abaixo de R$65.'),
    (4, 'SAPR4', 'Sanepar', 'Saneamento', 27, 'Positivo', GD_GREEN,
     'Uma das maiores altas da semana, perto de 38% em cinco pregões e próxima de R$9, rumo à máxima histórica. '
     'Quem montou posição entre R$6 e R$6,70 comemora; o consenso é aguardar realização antes de novos aportes.'),
    (5, 'TIMS3', 'TIM', 'Telecom', 23, 'Negativo', GD_RED,
     'Queda puxada pela notícia da entrada da Starlink na telefonia móvel e pela decisão da Anatel sobre banda S. '
     'Parte dos alunos vê disrupção inevitável no longo prazo; outros apontam limites físicos e aproveitaram para '
     'comprar a R$18 ou vender puts.'),
    (6, 'ITUB3/4', 'Itaú Unibanco', 'Financeiro', 20, 'Positivo', GD_GREEN,
     'ITUB3 subiu 8% na segunda e superou o preço-teto de muitos alunos (PM entre R$28 e R$41). A maioria prefere '
     'manter; destaque para aluno que arbitrou a diferença de R$4 entre ITUB3 e ITUB4, gerando caixa com isenção de IR.'),
    (7, 'BRBI11', 'BR Partners', 'Financeiro', 12, 'Positivo', GD_GREEN,
     'Saltou de 14% a 18% na segunda. Vários alunos encerraram posição com lucro; outros mantêm apostando na queda de '
     'juros. Lembrete recorrente: units pagam 15% de IR sobre o lucro, sem a isenção dos R$20 mil.'),
    (8, 'FIQE3', 'Unifique', 'Telecom', 11, 'Misto', GD_ORA,
     'Controladora propôs OPA a R$6,00 por ação para fechar o capital. O papel chegou a R$6,20, acima da oferta, e '
     'alunos venderam entre R$5,98 e R$6,01; outros mantêm à espera de uma eventual contestação do laudo.'),
]

# Renda Fixa
rf_items = [
    ('Tesouro Direto', 'Renda+ 2065, IPCA+', 34,
     'Marcação a mercado foi destaque: taxa do Renda+ 2065 caiu de 6,89% para 6,36% (mínima de 6,18%), com ganhos de '
     '25% a 44%. Debate sobre resgatar considerou o spread de resgate (cerca de 5% no preço) e o IR; a maioria manteve. '
     'Também houve dúvidas sobre transferência de custódia.'),
    ('CDB / LCI / LCA', 'Caixinhas e liquidez diária', 11,
     'CDB pós-fixado de liquidez diária segue como reserva de emergência. Dúvidas sobre caixinhas da EQI e o cashback '
     'de 1% do cartão. Alerta: saldo remunerado do Mercado Livre não tem cobertura do FGC.'),
    ('LFTB11', 'ETF de Tesouro Selic', 9,
     'Usado como "estacionamento" do caixa: alunos alocaram aportes do mês e o resultado das vendas em LFTB11 enquanto '
     'aguardam a acomodação do mercado até o 2º turno.'),
]

# ETFs
etfs = [
    ('IVVB11', 'ETF Internacional', 33,
     'Principal veículo de dolarização com o dólar abaixo de R$5. Compras na segunda, quando o ETF caiu cerca de 4%, '
     'e ordens escalonadas; alunos com PM entre R$362 e R$405 avaliam novas entradas.'),
    ('WRLD11', 'ETF Internacional', 22,
     'Preferido por quem já tem muito S&amp;P 500; houve trocas diretas de PETR4 por WRLD11. Lembretes: cerca de 60% a '
     '68% da carteira ainda é EUA, e a liquidez é muito superior à do MUND11.'),
    ('SPXB11', 'ETF Internacional', 5,
     'Alternativa citada para dolarizar com pouco capital; alguns alunos venderam para concentrar em IVVB11.'),
    ('BIXU39', 'BDR de ETF ex-EUA', 5,
     'ETF global sem EUA, gerido pela BlackRock, usado para reduzir a sobreposição com IVVB11 (proporção 80/20). '
     'GXUS11 e VXUS aparecem na mesma lógica.'),
]

# Temas: (tema, volume, índice de sentimento 0-100 pelo método do Termômetro aplicado às mensagens do tema, análise)
temas = [
    ('Realização de lucros', 301, 68,
     'Tema dominante. O rally levou a vendas parciais de BBAS3, PETR4, BRBI11, ITUB3 e B3SA3, muitas dentro do limite '
     'de isenção de R$20 mil. Também serviu para "limpar a casa": VAMO3, AUAU3, INTB3, KLBN4 e RZTR11 foram encerradas.'),
    ('Lives e conteúdo GD', 170, 70,
     'A live extra de segunda (vender, comprar ou esperar? o que fazer com a marcação a mercado?) foi a referência da '
     'semana. O vídeo de 09/10 com o estudo de FIIs foi muito elogiado. Expectativa pelo consolidador da Ward, em beta.'),
    ('FIIs', 163, 66,
     'O IFIX reagiu a partir de terça com o juro futuro em queda, e muitos alunos viram a carteira de FIIs voltar ao '
     'verde. Contrapontos: RZTR11 (disputa judicial), TRXF11 (sem reação) e HSLG11 (ação de despejo contra a Casas Bahia).'),
    ('Dolarização e ETFs', 151, 52,
     'Dólar abaixo de R$5 abriu uma janela de dolarização: IVVB11, WRLD11, SPXB11, BIXU39 e conversões via Nomad, Wise '
     'e Avenue. Debate técnico sobre sobreposição com os EUA e liquidez de ETFs novos.'),
    ('Corretoras e plataformas', 138, 55,
     'Instabilidade na segunda: EQI, BTG, XP e Ágora fora do ar no pico do pregão, enquanto Nubank, Clear e Rico '
     'funcionavam. Relatos de ordens duplicadas e de venda acima de R$20 mil por erro de plataforma.'),
    ('Valuation e preço-teto', 104, 63,
     '"Quase tudo passou do preço-teto": alunos recalculando PETR4, ITSA4, ABCB4, VULC3 e SAPR4, com diferenças entre '
     'métodos (dividendos vs. fluxo de caixa descontado) e entre premissas próprias e de referência.'),
    ('Eleições e política', 102, 65,
     'O resultado do 1º turno e um Congresso mais à direita foram precificados pelo mercado. Alunos lembram que ainda '
     'há 2º turno em 25/10, que parte do cenário já está no preço e que os fundamentos não mudaram de sexta para segunda.'),
    ('Opções', 84, 52,
     'Calls vendidas em BBAS3, BBDC3, ABCB4 e EZTC3 ficaram dentro do dinheiro, com exercício possível no vencimento de '
     '16/10. Em contrapartida, estruturas em BBAS3, ITSA4 e ITUB4 renderam ganhos expressivos; dúvidas sobre rolagem.'),
]

# Comportamento
comportamento = [
    ('Realização de lucros na euforia', 'Muito Alta', GD_RED,
     'A segunda-feira concentrou vendas parciais de BBAS3 e PETR4 (casos de 30% a 50% da posição), muitas em '
     'escadinha e dentro do limite de isenção de R$20 mil.'),
    ('Dolarização oportunista', 'Alta Ativa', colors.HexColor('#E05020'),
     'Com o dólar a R$4,97, alunos usaram reserva e caixa para IVVB11, WRLD11, VWRA11 e GXUS11. Um aluno passou de '
     '6% a 7% para 13% de exposição internacional na semana.'),
    ('Disciplina contra o FOMO', 'Alta', colors.HexColor('#D4880A'),
     '"Calma, muita calma" e "hoje não é dia de aportar": forte reforço da orientação do Léo de não agir por emoção, '
     'assistir à live antes de operar e lembrar que os fundamentos não mudaram.'),
    ('Limpeza da carteira', 'Alta', colors.HexColor('#D4880A'),
     'Alta usada para sair, no 0x0 ou com pouco prejuízo, de posições que já se queria encerrar: VAMO3, AUAU3, BRBI11, '
     'INTB3, MCRE11, TAEE11 e RZTR11. "Em alta é bom para limpar; em baixa, para aportar."'),
    ('Paradoxo da alta', 'Moderada', GD_BLUE_LT,
     'Insatisfação com o próprio ganho: alunos tristes porque o rally fechou janelas de compra, arrependidos de vender '
     'cedo ou de não ter comprado mais, e reclamando que "não há o que comprar".'),
    ('Tentação da marcação a mercado', 'Moderada', GD_BLUE_LT,
     'Ganhos de 25% a 44% no Renda+ 2065 despertaram vontade de resgatar; a maioria manteve após a live, considerando '
     'o spread de resgate, o IR e a tese de queda de juros independente do resultado eleitoral.'),
]

# Insights
insights = [
    ('O rally pós-1º turno',
     'A segunda-feira (05/10) teve Ibovespa com alta próxima de 8%, dólar caindo quase 5% para R$4,97 e EWZ subindo '
     '13% em Nova York. BBAS3 chegou a +11%, B3SA3 a +20%, BRBI11 a +18% e até os FIIs subiram. O volume foi tamanho '
     'que EQI, BTG e XP ficaram fora do ar. Léo fez uma live extra à noite para orientar a turma sobre como agir na euforia.'),
    ('Realizar ou segurar BBAS3 e PETR4',
     'Os dois ativos mais citados concentraram o maior dilema da semana. Em BBAS3, quem tinha PM de R$19 a R$22 vendeu '
     'entre R$25 e R$27, apoiado na leitura de que o preço não se justificava com a inadimplência atual. Em PETR4, a '
     'valorização de 75% a 90% esbarrou na banda de balanceamento: parte vendeu de 25% a 30% para dolarizar, parte '
     'mantém pela qualidade da empresa.'),
    ('Renda+ 2065: o ganho que tenta',
     'A queda da taxa de 6,89% para 6,36% gerou marcação a mercado de 25% a 44% em poucos meses. O debate foi técnico: '
     'spread de cerca de 5% entre compra e resgate, IR regressivo e a hipótese de a taxa cair abaixo de 5,5%, o que '
     'elevaria o ganho para perto de 80%. A conclusão predominante foi manter, já que a queda de juros tende a ocorrer '
     'em qualquer cenário eleitoral.'),
    ('RZTR11 e o risco jurídico',
     'Um vídeo detalhando a disputa judicial em uma das fazendas do fundo foi a "gota d\'água" para vários alunos, que '
     'zeraram posição, alguns com prejuízo usado para compensar IR futuro. O ponto central não é o caso isolado, e sim '
     'o risco de precedente para outros arrendatários. Houve também quem lembrasse que RZTR11 não é fiagro e que o '
     'processo ainda tem muitos recursos.'),
    ('Telecom sob a sombra da Starlink',
     'TIMS3 e Vivo caíram em plena alta da bolsa após notícias da Starlink na telefonia móvel e da decisão da Anatel '
     'sobre banda S. A turma se dividiu: uns veem perda inevitável de participação a partir de 2030; outros apontam '
     'limites físicos do satélite e um mercado regulado por leilão. Alguns aproveitaram para comprar a R$18 e vender puts.'),
    ('Bolsa sem margem: caixa e dólar',
     'Com SAPR4 subindo perto de 38% na semana e "quase tudo" acima do preço-teto, a percepção dominante foi de falta '
     'de oportunidades na bolsa brasileira. A resposta foi recompor caixa em LFTB11, dolarizar com IVVB11, WRLD11 e '
     'BIXU39, e garimpar exceções como VALE3 (R$66 a R$68), LVBI11 e TRXF11.'),
]

# Sentimento (palavras-chave positivas x negativas nas mensagens da semana)
SENT_SCORE = 65
SENT_POS, SENT_NEG = 530, 281

# ════════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ════════════════════════════════════════════════════════════════════════════════
OUT = '/home/claude/relatorio_MGD8_05-11out2026.pdf'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    topMargin=1.8*cm, bottomMargin=1.3*cm,
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    title='Relatório Semanal MGD8 · 05 a 11/10/2026', author='Geração Dividendos',
)

story = []
SP = lambda n=0.3: Spacer(1, n*cm)

def fmt(n):
    return f'{n:,}'.replace(',', '.')

# ── PAGE 1: CAPA ─────────────────────────────────────────────────────────────
story.append(SP(1.5))
if os.path.exists(LOGO):
    from reportlab.platypus import Image as RLImage
    logo_img = RLImage(LOGO, width=8.56*cm, height=1.994*cm)
    logo_tbl = Table([[logo_img]], colWidths=[BODY_W])
    logo_tbl.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(logo_tbl)
else:
    story.append(P('GERAÇÃO DIVIDENDOS', S('lgf', fontName='Helvetica-Bold', fontSize=22,
                                            textColor=GD_BLUE, alignment=TA_CENTER)))

story.append(SP(0.8))
story.append(BlueLine(color=GD_BLUE, h=3))
story.append(SP(0.18))
story.append(BlueLine(color=GD_GOLD, h=1.5))
story.append(SP(1.0))

story.append(P('Relatório de Inteligência de Mercado',
               S('ri', fontSize=11, textColor=GD_MUTED, alignment=TA_CENTER)))
story.append(SP(0.5))
story.append(P('MGD8', S('mgd', fontName='Helvetica-Bold', fontSize=54, textColor=GD_BLUE, alignment=TA_CENTER, leading=58)))
story.append(SP(0.5))
story.append(P('05 a 11 de outubro de 2026  ·  Grupos MGD8.1 a MGD8.4',
               S('ds', fontSize=11, textColor=GD_MUTED, alignment=TA_CENTER)))
story.append(SP(0.7))

meta = Table([
    [P('PERÍODO', sWhiteBC), P('TURMA', sWhiteBC), P('MENSAGENS', sWhiteBC), P('ELABORADO EM', sWhiteBC)],
    [P('05–11/out/2026', sBoldC), P('MGD8', sBoldC), P(fmt(TOTAL_MSGS), sBoldC), P('out/2026', sBoldC)],
], colWidths=[BODY_W/4]*4)
meta.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), GD_BG),
    ('BACKGROUND', (0,0), (-1,0), GD_BLUE),
    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
    ('GRID',       (0,0), (-1,-1), 0.3, GD_BORDER),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('FONTSIZE',   (0,0), (-1,-1), 9),
]))
story.append(meta)
story.append(SP(0.4))

nav_items = ['FIIs', 'Ações', 'Renda Fixa', 'ETFs', 'Comportamento', 'Insights']
nav_cells = [P(item, S(f'nv{i}', fontName='Helvetica-Bold', fontSize=8.5,
                        textColor=WHITE, alignment=TA_CENTER)) for i, item in enumerate(nav_items)]
nav_tbl = Table([nav_cells], colWidths=[BODY_W/6]*6)
nav_tbl.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), GD_BLUE),
    ('TOPPADDING', (0,0), (-1,-1), 7),
    ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#1A3D6A')),
]))
story.append(nav_tbl)
story.append(SP(0.4))

sumario = [
    [P('#', sWhiteBC), P('Métrica', sWhiteB), P('Valor', sWhiteB), P('Detalhe', sWhiteB)],
    [P('1', sBoldC), P('Ativo mais citado (Ações)', sBold), P('BBAS3', sBold), P('59 menções. Alta de até 11% na segunda e forte realização de lucros.', sNorm)],
    [P('2', sBoldC), P('Ativo mais citado (FIIs)', sBold), P('TRXF11', sBold), P('23 menções. Único FII a não acompanhar o rally da semana.', sNorm)],
    [P('3', sBoldC), P('Ativo mais citado (ETFs)', sBold), P('IVVB11', sBold), P('33 menções. Dolarização com o dólar abaixo de R$5.', sNorm)],
    [P('4', sBoldC), P('Tema principal', sBold), P('Realização de lucros', sBold), P('301 menções. Rally pós-1º turno levou a vendas parciais e limpeza de carteira.', sNorm)],
    [P('5', sBoldC), P('Sentimento geral', sBold), P('65/100', sBold), P('Misto (topo da faixa). Euforia temperada por cautela, RZTR11 e instabilidade das corretoras.', sNorm)],
]
sum_tbl = std_tbl(sumario, [0.8*cm, 4.6*cm, 3.4*cm, BODY_W - 0.8*cm - 4.6*cm - 3.4*cm],
                  extra=[('VALIGN', (0,0), (-1,-1), 'MIDDLE')])
story.append(sum_tbl)
story.append(PageBreak())

# ── PAGE 2: FIIs ─────────────────────────────────────────────────────────────
story.append(SP(0.3))
story.append(sec_header(1, 'Fundos de Investimento Imobiliário | Ranking e Análise'))
story.append(SP(0.2))
story.append(callout(
    'A semana foi dominada pelo rally pós-1º turno das eleições: Ibovespa com alta próxima de 8% na segunda, dólar '
    'abaixo de R$5,00 e corretoras fora do ar pelo volume de ordens. Nos FIIs, o IFIX acompanhou a partir de terça, '
    'com alta de cerca de 3%, mas TRXF11 ficou para trás e RZTR11 virou o principal ponto de tensão após a revelação '
    'de uma disputa judicial em uma de suas fazendas.',
    color=GD_BG, border_color=GD_BLUE_LT
))
story.append(SP(0.15))
story.append(P('Ranking FIIs, Semana 05–11 de outubro de 2026',
               S('sub1', fontName='Helvetica-Bold', fontSize=10, textColor=colors.black)))
story.append(SP(0.2))

sHdr = S('hdr', fontName='Helvetica-Bold', fontSize=7.5, textColor=WHITE)
sHdrC = S('hdrc', fontName='Helvetica-Bold', fontSize=7.5, textColor=WHITE, alignment=TA_CENTER)
fii_header = [P(h, sHdrC if h == 'Menções' else sHdr) for h in ['#', 'Ticker', 'Gestora', 'Setor', 'Menções', 'Sentimento', 'Contexto da Semana']]
fii_rows = [fii_header]
for rank, ticker, gestora, setor, mencoes, sent_lbl, sent_col, ctx in fiis:
    fii_rows.append([
        P(str(rank), sBoldC), P(ticker, sBold), P(gestora, sNorm), P(setor, sSmall),
        P(str(mencoes), S('mc', fontName='Helvetica-Bold', alignment=TA_CENTER)),
        sentiment_badge(sent_lbl, sent_col),
        P(ctx, S('ctx', fontSize=8, leading=12)),
    ])
fii_tbl = std_tbl(fii_rows, [0.7*cm, 1.9*cm, 2.5*cm, 2.1*cm, 1.6*cm,
                              2.2*cm, BODY_W - (0.7+1.9+2.5+2.1+1.6+2.2)*cm],
                 extra=[('ALIGN', (4,0), (4,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-2,-1), 'MIDDLE'),
                        ('VALIGN', (-1,0), (-1,-1), 'TOP')])
story.append(fii_tbl)
story.append(SP(0.35))
story.append(callout(
    'Destaque da semana: RZTR11 concentrou as decisões de venda entre os FIIs, com alunos priorizando a segurança '
    'jurídica sobre a rentabilidade. TRXF11 segue pressionado, mas o relatório mensal manteve o guidance de '
    'distribuição. No radar de compras, LVBI11, BTLG11 (fim da emissão com desconto) e GARE11, que anunciou nova '
    'aquisição logística com yield-alvo de 13,5%.',
    color=GD_BG, border_color=GD_GOLD
))
story.append(PageBreak())

# ── PAGE 3: AÇÕES ────────────────────────────────────────────────────────────
story.append(sec_header(2, 'Ações | Ranking e Análise'))
story.append(SP(0.2))
story.append(P(
    'Semana histórica para a bolsa brasileira, com o mercado precificando o resultado do 1º turno. Bancos e estatais '
    'lideraram a alta e a discussão migrou de "o que comprar" para "quanto realizar". Na contramão, VALE3 recuou com '
    'minério e dólar em queda, e TIMS3 sofreu com as notícias sobre a Starlink.',
    S('intro2', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.25))
ac_header = [P(h, sHdrC if h == 'Menções' else sHdr) for h in ['#', 'Ticker', 'Empresa', 'Setor', 'Menções', 'Sentimento', 'Contexto da Semana']]
ac_rows = [ac_header]
for rank, ticker, empresa, setor, mencoes, sent_lbl, sent_col, ctx in acoes:
    ac_rows.append([
        P(str(rank), sBoldC), P(ticker, sBold), P(empresa, sNorm), P(setor, sSmall),
        P(str(mencoes), S('mca', fontName='Helvetica-Bold', alignment=TA_CENTER)),
        sentiment_badge(sent_lbl, sent_col),
        P(ctx, S('ctxa', fontSize=8, leading=11.5)),
    ])
ac_tbl = std_tbl(ac_rows, [0.7*cm, 1.9*cm, 2.3*cm, 2.0*cm, 1.6*cm, 2.2*cm,
                            BODY_W - (0.7+1.9+2.3+2.0+1.6+2.2)*cm],
                extra=[('ALIGN', (4,0), (4,-1), 'CENTER'),
                       ('VALIGN', (0,0), (-2,-1), 'MIDDLE'),
                       ('VALIGN', (-1,0), (-1,-1), 'TOP'),
                       ('TOPPADDING', (0,1), (-1,-1), 4), ('BOTTOMPADDING', (0,1), (-1,-1), 4)])
story.append(ac_tbl)
story.append(PageBreak())

# ── PAGE 4: RENDA FIXA + ETFs ───────────────────────────────────────────────
story.append(sec_header(3, 'Renda Fixa | Ranking e Análise'))
story.append(SP(0.2))
story.append(callout(
    'Renda Fixa: o Renda+ 2065 roubou a cena com a forte marcação a mercado após a queda dos juros futuros. '
    'A discussão entre resgatar ou manter dominou a categoria, enquanto LFTB11 e CDBs de liquidez diária serviram de '
    'destino para o caixa gerado pelas vendas de ações.',
    color=GD_BG, border_color=GD_BLUE_LT
))
story.append(SP(0.2))
rf_header = [P(h, sWhiteBC if h == 'Menções' else sWhiteB) for h in ['#', 'Instrumento', 'Menções', 'Contexto da Semana']]
rf_rows = [rf_header]
for i, (inst, det, mencoes, ctx) in enumerate(rf_items, 1):
    rf_rows.append([
        P(str(i), sBoldC),
        P(f'<b>{inst}</b><br/><font size="7.5" color="#5A5A5A">{det}</font>', S('rfn', fontSize=8.5, leading=13)),
        P(str(mencoes), S('rfm', fontName='Helvetica-Bold', alignment=TA_CENTER)),
        P(ctx, S('rfc', fontSize=8, leading=12)),
    ])
rf_tbl = std_tbl(rf_rows, [0.8*cm, 3.6*cm, 2.0*cm, BODY_W - (0.8+3.6+2.0)*cm],
                extra=[('ALIGN', (2,0), (2,-1), 'CENTER'), ('VALIGN', (0,0), (2,-1), 'MIDDLE')])
story.append(rf_tbl)
story.append(SP(0.35))

story.append(sec_header(4, 'ETFs | Ranking e Análise', 'Fundos de Índice Nacionais e Internacionais'))
story.append(SP(0.2))
story.append(callout(
    'ETFs internacionais dominaram a categoria. Com o dólar abaixo de R$5,00 pela primeira vez em muito tempo, IVVB11 '
    'liderou como principal instrumento de dolarização, seguido por WRLD11. Ganhou força o debate sobre reduzir a '
    'concentração em EUA com ETFs globais ex-EUA.',
    color=GD_BG, border_color=GD_BLUE_LT
))
story.append(SP(0.15))
etf_header = [P(h, sWhiteBC if h == 'Menções' else sWhiteB) for h in ['#', 'Ativo', 'Categoria', 'Menções', 'Contexto da Semana']]
etf_rows = [etf_header]
for i, (ticker, cat, mencoes, ctx) in enumerate(etfs, 1):
    etf_rows.append([
        P(str(i), sBoldC), P(ticker, sBold), P(cat, sNorm),
        P(str(mencoes), S('etfm', fontName='Helvetica-Bold', alignment=TA_CENTER)),
        P(ctx, S('etfc', fontSize=8.5, leading=12.5)),
    ])
etf_tbl = std_tbl(etf_rows, [0.8*cm, 1.9*cm, 3.0*cm, 2.0*cm, BODY_W - (0.8+1.9+3.0+2.0)*cm],
                 extra=[('ALIGN', (3,0), (3,-1), 'CENTER'), ('VALIGN', (0,0), (3,-1), 'MIDDLE')])
story.append(etf_tbl)
story.append(PageBreak())

# ── PAGE 5: TEMAS ────────────────────────────────────────────────────────────
story.append(sec_header(5, 'Principais Temas da Semana'))
story.append(SP(0.2))
story.append(P(
    'Os principais temas debatidos nos 4 grupos MGD8 de 05 a 11 de outubro. O volume indica quantas mensagens da semana '
    'tocaram cada tema (uma mensagem pode tocar mais de um). O sentimento usa o mesmo método do Termômetro (seção 08), '
    'aplicado apenas às mensagens de cada tema, na escala de 0 a 100.',
    S('intro4', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.25))
def zona(score):
    if score <= 33: return 'Negativo', GD_RED
    if score <= 66: return 'Misto', GD_ORA
    return 'Positivo', GD_GREEN
tema_header = [P(h, sWhiteBC if h in ('Volume', 'Sentimento') else sWhiteB)
               for h in ['#', 'Tema', 'Volume', 'Sentimento', 'Análise da Semana']]
tema_rows = [tema_header]
for i, (tema, vol, score, analise) in enumerate(temas, 1):
    z_lbl, z_col = zona(score)
    tema_rows.append([
        P(str(i), sBoldC), P(tema, sBold),
        P(fmt(vol), S('tmv', fontName='Helvetica-Bold', alignment=TA_CENTER)),
        sentiment_badge(f'{z_lbl} · {score}', z_col),
        P(analise, S('tma', fontSize=8.5, leading=12.5)),
    ])
tema_tbl = std_tbl(tema_rows, [0.8*cm, 3.4*cm, 1.6*cm, 2.6*cm, BODY_W - (0.8+3.4+1.6+2.6)*cm],
                   extra=[('VALIGN', (0,0), (3,-1), 'MIDDLE')])
story.append(tema_tbl)
story.append(SP(0.15))
story.append(P('Escala: 0–33 Negativo · 34–66 Misto · 67–100 Positivo. O número ao lado do selo é o índice do tema.',
               S('note5', fontSize=7.5, textColor=GD_MUTED)))
story.append(PageBreak())

# ── PAGE 6: COMPORTAMENTO + INSIGHTS I-III ───────────────────────────────────
story.append(sec_header(6, 'Padrões Comportamentais da Semana'))
story.append(SP(0.2))
story.append(P(
    'Análise qualitativa dos padrões de comportamento e psicologia observados nas conversas '
    'dos grupos durante a semana. Cada padrão reflete tendências recorrentes identificadas.',
    S('intro5', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.25))
comp_header = [P(h, sWhiteB) for h in ['Padrão Observado', 'Intensidade', 'Evidência na Semana']]
comp_rows = [comp_header]
for padrao, intens_lbl, intens_col, evid in comportamento:
    comp_rows.append([P(padrao, sBold), intensity_badge(intens_lbl, intens_col),
                      P(evid, S('cpev', fontSize=8.5, leading=12.5))])
comp_tbl = std_tbl(comp_rows, [4.3*cm, 2.6*cm, BODY_W - (4.3+2.6)*cm],
                   extra=[('VALIGN', (0,0), (1,-1), 'MIDDLE')])
story.append(comp_tbl)
story.append(PageBreak())

romans = ['I', 'II', 'III', 'IV', 'V', 'VI']
def insight_block(idx, titulo, texto):
    rh = Table([[
        P(romans[idx], S(f'rn{idx}', fontName='Helvetica-Bold', fontSize=10, textColor=WHITE, alignment=TA_CENTER)),
        P(titulo.upper(), S(f'rt{idx}', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE))
    ]], colWidths=[1.2*cm, BODY_W - 1.2*cm])
    rh.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GD_BLUE),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    body = Table([[P(texto, S(f'rb{idx}', fontSize=9, leading=14, alignment=TA_JUSTIFY))]], colWidths=[BODY_W])
    body.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GD_BG),
        ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 14), ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    return KeepTogether([rh, SP(0.08), body, SP(0.25)])

# ── PAGE 7: INSIGHTS ─────────────────────────────────────────────────────────
story.append(sec_header(7, 'Insights Estratégicos da Semana'))
story.append(SP(0.2))
story.append(P(
    'Leituras estratégicas elaboradas a partir das conversas da semana. Cada insight traduz um movimento de mercado '
    'ou comportamento relevante observado nos grupos MGD8 entre 05 e 11 de outubro de 2026.',
    S('intro6', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.3))
for idx, (titulo, texto) in enumerate(insights):
    story.append(insight_block(idx, titulo, texto))
story.append(PageBreak())

# ── PAGE 8: TERMÔMETRO ───────────────────────────────────────────────────────
story.append(sec_header(8, 'Termômetro de Sentimento MGD | Semana 05/10–11/10/2026'))
story.append(SP(0.25))
story.append(P(
    'Índice de sentimento calculado a partir da análise de palavras-chave positivas e negativas '
    'nas conversas da semana. Escala de 0 a 100: 0–33 Negativo, 34–66 Misto, 67–100 Positivo.',
    S('intro7', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.3))
gauge = GaugeFlowable(SENT_SCORE, width=BODY_W, height=230)
gauge_wrap = Table([[gauge]], colWidths=[BODY_W])
gauge_wrap.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('BACKGROUND', (0,0), (-1,-1), WHITE),
    ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('BOX', (0,0), (-1,-1), 1.5, GD_BORDER),
]))
story.append(gauge_wrap)
story.append(SP(0.25))
tot = SENT_POS + SENT_NEG
metrics_row = Table([[
    P('ÍNDICE DE SENTIMENTO', S('sd0', fontName='Helvetica-Bold', fontSize=7.5, textColor=GD_MUTED)),
    P(f'{SENT_SCORE} / 100', S('sd1', fontName='Helvetica-Bold', fontSize=13, textColor=GD_BLUE, alignment=TA_CENTER)),
    P('ZONA MISTO', S('sd2', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#D4880A'), alignment=TA_CENTER)),
    P(f'Positivas: {SENT_POS} ({round(100*SENT_POS/tot)}%)  ·  Negativas: {SENT_NEG} ({round(100*SENT_NEG/tot)}%)',
      S('sd3', fontSize=7.5, textColor=GD_MUTED, alignment=TA_RIGHT)),
]], colWidths=[4.0*cm, 3.0*cm, 3.5*cm, BODY_W - 10.5*cm])
metrics_row.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BACKGROUND', (0,0), (-1,-1), GD_BG),
    ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 12), ('BOX', (0,0), (-1,-1), 1.5, GD_BORDER),
    ('LINEAFTER', (0,0), (2,0), 0.5, GD_BORDER),
]))
story.append(metrics_row)
story.append(SP(0.3))
story.append(P(
    'A semana de 05 a 11 de outubro combinou euforia e cautela. O rally pós-1º turno trouxe ganhos expressivos em '
    'ações, FIIs e Tesouro, mas foi contrabalançado pela instabilidade das corretoras na segunda, pela tensão em '
    'RZTR11, pela queda de TIMS3 e VALE3 e pela sensação de que a bolsa ficou sem margem para novos aportes. '
    'Score resultante: 65 pontos, no topo da zona Misto, a um passo da faixa Positiva.',
    S('sent_desc', fontSize=9, leading=14, textColor=GD_BLUE, alignment=TA_JUSTIFY)
))
story.append(PageBreak())

# ── PAGE 9: RANKING DIÁRIO ───────────────────────────────────────────────────
story.append(sec_header(9, 'Ranking Diário de Mensagens | Semana 05/10–11/10/2026'))
story.append(SP(0.2))
story.append(P(
    'Distribuição de mensagens por dia ao longo da semana de 05 a 11 de outubro de 2026 nos 4 grupos. '
    'A segunda-feira (05/10) concentrou 35% de todo o volume da semana, refletindo o rally pós-1º turno e a '
    'instabilidade das corretoras. Quinta (08/10) foi o dia útil mais calmo, e o fim de semana teve baixa atividade.',
    S('intro8', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.25))
sorted_days = sorted(ranking_raw, key=lambda x: -x[2])
rd_header = [P(h, sWhiteB) for h in ['#', 'Data', 'Dia da Semana', 'Mensagens']]
rd_rows = [rd_header]
for i, (data, dia, cnt) in enumerate(sorted_days, 1):
    rd_rows.append([P(str(i), sBoldC), P(data, sBold), P(dia, sNorm),
                    P(fmt(cnt), S('rdv', fontName='Helvetica-Bold', alignment=TA_RIGHT))])
story.append(std_tbl(rd_rows, [1.0*cm, 3.0*cm, 5.0*cm, BODY_W - (1.0+3.0+5.0)*cm]))
story.append(SP(0.3))

chart_labels = [f'{d}\n({dia[:3]})' for d, dia, _ in ranking_raw]
chart_vals   = [v for _, _, v in ranking_raw]
chart_avg    = round(sum(chart_vals) / len(chart_vals))
story.append(BarChart(chart_labels, chart_vals, width=BODY_W, height=115,
                      weekend_idxs=WEEKEND_IDXS, avg=chart_avg))
story.append(SP(0.2))

def swatch(col):
    t = Table([['']], colWidths=[0.5*cm], rowHeights=[0.5*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), col),
                           ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0)]))
    return t
leg_tbl = Table([[swatch(GD_BLUE), P('Dias úteis', sSmall), swatch(colors.HexColor('#8AAEC8')),
                  P('Fim de semana', sSmall), P('--- Média diária', S('avg_leg', fontSize=7.5, textColor=GD_GOLD))]],
                colWidths=[0.7*cm, 3.0*cm, 0.7*cm, 3.0*cm, BODY_W - (0.7+3.0+0.7+3.0)*cm])
leg_tbl.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                             ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
story.append(leg_tbl)
story.append(SP(0.2))
story.append(callout(
    f'Média diária: {fmt(chart_avg)} mensagens/dia  ·  Dia mais ativo: 05/10 (Segunda) com 1.182 msgs  ·  '
    'Dia menos ativo: 11/10 (Domingo) com 95 msgs',
    color=GD_BG, border_color=GD_BLUE_LT
))
story.append(PageBreak())

# ── PAGE 10: VOLUME POR GRUPO ────────────────────────────────────────────────
story.append(sec_header(10, 'Volume de Mensagens por Grupo | MGD8'))
story.append(SP(0.2))
story.append(P(
    'Distribuição das 3.331 mensagens da semana entre os 4 grupos da turma MGD8. Todos os grupos tiveram o pico de '
    'atividade na segunda-feira (05/10). O MGD8.4 foi o mais ativo em volume, enquanto o MGD8.2 reuniu o maior número '
    'de participantes ativos.',
    S('intro9', fontSize=9, textColor=GD_MUTED, alignment=TA_JUSTIFY)
))
story.append(SP(0.3))
story.append(MonthlyBarChart([g[0] for g in grupos], [g[1] for g in grupos], width=BODY_W, height=130))
story.append(SP(0.35))
vol_header = [P(h, sWhiteB) for h in ['Grupo', 'Mensagens', '% do Total', 'Participantes Ativos', 'Pico']]
vol_rows = [vol_header]
for g, n, part, dpico, npico in grupos:
    vol_rows.append([
        P(g, sBold),
        P(fmt(n), S('vv', fontName='Helvetica-Bold', alignment=TA_CENTER)),
        P(f'{100*n/TOTAL_MSGS:.1f}%'.replace('.', ','), sCenter),
        P(str(part), sCenter),
        P(f'{dpico} ({fmt(npico)} msgs)', sNorm),
    ])
vol_rows.append([P('Total', sBold), P(fmt(TOTAL_MSGS), S('vvt', fontName='Helvetica-Bold', alignment=TA_CENTER)),
                 P('100%', sBoldC), P('310', sBoldC), P('05/10 (1.182 msgs)', sBold)])
story.append(std_tbl(vol_rows, [3.0*cm, 3.0*cm, 2.6*cm, 3.6*cm, BODY_W - (3.0+3.0+2.6+3.6)*cm],
                     extra=[('BACKGROUND', (0,-1), (-1,-1), GD_BG)]))
story.append(SP(0.15))
story.append(P('Participantes ativos: autores distintos com ao menos uma mensagem no período (o total considera '
               'autores únicos nos 4 grupos).', S('note9', fontSize=7.5, textColor=GD_MUTED)))
story.append(SP(0.4))

story.append(BlueLine(color=GD_BLUE, h=2))
story.append(SP(0.15))
story.append(BlueLine(color=GD_GOLD, h=1.5))
story.append(SP(0.3))
story.append(P(
    'Relatório de Inteligência de Mercado  ·  MGD8  ·  Semana 05 a 11 de outubro de 2026<br/>'
    'Elaborado pela equipe Geração Dividendos com base nas conversas dos 4 grupos MGD8.<br/>'
    'Análise qualitativa e quantitativa das mensagens do período.',
    S('end_note', fontSize=8, textColor=GD_MUTED, alignment=TA_CENTER, leading=14)
))

def first_page_dispatch(canvas, doc):
    canvas.saveState(); _draw_header(canvas, doc, page_num=1); _draw_footer(canvas, doc); canvas.restoreState()

def later_pages_dispatch(canvas, doc):
    canvas.saveState(); _draw_header(canvas, doc); _draw_footer(canvas, doc); canvas.restoreState()

doc.build(story, onFirstPage=first_page_dispatch, onLaterPages=later_pages_dispatch)
print(f'PDF gerado: {OUT}')
