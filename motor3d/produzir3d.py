#!/usr/bin/env python3
"""Produz um episódio do Trono Abissal em 3D (Ren de cápsulas + animações do Mixamo).

Mesmo historia.json e mesmas vozes do kit Viral Sem Aparecer. O kit continua cuidando da linha do tempo
(montar_historia.py) e da trilha; este script troca só a imagem: o desenho 2D vira a cena 3D de episodio.html.

Uso
  python motor3d/produzir3d.py historia.json pasta_vozes saida --kit $KIT
      -> saida_vertical.mp4 (com a trilha e as vozes, sem o anúncio do curso)
  python motor3d/produzir3d.py historia.json pasta_vozes saida --kit $KIT --quadros 2,9,20,fim
      -> só confere quadros (PNG), sem renderizar o vídeo
  python motor3d/produzir3d.py historia.json - saida --audio video_ou_audio.mp4 [--cortar 7]
      -> teste sem gastar voz: usa o áudio de um episódio já publicado e acha o tempo das falas com o Whisper

Precisa: node + playwright (npm i em motor3d/), Chromium (PLAYWRIGHT_BROWSERS_PATH), ffmpeg.
Render: ~1 s por quadro em CPU; com --partes N divide o vídeo em N navegadores.
"""
import argparse, json, os, re, subprocess, sys, unicodedata, difflib, shutil
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))


def falas_de(H):
    out = []
    for ci, c in enumerate(H['cenas']):
        for f in c['falas']:
            out.append(dict(f, cena=ci))
    return out


# ---------- linha do tempo a partir de um áudio pronto (teste sem gastar voz)
def timeline_whisper(H, audio, cortar, pasta):
    import numpy as np
    from faster_whisper import WhisperModel
    wav = os.path.join(pasta, 'audio_teste.wav')
    dur_total = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio], capture_output=True, text=True).stdout)
    D = dur_total - cortar
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', audio, '-t', f'{D:.3f}', '-vn', '-ac', '2', '-ar', '44100', wav], check=True)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    m = WhisperModel(os.environ.get('WHISPER', 'small'), device='cpu', compute_type='int8')
    segs, _ = m.transcribe(a, language='pt', word_timestamps=True)
    WW = [(w.word.strip(), float(w.start), float(w.end)) for s in segs for w in s.words]
    F = falas_de(H)
    script = [(fi, w) for fi, f in enumerate(F) for w in f['txt'].split()]
    sn = [norm(w) for _, w in script]
    wn = [norm(w[0]) for w in WW]
    sm = difflib.SequenceMatcher(a=sn, b=wn, autojunk=False)
    tempo = [None] * len(script)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            tempo[blk.a + k] = WW[blk.b + k][1:]
    # palavras sem par: interpolar entre vizinhas
    for i in range(len(tempo)):
        if tempo[i] is None:
            j0 = next((j for j in range(i - 1, -1, -1) if tempo[j]), None)
            j1 = next((j for j in range(i + 1, len(tempo)) if tempo[j]), None)
            a0 = tempo[j0][1] if j0 is not None else 0.5
            b0 = tempo[j1][0] if j1 is not None else a0 + 0.4
            n = (j1 if j1 is not None else i + 1) - (j0 if j0 is not None else i - 1) - 1
            k = i - (j0 if j0 is not None else i - 1)
            s0 = a0 + (b0 - a0) * (k - 1) / max(1, n)
            tempo[i] = (s0, s0 + (b0 - a0) / max(1, n))
    blocks = []
    for fi, f in enumerate(F):
        idx = [i for i, (q, _) in enumerate(script) if q == fi]
        words = [[script[i][1], round(tempo[i][0], 3), round(tempo[i][1], 3)] for i in idx]
        blocks.append({'start': words[0][1], 'end': words[-1][2], 'words': words, 'quem': f['quem'], 'cena': f['cena']})
    cenas = []
    for ci in range(len(H['cenas'])):
        bs = [b for b in blocks if b['cena'] == ci]
        cenas.append({'start': 0.0 if ci == 0 else round(bs[0]['start'] - 0.2, 3), 'end': None})
    for i in range(len(cenas) - 1):
        cenas[i]['end'] = cenas[i + 1]['start']
    cenas[-1]['end'] = D
    tail = D - blocks[-1]['end'] - 0.3
    # envelope da voz (para a boca) a 30 qps
    hop = 16000 // 30
    a2 = a[:int(D * 16000)]
    n = len(a2) // hop
    rms = np.sqrt(np.mean(a2[:n * hop].reshape(n, hop) ** 2, axis=1))
    env = np.clip((rms - .01) / (np.percentile(rms, 95) - .01 + 1e-6), 0, 1)
    return {'duration': round(D, 3), 'audio': wav, 'blocks': blocks, 'cenas': cenas, 'env': [round(float(v), 3) for v in env],
            'tempo_escolha': round(max(3.0, tail), 3) if H.get('escolha') else 0, 'mix_pronto': True}


# ---------- tempo de cada ação (campo "acao" das falas, mesmo formato de serie/acoes.md)
def montar_falas(H, T):
    F = falas_de(H)
    blocos = T['blocks']
    if len(blocos) != len(F):
        sys.exit(f'linha do tempo com {len(blocos)} falas, roteiro com {len(F)}')
    out = []
    for f, b in zip(F, blocos):
        acs = f.get('acao') or []
        if isinstance(acs, dict):
            acs = [acs]
        lista = []
        for a in acs:
            t = b['start']
            if 'em' in a:
                t = b['start'] + float(a['em'])
            elif a.get('palavra'):
                alvo = norm(a['palavra'])
                w = next((w for w in b['words'] if norm(w[0]).startswith(alvo) or alvo.startswith(norm(w[0]) or '#')), None)
                if w:
                    t = w[1]
            lista.append(dict(a, t=round(t, 3)))
        out.append({k: f[k] for k in ('quem', 'txt', 'cena', 'pose', 'expressao', 'efeito', 'etiqueta') if k in f} | {'bloco': {'start': b['start'], 'end': b['end'], 'words': b['words']}, 'acoes': lista})
    return out


def render(trab, plano_rel, D, saida_mp4, mix, partes, fps=30):
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers'))
    pagina = f'episodio.html?plano={plano_rel}'
    n = max(1, partes)
    cortes = [round(D * i / n * fps) / fps for i in range(n + 1)]
    pedacos = [os.path.join(trab, f'parte{i}.mp4') for i in range(n)]

    def um(i):
        a, b = cortes[i], cortes[i + 1]
        node = subprocess.Popen(['node', 'servidor.js', pagina, '-', f'{a:.4f}', f'{b:.4f}', str(fps)], cwd=AQUI, env=env, stdout=subprocess.PIPE)
        ff = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'mjpeg', '-i', '-',
                             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', pedacos[i]], stdin=node.stdout)
        node.wait()
        if node.returncode or ff.returncode:
            raise SystemExit(f'falhou a parte {i}')
    with ThreadPoolExecutor(n) as ex:
        list(ex.map(um, range(n)))
    lst = os.path.join(trab, 'lista.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in pedacos))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', mix, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', saida_mp4], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('historia'); ap.add_argument('vozes'); ap.add_argument('saida')
    ap.add_argument('--kit', help='pasta scripts do kit Viral Sem Aparecer (a $KIT da rotina)')
    ap.add_argument('--audio', help='teste: áudio/vídeo pronto no lugar das vozes')
    ap.add_argument('--cortar', type=float, default=0, help='teste: segundos a tirar do fim do áudio (anúncio do curso)')
    ap.add_argument('--quadros', help='só conferir quadros: lista de segundos, ex.: 2,9,20,fim')
    ap.add_argument('--partes', type=int, default=max(1, min(4, (os.cpu_count() or 2) // 1)))
    a = ap.parse_args()
    H = json.load(open(a.historia, encoding='utf-8'))
    saida = os.path.abspath(a.saida)
    nome = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.basename(saida))
    trab = os.path.join(AQUI, 'trabalho', nome)
    os.makedirs(trab, exist_ok=True)
    if a.audio:
        cache = os.path.join(trab, 'timeline_whisper.json')
        if os.path.exists(cache) and os.path.exists(os.path.join(trab, 'audio_teste.wav')):
            T = json.load(open(cache, encoding='utf-8'))
        else:
            T = timeline_whisper(H, a.audio, a.cortar, trab)
            json.dump(T, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
        mix = T['audio']
    else:
        if not a.kit:
            sys.exit('informe --kit (a pasta scripts do kit)')
        tl = os.path.join(trab, 'timeline.json')
        subprocess.run([sys.executable, os.path.join(a.kit, 'montar_historia.py'), os.path.abspath(a.historia), os.path.abspath(a.vozes), tl], check=True)
        T = json.load(open(tl, encoding='utf-8'))
        mix = None
    plano = {'historia': H, 'timeline': T, 'falas': montar_falas(H, T)}
    pj = os.path.join(trab, 'plano.json')
    json.dump(plano, open(pj, 'w', encoding='utf-8'), ensure_ascii=False)
    plano_rel = os.path.relpath(pj, AQUI).replace(os.sep, '/')
    D = T['duration']
    print(f'plano: {len(plano["falas"])} falas, {D:.1f} s, {sum(len(f["acoes"]) for f in plano["falas"])} ações')
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers'))
    if a.quadros:
        for s in a.quadros.split(','):
            t = D - 2.0 if s == 'fim' else float(s)
            png = f'{saida}_q{t:05.1f}.png'
            subprocess.run(['node', 'servidor.js', f'episodio.html?plano={plano_rel}', 'still', f'{t:.3f}', png], cwd=AQUI, env=env, check=True)
            print('quadro', png)
        return
    if mix is None:
        # trilha e mixagem iguais às do kit
        sys.path.insert(0, a.kit)
        import trilha as tr
        mus = os.path.join(trab, 'musica.wav')
        tr.salvar(tr.gerar(H.get('clima', 'calmo'), D, tr.eventos_da_timeline(T)), mus)
        mix = os.path.join(trab, 'mix.m4a')
        vol = float(H.get('volume_trilha', 0.7))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', T['audio'], '-i', mus, '-filter_complex',
                        '[0:a]aresample=44100,aformat=channel_layouts=stereo,loudnorm=I=-15:TP=-1.5,apad,asplit=2[v][key];'
                        f'[1:a]aresample=44100,aformat=channel_layouts=stereo,loudnorm=I=-22:TP=-3,volume={vol}[m0];'
                        '[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[m];'
                        f'[v][m]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,atrim=0:{D}[out]',
                        '-map', '[out]', '-c:a', 'aac', '-b:a', '192k', mix], check=True)
    out = saida + '_vertical.mp4'
    render(trab, plano_rel, D, out, mix, a.partes)
    print('pronto:', out, f'({D:.1f} s)')


if __name__ == '__main__':
    main()
