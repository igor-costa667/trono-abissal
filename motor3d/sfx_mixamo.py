import numpy as np, wave, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '/home/claude/kit_trono/scripts')
SR = 44100; D = 13.41
out = np.zeros(int(D * SR) + SR, np.float32)
rng = np.random.default_rng(3)
def add(t, sig, g=1.0):
    i = int(t * SR); n = min(len(sig), len(out) - i); out[i:i + n] += sig[:n] * g
def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def noise(n, suave=1):
    x = rng.normal(0, 1, n).astype(np.float32)
    if suave > 1: x = np.convolve(x, np.ones(suave) / suave, 'same')
    return x
def thud(f0=90, d=0.18, g=1):
    n = int(SR * d * 4); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f0 * t + 30 * (1 - np.exp(-t * 30)))) * env(n, 0.002, d) + 0.3 * noise(n, 20) * env(n, 0.001, d / 3)
    return s * g
def passo():
    n = int(SR * 0.16); x = noise(n, 30) * env(n, 0.002, 0.03) * 0.8; th = thud(70, 0.04, 0.4); m = min(n, len(th)); x[:m] += th[:m]; return x
def whoosh(d=0.25):
    n = int(SR * d); t = np.arange(n) / SR
    x = noise(n, 6); e = np.sin(np.pi * t / d) ** 2
    return x * e * 0.5
def boing(d=0.5):
    n = int(SR * d); t = np.arange(n) / SR
    f = 180 + 60 * np.sin(2 * np.pi * 11 * t) * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.18) * 0.5
def clank():
    n = int(SR * 0.6); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(1250, 9), (1870, 12), (2630, 15), (3400, 20)]) * 0.18
def blip(f=880):
    n = int(SR * 0.12); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * env(n, 0.002, 0.05) * 0.25
# tempos do prototipo_mixamo.html (ver window.MARCAS): golpe 3.08, troco 3.77, chao 4.52, pausa de impacto 0.08
HS = 0.08; T_HIT = 3.08; T_TROCO = 3.77; T_CHAO = 4.52
for k in range(4): add(0.38 + k * 0.533, passo(), 0.5)
add(2.55, passo(), 0.35)
add(T_HIT - 0.16, whoosh(0.2), 0.8)
add(T_HIT, thud(110, 0.2), 1.2); add(T_HIT, noise(int(SR * .4), 3) * env(int(SR * .4), 0.001, 0.08), 0.35)
add(T_TROCO + HS - 0.22, whoosh(0.3), 0.45)
add(T_TROCO + HS, thud(95, 0.22), 1.3); add(T_TROCO + HS, boing(), 0.8)
add(T_TROCO + HS + 0.35, passo(), 0.45); add(T_TROCO + HS + 0.6, passo(), 0.45)
add(T_CHAO + HS, thud(60, 0.25), 1.3); add(T_CHAO + HS, noise(int(SR * .6), 40) * env(int(SR * .6), 0.01, 0.2), 0.5)
add(T_CHAO + HS + 0.12, clank(), 0.6)
for tt in (7.55, 8.05, 8.5, 8.95): add(tt + HS, passo(), 0.4)
add(9.3 + HS, thud(80, 0.12), 0.6)
add(11.2 + HS, whoosh(0.25), 0.5); add(11.45 + HS, clank(), 0.35)
out = out[:int(D * SR)]
out = out / max(1e-6, np.abs(out).max()) * 0.85
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
import trilha as tr
tr.salvar(tr.gerar('epico', D, []), 'musica.wav')
print('ok')
