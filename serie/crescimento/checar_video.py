#!/usr/bin/env python3
"""checar_video.py - confere o MP4 antes de postar no Reels, Shorts e TikTok.

Lê o arquivo com ffprobe e aponta: formato (vertical 9:16 ou horizontal 16:9), duração por
plataforma, codec (H.264 + AAC), áudio presente, tamanho do arquivo e taxa de quadros.

Os limites das plataformas mudam: confirme na ajuda da plataforma se algo parecer estranho.

Inspirado no short-video-distribution do Everything Claude Code (Affaan Mustafa, MIT). Ver CREDITOS.md.

Uso
  python checar_video.py video.mp4
"""
import json, subprocess, sys


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    f = sys.argv[1]
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
                          "-of", "json", f], capture_output=True, text=True)
    if out.returncode:
        print("Não consegui ler o vídeo:", out.stderr.strip()); sys.exit(2)
    d = json.loads(out.stdout)
    dur = float(d["format"].get("duration", 0)); mb = int(d["format"].get("size", 0)) / 1e6
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        print("O arquivo não tem vídeo."); sys.exit(2)
    w, h = v["width"], v["height"]
    num, den = (v.get("r_frame_rate", "30/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den or 1)
    vert = h > w; prop = w / h
    print(f"\nVÍDEO  {w}x{h} · {dur:.1f}s · {fps:.0f} fps · {v['codec_name']} · áudio: {au['codec_name'] if au else 'NENHUM'} · {mb:.1f} MB\n")
    av = []
    if vert and abs(prop - 9 / 16) > 0.02:
        av.append("Vertical, mas não é 9:16 (1080x1920). Pode aparecer com faixas ou cortado.")
    if not vert and abs(prop - 16 / 9) > 0.02:
        av.append("Horizontal, mas não é 16:9 (1920x1080).")
    if v["codec_name"] != "h264":
        av.append(f"Codec {v['codec_name']}. O mais seguro é H.264.")
    if not au:
        av.append("Sem áudio. Reels e TikTok mostram menos vídeo sem som.")
    elif au["codec_name"] != "aac":
        av.append(f"Áudio {au['codec_name']}. O mais seguro é AAC.")
    if fps > 60 or fps < 24:
        av.append(f"{fps:.0f} fps. Use entre 24 e 60.")
    plats = []
    if vert:
        plats.append(("Reels", dur <= 180, "até 3 min para entrar como Reel"))
        plats.append(("Shorts", dur <= 180, "até 3 min, vertical ou quadrado"))
        plats.append(("TikTok", dur <= 600, "até 10 min pelo app (o limite da conta pode ser outro)"))
    else:
        plats.append(("YouTube (vídeo normal)", True, "horizontal vai como vídeo longo, não como Shorts"))
        plats.append(("Reels/TikTok", False, "horizontal aparece pequeno com faixas: faça a versão vertical"))
    for nome, ok, nota in plats:
        print(f"  {'OK   ' if ok else 'NÃO  '} {nome:<24} {nota}")
    if dur > 90 and vert:
        print("\n  Obs.: acima de 90 s o Reels costuma reter menos. Para série, 60 a 110 s funciona.")
    print()
    for x in av:
        print("  ARRUMAR  " + x)
    print("\n" + ("PRONTO PARA POSTAR" if not av else "Arrume os itens acima (o kit refaz o vídeo com ffmpeg).") + "\n")


if __name__ == "__main__":
    main()
