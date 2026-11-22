# ====================================================================== Trono Abissal: pacote de AÇÕES
# Extensão do modo historinha do kit Viral Sem Aparecer. Lido no fim do desenho.py (ver serie/preparar_kit.sh).
# Dá ação aos personagens: golpe com arma, feitiço com projétil, faísca, pulo, investida, levar golpe,
# cair, ficar ofegante, aura, impacto com linhas de anime, e objetos na mão (espada, machado, cajado, escudo).
# Como usar no historia.json: ver serie/acoes.md.
import re as _re_acoes

_ACAO_CTX = {}
_ACAO_CHAR = {}          # posições de tela de cada personagem no quadro atual (mão, tronco, cabeça)

# O personagem ganha espaço lateral para braços esticados e armas (antes 760 px, a mão cortava).
MW_, MHX = 1000, 500

# ---------------------------------------------------------------- 1) campos das falas que o kit não passa para os blocos
_FALAS_ACOES = [f for c in CENAS for f in c.get("falas", [])]
if len(_FALAS_ACOES) != len(TBLK):
    raise SystemExit(f"acoes.py: {len(_FALAS_ACOES)} falas e {len(TBLK)} blocos na linha do tempo; não sei casar")
for _f, _b in zip(_FALAS_ACOES, TBLK):
    for _k in ("etiqueta", "acao"):
        if _k in _f and _k not in _b:
            _b[_k] = _f[_k]


def _norm_acao(s):
    return _re_acoes.sub(r"[^\wÀ-ú]", "", s.lower())


def _t_palavra(b, palavra):
    alvo = _norm_acao(palavra)
    for w in b["words"]:
        if _norm_acao(w[0]).startswith(alvo) or (alvo and alvo in _norm_acao(w[0])):
            return w[1]
    return b["start"] + .1


DUR_ACAO = {"golpe": 1.0, "erra": 1.5, "feitico": 1.3, "faisca": 1.4, "pulo": .75, "atingido": .9, "queda": 1.8,
            "investida": .55, "ofegante": 1.8, "impacto": .45}
CAMERA_ACAO = {"golpe", "erra", "feitico", "faisca", "pulo", "atingido", "queda", "investida", "impacto", "ofegante"}
CORES_ACAO = {"roxo": (170, 80, 255), "azul": (70, 170, 255), "dourado": (255, 205, 70), "vermelho": (255, 70, 60),
              "verde": (90, 230, 120), "branco": (240, 245, 255), "gelo": (150, 230, 255)}
T_GOLPE = .43            # momento do acerto no golpe
T_CARGA, T_VOO = .45, .32


def _cor_acao(a, padrao="azul"):
    c = a.get("cor", padrao)
    return CORES_ACAO.get(c, CORES_ACAO[padrao]) if isinstance(c, str) else tuple(c)


ACOES = []
for _b in TBLK:
    _a = _b.get("acao")
    if not _a:
        continue
    for _x in (_a if isinstance(_a, list) else [_a]):
        _t0 = _t_palavra(_b, _x["palavra"]) if _x.get("palavra") else _b["start"] + float(_x.get("em", .1))
        _tp = _x["tipo"]
        _dur = float(_x.get("dur") or DUR_ACAO.get(_tp) or max(.6, _b["end"] - _t0 + .3))
        _id = _x.get("id") or (_b["quem"] if _b["quem"] in _ids else (HIST.get("protagonista") or _ids[0]))
        ACOES.append(dict(_x, t0=_t0, t1=_t0 + _dur, cena=_b["cena"], id=_id))
        # quem leva o golpe ou o feitiço reage sozinho
        if _x.get("alvo") and _tp in ("golpe", "feitico"):
            _th = _t0 + (T_GOLPE if _tp == "golpe" else T_CARGA + T_VOO)
            ACOES.append(dict(tipo=_x.get("reacao", "atingido"), id=_x["alvo"], de=_id, t0=_th, t1=_th + DUR_ACAO[_x.get("reacao", "atingido")],
                              cena=_b["cena"], auto=True))


def _acoes_de(pid, ci, t, pad=0.0):
    return [a for a in ACOES if a["id"] == pid and a["cena"] == ci and a["t0"] - pad <= t <= a["t1"] + pad]


def _golpe_bracos(u):
    """ângulos do braço da frente no golpe (graus: 0 = esticado para fora, positivo = para baixo)."""
    if u < .28:
        k = ease(u / .28)
        return 85 + (-115 - 85) * k, 20 + (-30 - 20) * k
    if u < T_GOLPE:
        k = (u - .28) / (T_GOLPE - .28)
        return -115 + (55 + 115) * k, -30 + 30 * k
    if u < .75:
        return 55.0, 0.0
    k = ease(min(1, (u - .75) / .25))
    return 55 + (85 - 55) * k, 20 * k


def _acao_estado(pc, ci, t, mirror):
    """deslocamento, giro, braços, pose e objeto do personagem neste instante."""
    st = dict(dx=0.0, dy=0.0, rot=0.0, flash=0.0, bracos=None, rapido=False, prop=pc.get("segura"), aura=None,
              pose=None, andando=None, expr=None)
    fr = -1 if mirror else 1
    el = ELENCO.get(pc["id"], {})
    pcs_cena = {p["id"]: p for p in CENAS[ci].get("personagens", [])}
    if el.get("aura"):
        st["aura"] = (CORES_ACAO.get(el["aura"], CORES_ACAO["roxo"]), .8)
    if pc.get("aura"):
        st["aura"] = (CORES_ACAO.get(pc["aura"], CORES_ACAO["roxo"]), .8)
    for a in ACOES:                       # investidas já terminadas: o personagem fica onde chegou
        if a["id"] == pc["id"] and a["cena"] == ci and a["tipo"] == "investida" and t > a["t1"]:
            st["dx"] += fr * float(a.get("dist", .18)) * SW
    for a in _acoes_de(pc["id"], ci, t):
        u = t - a["t0"]
        d = a["t1"] - a["t0"]
        tp = a["tipo"]
        if tp in ("golpe", "erra"):
            st["prop"] = a.get("arma") or st["prop"] or "espada"
            st["rapido"] = True
            a1, a2 = _golpe_bracos(u)
            st["bracos"] = ((95, 20), (a1, a2))
            ida = ease(min(1, max(0, (u - .28) / (T_GOLPE - .28))))
            volta = ease(min(1, max(0, (u - .75) / .25)))
            levanta = 1 - ease(max(0, min(1, (u - (d - .45)) / .45)))      # volta ao normal no fim da ação
            st["dx"] += fr * .07 * SW * (ida - volta if tp == "golpe" else ida * levanta)
            if tp == "erra" and u > T_GOLPE:      # passou do ponto: desequilibra para a frente e cai sentado
                v = min(1, (u - T_GOLPE) / .35)
                st["rot"] += -fr * 24 * ease(v) * levanta
                st["dy"] += SH * .05 * ease(max(0, min(1, (u - .7) / .25))) * levanta
                st["dx"] += fr * .015 * SW * ease(v) * levanta
                st["expr"] = "surpreso"
        elif tp == "feitico":
            st["rapido"] = True
            k = ease(min(1, u / .2))
            st["bracos"] = ((95, 20), (85 + (-12 - 85) * k, 20 + (4 - 20) * k))
            if u > T_CARGA + T_VOO:          # coice do disparo
                st["dx"] -= fr * .015 * SW * (1 - ease(min(1, (u - T_CARGA - T_VOO) / .4)))
        elif tp == "faisca":
            k = ease(min(1, u / .25))
            st["bracos"] = ((95, 20), (85 + (-8 - 85) * k, 20 + (-45 - 20) * k))
            st["rapido"] = True
        elif tp == "pulo":
            v = min(1, u / d)
            st["dy"] -= SH * .13 * math.sin(math.pi * v)
            st["bracos"] = ((-70, -20), (-70, -20))
            st["rapido"] = True
        elif tp == "investida":
            st["pose"] = "correndo"
            st["andando"] = u * 4.0
            st["dx"] += fr * float(a.get("dist", .18)) * SW * ease(min(1, u / d))
        elif tp in ("atingido", "queda"):
            back = -fr                         # cai para trás de quem olha; se veio de alguém, para longe dele
            if a.get("de") in pcs_cena:
                back = 1 if _char_world_base(ci, pc, t)[0] >= _char_world_base(ci, pcs_cena[a["de"]], t)[0] else -1
        if tp == "atingido":
            v = min(1, u / .22)
            st["dx"] += back * .06 * SW * ease(v) * (1 - .4 * ease(max(0, (u - .3) / .5)))
            st["rot"] += -back * 16 * ease(v) * (1 - ease(max(0, (u - .3) / .5)))
            st["flash"] = max(st["flash"], 1 - min(1, u / .16))
            st["pose"] = "medo"
            st["expr"] = "medo"
        elif tp == "queda":
            v = min(1, u / .45)
            levanta = 1 - ease(max(0, min(1, (u - (d - .5)) / .5)))
            st["dx"] += back * .09 * SW * ease(v) * levanta
            st["rot"] += -back * 78 * ease(v) * levanta
            st["flash"] = max(st["flash"], 1 - min(1, u / .14))
            st["pose"] = "bracos_abertos"
            st["expr"] = "medo"
        elif tp == "ofegante":
            st["dy"] += SH * .012 * (1 + math.sin(u * 14)) / 2
            st["rot"] += -fr * 10
            st["pose"] = "cintura"
            st["expr"] = st["expr"] or "triste"
        elif tp == "aura":
            fade = min(1, u / .3, (d - u) / .3)
            st["aura"] = (_cor_acao(a, "roxo"), max(0, fade))
    return st


# ---------------------------------------------------------------- 2) posição: deslocamentos entram no _char_world (a câmera acompanha)
_char_world_base = _char_world


def _char_world(ci, pc, t):
    x, fy, sc, mirror, andando = _char_world_base(ci, pc, t)
    if not ACOES and not pc.get("aura"):
        return x, fy, sc, mirror, andando
    st = _acao_estado(pc, ci, t, mirror)
    if st["andando"] is not None:
        andando = st["andando"]
    return x + st["dx"], fy + st["dy"], sc, mirror, andando


# ---------------------------------------------------------------- 3) câmera: enquadra a ação e treme no impacto
_camera_ritmo_base = _camera_ritmo


def _impactos(ci):
    out = []
    for a in ACOES:
        if a["cena"] != ci:
            continue
        if a["tipo"] in ("golpe",) and a.get("alvo"):
            out.append((a["t0"] + T_GOLPE, 1.0))
        elif a["tipo"] == "erra":
            out.append((a["t0"] + .75, .6))
        elif a["tipo"] == "feitico":
            out.append((a["t0"] + T_CARGA + T_VOO, 1.0))
        elif a["tipo"] in ("queda",):
            out.append((a["t0"] + .45, 1.0))
        elif a["tipo"] in ("impacto",):
            out.append((a["t0"], 1.2))
        elif a["tipo"] == "atingido" and not a.get("auto"):
            out.append((a["t0"], .8))
        elif a["tipo"] == "pulo":
            out.append((a["t1"], .4))
    return out


def _camera_ritmo(ci, t, blk):
    z, cx, cy = _camera_ritmo_base(ci, t, blk)
    ativas = [a for a in ACOES if a["cena"] == ci and a["t0"] - .05 <= t <= a["t1"] and a["tipo"] in CAMERA_ACAO
              and not a.get("auto") and a.get("camera", True)]
    if ativas:
        a = ativas[-1]
        pcs = {p["id"]: p for p in CENAS[ci].get("personagens", [])}
        if a["id"] in pcs:
            x, fy, sc, mirror, _ = _char_world(ci, pcs[a["id"]], t)
            fr = -1 if mirror else 1
            if a["tipo"] == "feitico" or a.get("alvo") in pcs:
                xs = [x]
                if a.get("alvo") in pcs:
                    xs.append(_char_world(ci, pcs[a["alvo"]], t)[0])
                else:
                    xs.append(x + fr * .45 * SW)
                cx, cy, z = sum(xs) / len(xs), fy - 800 * sc, max(1.0, min(1.35, .82 * SW / max(1, abs(xs[0] - xs[-1]) + .3 * SW)))
            elif a["tipo"] == "faisca":
                u = t - a["t0"]
                z = 1.6 + .7 * ease(min(1, u / .5))
                cx, cy = x + fr * 260 * sc, fy - 1050 * sc
            elif a["tipo"] == "impacto":
                pass
            else:
                z = 1.42
                cx, cy = x + fr * 120 * sc, fy - 820 * sc
            hw, hh = SW / (2 * z), SH / (2 * z)
            cx = min(max(cx, hw), SW - hw)
            cy = min(max(cy, hh), SH - hh)
    for ti, forca in _impactos(ci):
        if ti <= t <= ti + .4:
            amp = 30 * forca * (1 - (t - ti) / .4)
            cx += amp * math.sin(t * 93)
            cy += amp * math.cos(t * 71)
    return z, cx, cy


# ---------------------------------------------------------------- 4) corpo: braços comandados pela ação + registro das mãos
def _injeta(src, velho, novo, nome):
    if velho not in src:
        raise SystemExit(f"acoes.py: o kit mudou e não achei o trecho '{nome}'. Avise para atualizar serie/acoes.py.")
    return src.replace(velho, novo, 1)


def _extrai_def(src, nome, fim):
    i = src.index(f"def {nome}(")
    j = src.index(fim, i) if fim else len(src)
    return src[i:j]


_src_corpo = open(os.path.join(_HERE, "corpo.py"), encoding="utf-8").read()
_src_corpo = _extrai_def(_src_corpo, "corpo_layer", None)
_src_corpo = _injeta(_src_corpo, '    (la, le), (ra, re_) = poses.get(pose, poses["parado"])\n',
                     '    (la, le), (ra, re_) = poses.get(pose, poses["parado"])\n'
                     '    if _ACAO_CTX.get("bracos"):\n        (la, le), (ra, re_) = _ACAO_CTX["bracos"]\n', "poses")
_src_corpo = _injeta(_src_corpo, '* .3 for a0, b0 in zip(st["a"], tgt)]', '* (1.0 if _ACAO_CTX.get("rapido") else .3) for a0, b0 in zip(st["a"], tgt)]', "suavizacao")
_src_corpo = _injeta(_src_corpo, '        E(hand[0], hand[1], aw * .62, aw * .66, SK, ow=4)\n',
                     '        E(hand[0], hand[1], aw * .62, aw * .66, SK, ow=4)\n'
                     '        _ACAO_CTX.setdefault("mao", {})[sx] = (shp, elb, hand, aw)\n', "maos")
exec(_src_corpo)


# ---------------------------------------------------------------- 5) desenho do quadro: ganchos antes e depois de cada personagem
def _acao_pre(pc, ci, t, mirror):
    _ACAO_CTX.clear()
    st = _acao_estado(pc, ci, t, mirror)
    _ACAO_CTX.update(st)
    _ACAO_CTX["mirror"] = mirror
    return st


def _acao_pos(lay2, s_scr, foot_m):
    st = _ACAO_CTX
    _ACAO_CTX["pad"] = (0, 0)
    if st.get("flash", 0) > .01:                       # pisca branco ao levar golpe
        a_ = lay2.getchannel("A")
        br = Image.new("RGBA", lay2.size, (255, 255, 255, 255))
        lay2 = Image.blend(lay2, br, .75 * st["flash"])
        lay2.putalpha(a_)
    if st.get("aura") and st["aura"][1] > .02:          # aura colorida em volta do corpo
        col, forca = st["aura"]
        a_ = lay2.getchannel("A")
        k = max(3, int(30 * s_scr) | 1)
        sm = a_.resize((max(1, lay2.width // 4), max(1, lay2.height // 4)), Image.BILINEAR)
        sm = sm.filter(ImageFilter.MaxFilter(max(3, (k // 4) | 1))).filter(ImageFilter.GaussianBlur(max(2, k / 6)))
        pul = .75 + .25 * math.sin(_ACAO_CTX.get("t", 0) * 9)
        sm = sm.resize(lay2.size, Image.BILINEAR).point(lambda v: int(v * forca * pul))
        au = Image.new("RGBA", lay2.size, col + (0,))
        au.putalpha(sm)
        au.alpha_composite(lay2)
        lay2 = au
    rot = st.get("rot", 0)
    if abs(rot) > .5:
        w, h = lay2.size
        pw, ph = h, h // 3
        big = Image.new("RGBA", (w + 2 * pw, h + ph), (0, 0, 0, 0))
        big.paste(lay2, (pw, ph))
        piv = (pw + w / 2, ph + foot_m * s_scr)
        lay2 = big.rotate(rot, resample=Image.BICUBIC, center=piv)
        _ACAO_CTX["pad"] = (pw, ph)
    return lay2


def _rot_pt(p, piv, ang):
    if abs(ang) < .5:
        return p
    r = math.radians(ang)
    dx, dy = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + dx * math.cos(r) + dy * math.sin(r), piv[1] - dx * math.sin(r) + dy * math.cos(r))


def _glow(img, x, y, r, col, forca=1.0):
    if r < 1 or forca <= 0:
        return
    R = int(r * 2.2) + 4
    p = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.ellipse([R - r * 1.6, R - r * 1.6, R + r * 1.6, R + r * 1.6], fill=col + (int(110 * forca),))
    p = p.filter(ImageFilter.GaussianBlur(max(1, r * .45)))
    d = ImageDraw.Draw(p)
    d.ellipse([R - r * .75, R - r * .75, R + r * .75, R + r * .75], fill=col + (int(255 * forca),))
    d.ellipse([R - r * .38, R - r * .38, R + r * .38, R + r * .38], fill=(255, 255, 255, int(255 * forca)))
    img.alpha_composite(p, (int(x - R), int(y - R))) if x - R >= 0 and y - R >= 0 else img.paste(p, (int(x - R), int(y - R)), p)


def _estrela(d, x, y, r, col, pontas=8, giro=0.0, interno=.38):
    pts = []
    for i in range(pontas * 2):
        rr = r if i % 2 == 0 else r * interno
        a = giro + i * math.pi / pontas
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=col)


def _particulas(img, x, y, n, raio, col, t, seed, tam=8, sobe=0.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = random.Random(seed)
    for i in range(n):
        ang = r.random() * 2 * math.pi
        dist = raio * (.3 + .7 * r.random())
        s = tam * (.5 + r.random())
        px, py = x + dist * math.cos(ang), y + dist * math.sin(ang) - sobe * r.random()
        d.ellipse([px - s, py - s, px + s, py + s], fill=col + (int(230 * (.5 + .5 * r.random())),))
    img.alpha_composite(lay)


def _prop(img, nome, elb, mao, s, cor_mao, aw):
    """desenha o objeto na mão (coordenadas de tela). Direção = antebraço (cotovelo -> mão)."""
    ux, uy = mao[0] - elb[0], mao[1] - elb[1]
    n_ = math.hypot(ux, uy) or 1
    ux, uy = ux / n_, uy / n_
    nx, ny = -uy, ux
    P_ = lambda k, m=0: (mao[0] + ux * k * s + nx * m * s, mao[1] + uy * k * s + ny * m * s)
    d = ImageDraw.Draw(img)
    O = (25, 22, 34)
    lw = lambda v: max(2, int(v * s))
    if nome == "espada":
        d.line([P_(-45), P_(40)], fill=O, width=lw(30))
        d.line([P_(-45), P_(40)], fill=(110, 70, 40), width=lw(20))
        lam = [P_(45, -17), P_(330, -15), P_(385, 0), P_(330, 15), P_(45, 17)]
        d.polygon(lam, fill=(214, 220, 232), outline=O, width=lw(6))
        d.line([P_(55, 0), P_(345, 0)], fill=(250, 252, 255), width=lw(5))
        d.line([P_(40, -62), P_(40, 62)], fill=O, width=lw(26))
        d.line([P_(40, -58), P_(40, 58)], fill=(225, 180, 60), width=lw(16))
        d.ellipse([P_(-52)[0] - 13 * s, P_(-52)[1] - 13 * s, P_(-52)[0] + 13 * s, P_(-52)[1] + 13 * s], fill=(225, 180, 60), outline=O, width=lw(4))
    elif nome == "machado":
        d.line([P_(-70), P_(270)], fill=O, width=lw(28))
        d.line([P_(-70), P_(270)], fill=(120, 80, 45), width=lw(18))
        cab = [P_(190, 8), P_(165, 95), P_(250, 120), P_(285, 8)]
        d.polygon(cab, fill=(200, 205, 215), outline=O, width=lw(6))
    elif nome == "cajado":
        d.line([P_(-260), P_(300)], fill=O, width=lw(26))
        d.line([P_(-260), P_(300)], fill=(125, 85, 50), width=lw(16))
        _glow(img, *P_(330), 30 * s, (150, 110, 255))
        d = ImageDraw.Draw(img)
    elif nome == "tocha":
        d.line([P_(-60), P_(150)], fill=O, width=lw(26))
        d.line([P_(-60), P_(150)], fill=(120, 80, 45), width=lw(16))
        _glow(img, *P_(190), 36 * s * (1 + .12 * math.sin(_ACAO_CTX.get("t", 0) * 20)), (255, 150, 40))
        d = ImageDraw.Draw(img)
    # a mão por cima do cabo
    r = aw * .62 * s
    d.ellipse([mao[0] - r - 4 * s, mao[1] - r - 4 * s, mao[0] + r + 4 * s, mao[1] + r + 4 * s], fill=O)
    d.ellipse([mao[0] - r, mao[1] - r, mao[0] + r, mao[1] + r], fill=cor_mao)


def _escudo(img, mao, s):
    d = ImageDraw.Draw(img)
    O = (25, 22, 34)
    r = 105 * s
    d.ellipse([mao[0] - r - 6 * s, mao[1] - r - 6 * s, mao[0] + r + 6 * s, mao[1] + r + 6 * s], fill=O)
    d.ellipse([mao[0] - r, mao[1] - r, mao[0] + r, mao[1] + r], fill=(150, 40, 50))
    d.ellipse([mao[0] - r * .72, mao[1] - r * .72, mao[0] + r * .72, mao[1] + r * .72], outline=(225, 180, 60), width=max(2, int(10 * s)))
    d.ellipse([mao[0] - r * .2, mao[1] - r * .2, mao[0] + r * .2, mao[1] + r * .2], fill=(200, 205, 215), outline=O, width=max(2, int(4 * s)))


def _acao_pos_char(img, pc, ci, t, px, py, s_scr, mirror, w_lay, foot_m):
    """depois de colar o personagem: objeto na mão, rastro do golpe e posições para os efeitos."""
    pad = _ACAO_CTX.get("pad", (0, 0))
    w2 = int(MW_ * s_scr)
    X0, Y0 = px + pad[0], py + pad[1]          # canto do personagem sem a margem do giro
    piv = (X0 + w2 / 2, Y0 + foot_m * s_scr)
    rot = _ACAO_CTX.get("rot", 0)

    def tela(m):
        x = m[0] * s_scr
        if mirror:
            x = w2 - x
        return _rot_pt((X0 + x, Y0 + m[1] * s_scr), piv, rot)

    maos = _ACAO_CTX.get("mao", {})
    info = {"tronco": tela((MHX, 760)), "cabeca": tela((MHX, MHY)), "pes": piv, "s": s_scr, "mirror": mirror}
    if 1 in maos:
        shp, elb, hand, aw = maos[1]
        info.update(mao=tela(hand), cot=tela(elb), omb=tela(shp), aw=aw)
    if -1 in maos:
        info["mao_tras"] = tela(maos[-1][2])
    _ACAO_CHAR[pc["id"]] = info
    if "mao" not in info:
        return
    # rastro do golpe (calculado pelos ângulos de instantes anteriores)
    for a in _acoes_de(pc["id"], ci, t):
        if a["tipo"] in ("golpe", "erra"):
            u = t - a["t0"]
            if .28 <= u <= T_GOLPE + .14:
                fr = -1 if mirror else 1
                up = 170 * s_scr
                fo = up * .9
                om = info["omb"]
                ext, inn = [], []
                for k in range(10):
                    uu = max(.28, min(u, T_GOLPE)) - (min(u, T_GOLPE) - max(.28, u - .14)) * k / 9
                    a1, a2 = _golpe_bracos(uu)
                    r1, r2 = math.radians(a1), math.radians(a1 + a2)
                    hx_ = om[0] + fr * (up * math.cos(r1) + fo * math.cos(r2))
                    hy_ = om[1] + up * math.sin(r1) + fo * math.sin(r2)
                    ext.append((hx_ + fr * 380 * s_scr * math.cos(r2), hy_ + 380 * s_scr * math.sin(r2)))
                    inn.append((hx_ + fr * 90 * s_scr * math.cos(r2), hy_ + 90 * s_scr * math.sin(r2)))
                alfa = int(200 * (1 - max(0, u - T_GOLPE) / .14))
                lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(lay).polygon(ext + inn[::-1], fill=(255, 255, 255, alfa))
                lay = lay.filter(ImageFilter.GaussianBlur(3))
                img.alpha_composite(lay)
    prop = _ACAO_CTX.get("prop")
    if prop == "escudo" and "mao_tras" in info:
        _escudo(img, info["mao_tras"], s_scr)
    elif prop:
        _prop(img, prop, info["cot"], info["mao"], s_scr, SK, info["aw"])


def _linhas_foco(img, cx, cy, t, forca, seed):
    """linhas de velocidade de anime convergindo para o centro."""
    lay = Image.new("RGBA", (SW // 2, SH // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = random.Random(seed + int(t * 30))
    R = math.hypot(SW, SH) / 2
    c = (cx / 2, cy / 2)
    for i in range(70):
        a = r.random() * 2 * math.pi
        r0 = R * (.42 + .3 * r.random())
        w = .012 + .02 * r.random()
        p1 = (c[0] + R * math.cos(a - w), c[1] + R * math.sin(a - w))
        p2 = (c[0] + R * math.cos(a + w), c[1] + R * math.sin(a + w))
        p0 = (c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a))
        d.polygon([p1, p2, p0], fill=(255, 255, 255, int(200 * forca)))
    img.alpha_composite(lay.resize((SW, SH), Image.BILINEAR))


def _flash_tela(img, forca, col=(255, 255, 255)):
    if forca > .01:
        img.alpha_composite(Image.new("RGBA", img.size, col + (int(200 * min(1, forca)),)))


def _acao_efeitos(img, ci, t):
    """efeitos de tela: carga e voo do feitiço, faíscas, impactos, poeira, suor, linhas de anime, flash."""
    flash = 0.0
    for a in ACOES:
        if a["cena"] != ci or not (a["t0"] - .05 <= t <= a["t1"] + .5):
            continue
        u = t - a["t0"]
        ch = _ACAO_CHAR.get(a["id"])
        if not ch:
            continue
        s = ch["s"]
        fr = -1 if ch["mirror"] else 1
        seed = int(a["t0"] * 100)
        tp = a["tipo"]
        if tp == "feitico" and "mao" in ch:
            col = _cor_acao(a, "azul")
            mx, my = ch["mao"][0] + fr * 30 * s, ch["mao"][1]
            alvo = _ACAO_CHAR.get(a.get("alvo"))
            dest = alvo["tronco"] if alvo else (mx + fr * SW * .7, my - 40 * s)
            if u < T_CARGA:
                k = u / T_CARGA
                _glow(img, mx, my, (18 + 52 * ease(k)) * s, col)
                _particulas(img, mx, my, 14, 160 * s * (1 - k) + 30 * s, col, t, seed + int(u * 30), tam=7 * s * 2)
            elif u < T_CARGA + T_VOO:
                k = ease((u - T_CARGA) / T_VOO)
                bx, by = mx + (dest[0] - mx) * k, my + (dest[1] - my) * k
                for j in range(6, 0, -1):
                    kk = max(0, k - j * .05)
                    _glow(img, mx + (dest[0] - mx) * kk, my + (dest[1] - my) * kk, (60 - j * 7) * s, col, .5 - j * .06)
                _glow(img, bx, by, 62 * s, col)
            elif u < T_CARGA + T_VOO + .45:
                k = (u - T_CARGA - T_VOO) / .45
                lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                _estrela(ImageDraw.Draw(lay), dest[0], dest[1], (120 + 260 * ease(k)) * s, col + (int(255 * (1 - k)),), 10, seed)
                _estrela(ImageDraw.Draw(lay), dest[0], dest[1], (70 + 140 * ease(k)) * s, (255, 255, 255, int(255 * (1 - k))), 10, seed + .3)
                img.alpha_composite(lay)
                _particulas(img, dest[0], dest[1], 22, (80 + 420 * ease(k)) * s, col, t, seed, tam=12 * s * 2)
                flash = max(flash, .35 * (1 - k / .3) if k < .3 else 0)
                if k < .5:
                    _linhas_foco(img, dest[0], dest[1], t, 1 - 2 * k, seed)
        elif tp == "faisca" and "mao" in ch:
            col = _cor_acao(a, "dourado")
            mx, my = ch["mao"][0] + fr * 26 * s, ch["mao"][1] - 10 * s
            if .25 < u < a["t1"] - a["t0"]:
                k = u - .25
                pul = 1 + .25 * math.sin(k * 30)
                lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                _estrela(ImageDraw.Draw(lay), mx, my, 34 * s * pul * min(1, k / .15), (255, 240, 170, 255), 4, k * 3, .18)
                img.alpha_composite(lay)
                _glow(img, mx, my, 16 * s * min(1, k / .15), col)
                # anel perfeito: a mana exata
                if k > .2:
                    kk = min(1, (k - .2) / .7)
                    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                    rr = (40 + 220 * ease(kk)) * s
                    ImageDraw.Draw(lay).ellipse([mx - rr, my - rr, mx + rr, my + rr], outline=col + (int(230 * (1 - kk)),), width=max(2, int(7 * s)))
                    img.alpha_composite(lay)
        elif tp in ("golpe", "erra") and "mao" in ch:
            if a.get("alvo") and T_GOLPE <= u <= T_GOLPE + .35:
                k = (u - T_GOLPE) / .35
                alvo = _ACAO_CHAR.get(a["alvo"])
                p = alvo["tronco"] if alvo else (ch["mao"][0] + fr * 300 * s, ch["mao"][1])
                lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                _estrela(ImageDraw.Draw(lay), p[0], p[1], (90 + 220 * ease(k)) * s, (255, 230, 120, int(255 * (1 - k))), 9, seed)
                _estrela(ImageDraw.Draw(lay), p[0], p[1], (50 + 110 * ease(k)) * s, (255, 255, 255, int(255 * (1 - k))), 9, seed + .2)
                img.alpha_composite(lay)
                flash = max(flash, .3 * (1 - k / .25) if k < .25 else 0)
                if k < .6:
                    _linhas_foco(img, p[0], p[1], t, 1 - k / .6, seed)
            if tp == "erra" and .7 <= u <= 1.3:            # poeira ao cair
                k = (u - .7) / .6
                pe = ch["pes"]
                _particulas(img, pe[0], pe[1] - 20 * s, 16, (60 + 260 * k) * s, (190, 180, 165), t, seed + 5, tam=20 * s * 2 * (1 - k * .6))
        elif tp == "queda" and .4 <= u <= 1.1:
            k = (u - .4) / .7
            pe = ch["pes"]
            _particulas(img, pe[0] - fr * 200 * s, pe[1] - 30 * s, 20, (80 + 320 * k) * s, (190, 180, 165), t, seed + 5, tam=24 * s * 2 * (1 - k * .6))
        elif tp == "pulo":
            pe = ch["pes"]
            for t_ev in (0.0, a["t1"] - a["t0"]):
                if t_ev <= u <= t_ev + .45:
                    k = (u - t_ev) / .45
                    chao = pe[1] + SH * .13 * math.sin(math.pi * min(1, u / (a["t1"] - a["t0"])))
                    _particulas(img, pe[0], chao - 10 * s, 12, (40 + 220 * k) * s, (190, 180, 165), t, seed + int(t_ev * 10), tam=16 * s * 2 * (1 - k * .6))
        elif tp == "investida" and u <= a["t1"] - a["t0"] + .2:
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            r = random.Random(seed + int(t * 30))
            tr_ = ch["tronco"]
            for i in range(14):
                yy = tr_[1] + (r.random() - .5) * 900 * s
                x0 = tr_[0] - fr * (200 + 300 * r.random()) * s
                d.line([(x0, yy), (x0 - fr * (300 + 500 * r.random()) * s, yy)], fill=(255, 255, 255, 170), width=max(2, int(8 * s)))
            img.alpha_composite(lay)
        elif tp == "atingido" and u <= .35:
            k = u / .35
            p = ch["tronco"]
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            _estrela(ImageDraw.Draw(lay), p[0], p[1], (60 + 160 * ease(k)) * s, (255, 255, 255, int(230 * (1 - k))), 8, seed + .5)
            img.alpha_composite(lay)
        elif tp == "ofegante":
            cb = ch["cabeca"]
            r = random.Random(seed)
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            for i in range(3):
                ph = ((u * 1.6) + i / 3) % 1
                sx_ = cb[0] + (-1 if i % 2 else 1) * (150 + 60 * ph) * s
                sy_ = cb[1] - 120 * s + 160 * ph * s
                rr = 16 * s * (1.3 - ph * .5)
                d.polygon([(sx_, sy_ - rr * 2.2), (sx_ - rr, sy_), (sx_ + rr, sy_)], fill=(140, 200, 255, int(230 * (1 - ph))))
                d.ellipse([sx_ - rr, sy_ - rr, sx_ + rr, sy_ + rr], fill=(140, 200, 255, int(230 * (1 - ph))))
            img.alpha_composite(lay)
        elif tp == "aura":
            col = _cor_acao(a, "roxo")
            tr_ = ch["tronco"]
            r = random.Random(seed)
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            for i in range(18):
                ph = (u * (.6 + .5 * r.random()) + r.random()) % 1
                xx = tr_[0] + (r.random() - .5) * 520 * s
                yy = tr_[1] + 700 * s - ph * 1500 * s
                rr = (6 + 10 * r.random()) * s * 2
                d.ellipse([xx - rr, yy - rr, xx + rr, yy + rr], fill=col + (int(220 * (1 - ph)),))
            img.alpha_composite(lay)
        elif tp == "impacto" and u <= .45:
            k = u / .45
            p = ch["tronco"]
            _linhas_foco(img, p[0], p[1], t, 1 - k, seed)
            flash = max(flash, .35 * (1 - k / .3) if k < .3 else 0)
    _flash_tela(img, flash)


def _plano_acao(pid, ci, t):
    """quem está agindo vem para a frente (a arma não some atrás de outro personagem)."""
    at = _acoes_de(pid, ci, t)
    if not at:
        return 0
    return 3 if all(a.get("auto") for a in at) else 5


# ---------------------------------------------------------------- 6) reescreve o frame_historia com os ganchos
_src_des = open(os.path.join(_HERE, "desenho.py"), encoding="utf-8").read()
_src_des = _extrai_def(_src_des, "frame_historia", "\n\nframe = frame_historia")
_src_des = _injeta(_src_des, 'pcs = sorted(cena.get("personagens", []), key=lambda p: p.get("plano", 0))',
                   'pcs = sorted(cena.get("personagens", []), key=lambda p: p.get("plano", 0) + _plano_acao(p["id"], ci, t))', "plano")
_src_des = _injeta(_src_des, "    heads = {}\n", "    heads = {}\n    _ACAO_CHAR.clear()\n", "heads")
_src_des = _injeta(_src_des, "        lay2 = corpo_layer(spec, t, pose=pose,",
                   "        _st_ac = _acao_pre(pc, ci, t, mirror)\n"
                   "        _ACAO_CTX['t'] = t\n"
                   "        pose = _st_ac['pose'] or pose\n"
                   "        expr = _st_ac['expr'] or expr\n"
                   "        lay2 = corpo_layer(spec, t, pose=pose,", "corpo_layer")
_src_des = _injeta(_src_des, "        if mirror:\n            lay2 = ImageOps.mirror(lay2)\n",
                   "        if mirror:\n            lay2 = ImageOps.mirror(lay2)\n"
                   "        _w_lay = lay2.width\n", "mirror")
_src_des = _injeta(_src_des, "        px, py = int(sx - MW_ / 2 * s_scr), int(sy - foot_m * s_scr)\n",
                   "        lay2 = _acao_pos(lay2, s_scr, foot_m)\n"
                   "        px, py = int(sx - MW_ / 2 * s_scr) - _ACAO_CTX['pad'][0], int(sy - foot_m * s_scr) - _ACAO_CTX['pad'][1]\n", "px")
_src_des = _injeta(_src_des, "        heads[pc[\"id\"]] = (sx, sy - (foot_m - (MHY - 200)) * s_scr)\n",
                   "        heads[pc[\"id\"]] = (sx, sy - (foot_m - (MHY - 200)) * s_scr)\n"
                   "        _acao_pos_char(img, pc, ci, t, px, py, s_scr, mirror, _w_lay, foot_m)\n", "heads_set")
_src_des = _injeta(_src_des, "    # falas\n", "    _acao_efeitos(img, ci, t)\n    # falas\n", "falas")
exec(_src_des)
frame = frame_historia
