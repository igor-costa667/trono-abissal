// Personagem 3D estilizado (corpo de peças rígidas presas a um esqueleto), com sombreamento de desenho.
import * as THREE from 'three';

export const DEG = Math.PI / 180;

let _grad = null;
export function gradiente() {
  if (_grad) return _grad;
  const d = new Uint8Array([90, 90, 90, 255, 170, 170, 170, 255, 255, 255, 255, 255]);
  _grad = new THREE.DataTexture(d, 3, 1, THREE.RGBAFormat);
  _grad.minFilter = _grad.magFilter = THREE.NearestFilter;
  _grad.needsUpdate = true;
  return _grad;
}

export function toon(cor, extra = {}) {
  return new THREE.MeshToonMaterial({ color: cor, gradientMap: gradiente(), ...extra });
}

function malha(geo, mat, pai, pos = [0, 0, 0], rot = [0, 0, 0], esc = [1, 1, 1]) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(...pos);
  m.rotation.set(rot[0] * DEG, rot[1] * DEG, rot[2] * DEG);
  m.scale.set(...esc);
  m.castShadow = true;
  m.receiveShadow = true;
  pai.add(m);
  return m;
}

function osso(nome, pai, pos) {
  const g = new THREE.Group();
  g.name = nome;
  g.position.set(...pos);
  pai.add(g);
  return g;
}

// membro: cilindro arredondado (cápsula) pendurado para baixo a partir do osso
function membro(pai, comp, r0, r1, mat) {
  const geo = new THREE.CylinderGeometry(r0, r1, comp, 18, 1);
  const m = malha(geo, mat, pai, [0, -comp / 2, 0]);
  malha(new THREE.SphereGeometry(r0 * 1.02, 18, 12), mat, pai, [0, 0, 0]);
  return m;
}

export const PALETAS = {
  ren_f1: { pele: 0xf1c7a0, cabelo: 0x1b1b24, tunica: 0x6f7542, tunica2: 0x585d33, calca: 0x6b4a30, bota: 0x4a301e,
    cinto: 0x3d2a1c, mochila: 0x7a5a3a, coberta: 0x8f7a5a, olho: 0x3a2618 },
  ren_moletom: { pele: 0xf1c7a0, cabelo: 0x1b1b24, tunica: 0x1d1d24, tunica2: 0x15151b, calca: 0x6d6f78, bota: 0x22222a,
    cinto: 0x1d1d24, mochila: null, olho: 0x3a2618 },
};

export function criarPersonagem(opts = {}) {
  const P = PALETAS[opts.paleta || 'ren_f1'];
  const M = {
    pele: toon(P.pele), cabelo: toon(P.cabelo), tunica: toon(P.tunica), tunica2: toon(P.tunica2),
    calca: toon(P.calca), bota: toon(P.bota), cinto: toon(P.cinto), preto: toon(0x15131a),
    branco: toon(0xffffff), olho: toon(P.olho),
  };
  const raiz = new THREE.Group();
  raiz.name = 'raiz';
  const B = {};
  // alturas (m): pernas .80, tronco .50, cabeça grande (estilo desenho)
  B.hips = osso('hips', raiz, [0, 0.86, 0]);
  B.spine = osso('spine', B.hips, [0, 0.10, 0]);
  B.chest = osso('chest', B.spine, [0, 0.16, 0]);
  B.neck = osso('neck', B.chest, [0, 0.22, 0]);
  B.head = osso('head', B.neck, [0, 0.07, 0]);
  B.head.scale.setScalar(opts.cabeca || 1.18);
  for (const [s, lado] of [['L', 1], ['R', -1]]) {
    B['ua' + s] = osso('ua' + s, B.chest, [lado * 0.205, 0.17, 0]);
    B['fa' + s] = osso('fa' + s, B['ua' + s], [0, -0.27, 0]);
    B['hand' + s] = osso('hand' + s, B['fa' + s], [0, -0.25, 0]);
    B['th' + s] = osso('th' + s, B.hips, [lado * 0.095, -0.02, 0]);
    B['sh' + s] = osso('sh' + s, B['th' + s], [0, -0.40, 0]);
    B['ft' + s] = osso('ft' + s, B['sh' + s], [0, -0.38, 0]);
  }
  // ---- quadril, calça, túnica (saia presa ao quadril)
  malha(new THREE.SphereGeometry(0.15, 20, 14), M.calca, B.hips, [0, -0.02, 0], [0, 0, 0], [1.05, .7, .8]);
  const saia = new THREE.LatheGeometry([new THREE.Vector2(0.155, 0.09), new THREE.Vector2(0.17, 0), new THREE.Vector2(0.2, -0.13), new THREE.Vector2(0.215, -0.17)], 24);
  malha(saia, toon(P.tunica, { side: THREE.DoubleSide }), B.hips, [0, 0, 0], [0, 0, 0], [1, 1, .82]);
  malha(new THREE.TorusGeometry(0.165, 0.022, 8, 28), M.cinto, B.hips, [0, 0.07, 0], [90, 0, 0], [1, .82, 1]);
  malha(new THREE.BoxGeometry(0.06, 0.05, 0.02), toon(0xb8913c), B.hips, [0, 0.07, 0.14]);
  // ---- tronco
  malha(new THREE.CylinderGeometry(0.152, 0.158, 0.2, 20), M.tunica, B.spine, [0, 0.02, 0], [0, 0, 0], [1.03, 1, .8]);
  const peito = new THREE.LatheGeometry([new THREE.Vector2(0.15, -0.02), new THREE.Vector2(0.175, 0.08), new THREE.Vector2(0.19, 0.16), new THREE.Vector2(0.15, 0.22), new THREE.Vector2(0.05, 0.24)], 24);
  malha(peito, toon(P.tunica, { side: THREE.DoubleSide }), B.chest, [0, 0, 0], [0, 0, 0], [1.05, 1, .78]);
  // gola em V
  malha(new THREE.ConeGeometry(0.05, 0.09, 3), M.pele, B.chest, [0, 0.2, 0.125], [200, 0, 0], [1, 1, .3]);
  // pescoço
  malha(new THREE.CylinderGeometry(0.045, 0.05, 0.1, 12), M.pele, B.neck, [0, 0.02, 0]);
  // ---- cabeça (grande e redonda)
  const cab = malha(new THREE.SphereGeometry(0.17, 32, 24), M.pele, B.head, [0, 0.16, 0.01], [0, 0, 0], [0.95, 1.02, 0.95]);
  malha(new THREE.SphereGeometry(0.035, 12, 10), M.pele, B.head, [0.158, 0.15, 0], [0, 0, 0], [.5, 1, .8]);
  malha(new THREE.SphereGeometry(0.035, 12, 10), M.pele, B.head, [-0.158, 0.15, 0], [0, 0, 0], [.5, 1, .8]);
  // rosto: controles de expressão
  const rosto = new THREE.Group();
  rosto.position.set(0, 0.16, 0.01);
  B.head.add(rosto);
  B.rosto = rosto;
  const olhos = {}, sob = {};
  for (const [s, lado] of [['L', 1], ['R', -1]]) {
    const g = new THREE.Group();
    // olho sobre a superfície da esfera
    const az = lado * 0.34, el = -0.1;
    const r = 0.166;
    g.position.set(r * Math.sin(az) * Math.cos(el) * .95, r * Math.sin(el) * 1.02, r * Math.cos(az) * Math.cos(el) * .95 + 0.004);
    g.lookAt(g.position.clone().multiplyScalar(3));
    rosto.add(g);
    const branco = malha(new THREE.SphereGeometry(0.042, 18, 14), M.branco, g, [0, 0, 0], [0, 0, 0], [0.85, 1.15, 0.3]);
    const iris = malha(new THREE.SphereGeometry(0.031, 18, 14), M.olho, g, [0, -0.006, 0.01], [0, 0, 0], [0.85, 1.1, 0.3]);
    malha(new THREE.SphereGeometry(0.017, 12, 10), M.preto, iris, [0, -0.002, 0.01], [0, 0, 0], [1, 1, .6]);
    malha(new THREE.SphereGeometry(0.009, 8, 6), M.branco, iris, [0.01 * lado, 0.014, 0.022]);
    branco.castShadow = iris.castShadow = false;
    olhos[s] = g;
    // sobrancelha
    const sb = new THREE.Group();
    sb.position.set(lado * 0.058, 0.02, 0.165);
    sb.rotation.y = lado * 0.35;
    rosto.add(sb);
    malha(new THREE.CapsuleGeometry(0.008, 0.045, 4, 8), M.cabelo, sb, [0, 0, 0], [0, 0, 90]);
    sob[s] = sb;
  }
  B.olhos = olhos;
  B.sob = sob;
  const boca = new THREE.Group();
  boca.position.set(0, -0.098, 0.145);
  boca.rotation.x = 0.35;
  rosto.add(boca);
  malha(new THREE.SphereGeometry(0.016, 12, 8), toon(0x5a2626), boca, [0, 0, 0], [0, 0, 0], [1.1, .35, .3]);
  B.boca = boca;
  // ---- cabelo bagunçado: mechas pontudas com balanço
  const cabelo = new THREE.Group();
  cabelo.position.set(0, 0.16, 0.01);
  B.head.add(cabelo);
  B.cabelo = cabelo;
  malha(new THREE.SphereGeometry(0.178, 28, 20, 0, Math.PI * 2, 0, Math.PI * 0.5), M.cabelo, cabelo, [0, 0.02, -0.02], [-22, 0, 0], [1, 1.02, 1.02]);
  B.mechas = [];
  const rnd = mulberry(7);
  const mechas = [];
  for (let i = 0; i < 22; i++) {
    const th = (i / 22) * Math.PI * 2 + (rnd() - .5) * .25;
    const ph = 0.55 + rnd() * 0.75;
    mechas.push([th, ph]);
  }
  for (let i = 0; i < 6; i++) mechas.push([rnd() * Math.PI * 2, 0.15 + rnd() * 0.3]);
  // franja na frente
  for (let i = 0; i < 7; i++) mechas.push([Math.PI / 2 + (i - 3) * 0.2 + (rnd() - .5) * .1, 0.72 + rnd() * 0.12, true]);
  for (const [th, ph, franja] of mechas) {
    const piv = new THREE.Group();
    const r = 0.165;
    const dir = new THREE.Vector3(Math.cos(th) * Math.sin(ph), Math.cos(ph), Math.sin(th) * Math.sin(ph));
    if (!franja && dir.z > 0.35 && dir.y < 0.75) continue;      // deixa o rosto livre
    piv.position.copy(dir.clone().multiplyScalar(r));
    piv.position.z -= 0.01;
    cabelo.add(piv);
    const comp = franja ? 0.075 + rnd() * 0.03 : 0.1 + rnd() * 0.07;
    const cone = malha(new THREE.ConeGeometry(0.055 + rnd() * 0.02, comp, 7), M.cabelo, piv, [0, comp / 2 - 0.015, 0], [0, 0, 0], [1, 1, 0.55]);
    // aponta para fora e para baixo (gravidade), mechas achatadas como cabelo de anime
    const alvo = dir.clone().add(new THREE.Vector3(0, franja ? -1.1 : -0.9, 0)).normalize();
    piv.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), alvo);
    piv.userData.base = piv.quaternion.clone();
    cone.castShadow = false;
    B.mechas.push(piv);
  }
  // ---- braços (manga longa verde) e mãos
  for (const s of ['L', 'R']) {
    membro(B['ua' + s], 0.27, 0.058, 0.05, M.tunica);
    membro(B['fa' + s], 0.25, 0.05, 0.043, M.tunica);
    malha(new THREE.TorusGeometry(0.046, 0.012, 6, 16), M.tunica2, B['fa' + s], [0, -0.21, 0], [90, 0, 0]);
    malha(new THREE.SphereGeometry(0.052, 16, 12), M.pele, B['hand' + s], [0, -0.035, 0], [0, 0, 0], [.85, 1.1, .75]);
    malha(new THREE.SphereGeometry(0.022, 10, 8), M.pele, B['hand' + s], [s === 'L' ? -0.035 : 0.035, -0.02, 0.025]);
    membro(B['th' + s], 0.40, 0.075, 0.06, M.calca);
    membro(B['sh' + s], 0.38, 0.058, 0.05, M.calca);
    // bota de cano alto
    malha(new THREE.CylinderGeometry(0.064, 0.06, 0.2, 16), M.bota, B['sh' + s], [0, -0.28, 0]);
    malha(new THREE.TorusGeometry(0.064, 0.012, 6, 16), M.cinto, B['sh' + s], [0, -0.2, 0], [90, 0, 0]);
    const pe = malha(new THREE.SphereGeometry(0.07, 16, 12), M.bota, B['ft' + s], [0, -0.03, 0.05], [0, 0, 0], [0.9, 0.62, 1.55]);
    malha(new THREE.BoxGeometry(0.12, 0.025, 0.24), M.preto, B['ft' + s], [0, -0.07, 0.05]);
  }
  // ---- mochila (com balanço)
  if (P.mochila) {
    const moc = new THREE.Group();
    moc.position.set(0, 0.12, -0.15);
    B.chest.add(moc);
    malha(new THREE.BoxGeometry(0.3, 0.34, 0.16), toon(P.mochila), moc, [0, 0, -0.07]);
    malha(new THREE.BoxGeometry(0.31, 0.12, 0.17), toon(0x6a4c30), moc, [0, 0.13, -0.07], [-8, 0, 0]);
    malha(new THREE.CylinderGeometry(0.075, 0.075, 0.42, 16), toon(P.coberta), moc, [0, 0.22, -0.06], [0, 0, 90]);
    malha(new THREE.BoxGeometry(0.2, 0.12, 0.05), toon(0x6a4c30), moc, [0, -0.06, -0.165]);
    for (const lado of [1, -1]) malha(new THREE.BoxGeometry(0.04, 0.3, 0.02), M.cinto, B.chest, [lado * 0.1, 0.1, 0.125], [8, 0, 0]);
    B.mochila = moc;
  }
  cabelo.traverse(o => { if (o.isMesh) o.castShadow = false; });
  return { raiz, B };
}

export function criarEspada() {
  const g = new THREE.Group();
  const aco = toon(0xd9dee8), ouro = toon(0xc9a13e), couro = toon(0x5a3a22);
  // eixo da espada ao longo de +Z (a mão segura no cabo, em z=0)
  malha(new THREE.CylinderGeometry(0.018, 0.02, 0.17, 10), couro, g, [0, 0, -0.02], [90, 0, 0]);
  malha(new THREE.SphereGeometry(0.03, 10, 8), ouro, g, [0, 0, -0.115]);
  malha(new THREE.BoxGeometry(0.2, 0.03, 0.035), ouro, g, [0, 0, 0.07]);
  const lam = new THREE.Shape();
  lam.moveTo(-0.032, 0); lam.lineTo(0.032, 0); lam.lineTo(0.03, 0.62); lam.lineTo(0, 0.7); lam.lineTo(-0.03, 0.62); lam.closePath();
  const geo = new THREE.ExtrudeGeometry(lam, { depth: 0.012, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.006, bevelSegments: 1 });
  const m = malha(geo, aco, g, [0, -0.006, 0.085], [90, 0, 0]);
  return g;
}

export function mulberry(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
