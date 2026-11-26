#!/usr/bin/env python3
"""carrossel.py - gera as imagens de um carrossel do Instagram (1080x1350, 4:5) a partir de um JSON.

Entrada (carrossel.json):
{
  "arroba": "@contosemorbita",
  "cor": "#7c3aed",            (cor de destaque; opcional)
  "fundo": "#0f0f14",          (opcional; escuro por padrão)
  "formato": "story",          (opcional; gera 1080x1920 para stories, com o texto longe das bordas)
  "slides": [
    {"titulo": "O REI MORREU", "texto": "E deixou a coroa pra quem menos esperava."},
    {"titulo": "Quem era o rei", "texto": "Nível 100. Protegia a vila há um século."},
    ...
  ]
}
O primeiro slide é a capa (título grande). Os outros levam número (2/8), título e texto.
Texto da capa fica longe das bordas, então o corte da grade não atrapalha.

Uso
  python carrossel.py carrossel.json pasta_saida/
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, "..", "fonts")
W, H, M = 1080, 1350, 120
TOPO, BASE = M, M


def fonte(nome, tam):
    p = os.path.join(FONTES, nome)
    return ImageFont.truetype(p, tam) if os.path.exists(p) else ImageFont.load_default()


def quebra(d, txt, f, larg):
    if "\n" in txt:
        return [l for par in txt.split("\n") for l in (quebra(d, par, f, larg) or [""])]
    linhas, atual = [], ""
    for p in txt.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) <= larg:
            atual = t
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def cabe(d, txt, nome, tam, larg, max_linhas):
    while tam > 30:
        f = fonte(nome, tam)
        ls = quebra(d, txt, f, larg)
        if len(ls) <= max_linhas:
            return f, ls
        tam -= 4
    f = fonte(nome, 30)
    return f, quebra(d, txt, f, larg)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    global H, TOPO, BASE
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    if cfg.get("formato") == "story":
        H, TOPO, BASE = 1920, 260, 340
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    cor, fundo = hexrgb(cfg.get("cor", "#f5c518")), hexrgb(cfg.get("fundo", "#0f0f14"))
    texto_cor = (245, 245, 245) if sum(fundo) < 380 else (20, 20, 20)
    slides = cfg["slides"]; n = len(slides)
    if not 2 <= n <= 20:
        print("Use de 2 a 20 slides (ideal: 6 a 10)."); sys.exit(2)
    larg = W - 2 * M
    for i, s in enumerate(slides, 1):
        im = Image.new("RGB", (W, H), fundo); d = ImageDraw.Draw(im)
        if i == 1:
            f, ls = cabe(d, s.get("titulo", "").upper(), "Mont-700.ttf", 132, larg, 4)
            alt = sum(f.size * 1.08 for _ in ls)
            y = (H - alt) / 2 - 60
            d.rectangle([M, y - 50, M + 120, y - 36], fill=cor)
            for l in ls:
                d.text((M, y), l, font=f, fill=texto_cor); y += f.size * 1.08
            if s.get("texto"):
                f2, l2 = cabe(d, s["texto"], "Mont-600.ttf", 48, larg, 3)
                y += 30
                for l in l2:
                    d.text((M, y), l, font=f2, fill=cor); y += f2.size * 1.25
            if H != 1920:
                d.text((M, H - BASE), "ARRASTA PRO LADO  >>", font=fonte("Mont-600.ttf", 36), fill=texto_cor)
        else:
            d.text((M, TOPO - 20), f"{i}/{n}", font=fonte("Mont-700.ttf", 40), fill=cor)
            f, ls = cabe(d, s.get("titulo", ""), "Mont-700.ttf", 96, larg, 3)
            f2, l2 = cabe(d, s.get("texto", ""), "Mont-600.ttf", 62, larg, 9)
            alt = len(ls) * f.size * 1.1 + 100 + len(l2) * f2.size * 1.3
            y = max(TOPO + 80, (H - alt) / 2 - 20)
            for l in ls:
                d.text((M, y), l, font=f, fill=texto_cor); y += f.size * 1.1
            y += 40
            d.rectangle([M, y, M + 90, y + 10], fill=cor); y += 60
            for l in l2:
                d.text((M, y), l, font=f2, fill=texto_cor); y += f2.size * 1.3
        arroba = cfg.get("arroba", "")
        if arroba:
            fa = fonte("Mont-600.ttf", 32)
            d.text((W - M - d.textlength(arroba, font=fa), H - BASE), arroba, font=fa, fill=texto_cor)
        im.save(os.path.join(out, f"slide_{i:02d}.png"))
    print(f"{n} slides salvos em {out}")


if __name__ == "__main__":
    main()
