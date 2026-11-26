"""Monta o esqueleto do Ren 3D (modelo do Hunyuan) e calcula os pesos de pele.

Uso: python3 esqueleto_modelo.py modelo.obj vmap.npy saida.json
- modelo.obj em cm (Y para cima, olhando para +Z, pose A), como ren_modelo.obj
- vmap.npy: do pintar_modelo.py (vértice do GLB pintado -> vértice do OBJ)
Saída JSON: juntas (m), pais, e para cada vértice do GLB os 4 ossos e pesos.

Pesos: cada osso "segura" os vértices bem perto dele (sementes) e o resto da malha é
preenchido por difusão sobre a própria malha (pesos harmônicos), então a bolsa da
mochila segue o tronco e não o braço que passa perto, porque está ligada à mochila.
"""
import sys, json
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

# juntas em metros (lado esquerdo do personagem = +X); o lado direito é espelhado
J = {
    'hips': [0, 0.80, 0.04], 'spine': [0, 0.90, 0.04], 'chest': [0, 1.08, 0.03], 'neck': [0, 1.30, 0.02], 'head': [0, 1.38, 0.02],
    'uaL': [0.18, 1.25, 0.02], 'faL': [0.275, 1.075, 0.035], 'handL': [0.37, 0.90, 0.055],
    'thL': [0.095, 0.78, 0.04], 'shL': [0.115, 0.42, 0.04], 'ftL': [0.125, 0.10, 0.03],
}
FIM = {'head': [0, 1.62, 0.0], 'handL': [0.47, 0.73, 0.09], 'ftL': [0.125, 0.03, 0.17]}
for k in list(J):
    if k.endswith('L'): J[k[:-1] + 'R'] = [-J[k][0]] + J[k][1:]
for k in list(FIM):
    if k.endswith('L'): FIM[k[:-1] + 'R'] = [-FIM[k][0]] + FIM[k][1:]
PAI = {'hips': None, 'spine': 'hips', 'chest': 'spine', 'neck': 'chest', 'head': 'neck',
       'uaL': 'chest', 'faL': 'uaL', 'handL': 'faL', 'uaR': 'chest', 'faR': 'uaR', 'handR': 'faR',
       'thL': 'hips', 'shL': 'thL', 'ftL': 'shL', 'thR': 'hips', 'shR': 'thR', 'ftR': 'shR'}
FILHO = {'hips': 'spine', 'spine': 'chest', 'chest': 'neck', 'neck': 'head', 'uaL': 'faL', 'faL': 'handL', 'uaR': 'faR', 'faR': 'handR',
         'thL': 'shL', 'shL': 'ftL', 'thR': 'shR', 'shR': 'ftR'}
OSSOS = list(PAI)
RAIO = {'hips': 0.2, 'spine': 0.2, 'chest': 0.2, 'neck': 0.06, 'head': 0.2, 'ua': 0.07, 'fa': 0.065, 'hand': 0.08, 'th': 0.1, 'sh': 0.085, 'ft': 0.09}


def seg(b):
    a = np.array(J[b]); c = np.array(J[FILHO[b]] if b in FILHO else FIM[b]); return a, c


def dist_seg(P, a, c):
    d = c - a; t = np.clip(((P - a) @ d) / (d @ d), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * d), axis=1)


def main():
    obj, vmap_p, saida = sys.argv[1:4]
    V, F = [], []
    for l in open(obj):
        if l.startswith('v '): V.append([float(x) for x in l.split()[1:4]])
        elif l.startswith('f '): F.append([int(x) - 1 for x in l.split()[1:4]])
    V = np.array(V) / 100.0; F = np.array(F)
    n = len(V)
    D = np.stack([dist_seg(V, *seg(b)) for b in OSSOS], 1)
    # um lado não segura o outro
    for j, b in enumerate(OSSOS):
        if b.endswith('L'): D[V[:, 0] < -0.01, j] = 9
        if b.endswith('R'): D[V[:, 0] > 0.01, j] = 9
    perto = D.argmin(1)
    raio = np.array([RAIO.get(b, RAIO.get(b[:-1], 0.1)) for b in OSSOS])
    semente = D[np.arange(n), perto] < raio[perto]
    alvo = perto.copy()
    # mochila e cobertor (atrás do corpo) ficam presos ao peito; cabelo de trás à cabeça
    costas = (V[:, 2] < -0.075) & (V[:, 1] > 0.72) & (V[:, 1] < 1.42) & (np.abs(V[:, 0]) < 0.4)
    alvo[costas] = OSSOS.index('chest'); semente |= costas
    cabelo = (V[:, 1] > 1.42) & (np.abs(V[:, 0]) < 0.2)
    alvo[cabelo] = OSSOS.index('head'); semente |= cabelo
    # Laplaciano uniforme
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    A = sp.coo_matrix((np.ones(len(E)), (E[:, 0], E[:, 1])), shape=(n, n)).tocsr()
    A = ((A + A.T) > 0).astype(float)
    L = sp.diags(np.asarray(A.sum(1)).ravel()) - A
    livre = np.where(~semente)[0]; fixo = np.where(semente)[0]
    print('sementes', len(fixo), 'livres', len(livre))
    W = np.zeros((n, len(OSSOS)))
    W[fixo, alvo[fixo]] = 1
    if len(livre):
        Lff = L[livre][:, livre].tocsc(); Lfx = L[livre][:, fixo]
        rhs = -(Lfx @ W[fixo])
        sol = spl.splu(Lff + sp.identity(len(livre)) * 1e-8)
        W[livre] = np.column_stack([sol.solve(rhs[:, j]) for j in range(len(OSSOS))])
    # suaviza um pouco as fronteiras das sementes (dobra mais macia em cotovelo e joelho)
    Am = sp.diags(1 / np.asarray(A.sum(1)).ravel()) @ A
    for _ in range(4): W = 0.5 * W + 0.5 * (Am @ W)
    W = np.clip(W, 0, None)
    top = np.argsort(-W, 1)[:, :4]
    tw = np.take_along_axis(W, top, 1); tw /= tw.sum(1, keepdims=True) + 1e-9
    vmap = np.load(vmap_p)
    out = {'ossos': OSSOS, 'pais': [PAI[b] for b in OSSOS], 'juntas': [J[b] for b in OSSOS],
           'indices': top[vmap].astype(int).ravel().tolist(), 'pesos': np.round(tw[vmap], 4).ravel().tolist()}
    json.dump(out, open(saida, 'w'))
    print('ok', len(vmap), 'vértices; ossos por vértice (peso>0.05):', np.round(((tw > 0.05).sum(1)).mean(), 2))


if __name__ == '__main__':
    main()
