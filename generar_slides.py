"""
Generador de carrusel Instagram — Mercado E-learning Argentina
Produce 7 PNGs de 1080x1350 px
"""

from PIL import Image, ImageDraw, ImageFont
import os, textwrap, math

# ── Configuración ────────────────────────────────────────────
W, H = 1080, 1350
OUT = os.path.join(os.path.dirname(__file__), "slides_png")
os.makedirs(OUT, exist_ok=True)

FONT_PATH   = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_BOLD   = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_INDEX  = 0   # Regular
BOLD_INDEX  = 2   # Bold

def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_PATH
    idx  = BOLD_INDEX if bold else FONT_INDEX
    try:
        return ImageFont.truetype(path, size, index=idx)
    except:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)

# ── Helpers ──────────────────────────────────────────────────

def wrap(text, f, max_width, draw):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textlength(test, font=f) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_text_block(draw, text, f, x, y, max_width, fill, align="center", line_spacing=1.35):
    lines = wrap(text, f, max_width, draw)
    total_h = sum(f.size * line_spacing for l in lines)
    cy = y
    for l in lines:
        lw = draw.textlength(l, font=f)
        if align == "center":
            draw.text(((W - lw) / 2, cy), l, font=f, fill=fill)
        elif align == "left":
            draw.text((x, cy), l, font=f, fill=fill)
        cy += f.size * line_spacing
    return cy

def gradient_bg(img, colors):
    """Vertical or radial gradient background."""
    draw = ImageDraw.Draw(img)
    top = tuple(int(c, 16) for c in [colors[0][1:3], colors[0][3:5], colors[0][5:7]])
    bot = tuple(int(c, 16) for c in [colors[1][1:3], colors[1][3:5], colors[1][5:7]])
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return draw

def tag_pill(draw, text, cx, y, fg, bg, f):
    tw = draw.textlength(text, font=f)
    pad_x, pad_y = 32, 14
    rx0 = cx - tw/2 - pad_x
    ry0 = y
    rx1 = cx + tw/2 + pad_x
    ry1 = y + f.size + pad_y * 2
    draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=(ry1-ry0)//2, fill=bg)
    draw.text((cx - tw/2, y + pad_y), text, font=f, fill=fg)
    return ry1

def metric_card(draw, img, val, lbl, x, y, w, h, accent):
    # card bg
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([x, y, x+w, y+h], radius=24,
                          fill=(255,255,255,12), outline=(255,255,255,22), width=1)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"),
              mask=overlay.split()[3])
    draw = ImageDraw.Draw(img)
    fv = font(52, bold=True)
    fl = font(28)
    # value
    vw = draw.textlength(val, font=fv)
    draw.text((x + (w - vw)/2, y + 28), val, font=fv, fill=accent)
    # label wrapped
    llines = wrap(lbl, fl, w - 40, draw)
    ly = y + 28 + fv.size + 12
    for ll in llines:
        lw = draw.textlength(ll, font=fl)
        draw.text((x + (w-lw)/2, ly), ll, font=fl, fill=(180,180,180))
        ly += fl.size * 1.3
    return draw

def divider(draw, x1, x2, y, color=(255,255,255,40)):
    draw.line([(x1, y), (x2, y)], fill=color[:3], width=1)

def row_item(draw, icon, bold_text, rest_text, y, x0=100, max_w=880):
    fi = font(44)
    fb = font(36, bold=True)
    fn = font(36)
    draw.text((x0, y), icon, font=fi, fill=(255,255,255))
    tx = x0 + 70
    bw = draw.textlength(bold_text, font=fb)
    draw.text((tx, y + 4), bold_text, font=fb, fill=(255,255,255))
    draw.text((tx + bw + 8, y + 4), rest_text, font=fn, fill=(180,180,180))
    return y + fi.size * 1.5


# ═══════════════════════════════════════════════════════════════
# SLIDE 1 — GANCHO
# ═══════════════════════════════════════════════════════════════
def slide1():
    img = Image.new("RGB", (W, H))
    draw = gradient_bg(img, ["#0a0a1a", "#0f2044"])

    CX = W // 2
    MARGIN = 100

    # Orb decorativo
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for r in range(220, 0, -1):
        alpha = int(50 * (1 - r/220))
        od.ellipse([W-r-60, -r, W-60+r, r], fill=(14,165,233,alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Eyebrow
    fe = font(28)
    ey = 210
    ew = draw.textlength("INVESTIGACIÓN DE MERCADO · ARGENTINA 2024–2026", font=fe)
    draw.text(((W-ew)/2, ey), "INVESTIGACIÓN DE MERCADO · ARGENTINA 2024–2026",
              font=fe, fill=(14,165,233))

    # Título principal
    ft1 = font(76, bold=True)
    ft2 = font(76, bold=True)

    line1 = "El e-learning corporativo"
    line2 = "en LATAM ya mueve"
    line3 = "más de USD 1.400 M"
    line4 = "¿Tu empresa ya subió al tren?"

    y = 320
    for line, color in [
        (line1, (255,255,255)),
        (line2, (255,255,255)),
        (line3, (14,165,233)),
        (line4, (255,255,255)),
    ]:
        lw = draw.textlength(line, font=ft1)
        draw.text(((W-lw)/2, y), line, font=ft1, fill=color)
        y += ft1.size * 1.18

    # Subtítulo
    y += 30
    fs = font(36)
    sub = "El mercado crece al 17% anual y redefine cómo las organizaciones desarrollan talento en Argentina."
    y = draw_text_block(draw, sub, fs, MARGIN, y, W-MARGIN*2, (180,180,180))

    # Badge
    y += 30
    fb2 = font(32, bold=True)
    badge_text = "CAGR 17,08% proyectado hasta 2033"
    bw = draw.textlength(badge_text, font=fb2)
    bx0 = (W-bw)/2 - 36
    by0 = y
    bx1 = (W+bw)/2 + 36
    by1 = y + 70
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=35,
                            fill=(14,165,233,30), outline=(14,165,233,80), width=2)
    draw.text(((W-bw)/2, by0+16), badge_text, font=fb2, fill=(14,165,233))

    # Número de slide
    fn2 = font(28)
    draw.text((60, H-70), "01 / 07", font=fn2, fill=(80,100,140))

    img.save(f"{OUT}/01-gancho.png")
    print("✓ Slide 1 — Gancho")


# ═══════════════════════════════════════════════════════════════
# SLIDE 2 — MERCADO / NÚMEROS
# ═══════════════════════════════════════════════════════════════
def slide2():
    img = Image.new("RGB", (W, H), (6,11,24))
    draw = ImageDraw.Draw(img)
    CX = W // 2

    fe = font(28)
    ew = draw.textlength("EL TAMAÑO DEL MERCADO", font=fe)
    draw.text(((W-ew)/2, 130), "EL TAMAÑO DEL MERCADO", font=fe, fill=(14,165,233))

    fh = font(62, bold=True)
    title = "Los números que todo líder\nde RR.HH. debería conocer"
    y = 210
    for line in title.split("\n"):
        lw = draw.textlength(line, font=fh)
        draw.text(((W-lw)/2, y), line, font=fh, fill=(255,255,255))
        y += fh.size * 1.2

    # Grid 2x2 de métricas
    cards = [
        ("USD 21.400M", "Mercado LMS\nGlobal 2024",       (14,165,233)),
        ("USD 4.200M",  "E-learning\nLATAM 2024",         (139,92,246)),
        ("52M",         "Usuarios online\nen LATAM",       (14,165,233)),
        ("+60%",        "Ahorro vs.\ncapacitación pres.",  (139,92,246)),
    ]
    gx0, gy0, gap = 80, 560, 24
    cw = (W - gx0*2 - gap) // 2
    ch = 240
    for i, (val, lbl, accent) in enumerate(cards):
        col = i % 2
        row = i // 2
        cx = gx0 + col*(cw+gap)
        cy = gy0 + row*(ch+gap)
        # card
        overlay = Image.new("RGBA", (W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=20,
                              fill=(255,255,255,10), outline=(*accent,40), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        fv = font(58, bold=True)
        fl = font(30)
        vw = draw.textlength(val, font=fv)
        draw.text((cx+(cw-vw)/2, cy+28), val, font=fv, fill=accent)
        ly = cy + 28 + fv.size + 10
        for ll in lbl.split("\n"):
            lw = draw.textlength(ll, font=fl)
            draw.text((cx+(cw-lw)/2, ly), ll, font=fl, fill=(160,160,160))
            ly += fl.size*1.3

    # Nota
    fn2 = font(30)
    note = "El segmento corporativo supera al académico tradicional en toda la región."
    y = gy0 + 2*(ch+gap) + 30
    nw = draw.textlength(note, font=fn2)
    draw.text(((W-nw)/2, y), note, font=fn2, fill=(100,120,150))

    fn3 = font(28)
    draw.text((60, H-70), "02 / 07", font=fn3, fill=(80,100,140))
    img.save(f"{OUT}/02-mercado-numeros.png")
    print("✓ Slide 2 — Mercado")


# ═══════════════════════════════════════════════════════════════
# SLIDE 3 — IA
# ═══════════════════════════════════════════════════════════════
def slide3():
    img = Image.new("RGB", (W, H))
    draw = gradient_bg(img, ["#0a1628", "#0d2137"])
    draw = ImageDraw.Draw(img)
    CX = W//2

    fe = font(28)
    ew = draw.textlength("INTELIGENCIA ARTIFICIAL EN CAPACITACIÓN", font=fe)
    draw.text(((W-ew)/2, 130), "INTELIGENCIA ARTIFICIAL EN CAPACITACIÓN", font=fe, fill=(139,92,246))

    fh = font(60, bold=True)
    lines = ["La IA hace que cada empleado", "aprenda más rápido."]
    y = 218
    for l in lines:
        lw = draw.textlength(l, font=fh)
        draw.text(((W-lw)/2, y), l, font=fh, fill=(255,255,255))
        y += fh.size*1.18

    fs = font(34)
    sub = "En Argentina, el uso de IA en formación corporativa ya tiene resultados comprobados:"
    y = draw_text_block(draw, sub, fs, 100, y+10, W-200, (170,170,190)) + 40

    # 2 stats
    for val, desc, x0 in [
        ("+26%", "Retención del\nconocimiento", 80),
        ("+45%", "Efectividad\ndel programa", W//2+20),
    ]:
        bw, bh = W//2-100, 190
        overlay = Image.new("RGBA",(W,H),(0,0,0,0))
        od=ImageDraw.Draw(overlay)
        od.rounded_rectangle([x0,y,x0+bw,y+bh],radius=20,fill=(139,92,246,20),outline=(139,92,246,60),width=2)
        img=Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
        draw=ImageDraw.Draw(img)
        fv=font(80,bold=True)
        vw=draw.textlength(val,font=fv)
        draw.text((x0+(bw-vw)/2,y+16),val,font=fv,fill=(167,139,250))
        fl=font(30)
        for ll in desc.split("\n"):
            lw=draw.textlength(ll,font=fl)
            draw.text((x0+(bw-lw)/2,y+16+fv.size+6),ll,font=fl,fill=(150,130,210))
            y_tmp=y+16+fv.size+6+fl.size*1.3
        # fix y only for label
        pass

    y += 210
    items = [
        ("Personalización dinámica:", "itinerarios adaptados en tiempo real según el desempeño."),
        ("Tutores IA 24/7:", "asistentes que simulan escenarios reales de ventas o soporte."),
        ("Cursos exprés:", "de documentación interna a módulo formativo en minutos."),
    ]
    for bold, rest in items:
        fb2=font(34,bold=True)
        fr=font(34)
        draw.ellipse([100,y+10,118,y+28],fill=(139,92,246))
        bw=draw.textlength(bold,font=fb2)
        draw.text((132,y),bold,font=fb2,fill=(255,255,255))
        # wrap rest
        rlines=wrap(rest,fr,W-132-bw-90,draw)
        draw.text((132+bw+8,y),rlines[0] if rlines else "",font=fr,fill=(180,180,200))
        y+=fb2.size*1.5

    fn3=font(28)
    draw.text((60,H-70),"03 / 07",font=fn3,fill=(80,100,140))
    img.save(f"{OUT}/03-ia-capacitacion.png")
    print("✓ Slide 3 — IA")


# ═══════════════════════════════════════════════════════════════
# SLIDE 4 — MICROLEARNING
# ═══════════════════════════════════════════════════════════════
def slide4():
    img = Image.new("RGB",(W,H),(3,7,15))
    draw = ImageDraw.Draw(img)

    fe=font(28)
    ew=draw.textlength("MICROLEARNING Y APRENDIZAJE EN EL FLUJO",font=fe)
    draw.text(((W-ew)/2,130),"MICROLEARNING Y APRENDIZAJE EN EL FLUJO",font=fe,fill=(16,185,129))

    fh=font(58,bold=True)
    lines=["La capacitación del futuro","no interrumpe el trabajo.","Se integra en él."]
    y=218
    for l in lines:
        lw=draw.textlength(l,font=fh)
        draw.text(((W-lw)/2,y),l,font=fh,fill=(255,255,255))
        y+=fh.size*1.18

    # Stat grande
    y+=20
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    od=ImageDraw.Draw(overlay)
    od.rounded_rectangle([80,y,W-80,y+200],radius=24,fill=(16,185,129,20),outline=(16,185,129,60),width=2)
    img=Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
    draw=ImageDraw.Draw(img)
    fv=font(100,bold=True)
    vw=draw.textlength("17%",font=fv)
    draw.text(((W-vw)/2,y+20),"17%",font=fv,fill=(16,185,129))
    fl=font(34)
    sub="más eficaz que los métodos de formación tradicionales"
    sw=draw.textlength(sub,font=fl)
    draw.text(((W-sw)/2,y+20+fv.size+6),sub,font=fl,fill=(130,200,160))
    y+=230

    items=[
        ("⚡","Menos de 5 minutos","Cápsulas entregadas en Slack, Teams o WhatsApp — donde ya trabaja el equipo."),
        ("🎮","Gamificación avanzada","El 83% de los empleados aprende más motivado con mecánicas de juego y recompensas."),
        ("📱","Mobile learning","CAGR del 36% global — en Argentina reforzado por la alta penetración de smartphones."),
    ]
    for icon,bold,rest in items:
        fi=font(44)
        fb2=font(36,bold=True)
        fr=font(34)
        draw.text((80,y),icon,font=fi,fill=(255,255,255))
        bw=draw.textlength(bold,font=fb2)
        draw.text((148,y+4),bold,font=fb2,fill=(16,185,129))
        ry=y+fb2.size+4
        rlines=wrap(rest,fr,W-148-80,draw)
        for rl in rlines:
            draw.text((148,ry),rl,font=fr,fill=(160,180,170))
            ry+=fr.size*1.3
        y=ry+18
        divider(draw,80,W-80,y-8,(40,70,50))

    fn3=font(28)
    draw.text((60,H-70),"04 / 07",font=fn3,fill=(80,100,140))
    img.save(f"{OUT}/04-microlearning.png")
    print("✓ Slide 4 — Microlearning")


# ═══════════════════════════════════════════════════════════════
# SLIDE 5 — INCENTIVOS FISCALES
# ═══════════════════════════════════════════════════════════════
def slide5():
    img=Image.new("RGB",(W,H))
    draw=gradient_bg(img,["#0a1a0a","#0d2810"])
    draw=ImageDraw.Draw(img)

    fe=font(28)
    ew=draw.textlength("MARCO REGULATORIO · ARGENTINA",font=fe)
    draw.text(((W-ew)/2,130),"MARCO REGULATORIO · ARGENTINA",font=fe,fill=(251,191,36))

    fh=font(56,bold=True)
    lines=["El Estado paga parte de tu","inversión en capacitación.","¿Ya lo sabías?"]
    y=218
    for l in lines:
        lw=draw.textlength(l,font=fh)
        draw.text(((W-lw)/2,y),l,font=fh,fill=(255,255,255))
        y+=fh.size*1.18

    y+=20
    items=[
        ("-60%","Ley de Economía del Conocimiento","Reducción en Impuesto a las Ganancias para empresas de software educativo registradas."),
        ("0%","Retenciones a exportación","Alícuota cero para servicios digitales y e-learning exportados al exterior."),
        ("30%","Crédito Fiscal para Capacitación","MiPyMEs recuperan hasta el 30% de la masa salarial anual invertida en formación."),
    ]
    for pct,title,desc in items:
        overlay=Image.new("RGBA",(W,H),(0,0,0,0))
        od=ImageDraw.Draw(overlay)
        od.rounded_rectangle([80,y,W-80,y+180],radius=18,fill=(251,191,36,14),outline=(251,191,36,45),width=2)
        img=Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
        draw=ImageDraw.Draw(img)
        fp=font(68,bold=True)
        pw=draw.textlength(pct,font=fp)
        draw.text((110,y+20),pct,font=fp,fill=(251,191,36))
        tx=110+pw+30
        ft2=font(38,bold=True)
        draw.text((tx,y+22),title,font=ft2,fill=(255,255,255))
        fr=font(32)
        rlines=wrap(desc,fr,W-tx-90,draw)
        ry=y+22+ft2.size+6
        for rl in rlines:
            draw.text((tx,ry),rl,font=fr,fill=(160,175,150))
            ry+=fr.size*1.3
        y+=195

    fn2=font(34,bold=True)
    tip="La combinación correcta puede cubrir hasta el 100% de la inversión."
    tw=draw.textlength(tip,font=fn2)
    draw.text(((W-tw)/2,y+10),tip,font=fn2,fill=(251,191,36))

    fn3=font(28)
    draw.text((60,H-70),"05 / 07",font=fn3,fill=(80,100,140))
    img.save(f"{OUT}/05-incentivos-fiscales.png")
    print("✓ Slide 5 — Incentivos Fiscales")


# ═══════════════════════════════════════════════════════════════
# SLIDE 6 — SECTORES
# ═══════════════════════════════════════════════════════════════
def slide6():
    img=Image.new("RGB",(W,H),(8,5,15))
    draw=ImageDraw.Draw(img)

    fe=font(28)
    ew=draw.textlength("SECTORES CON MAYOR INVERSIÓN EN E-LEARNING",font=fe)
    draw.text(((W-ew)/2,130),"SECTORES CON MAYOR INVERSIÓN EN E-LEARNING",font=fe,fill=(244,114,182))

    fh=font(56,bold=True)
    lines=["¿Tu industria ya capacita online?","Estas son las que lideran."]
    y=218
    for l in lines:
        lw=draw.textlength(l,font=fh)
        draw.text(((W-lw)/2,y),l,font=fh,fill=(255,255,255))
        y+=fh.size*1.18

    y+=30
    sectors=[
        ("💻","Software y Tecnología",    (14,165,233),  "Reskilling en IA, Prompt Engineering e inglés para exportar servicios."),
        ("🏦","Fintech y Financiero",      (139,92,246),  "Compliance, ciberseguridad y prevención de lavado de activos."),
        ("🛒","E-commerce y Logística",    (16,185,129),  "Gestión de tiendas online, última milla y publicidad digital."),
        ("⚡","Energías Renovables",       (251,191,36),  "Blended learning para formación técnica en infraestructuras verdes."),
    ]
    for icon,name,color,need in sectors:
        # Card
        overlay=Image.new("RGBA",(W,H),(0,0,0,0))
        od=ImageDraw.Draw(overlay)
        od.rounded_rectangle([80,y,W-80,y+170],radius=14,
                              fill=(255,255,255,6),outline=(255,255,255,15),width=1)
        od.rectangle([80,y,92,y+170],fill=(*color,200))
        img=Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
        draw=ImageDraw.Draw(img)
        fi=font(52)
        draw.text((110,y+22),icon,font=fi,fill=(255,255,255))
        fn2=font(40,bold=True)
        draw.text((190,y+24),name,font=fn2,fill=(255,255,255))
        fr=font(32)
        nlines=wrap(need,fr,W-190-90,draw)
        ny=y+24+fn2.size+6
        for nl in nlines:
            draw.text((190,ny),nl,font=fr,fill=(160,160,175))
            ny+=fr.size*1.3
        y+=182

    fn3=font(28)
    draw.text((60,H-70),"06 / 07",font=fn3,fill=(80,100,140))
    img.save(f"{OUT}/06-sectores.png")
    print("✓ Slide 6 — Sectores")


# ═══════════════════════════════════════════════════════════════
# SLIDE 7 — CTA
# ═══════════════════════════════════════════════════════════════
def slide7():
    img=Image.new("RGB",(W,H))
    draw=gradient_bg(img,["#0a0a1a","#0f1f3d"])
    # orb
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    od=ImageDraw.Draw(overlay)
    for r in range(250,0,-1):
        alpha=int(40*(1-r/250))
        od.ellipse([W-r-40,-r,W-40+r,r],fill=(14,165,233,alpha))
    img=Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")
    draw=ImageDraw.Draw(img)

    fe=font(28)
    ew=draw.textlength("EL MOMENTO DE ACTUAR ES AHORA",font=fe)
    draw.text(((W-ew)/2,180),"EL MOMENTO DE ACTUAR ES AHORA",font=fe,fill=(14,165,233))

    fh=font(64,bold=True)
    lines=["Argentina: hub de","innovación en","educación digital."]
    y=260
    for l in lines:
        lw=draw.textlength(l,font=fh)
        draw.text(((W-lw)/2,y),l,font=fh,fill=(255,255,255))
        y+=fh.size*1.18

    fs=font(36)
    sub="Las empresas que adopten ecosistemas de aprendizaje inteligentes hoy tendrán la ventaja competitiva decisiva en los próximos 5 años."
    y=draw_text_block(draw,sub,fs,100,y+10,W-200,(160,170,190))+40

    # CTA box
    overlay2=Image.new("RGBA",(W,H),(0,0,0,0))
    od2=ImageDraw.Draw(overlay2)
    for xi in range(W-160):
        t=xi/(W-161)
        r=int(14+(37-14)*t)
        g=int(165+(99-165)*t)
        b=int(233+(235-233)*t)
        od2.rectangle([80+xi,y,81+xi,y+220],fill=(r,g,b,240))
    mask=Image.new("L",(W,H),0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle([80,y,W-80,y+220],radius=24,fill=255)
    img.paste(Image.alpha_composite(img.convert("RGBA"),overlay2).convert("RGB"),mask=mask)
    draw=ImageDraw.Draw(img)

    fq=font(44,bold=True)
    q="¿Cuánto invierte tu empresa en capacitación online?"
    qlines=wrap(q,fq,W-200,draw)
    qy=y+26
    for ql in qlines:
        qw=draw.textlength(ql,font=fq)
        draw.text(((W-qw)/2,qy),ql,font=fq,fill=(255,255,255))
        qy+=fq.size*1.2

    fa=font(36)
    act="Cuéntanos en comentarios 👇  Guardá y compartí con tu equipo."
    aw=draw.textlength(act,font=fa)
    draw.text(((W-aw)/2,qy+4),act,font=fa,fill=(200,230,255))

    # Hashtags
    fh2=font(28)
    tags="#elearning  #capacitacioncorporativa  #RRHHargentina  #LMS  #transformaciondigital"
    tw=draw.textlength(tags,font=fh2)
    draw.text(((W-tw)/2,y+240),tags,font=fh2,fill=(70,90,120))

    fn3=font(28)
    draw.text((60,H-70),"07 / 07",font=fn3,fill=(80,100,140))
    img.save(f"{OUT}/07-cta.png")
    print("✓ Slide 7 — CTA")


# ── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generando slides en: {OUT}\n")
    slide1()
    slide2()
    slide3()
    slide4()
    slide5()
    slide6()
    slide7()
    print(f"\n✅ 7 PNGs de 1080×1350 guardados en:\n{OUT}")
