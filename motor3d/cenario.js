// Cenários 3D. campoDeTreino(): pátio de treino de Valdenmoor (chão de terra, cerca, boneco de palha, alvo, muralha).
import * as THREE from 'three';
import { toon, DEG, mulberry } from './personagem.js';

function m(geo, mat, pai, pos = [0, 0, 0], rot = [0, 0, 0], esc = [1, 1, 1], sombra = true) {
  const o = new THREE.Mesh(geo, mat);
  o.position.set(...pos); o.rotation.set(rot[0] * DEG, rot[1] * DEG, rot[2] * DEG); o.scale.set(...esc);
  o.castShadow = sombra; o.receiveShadow = true; pai.add(o); return o;
}

function texturaRuido(cor1, cor2, n = 256, manchas = 900, seed = 3, tam = [2, 7]) {
  const c = document.createElement('canvas'); c.width = c.height = n;
  const g = c.getContext('2d'); g.fillStyle = cor1; g.fillRect(0, 0, n, n);
  const r = mulberry(seed);
  for (let i = 0; i < manchas; i++) {
    g.fillStyle = cor2; g.globalAlpha = 0.25 + r() * 0.35;
    const s = tam[0] + r() * (tam[1] - tam[0]);
    g.beginPath(); g.ellipse(r() * n, r() * n, s, s * (0.4 + r() * 0.6), r() * 3, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function ceu(cena, topo = 0x6fa4d8, horizonte = 0xf3e2c4) {
  const geo = new THREE.SphereGeometry(80, 32, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { a: { value: new THREE.Color(topo) }, b: { value: new THREE.Color(horizonte) } },
    vertexShader: 'varying vec3 p; void main(){ p = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: 'uniform vec3 a; uniform vec3 b; varying vec3 p; void main(){ float k = smoothstep(-0.05, 0.45, p.y); gl_FragColor = vec4(pow(mix(b, a, k), vec3(1.0/2.2)), 1.0); }',
  });
  mat.userData.outlineParameters = { visible: false };
  const s = new THREE.Mesh(geo, mat); cena.add(s);
  // nuvens
  const nuv = toon(0xffffff);
  const r = mulberry(11);
  for (let i = 0; i < 9; i++) {
    const g = new THREE.Group();
    const a = (i / 9) * Math.PI * 1.2 - 1.9, d = 55 + r() * 10;
    g.position.set(Math.cos(a) * d, 14 + r() * 10, Math.sin(a) * d);
    for (let j = 0; j < 4; j++) m(new THREE.SphereGeometry(2 + r() * 2, 12, 8), nuv, g, [j * 2.4 - 3.6, r() * 1.2, 0], [0, 0, 0], [1.4, .7, 1], false);
    g.lookAt(0, g.position.y, 0);
    cena.add(g);
  }
}

export function bonecoDePalha() {
  const g = new THREE.Group();
  const madeira = toon(0x7a5232), palha = toon(0xd8b866), corda = toon(0x8a6a3a), saco = toon(0xc9a978);
  const piv = new THREE.Group(); g.add(piv);                     // gira na base quando apanha
  m(new THREE.CylinderGeometry(0.06, 0.07, 1.7, 10), madeira, piv, [0, 0.85, 0]);
  m(new THREE.CylinderGeometry(0.22, 0.2, 0.62, 14), palha, piv, [0, 1.12, 0]);
  for (const y of [0.88, 1.12, 1.36]) m(new THREE.TorusGeometry(0.215, 0.018, 6, 20), corda, piv, [0, y, 0], [90, 0, 0]);
  m(new THREE.CylinderGeometry(0.045, 0.045, 0.95, 8), madeira, piv, [0, 1.34, 0], [0, 0, 90]);
  for (const s of [1, -1]) m(new THREE.CylinderGeometry(0.075, 0.06, 0.28, 10), palha, piv, [s * 0.42, 1.34, 0], [0, 0, 90]);
  const cab = m(new THREE.SphereGeometry(0.17, 16, 12), saco, piv, [0, 1.6, 0]);
  m(new THREE.TorusGeometry(0.12, 0.016, 6, 16), corda, piv, [0, 1.47, 0], [90, 0, 0]);
  // "rosto" desenhado (x x)
  for (const s of [1, -1]) {
    m(new THREE.BoxGeometry(0.05, 0.012, 0.01), toon(0x3a2a1a), piv, [s * 0.055, 1.63, 0.165], [0, 0, 45], [1, 1, 1], false);
    m(new THREE.BoxGeometry(0.05, 0.012, 0.01), toon(0x3a2a1a), piv, [s * 0.055, 1.63, 0.165], [0, 0, -45], [1, 1, 1], false);
  }
  // fiapos de palha
  const r = mulberry(5);
  for (let i = 0; i < 18; i++) {
    const a = r() * Math.PI * 2;
    m(new THREE.CylinderGeometry(0.006, 0.006, 0.12, 4), palha, piv, [Math.cos(a) * 0.21, 0.84 + r() * 0.06, Math.sin(a) * 0.21], [r() * 40 - 20, 0, r() * 40 - 20], [1, 1, 1], false);
  }
  g.userData.piv = piv;
  return g;
}

export function campoDeTreino(cena) {
  ceu(cena);
  cena.fog = new THREE.Fog(0xe9dcc2, 14, 60);
  // chão de grama + arena de terra
  const tg = texturaRuido('#7d9a4e', '#5f7d3a', 256, 1400, 3); tg.repeat.set(30, 30);
  m(new THREE.PlaneGeometry(160, 160), toon(0xffffff, { map: tg }), cena, [0, 0, 0], [-90, 0, 0], [1, 1, 1], false);
  const tt = texturaRuido('#b89466', '#9c7a52', 256, 900, 8, [2, 9]); tt.repeat.set(4, 4);
  m(new THREE.CircleGeometry(4.6, 48), toon(0xffffff, { map: tt }), cena, [0.2, 0.004, 0], [-90, 0, 0], [1, 1, 1], false);
  // cerca de madeira em volta
  const madeira = toon(0x8a5e38), madeira2 = toon(0x6d4a2c);
  const N = 22;
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2, a2 = ((i + 1) / N) * Math.PI * 2, R = 5.3;
    if (Math.abs(Math.sin(a)) > 0.86 && Math.cos(a) < 0 && Math.sin(a) > 0) continue;  // abertura na frente
    const x = 0.2 + Math.cos(a) * R, z = Math.sin(a) * R;
    m(new THREE.CylinderGeometry(0.07, 0.08, 1.1, 8), madeira2, cena, [x, 0.55, z]);
    const x2 = 0.2 + Math.cos(a2) * R, z2 = Math.sin(a2) * R;
    const comp = Math.hypot(x2 - x, z2 - z);
    for (const y of [0.45, 0.85]) {
      const tab = m(new THREE.BoxGeometry(comp, 0.09, 0.05), madeira, cena, [(x + x2) / 2, y, (z + z2) / 2]);
      tab.rotation.y = -Math.atan2(z2 - z, x2 - x);
    }
  }
  // alvo de arco e arara de armas ao fundo
  const alvo = new THREE.Group(); alvo.position.set(-2.6, 0, -3.4); alvo.rotation.y = 0.5; cena.add(alvo);
  for (const [s, x] of [[1, 0.35], [-1, -0.35]]) m(new THREE.CylinderGeometry(0.05, 0.05, 1.5, 8), madeira2, alvo, [x, 0.75, -0.15], [-12, 0, 0]);
  const cores = [0xf1ead8, 0x2a2a2a, 0x3f78c8, 0xd23b32, 0xf2c23a];
  cores.forEach((c, i) => m(new THREE.CylinderGeometry(0.55 - i * 0.11, 0.55 - i * 0.11, 0.08 + i * 0.012, 28), toon(c), alvo, [0, 1.05, 0], [78, 0, 0]));
  const arara = new THREE.Group(); arara.position.set(2.9, 0, -3.3); arara.rotation.y = -0.6; cena.add(arara);
  m(new THREE.BoxGeometry(1.6, 0.08, 0.08), madeira, arara, [0, 1.15, 0]);
  m(new THREE.BoxGeometry(1.6, 0.08, 0.08), madeira, arara, [0, 0.3, 0.12]);
  for (const x of [-0.75, 0.75]) m(new THREE.BoxGeometry(0.08, 1.3, 0.3), madeira2, arara, [x, 0.65, 0.05]);
  const aco = toon(0xcfd5df), cabo = toon(0x4a2e1a);
  for (let i = 0; i < 4; i++) {
    m(new THREE.BoxGeometry(0.05, 0.95, 0.015), aco, arara, [-0.5 + i * 0.33, 0.72, 0.02], [0, 0, 4 - i * 3]);
    m(new THREE.BoxGeometry(0.16, 0.03, 0.04), toon(0xc9a13e), arara, [-0.5 + i * 0.33, 1.2, 0.02]);
  }
  m(new THREE.CylinderGeometry(0.03, 0.03, 1.3, 6), cabo, arara, [0.95, 0.65, 0.2], [0, 0, -12]);
  // fardos de feno e barril
  const feno = toon(0xd9bb6a);
  m(new THREE.BoxGeometry(0.9, 0.5, 0.55), feno, cena, [-3.8, 0.25, 1.4], [0, 20, 0]);
  m(new THREE.BoxGeometry(0.9, 0.5, 0.55), feno, cena, [-3.6, 0.75, 1.35], [0, 5, 0]);
  m(new THREE.CylinderGeometry(0.3, 0.27, 0.75, 14), toon(0x7d5432), cena, [3.7, 0.38, 1.7]);
  // muralha do castelo ao fundo
  const pedra = texturaRuido('#9c978e', '#7d786f', 256, 700, 21, [6, 16]); pedra.repeat.set(10, 2);
  const matP = toon(0xffffff, { map: pedra }), matP2 = toon(0x8a857c);
  m(new THREE.BoxGeometry(34, 5, 1.4), matP, cena, [0, 2.5, -11]);
  for (let i = 0; i < 24; i++) m(new THREE.BoxGeometry(0.7, 0.6, 1.4), matP2, cena, [-16.5 + i * 1.43, 5.3, -11]);
  for (const x of [-9, 9]) {
    m(new THREE.CylinderGeometry(1.8, 2, 8, 20), matP, cena, [x, 4, -11]);
    m(new THREE.ConeGeometry(2.3, 3, 20), toon(0x3d4f7a), cena, [x, 9.5, -11]);
    // estandarte
    m(new THREE.BoxGeometry(1.1, 2.4, 0.05), toon(0x9c2a2a), cena, [x, 4.6, -9.05]);
    m(new THREE.BoxGeometry(0.5, 0.5, 0.06), toon(0xd8b445), cena, [x, 4.9, -9.0], [0, 0, 45]);
  }
  // portão
  m(new THREE.BoxGeometry(3, 3.6, 0.3), toon(0x3a2a1e), cena, [0, 1.8, -10.25]);
  // árvores
  const r = mulberry(31);
  const folha = toon(0x4f7a3a), folha2 = toon(0x3f6630), tronco = toon(0x6b4a2e);
  for (let i = 0; i < 16; i++) {
    const a = r() * Math.PI * 2, d = 9 + r() * 9;
    const x = Math.cos(a) * d, z = Math.sin(a) * d;
    if (z < -9.5) continue;
    const s = 0.8 + r() * 0.7;
    m(new THREE.CylinderGeometry(0.12 * s, 0.16 * s, 1.4 * s, 8), tronco, cena, [x, 0.7 * s, z]);
    m(new THREE.SphereGeometry(0.9 * s, 12, 10), r() > .5 ? folha : folha2, cena, [x, 1.9 * s, z], [0, 0, 0], [1, 1.1, 1]);
    m(new THREE.SphereGeometry(0.6 * s, 10, 8), folha, cena, [x + 0.4 * s, 2.4 * s, z + .2], [0, 0, 0], [1, 1, 1]);
  }
  // montanhas
  for (let i = 0; i < 7; i++) {
    const x = -40 + i * 13 + r() * 4;
    m(new THREE.ConeGeometry(9 + r() * 5, 10 + r() * 8, 6), toon(0x8aa0b8), cena, [x, 4, -48 - r() * 6], [0, r() * 60, 0], [1, 1, 1], false);
  }
}

export function luzes(cena) {
  const sol = new THREE.DirectionalLight(0xfff0d8, 2.6);
  sol.position.set(-5, 9, 6);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  Object.assign(sol.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
  sol.shadow.bias = -0.0006;
  sol.shadow.normalBias = 0.02;
  cena.add(sol);
  cena.add(new THREE.HemisphereLight(0xd8e8ff, 0x7a6a48, 1.25));
  return sol;
}
