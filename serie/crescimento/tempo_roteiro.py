#!/usr/bin/env python3
"""tempo_roteiro.py - cronometra o roteiro antes de gastar crédito de voz.

Lê o roteiro.json do kit (lista de blocos; cada bloco é uma lista de frases) ou um .txt
(um bloco por parágrafo, frases separadas por ponto). Calcula o tempo falado de cada frase
e de cada bloco e aponta:
  - gancho (bloco 0) passando de 3 segundos
  - frase passando de 4 segundos (frase longa demais para falar de uma vez)
  - 3 blocos seguidos sem nada concreto (número, nome, valor)
  - duração total longe da meta (--meta)
  - final sem pedido (CTA) e sem eco do gancho (o "loop")

Adaptado do beats.py do Instagram Agent Skill (Jake Schincariol, MIT). Ver CREDITOS.md.

Uso
  python tempo_roteiro.py roteiro.json --meta 60
  python tempo_roteiro.py roteiro.txt --meta 30 --ppm 170
"""
import argparse, json, re, sys

PAL = re.compile(r"[\wÀ-ÿ'’-]+")
CONCRETO = re.compile(r"\d|r\$|\b(?:dois|duas|três|tres|quatro|cinco|seis|sete|oito|nove|dez|vinte|trinta|cem|mil|metade|reais)\b"
                      r"|(?<!^)(?<![.!?]\s)\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,}", re.I)
CTA = re.compile(r"\b(?:segue|siga|salva|salve|comenta|comente|compartilha|manda|envia|link na bio|clica|clique|toca|vota|escolhe|parte \d+)\b", re.I)
VAZIAS = set("a o as os um uma de da do das dos e é que em no na nos nas pra para por com se não mas mais eu você ele ela isso esse essa este esta foi era tem ter ser vai já só".split())


def ler(path):
    txt = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        d = json.loads(txt)
        return [[f for f in (b if isinstance(b, list) else [b]) if str(f).strip()] for b in d]
    blocos = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip()]
    return [[s.strip() for s in re.findall(r"[^.!?]+[.!?]*", b) if s.strip()] for b in blocos]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--meta", type=float, default=60, help="duração desejada em segundos")
    ap.add_argument("--ppm", type=float, default=160, help="palavras por minuto da voz (ElevenLabs pt-BR: ~150 a 175)")
    a = ap.parse_args()
    blocos = ler(a.roteiro)
    pps = a.ppm / 60
    t = 0.0; avisos = []; linhas = []; sem_concreto = 0
    for i, b in enumerate(blocos):
        dur_b = 0.0
        for f in b:
            n = len(PAL.findall(f)); d = n / pps + 0.15
            if d > 4.0:
                avisos.append(f"Bloco {i}: frase de {d:.1f}s ({n} palavras). Quebre em duas: \"{f[:50]}...\"")
            dur_b += d
        linhas.append((i, t, dur_b, " ".join(b)))
        if i == 0 and b:
            dg = len(PAL.findall(b[0])) / pps + 0.15
            if dg > 3.2:
                avisos.append(f"Gancho (primeira frase) com {dg:.1f}s. Precisa caber em 3 s: corte palavras.")
        if CONCRETO.search(" ".join(b)):
            sem_concreto = 0
        else:
            sem_concreto += 1
            if sem_concreto == 3:
                avisos.append(f"Blocos {i-2} a {i} sem nada concreto (número, nome, valor). É aí que a pessoa sai.")
        t += dur_b + 0.35
    total = t - 0.35 if blocos else 0
    if abs(total - a.meta) > a.meta * 0.15:
        avisos.append(f"Duração {total:.1f}s, meta {a.meta:.0f}s. {'Corte' if total > a.meta else 'Acrescente'} ~{abs(total - a.meta) * pps:.0f} palavras.")
    ult = " ".join(blocos[-1]) if blocos else ""
    if not CTA.search(ult):
        avisos.append("Último bloco sem pedido (segue, salva, comenta, link na bio, comenta A ou B).")
    p0 = {w.lower() for w in PAL.findall(" ".join(blocos[0])) if w.lower() not in VAZIAS and len(w) > 3} if blocos else set()
    pu = {w.lower() for w in PAL.findall(ult)}
    loop = sorted(p0 & pu)
    print(f"\nTEMPO DO ROTEIRO  ·  {len(blocos)} blocos  ·  {a.ppm:.0f} ppm\n" + "=" * 70)
    for i, ini, d, txt in linhas:
        print(f"  {ini:5.1f}s  +{d:4.1f}s  [{i}] {txt[:52] + ('...' if len(txt) > 52 else '')}")
    print("-" * 70 + f"\n  TOTAL ~{total:.1f}s (meta {a.meta:.0f}s)   loop: {', '.join(loop) if loop else 'nenhuma palavra do gancho volta no final'}")
    if avisos:
        print("\nARRUMAR")
        for x in avisos:
            print("  - " + x)
        print()
        sys.exit(1)
    print("\nLIMPO. Pode gerar a voz.\n")


if __name__ == "__main__":
    main()
