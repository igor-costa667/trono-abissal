#!/usr/bin/env python3
"""humanizar.py - tira o "jeito de robô" de um texto (roteiro, legenda, comentário, DM) e dá nota.

1. Limpa sozinho: caracteres invisíveis, travessão (—), aspas curvas, reticências de um caractere
   e as expressões de robô de vicios.json ("é importante ressaltar que", "mergulhar fundo", ...).
2. Aponta (não reescreve) as estruturas de robô: "não é só X, é Y", introdução de vídeo,
   lista com emoji, parede de hashtag, pedido de reflexo. Essas você reescreve à mão.
3. Dá nota em cinco checagens (0 a 100, maior = mais humano):
   VARIAÇÃO (frases de tamanhos diferentes), CONCRETO (números e nomes), VÍCIOS (expressões
   de robô por 100 palavras), MARCAS (invisíveis, travessões, aspas curvas) e FALA (jeito de
   falar: "pra", "tá", "a gente", "você", frases curtas).

Não é detector de IA de ninguém e não promete passar em detector. Mede o que deixa o texto com
cara de máquina, que é o que faz o público rolar o feed.

Adaptado do humanize.py e detect.py do Instagram Agent Skill (Jake Schincariol, MIT). Ver CREDITOS.md.

Uso
  python humanizar.py texto.txt                 # limpa, salva texto_limpo.txt e mostra a nota
  python humanizar.py texto.txt -o saida.txt
  python humanizar.py texto.txt --so-nota       # só dá a nota, sem mexer
  python humanizar.py roteiro.json              # funciona com o roteiro.json do kit (salva roteiro_limpo.json)
"""
import argparse, json, os, re, statistics, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
LEX = json.load(open(os.path.join(AQUI, "vicios.json"), encoding="utf-8"))
FRASE = re.compile(r"[^.!?\n]+[.!?]*")
PAL = re.compile(r"[\wÀ-ÿ']+")
NUM = re.compile(r"\d[\d.,]*%?|r\$", re.I)
PROPRIO = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,}\b", re.M)
FALA = re.compile(r"\b(?:pra|pro|tá|tô|né|cê|vc|a gente|bora|olha|aí|tipo|daí|beleza|cara|mano|gente)\b", re.I)
PESSOA = re.compile(r"\b(?:eu|meu|minha|me|você|vocês|seu|sua|te|a gente|nós|nosso|nossa)\b", re.I)


def casa_caixa(orig, novo):
    if not novo:
        return novo
    if orig.isupper():
        return novo.upper()
    if orig[:1].isupper():
        return novo[:1].upper() + novo[1:]
    return novo


def limpar(txt):
    mud = {"invisíveis": 0, "tipografia": 0, "vícios": []}
    for ch in LEX["invisiveis"]:
        mud["invisíveis"] += txt.count(ch); txt = txt.replace(ch, "")
    for ch in LEX["espacos"]:
        mud["invisíveis"] += txt.count(ch); txt = txt.replace(ch, " ")
    antes = len(txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Cf" or c in "\n")
    mud["invisíveis"] += antes - len(txt)
    for t in LEX["tipografia"]:
        mud["tipografia"] += txt.count(t["de"]); txt = txt.replace(t["de"], t["para"])
    itens = sorted(LEX["frases"] + LEX["palavras"], key=lambda x: -len(x["de"]))
    for it in itens:
        rx = re.compile(r"(?<![\wÀ-ÿ])" + re.escape(it["de"]) + r"(?![\wÀ-ÿ])", re.I)

        def troca(m):
            mud["vícios"].append(m.group(0))
            return casa_caixa(m.group(0), it["para"])
        txt = rx.sub(troca, txt)
    # arruma pontuação que sobrou depois de apagar expressões
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\s+([,.!?;:])", r"\1", txt)
    txt = re.sub(r",\s*,", ",", txt)
    txt = re.sub(r"([.!?])\s*,", r"\1", txt)
    txt = re.sub(r"(^|[.!?]\s+|\n)\s*,\s*", r"\1", txt)
    txt = re.sub(r"\b(E|e|Mas|mas), (?=[a-záéíóúâêôãõç])", r"\1 ", txt)
    txt = re.sub(r"(?m)^[ \t]+", "", txt.strip())
    txt = re.sub(r"(^|[.!?]\s+|\n)([a-záéíóúâêôãõç])", lambda m: m.group(1) + m.group(2).upper(), txt)
    return txt.strip(), mud


def estruturas(txt):
    achou = []
    for e in LEX["estruturas"]:
        for m in re.finditer(e["regex"], txt):
            achou.append((e["nome"], m.group(0).strip()[:60], e["conserto"]))
    return achou


def lim(n):
    return max(0.0, min(100.0, n))


def esc(v, humano, maquina):
    return lim((v - maquina) / (humano - maquina) * 100)


def nota(txt):
    fr = [f.strip() for f in FRASE.findall(txt) if len(f.split()) > 1]
    w = PAL.findall(txt); n = max(len(w), 1)
    r = {}
    lens = [len(f.split()) for f in fr]
    if len(lens) >= 4:
        cv = statistics.pstdev(lens) / statistics.mean(lens)
        r["VARIAÇÃO"] = (esc(cv, 0.70, 0.22), f"variação {cv:.2f} em {len(lens)} frases (ideal 0,55+)")
    else:
        r["VARIAÇÃO"] = (60.0, "texto curto, não dá pra medir")
    hits = len(NUM.findall(txt)) + len(set(PROPRIO.findall(txt)))
    dens = hits * 100 / n
    r["CONCRETO"] = ((esc(dens, 6, 0), f"{hits} números/nomes, {dens:.1f} a cada 100 palavras (ideal 4+)") if n >= 20
                     else (60.0, "texto curto, não dá pra medir"))
    _, m = limpar(txt)
    v = len(m["vícios"]) * 100 / n
    r["VÍCIOS"] = (esc(v, 0, 3), f"{len(m['vícios'])} expressão(ões) de robô" + (f": {', '.join(sorted(set(x.lower() for x in m['vícios']))[:4])}" if m["vícios"] else ""))
    marcas = m["invisíveis"] * 3 + txt.count("—") * 2 + txt.count("“") + txt.count("”") + txt.count("…")
    mk = marcas * 1000 / max(len(txt), 1)
    r["MARCAS"] = (esc(mk, 0, 8), f"{m['invisíveis']} invisível(is), {txt.count('—')} travessão(ões)")
    fala = len(FALA.findall(txt)) + len(PESSOA.findall(txt))
    est = len(estruturas(txt))
    fs = lim(esc(fala * 100 / n, 6, 0) - est * 12)
    r["FALA"] = (fs, f"{fala} marcas de fala/pessoa, {est} estrutura(s) de robô")
    sc = [x[0] for x in r.values()]
    tot = statistics.mean(sc) * 0.6 + min(sc) * 0.4
    ver = "PASSOU" if tot >= 70 and min(sc) >= 55 else ("REVISAR" if tot >= 50 else "ROBÔ")
    return r, tot, ver


def mostrar(titulo, r, tot, ver):
    print(f"\n{titulo}\n" + "=" * 60)
    for k, (s, d) in r.items():
        print(f"  {k:<9} {'#' * round(s / 100 * 20):<20} {s:5.1f}  {d}")
    print("-" * 60 + f"\n  NOTA      {'#' * round(tot / 100 * 20):<20} {tot:5.1f}  {ver}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("-o", "--saida")
    ap.add_argument("--so-nota", action="store_true")
    a = ap.parse_args()
    bruto = open(a.arquivo, encoding="utf-8").read()
    eh_json = a.arquivo.endswith(".json")
    roteiro = json.loads(bruto) if eh_json else None
    txt = "\n\n".join(" ".join(b) if isinstance(b, list) else str(b) for b in roteiro) if eh_json else bruto
    r0, t0, v0 = nota(txt)
    if a.so_nota:
        mostrar("NOTA DO TEXTO", r0, t0, v0)
        for nome, trecho, cons in estruturas(txt):
            print(f"\n  REESCREVER  {nome}: \"{trecho}\"\n              {cons}")
        print(); return
    if eh_json:
        tot = {"invisíveis": 0, "tipografia": 0, "vícios": []}
        novo = []
        for b in roteiro:
            nb = []
            for f in (b if isinstance(b, list) else [b]):
                c, m = limpar(f)
                for k in ("invisíveis", "tipografia"):
                    tot[k] += m[k]
                tot["vícios"] += m["vícios"]
                if c:
                    nb.append(c)
            novo.append(nb)
        mud = tot
        limpo_txt = "\n\n".join(" ".join(b) for b in novo)
        saida = a.saida or a.arquivo[:-5] + "_limpo.json"
        json.dump(novo, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        limpo_txt, mud = limpar(txt)
        saida = a.saida or os.path.splitext(a.arquivo)[0] + "_limpo.txt"
        open(saida, "w", encoding="utf-8").write(limpo_txt + "\n")
    r1, t1, v1 = nota(limpo_txt)
    print(f"\nLIMPEZA  ·  {mud['invisíveis']} invisível(is) · {mud['tipografia']} troca(s) de tipografia · {len(mud['vícios'])} expressão(ões) de robô")
    if mud["vícios"]:
        print("  trocadas: " + ", ".join(sorted(set(x.lower() for x in mud["vícios"]))))
    mostrar("ANTES", r0, t0, v0)
    mostrar("DEPOIS", r1, t1, v1)
    es = estruturas(limpo_txt)
    for nome, trecho, cons in es:
        print(f"\n  REESCREVER À MÃO  {nome}: \"{trecho}\"\n                    {cons}")
    print(f"\nSalvo em {saida}\n")


if __name__ == "__main__":
    main()
