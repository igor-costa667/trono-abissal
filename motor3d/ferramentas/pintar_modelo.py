"""Pinta o modelo 3D do Ren projetando as imagens de referência (frente, costas, lado).

Uso: python3 pintar_modelo.py modelo.obj frente.png costas.png lado.png saida_dir [tam_textura]
- modelo.obj: Y para cima, olhando para +Z, pés em y=0 (como o ren_modelo.obj que vai para o Mixamo)
- lado.png: vista do lado esquerdo do personagem (o rosto aponta para a esquerda da imagem)
Saída: saida_dir/ren_pintado.glb (malha com UV e textura) e saida_dir/textura.png.
Cada ponto da superfície pega a cor da vista que o enxerga melhor (normal virada para a câmera
e sem nada na frente, pelo mapa de profundidade de cada vista).
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
import xatlas, trimesh


def ler_obj(p):
    V, F = [], []
    for l in open(p):
        if l.startswith('v '): V.append([float(x) for x in l.split()[1:4]])
        elif l.startswith('f '): F.append([int(x.split('/')[0]) - 1 for x in l.split()[1:4]])
    return np.array(V), np.array(F)


def caixa_personagem(img):
    a = np.asarray(img.convert('RGB')).astype(int)
    m = (a < 238).any(2)
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def mascara_personagem(a, encolhe=3):
    from scipy import ndimage
    branco = (a > 232).all(2)
    rot, _ = ndimage.label(branco)
    borda = set(np.unique(np.concatenate([rot[0], rot[-1], rot[:, 0], rot[:, -1]]))) - {0}
    fundo = np.isin(rot, list(borda))
    return ndimage.binary_erosion(~fundo, iterations=encolhe)


class Vista:
    """Projeção ortográfica de uma imagem de referência sobre o modelo."""
    def __init__(self, img, eixo_dir, eixo_cima, olhar, V, espelhar=False, so_lateral=False):
        self.so_lateral = so_lateral
        self.img = np.asarray(img.convert('RGB')).astype(np.float32)
        if espelhar: self.img = self.img[:, ::-1]
        self.h, self.w = self.img.shape[:2]
        self.mascara = mascara_personagem(self.img)
        self.dir, self.cima, self.olhar = map(np.array, (eixo_dir, eixo_cima, olhar))
        x0, y0, x1, y1 = caixa_personagem(Image.fromarray(self.img.astype(np.uint8)))
        u = V @ self.dir; v = V @ self.cima
        # o modelo foi gerado destas imagens: alinha a caixa do modelo com a caixa do desenho
        self.ku = (x1 - x0) / (u.max() - u.min()); self.u0 = u.min(); self.px0 = x0
        self.kv = (y1 - y0) / (v.max() - v.min()); self.v0 = v.min(); self.py1 = y1

    def pix(self, P):
        x = self.px0 + (P @ self.dir - self.u0) * self.ku
        y = self.py1 - (P @ self.cima - self.v0) * self.kv
        return x, y

    def profundidade(self, V, F, res=1):
        """z-buffer da vista (no espaço da imagem): para saber se o ponto está escondido."""
        H, W = self.h // res, self.w // res
        zb = np.full((H, W), -1e9, np.float32)
        x, y = self.pix(V); x /= res; y /= res
        z = V @ (-self.olhar)          # maior = mais perto da câmera
        for f in F:
            xs, ys, zs = x[f], y[f], z[f]
            xmin, xmax = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            ymin, ymax = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if xmax < xmin or ymax < ymin: continue
            gx, gy = np.meshgrid(np.arange(xmin, xmax + 1) + .5, np.arange(ymin, ymax + 1) + .5)
            d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(d) < 1e-9: continue
            l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
            l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
            l2 = 1 - l0 - l1
            dentro = (l0 >= -1e-3) & (l1 >= -1e-3) & (l2 >= -1e-3)
            zz = l0 * zs[0] + l1 * zs[1] + l2 * zs[2]
            sub = zb[ymin:ymax + 1, xmin:xmax + 1]
            np.maximum(sub, np.where(dentro, zz, -1e9), out=sub)
        self.zb, self.res = zb, res

    def amostra(self, P, N):
        x, y = self.pix(P)
        xi = np.clip(x, 0, self.w - 1.001); yi = np.clip(y, 0, self.h - 1.001)
        x0 = np.floor(xi).astype(int); y0 = np.floor(yi).astype(int); fx = (xi - x0)[:, None]; fy = (yi - y0)[:, None]
        c = (self.img[y0, x0] * (1 - fx) * (1 - fy) + self.img[y0, x0 + 1] * fx * (1 - fy)
             + self.img[y0 + 1, x0] * (1 - fx) * fy + self.img[y0 + 1, x0 + 1] * fx * fy)
        z = P @ (-self.olhar)
        zx = np.clip((x / self.res).astype(int), 0, self.zb.shape[1] - 1); zy = np.clip((y / self.res).astype(int), 0, self.zb.shape[0] - 1)
        visivel = z >= self.zb[zy, zx] - 1.5     # 1,5 cm de tolerância
        frente = np.clip(N @ (-self.olhar), 0, 1)
        dentro = self.mascara[np.clip(y.astype(int), 0, self.h - 1), np.clip(x.astype(int), 0, self.w - 1)]
        peso = frente ** 2 * visivel * dentro
        if self.so_lateral: peso = peso * (np.abs(N[:, 0]) > 0.75)
        return c, peso


def main():
    obj, fr, co, la, saida = sys.argv[1:6]
    tam = int(sys.argv[6]) if len(sys.argv) > 6 else 2048
    os.makedirs(saida, exist_ok=True)
    V, F = ler_obj(obj)
    malha = trimesh.Trimesh(V, F, process=False)
    Nv = malha.vertex_normals
    # câmeras: frente olha para -Z (está em +Z); costas olha para +Z; lado esquerdo (+X) olha para -X
    vistas = [
        (Vista(Image.open(fr), [1, 0, 0], [0, 1, 0], [0, 0, -1], V), 1.0),
        (Vista(Image.open(co), [-1, 0, 0], [0, 1, 0], [0, 0, 1], V), 1.0),
        (Vista(Image.open(la), [0, 0, -1], [0, 1, 0], [-1, 0, 0], V, so_lateral=True), 0.4),
        (Vista(Image.open(la), [0, 0, 1], [0, 1, 0], [1, 0, 0], V, espelhar=True, so_lateral=True), 0.4),
    ]
    for v, _ in vistas: v.profundidade(V, F, res=2)
    vs = np.zeros((len(V), 3), np.float32); vw = np.zeros(len(V), np.float32)
    for v, k in vistas:
        c, w = v.amostra(V, Nv); vs += c * (w * k)[:, None]; vw += w * k
    vcor = vs / np.maximum(vw, 1e-6)[:, None]
    conhecido = vw > 0.05
    viz = [[] for _ in range(len(V))]
    for a, b in malha.edges_unique: viz[a].append(b); viz[b].append(a)
    for _ in range(200):
        falta = np.where(~conhecido)[0]
        if not len(falta): break
        novos = []
        for i in falta:
            n = [j for j in viz[i] if conhecido[j]]
            if n: vcor[i] = vcor[n].mean(0); novos.append(i)
        conhecido[novos] = True
    print('UV...')
    vmap, ind, uv = xatlas.parametrize(V.astype(np.float32), F.astype(np.uint32))
    V2, N2 = V[vmap], Nv[vmap]
    # rasteriza cada triângulo no espaço UV e pinta cada texel
    tex = np.zeros((tam, tam, 3), np.float32); acc = np.zeros((tam, tam), np.float32)
    P_list, N_list, T_list, C_list = [], [], [], []
    U = uv * (tam - 1)
    for f in ind:
        us, vs = U[f, 0], (tam - 1) - U[f, 1]
        xmin, xmax = int(np.floor(us.min())), int(np.ceil(us.max()))
        ymin, ymax = int(np.floor(vs.min())), int(np.ceil(vs.max()))
        gx, gy = np.meshgrid(np.arange(xmin, xmax + 1), np.arange(ymin, ymax + 1))
        d = (vs[1] - vs[2]) * (us[0] - us[2]) + (us[2] - us[1]) * (vs[0] - vs[2])
        if abs(d) < 1e-12: continue
        l0 = ((vs[1] - vs[2]) * (gx - us[2]) + (us[2] - us[1]) * (gy - vs[2])) / d
        l1 = ((vs[2] - vs[0]) * (gx - us[2]) + (us[0] - us[2]) * (gy - vs[2])) / d
        l2 = 1 - l0 - l1
        ok = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
        if not ok.any(): continue
        L = np.stack([l0[ok], l1[ok], l2[ok]], 1)
        P_list.append(L @ V2[f]); N_list.append(L @ N2[f]); T_list.append(np.stack([gy[ok], gx[ok]], 1)); C_list.append(L @ vcor[vmap[f]])
    P = np.concatenate(P_list); N = np.concatenate(N_list); T = np.concatenate(T_list)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    soma = np.zeros((len(P), 3), np.float32); pesos = np.zeros(len(P), np.float32)
    for v, k in vistas:
        c, w = v.amostra(P, N); w = w * k
        soma += c * w[:, None]; pesos += w
    # pontos que nenhuma vista enxerga (debaixo do braço, dentro da mochila): pega a cor do vizinho depois
    Cv = np.concatenate(C_list)
    cor = soma / np.maximum(pesos, 1e-6)[:, None]
    k = np.clip((pesos - 0.02) / 0.15, 0, 1)[:, None]     # pouca certeza: puxa para a cor da vizinhança
    cor = cor * k + Cv * (1 - k)
    T = np.clip(T, 0, tam - 1)
    tex[T[:, 0], T[:, 1]] += cor
    acc[T[:, 0], T[:, 1]] += 1
    preen = acc > 0
    tex[preen] /= acc[preen][:, None]
    img = Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8))
    # dilata as cores para dentro dos buracos e das bordas das ilhas (evita costura escura)
    mask = Image.fromarray((preen * 255).astype(np.uint8))
    for _ in range(24):
        viz = img.filter(ImageFilter.MaxFilter(3)); vmask = mask.filter(ImageFilter.MaxFilter(3))
        a = np.asarray(img).copy(); m = np.asarray(mask) > 0
        a[~m] = np.asarray(viz)[~m]; img = Image.fromarray(a); mask = vmask
    img.save(os.path.join(saida, 'textura.png'))
    print('cobertura', round(float(preen.mean()), 3), 'texels pintados', int(preen.sum()))
    mat = trimesh.visual.material.PBRMaterial(baseColorTexture=img, metallicFactor=0.0, roughnessFactor=0.9)
    m2 = trimesh.Trimesh(V2 / 100.0, ind, process=False, visual=trimesh.visual.TextureVisuals(uv=uv, material=mat))
    m2.export(os.path.join(saida, 'ren_pintado.glb'))
    np.save(os.path.join(saida, 'vmap.npy'), vmap)   # vértice do GLB -> vértice do OBJ (para o esqueleto)
    print('ok', len(V2), 'vértices,', len(ind), 'triângulos')


if __name__ == '__main__':
    main()
