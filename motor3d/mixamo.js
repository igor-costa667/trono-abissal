// Animações reais do Mixamo no Ren.
// Carrega os .fbx (Y Bot, sem skin, T-pose em cm), amostra cada clipe no tempo e redireciona a rotação de cada osso
// para o esqueleto do Ren pela diferença em relação ao T-pose (espaço do personagem):
//   mundoRen(t) = mundoMixamo(t) * mundoMixamo(T-pose)^-1 * mundoRen(T-pose)
// Assim o Ren repete a pose do Y Bot mesmo com proporções e eixos de osso diferentes.
import * as THREE from 'three';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

// osso do Ren <- osso do Mixamo (a ordem é a da hierarquia: pai antes do filho)
export const MAPA = [
  ['hips', 'Hips'], ['spine', 'Spine'], ['chest', 'Spine2'], ['neck', 'Neck'], ['head', 'Head'],
  ['uaL', 'LeftArm'], ['faL', 'LeftForeArm'], ['handL', 'LeftHand'],
  ['uaR', 'RightArm'], ['faR', 'RightForeArm'], ['handR', 'RightHand'],
  ['thL', 'LeftUpLeg'], ['shL', 'LeftLeg'], ['ftL', 'LeftFoot'],
  ['thR', 'RightUpLeg'], ['shR', 'RightLeg'], ['ftR', 'RightFoot'],
];
const PAI = { hips: null, spine: 'hips', chest: 'spine', neck: 'chest', head: 'neck', uaL: 'chest', faL: 'uaL', handL: 'faL',
  uaR: 'chest', faR: 'uaR', handR: 'faR', thL: 'hips', shL: 'thL', ftL: 'shL', thR: 'hips', shR: 'thR', ftR: 'shR' };

const ALTURA_QUADRIL_YBOT = 99.8;   // cm (T-pose)

// ---------- clipe do Mixamo: amostra a pose (quatérnios no espaço do personagem) em qualquer tempo
export async function carregarClipe(arquivo) {
  const obj = await new FBXLoader().loadAsync(arquivo);
  obj.updateMatrixWorld(true);
  const ossos = {};
  for (const [, m] of MAPA) ossos[m] = obj.getObjectByName('mixamorig' + m);
  ossos.LeftToeBase = obj.getObjectByName('mixamorigLeftToeBase');
  ossos.RightToeBase = obj.getObjectByName('mixamorigRightToeBase');
  const restQ = {};
  for (const [, m] of MAPA) restQ[m] = ossos[m].getWorldQuaternion(new THREE.Quaternion()).invert();
  const clip = obj.animations[0];
  const mixer = new THREE.AnimationMixer(obj);
  const acao = mixer.clipAction(clip); acao.play();
  const dur = clip.duration;
  const cache = new Map();
  function amostra(t) {
    t = Math.max(0, Math.min(dur - 1e-4, t));
    const chave = Math.round(t * 600);
    if (cache.has(chave)) return cache.get(chave);
    acao.time = t; mixer.update(0); obj.updateMatrixWorld(true);
    const delta = {}, q = new THREE.Quaternion();
    for (const [, m] of MAPA) { ossos[m].getWorldQuaternion(q); delta[m] = q.clone().multiply(restQ[m]); }
    const hips = ossos.Hips.position.clone();
    const pe = (n) => ossos[n].getWorldPosition(new THREE.Vector3());
    const r = { delta, hips, peL: pe('LeftToeBase'), peR: pe('RightToeBase') };
    if (cache.size > 4000) cache.clear();
    cache.set(chave, r);
    return r;
  }
  // velocidade do pé de apoio num clipe "In Place" (para a raiz andar sem o pé patinar)
  function velocidadeNoLugar() {
    const n = 60; let soma = 0, cont = 0;
    for (let i = 0; i < n; i++) {
      const t0 = dur * i / n, t1 = dur * (i + 1) / n;
      const a = amostra(t0), b = amostra(t1);
      const pe = a.peL.y < a.peR.y ? 'peL' : 'peR';
      if (Math.min(a.peL.y, a.peR.y) > 6) continue;   // nenhum pé no chão
      soma += -(b[pe].z - a[pe].z) / (t1 - t0); cont++;
    }
    return cont ? soma / cont : 0;   // cm/s
  }
  return { nome: arquivo, dur, amostra, velocidadeNoLugar };
}

// ---------- T-pose do Ren (braços abertos), gravado uma vez
export function prepararRen(per) {
  const { B, raiz } = per;
  const salva = {};
  for (const [r] of MAPA) salva[r] = B[r].quaternion.clone();
  const salvaRaiz = [raiz.position.clone(), raiz.quaternion.clone()];
  raiz.position.set(0, 0, 0); raiz.quaternion.identity();
  for (const [r] of MAPA) B[r].quaternion.identity();
  B.uaL.rotation.set(0, 0, Math.PI / 2);
  B.uaR.rotation.set(0, 0, -Math.PI / 2);
  raiz.updateMatrixWorld(true);
  const restRen = {};
  for (const [r] of MAPA) restRen[r] = B[r].getWorldQuaternion(new THREE.Quaternion());
  for (const [r] of MAPA) B[r].quaternion.copy(salva[r]);
  raiz.position.copy(salvaRaiz[0]); raiz.quaternion.copy(salvaRaiz[1]);
  per.restRen = restRen;
  per.alturaQuadril = B.hips.position.y || 0.86;
  return per;
}

// pose do Ren (quatérnio local de cada osso + posição do quadril em m) a partir de uma amostra do Mixamo
export function poseDoClipe(per, s, desloc = [0, 0]) {
  const k = per.alturaQuadril / ALTURA_QUADRIL_YBOT;
  const mundo = {}, local = {};
  for (const [r, m] of MAPA) {
    const w = s.delta[m].clone().multiply(per.restRen[r]);
    mundo[r] = w;
    const p = PAI[r];
    local[r] = p ? mundo[p].clone().invert().multiply(w) : w;
  }
  const hips = new THREE.Vector3(s.hips.x * k + desloc[0], s.hips.y * k, s.hips.z * k + desloc[1]);
  return { local, hips };
}

export function misturarPoses(a, b, u) {
  const local = {};
  for (const [r] of MAPA) local[r] = a.local[r].clone().slerp(b.local[r], u);
  return { local, hips: a.hips.clone().lerp(b.hips, u) };
}

export function aplicarPose(per, p, base) {
  const { B, raiz } = per;
  raiz.position.set(base.x, 0, base.z);
  raiz.rotation.set(0, base.ry, 0);
  B.hips.position.copy(p.hips);
  for (const [r] of MAPA) B[r].quaternion.copy(p.local[r]);
}

// ---------- sequência de clipes com transições suaves e raiz contínua
// itens: { clipe, de, ate, vel (multiplica o tempo), noLugar (anda pela raiz), mistura (s) }
export function sequencia(per, itens) {
  const k = per.alturaQuadril / ALTURA_QUADRIL_YBOT;
  let t = 0, avanco = 0, desl = [0, 0];
  const segs = [];
  for (const it of itens) {
    const de = it.de ?? 0, ate = it.ate ?? it.clipe.dur;
    const vel = it.vel ?? 1;
    const dur = (ate - de) / vel;
    const andar = it.noLugar ? it.clipe.velocidadeNoLugar() * k * vel * (it.passada ?? 1) : 0;   // m/s
    const seg = { ...it, de, ate, vel, t0: t, t1: t + dur, andar, avanco0: avanco };
    // continuidade do quadril: onde o clipe anterior terminou (no chão) é onde este começa
    if (segs.length) {
      const ant = segs[segs.length - 1];
      const fimAnt = ant.clipe.amostra(ant.ate).hips, iniEste = it.clipe.amostra(de).hips;
      desl = [ant.desl[0] + (fimAnt.x - iniEste.x) * k, ant.desl[1] + (fimAnt.z - iniEste.z) * k];
      if (it.zerarX) desl[0] = 0;
    }
    seg.desl = desl.slice();
    avanco += andar * dur;
    segs.push(seg);
    t += dur;
  }
  function poseSeg(seg, tt) {
    const tc = seg.de + Math.max(0, Math.min(tt - seg.t0, seg.t1 - seg.t0)) * seg.vel;
    let tcl = tc;
    if (seg.loop) tcl = seg.de + ((tc - seg.de) % (seg.clipe.dur - seg.de));
    const p = poseDoClipe(per, seg.clipe.amostra(tcl), seg.desl);
    const av = seg.avanco0 + seg.andar * Math.max(0, Math.min(tt - seg.t0, seg.t1 - seg.t0));
    return { p, av };
  }
  return {
    dur: t, segs,
    em(tt) {
      let i = segs.findIndex(s => tt < s.t1);
      if (i < 0) i = segs.length - 1;
      const s = segs[i];
      let { p, av } = poseSeg(s, tt);
      const mix = s.mistura ?? 0.3;
      if (i > 0 && tt < s.t0 + mix) {
        const ant = segs[i - 1];
        const a = poseSeg(ant, tt);   // o anterior fica congelado no último quadro
        const u = (tt - s.t0) / mix; const uu = u * u * (3 - 2 * u);
        p = misturarPoses(a.p, p, uu);
        av = a.av + (av - a.av) * uu;
      }
      p.hips.z += av;   // o personagem anda para a frente (+Z local)
      return { pose: p, seg: s, i };
    },
  };
}
