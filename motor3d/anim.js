// Animação: poses em graus, curvas suaves entre poses (Hermite / Catmull-Rom), caminhada com pé travado,
// e movimento secundário com molas (cabelo, mochila). Tudo é função do tempo, para renderizar quadro a quadro.
import * as THREE from 'three';
import { DEG } from './personagem.js';

export const OSSOS = ['spine', 'chest', 'neck', 'head', 'uaL', 'faL', 'handL', 'uaR', 'faR', 'handR', 'thL', 'shL', 'ftL', 'thR', 'shR', 'ftR'];

// pose "semântica" -> pose crua (euler em graus por osso + raiz)
// braço: [frente, abre, gira]; antebraço: dobra; coxa: [frente, abre]; canela: dobra; pé: [aponta]
export function pose(p = {}) {
  const o = { root: [...(p.root || [0, 0, 0])], rootRy: p.rootRy || 0, hips: [...(p.hips || [0, 0, 0])], hipsY: p.hipsY || 0 };
  const arr = (v) => v ? [...v, 0, 0, 0].slice(0, 3) : [0, 0, 0];
  o.spine = arr(p.spine); o.chest = arr(p.chest); o.neck = arr(p.neck); o.head = arr(p.head);
  for (const [s, lado] of [['L', 1], ['R', -1]]) {
    const ua = arr(p['ua' + s] || [0, 8, 0]);
    o['ua' + s] = [-ua[0], lado * ua[2], lado * ua[1]];
    o['fa' + s] = [-(p['fa' + s] ?? 12), 0, 0];
    const hd = arr(p['hand' + s]);
    o['hand' + s] = [hd[0], lado * hd[1], lado * hd[2]];
    const th = arr(p['th' + s]);
    o['th' + s] = [-th[0], lado * th[2], lado * (th[1] || 2)];
    o['sh' + s] = [p['sh' + s] ?? 3, 0, 0];
    o['ft' + s] = [arr(p['ft' + s])[0], 0, 0];
  }
  return o;
}

function lerpArr(a, b, k) { return a.map((v, i) => v + (b[i] - v) * k); }
export function mistura(a, b, k) {
  const o = {};
  for (const key of Object.keys(a)) o[key] = Array.isArray(a[key]) ? lerpArr(a[key], b[key], k) : a[key] + (b[key] - a[key]) * k;
  return o;
}
function soma(a, b, k = 1) {
  const o = {};
  for (const key of Object.keys(a)) o[key] = Array.isArray(a[key]) ? a[key].map((v, i) => v + (b[key] ? b[key][i] * k : 0)) : a[key] + ((b[key] || 0) * k);
  return o;
}
export const suave = (k) => k <= 0 ? 0 : k >= 1 ? 1 : k * k * (3 - 2 * k);

// trilha de poses no tempo, com interpolação cúbica (movimento contínuo, sem trancos)
// chaves: [{t, p: pose crua, fixa: true (para parado ali, tangente zero)}]
export function trilha(chaves) {
  const ks = chaves.slice().sort((a, b) => a.t - b.t);
  const tang = ks.map((k, i) => {
    if (k.fixa || i === 0 || i === ks.length - 1) return null;
    const a = ks[i - 1], b = ks[i + 1];
    const o = {};
    for (const key of Object.keys(k.p)) {
      const f = (x, y) => (y - x) / (b.t - a.t) * (k.tensao ?? 1);
      o[key] = Array.isArray(k.p[key]) ? k.p[key].map((v, j) => f(a.p[key][j], b.p[key][j])) : f(a.p[key], b.p[key]);
    }
    return o;
  });
  return (t) => {
    if (t <= ks[0].t) return ks[0].p;
    if (t >= ks[ks.length - 1].t) return ks[ks.length - 1].p;
    let i = 0;
    while (t > ks[i + 1].t) i++;
    const a = ks[i], b = ks[i + 1], h = b.t - a.t;
    let u = (t - a.t) / h;
    if (b.curva) u = b.curva(u);
    const h00 = 2 * u ** 3 - 3 * u ** 2 + 1, h10 = u ** 3 - 2 * u ** 2 + u, h01 = -2 * u ** 3 + 3 * u ** 2, h11 = u ** 3 - u ** 2;
    const ma = tang[i], mb = tang[i + 1];
    const o = {};
    for (const key of Object.keys(a.p)) {
      const f = (pa, pb, ta, tb) => h00 * pa + h10 * h * ta + h01 * pb + h11 * h * tb;
      o[key] = Array.isArray(a.p[key])
        ? a.p[key].map((v, j) => f(v, b.p[key][j], ma ? ma[key][j] : 0, mb ? mb[key][j] : 0))
        : f(a.p[key], b.p[key], ma ? ma[key] : 0, mb ? mb[key] : 0);
    }
    return o;
  };
}

// caminhada procedural: quadril em pêndulo invertido, pé de apoio travado no chão (sem patinar)
export function caminhada(opts = {}) {
  const L = opts.perna ?? 0.78, amp = (opts.amp ?? 24) * DEG, f = opts.passos ?? 1.9;   // passos por segundo
  const S = 2 * L * Math.sin(amp);
  const segura = opts.segura;   // braço direito segurando algo: balança menos
  return {
    passo: S, velocidade: S * f,
    pose(t) {
      const ph = t * f;                     // em passos
      const n = Math.floor(ph), u = ph - n; // u: 0..1 dentro do passo
      // perna de apoio vai de +amp a -amp; a outra balança de -amp a +amp
      const thA = amp * Math.cos(Math.PI * u);          // apoio (graus em rad)
      const thB = -thA;
      const apoioEsq = n % 2 === 0;
      const dobraB = 55 * Math.sin(Math.PI * u) ** 1.3;   // joelho da perna no ar
      const dobraA = 8 * Math.sin(Math.PI * u);
      const thL = (apoioEsq ? thA : thB) / DEG, thR = (apoioEsq ? thB : thA) / DEG;
      const shL = apoioEsq ? dobraA : dobraB, shR = apoioEsq ? dobraB : dobraA;
      const x = n * S + L * (Math.sin(amp) - Math.sin(thA));
      const hipsY = L * Math.cos(thA) * 1.0 - L * 0.985;     // sobe no meio do passo
      const lado = apoioEsq ? 1 : -1;
      const balA = 18;
      const p = pose({
        hipsY: hipsY + (opts.baixo || 0), hips: [0, -lado * 6 * Math.sin(Math.PI * u) * 0 + thL * 0.18, lado * 2.5 * Math.sin(Math.PI * u)],
        spine: [4, -thL * 0.12, 0], chest: [3, -thL * 0.22, -lado * 1.5 * Math.sin(Math.PI * u)],
        neck: [0, thL * 0.1, 0], head: [-2, thL * 0.12, lado * 1.2 * Math.sin(Math.PI * u)],
        uaL: [-thL * 0.85, 9, 0], faL: 18 + Math.max(0, -thL) * 0.6,
        uaR: segura ? [20 - thR * 0.3, 10, 0] : [-thR * 0.85, 9, 0], faR: segura ? 45 : 18 + Math.max(0, -thR) * 0.6,
        handR: segura ? [0, 0, 0] : [0, 0, 0],
        thL: [thL, 3], shL, ftL: [(apoioEsq ? -thL * 0.9 : -thL * 0.6 + shL * 0.4)],
        thR: [thR, 3], shR, ftR: [(apoioEsq ? -thR * 0.6 + shR * 0.4 : -thR * 0.9)],
      });
      p.root = [x, 0, 0];
      return p;
    },
  };
}

// aplica a pose crua no esqueleto (personagem olhando para +Z; raiz gira e anda no mundo)
export function aplicar(per, p, base) {
  const { raiz, B } = per;
  raiz.position.set(base.x + p.root[0] * Math.cos(-base.ry + Math.PI / 2) , p.root[1], base.z);
  // anda na direção para onde olha
  const dir = new THREE.Vector3(Math.sin(base.ry + p.rootRy * DEG), 0, Math.cos(base.ry + p.rootRy * DEG));
  raiz.position.set(base.x + dir.x * p.root[0] + p.root[2] * dir.z, p.root[1], base.z + dir.z * p.root[0] - p.root[2] * dir.x);
  raiz.rotation.y = base.ry + p.rootRy * DEG;
  B.hips.position.y = 0.86 + p.hipsY;
  B.hips.rotation.set(p.hips[0] * DEG, p.hips[1] * DEG, p.hips[2] * DEG);
  for (const o of OSSOS) B[o].rotation.set(p[o][0] * DEG, p[o][1] * DEG, p[o][2] * DEG);
}

// expressões do rosto
export const EXPR = {
  normal: { sob: 0, sobY: 0, boca: [1, 1], olho: 1 },
  decidido: { sob: 0.38, sobY: -0.008, boca: [0.8, 0.6], olho: 0.92 },
  surpreso: { sob: -0.15, sobY: 0.02, boca: [0.9, 3.2], olho: 1.12 },
  tonto: { sob: -0.3, sobY: 0.005, boca: [1.4, 1.6], olho: 1.0 },
  dor: { sob: 0.25, sobY: -0.004, boca: [1.6, 0.6], olho: 0.35 },
};
export function rosto(per, e, piscar = 0, girarOlho = 0, t = 0) {
  const { B } = per;
  B.sob.L.rotation.z = e.sob; B.sob.R.rotation.z = -e.sob;
  B.sob.L.position.y = B.sob.R.position.y = 0.02 + e.sobY;
  B.boca.scale.set(e.boca[0], e.boca[1], 1);
  for (const s of ['L', 'R']) {
    const g = B.olhos[s];
    g.scale.set(e.olho, e.olho * (1 - 0.9 * piscar), e.olho);
    const iris = g.children[1];
    iris.position.x = girarOlho * 0.008 * Math.cos(t * 14 + (s === 'L' ? 0 : 1.5));
    iris.position.y = -0.006 + girarOlho * 0.008 * Math.sin(t * 14 + (s === 'L' ? 0 : 1.5));
  }
}
export function mistExpr(a, b, k) {
  return { sob: a.sob + (b.sob - a.sob) * k, sobY: a.sobY + (b.sobY - a.sobY) * k, boca: lerpArr(a.boca, b.boca, k), olho: a.olho + (b.olho - a.olho) * k };
}

// molas: cabelo e mochila balançam atrasados em relação ao corpo
export function criarMolas(per) {
  const st = { ult: null, vel: new THREE.Vector3(), mola: new THREE.Vector3(), vmola: new THREE.Vector3(), tUlt: null };
  return function passo(t) {
    const pos = new THREE.Vector3();
    per.B.head.getWorldPosition(pos);
    if (st.ult === null || t <= st.tUlt) { st.ult = pos.clone(); st.tUlt = t; return; }
    const dt = t - st.tUlt;
    const n = Math.max(1, Math.round(dt / (1 / 240)));
    const v = pos.clone().sub(st.ult).divideScalar(dt);
    const acc = v.clone().sub(st.vel).divideScalar(dt);
    st.vel.copy(v);
    for (let i = 0; i < n; i++) {
      const h = dt / n;
      // mola amortecida puxada pela aceleração (inércia)
      const f = acc.clone().multiplyScalar(-0.012).sub(st.mola.clone().multiplyScalar(160)).sub(st.vmola.clone().multiplyScalar(11));
      st.vmola.add(f.multiplyScalar(h));
      st.mola.add(st.vmola.clone().multiplyScalar(h));
    }
    st.mola.clampLength(0, 0.6);
    st.ult.copy(pos); st.tUlt = t;
    // inclinação das mechas (no espaço da cabeça, aproximado)
    const inv = new THREE.Quaternion(); per.B.head.getWorldQuaternion(inv); inv.invert();
    const m = st.mola.clone().applyQuaternion(inv);
    const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(m.z * 2.2, 0, -m.x * 2.2));
    for (const piv of per.B.mechas) piv.quaternion.copy(q).multiply(piv.userData.base);
    if (per.B.mochila) per.B.mochila.rotation.x = THREE.MathUtils.clamp(m.z * 1.2, -0.35, 0.35);
  };
}
