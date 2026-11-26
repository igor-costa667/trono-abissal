#!/usr/bin/env python3
"""pesquisa_viral.py - transforma a coleta de vídeos de referência num "arquivo de ideias" (swipe).

Não ranqueia por visualização bruta. Ranqueia pelo MULTIPLICADOR: visualizações do vídeo divididas
pela mediana daquele perfil. 400 mil num perfil que faz 10 mil é achado (40x); 400 mil num perfil
que faz 300 mil é um dia normal (1,3x). Acima de 3x é sinal; abaixo de 1,5x não ensina nada.

Entrada: arquivo .tsv (separado por TAB) com cabeçalho:
  conta  seguidores  mediana  views  gancho  [duracao]  [cta]
(mediana = o número do meio das visualizações dos últimos 12 vídeos daquele perfil)

Saída: ranking na tela + arquivo de ideias em Markdown (--saida).

Adaptado do swipe.py do Instagram Agent Skill (Jake Schincariol, MIT). Ver CREDITOS.md.

Uso
  python pesquisa_viral.py coleta.tsv --saida ideias.md
"""
import argparse, csv, os, statistics, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nota_gancho import avaliar, formula  # noqa: E402


def num(x):
    x = str(x or "").strip().lower().replace(" ", "")
    mult = 1
    if x.endswith("mil"):
        mult, x = 1000, x[:-3]
    elif x.endswith("k"):
        mult, x = 1000, x[:-1]
    elif x.endswith("mi"):
        mult, x = 1_000_000, x[:-2]
    elif x.endswith("m"):
        mult, x = 1_000_000, x[:-1]
    x = x.replace(".", "").replace(",", ".") if mult == 1 else x.replace(",", ".")
    try:
        return float(x) * mult
    except ValueError:
        return 0.0


def br(n):
    return f"{n:,.0f}".replace(",", ".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("coleta")
    ap.add_argument("--saida", default="ideias.md")
    a = ap.parse_args()
    linhas = list(csv.DictReader(open(a.coleta, encoding="utf-8"), delimiter="\t"))
    rows = []
    for l in linhas:
        med, v = num(l.get("mediana")), num(l.get("views"))
        g = (l.get("gancho") or "").strip()
        if not g or not med:
            continue
        _, nota, _, _ = avaliar(g)
        rows.append(dict(conta=l.get("conta", "?"), seg=num(l.get("seguidores")), med=med, views=v, gancho=g,
                         mult=v / med, nota=nota, form=formula(g), dur=l.get("duracao", ""), cta=l.get("cta", ""),
                         pal=len(g.split())))
    if not rows:
        print("Nenhuma linha válida (precisa de conta, mediana, views e gancho)."); sys.exit(2)
    rows.sort(key=lambda r: -r["mult"])
    k = max(1, len(rows) // 3)
    topo, fundo = rows[:k], rows[-k:]
    contas = len(set(r["conta"] for r in rows))
    out = [f"# Arquivo de ideias · {len(rows)} vídeos · {contas} perfis · base: mediana de cada perfil\n"]
    out.append("## Fora da curva (acima de 3x)\n")
    for r in [r for r in rows if r["mult"] >= 3]:
        out.append(f"- **{r['mult']:.1f}x** · gancho {r['nota']:.0f} · {r['form'] or 'fórmula nova?'} · {r['conta']} · {br(r['views'])} views (mediana {br(r['med'])})  \n  \"{r['gancho']}\"")
    ct, cf = Counter(r["form"] for r in topo if r["form"]), Counter(r["form"] for r in fundo if r["form"])
    out.append("\n## O que aparece mais no terço de cima\n")
    for f, c in ct.most_common(6):
        out.append(f"- {f}: {c}x em cima, {cf.get(f, 0)}x embaixo")
    out.append(f"- tamanho do gancho: {statistics.median(r['pal'] for r in topo):.0f} palavras em cima, "
               f"{statistics.median(r['pal'] for r in fundo):.0f} embaixo")
    out.append(f"- nota média do gancho: {statistics.mean(r['nota'] for r in topo):.0f} em cima, {statistics.mean(r['nota'] for r in fundo):.0f} embaixo")
    sem = [r for r in rows if not r["form"]]
    out.append(f"\n## Sem fórmula conhecida ({len(sem)}) — leia à mão, pode ser uma fórmula nova\n")
    for r in sem:
        out.append(f"- {r['mult']:.1f}x · {r['conta']} · \"{r['gancho']}\"")
    conf = "boa" if len(rows) >= 40 and contas >= 6 else ("média" if len(rows) >= 20 else "baixa (amostra pequena; trate como pista, não como regra)")
    out.append(f"\n## Confiança: {conf}\n")
    out.append("## Todos\n\n| mult | nota | fórmula | conta | gancho |\n|---|---|---|---|---|")
    for r in rows:
        out.append(f"| {r['mult']:.1f}x | {r['nota']:.0f} | {r['form'] or '-'} | {r['conta']} | {r['gancho']} |")
    texto = "\n".join(out) + "\n"
    open(a.saida, "w", encoding="utf-8").write(texto)
    print(texto)
    print(f"Salvo em {a.saida}")


if __name__ == "__main__":
    main()
