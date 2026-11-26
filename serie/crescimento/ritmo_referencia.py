#!/usr/bin/env python3
"""ritmo_referencia.py - mede o ritmo de cortes de um vídeo de referência (de um perfil que está
crescendo) para você copiar o RITMO, nunca o vídeo.

Usa a detecção de troca de cena do ffmpeg e mostra: quantos cortes, tempo médio e mediano de cada
plano, cortes por 10 segundos, o tempo até o primeiro corte e a comparação com o ritmo rápido do kit
(troca a cada ~2 s).

Só use vídeos que o aluno baixou ou gravou com permissão para análise. O resultado é um número
de ritmo; nada do vídeo de referência entra no vídeo do aluno.

Inspirado no taste-distillation do Everything Claude Code (Affaan Mustafa, MIT). Ver CREDITOS.md.

Uso
  python ritmo_referencia.py referencia.mp4
  python ritmo_referencia.py referencia.mp4 --sensibilidade 0.25   (mais baixo = acha mais cortes)
"""
import argparse, re, statistics, subprocess, sys


def duracao(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                       capture_output=True, text=True)
    return float(o.stdout.strip() or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--sensibilidade", type=float, default=0.3)
    a = ap.parse_args()
    dur = duracao(a.video)
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.video, "-vf",
                        f"select='gt(scene,{a.sensibilidade})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    cortes = [float(x) for x in re.findall(r"pts_time:([\d.]+)", o.stderr)]
    cortes = [c for i, c in enumerate(cortes) if i == 0 or c - cortes[i - 1] > 0.25]
    marcas = [0.0] + cortes + [dur]
    planos = [b - a_ for a_, b in zip(marcas, marcas[1:]) if b - a_ > 0.05]
    if not planos:
        print("Não achei cortes. Tente --sensibilidade 0.2."); sys.exit(1)
    med, mediana = statistics.mean(planos), statistics.median(planos)
    por10 = len(cortes) / dur * 10 if dur else 0
    print(f"\nRITMO DA REFERÊNCIA  ·  {dur:.1f}s · {len(cortes)} cortes\n" + "=" * 56)
    print(f"  plano médio        {med:4.1f}s")
    print(f"  plano mediano      {mediana:4.1f}s")
    print(f"  cortes a cada 10s  {por10:4.1f}")
    print(f"  primeiro corte em  {cortes[0] if cortes else dur:4.1f}s")
    print(f"  plano mais longo   {max(planos):4.1f}s")
    faixas = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 999)]
    print("\n  distribuição dos planos")
    for lo, hi in faixas:
        n = sum(1 for p in planos if lo <= p < hi)
        rot = f"{lo}-{hi}s" if hi < 999 else f"{lo}s+"
        print(f"    {rot:<6} {'#' * n} {n}")
    print("\n  comparado ao kit (ritmo rápido, ~2 s por plano):")
    if mediana < 1.5:
        print("  A referência corta MAIS rápido que o kit. Para chegar perto: frases do narrador de 3 a 6 palavras.")
    elif mediana > 3:
        print("  A referência é mais calma que o kit. Se o público do nicho gosta assim, use \"ritmo\": \"normal\".")
    else:
        print("  Ritmo parecido com o do kit. Pode manter o padrão.")
    print()


if __name__ == "__main__":
    main()
