#!/usr/bin/env python3
"""Story do episódio (regra do Igor, 26/11/2026): só o começo do episódio, com a etiqueta "EPISÓDIO N · NOVO".
Uso: python serie/story_teaser.py saida_vertical.mp4 N episodios/epNN_story.mp4 [segundos=12]"""
import os, subprocess, sys
src, n, out = sys.argv[1], sys.argv[2], sys.argv[3]
seg = float(sys.argv[4]) if len(sys.argv) > 4 else 12
fonte = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'motor3d', 'fontes', 'Mont-800.ttf').replace('\\', '/').replace(':', '\\:')
vf = (
    f"drawbox=x=(iw-760)/2:y=150:w=760:h=120:color=0xFFD23C@1:t=fill:enable='lt(mod(t,1.2),0.9)+lt(t,1)',"
    f"drawtext=fontfile='{fonte}':text='EPISÓDIO {n} · NOVO':fontsize=66:fontcolor=0x1A1020:x=(w-text_w)/2:y=178:enable='lt(mod(t,1.2),0.9)+lt(t,1)',"
    f"drawbox=x=0:y=ih-330:w=iw:h=150:color=0x0B0A12@0.75:t=fill:enable='gte(t,{seg-4})',"
    f"drawtext=fontfile='{fonte}':text='ASSISTA COMPLETO NO REELS':fontsize=58:fontcolor=white:x=(w-text_w)/2:y=h-300:enable='gte(t,{seg-4})',"
    f"drawtext=fontfile='{fonte}':text='e vote A ou B':fontsize=44:fontcolor=0xFFD23C:x=(w-text_w)/2:y=h-230:enable='gte(t,{seg-4})',"
    f"fade=t=out:st={seg-0.4}:d=0.4"
)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-t', str(seg), '-vf', vf, '-af', f'afade=t=out:st={seg-0.6}:d=0.6',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '25', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], check=True)
print('story:', out)
