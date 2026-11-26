// Cenários dos episódios em 3D (mesmos nomes de cenário do kit: palacio, campo, quarto_gamer, floresta, aldeia, porao, templo...).
// Cada cenário é um grupo com as próprias luzes; o palco fica em volta de (0,0,0), personagens em x de -2,2 a 2,2, câmera em +Z.
import * as THREE from 'three';
import { toon, DEG, mulberry } from './personagem.js';
import { campoDeTreino, luzes as luzesDia, ceu } from './cenario.js';

function m(geo, mat, pai, pos = [0, 0, 0], rot = [0, 0, 0], esc = [1, 1, 1], sombra = true) {
  const o = new THREE.Mesh(geo, mat);
  o.position.set(...pos); o.rotation.set(rot[0] * DEG, rot[1] * DEG, rot[2] * DEG); o.scale.set(...esc);
  o.castShadow = sombra; o.receiveShadow = true; pai.add(o); return o;
}
function ruido(cor1, cor2, rep, seed = 3, manchas = 900, tam = [3, 10]) {
  const n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  const g = c.getContext('2d'); g.fillStyle = cor1; g.fillRect(0, 0, n, n);
  const r = mulberry(seed);
  for (let i = 0; i < manchas; i++) { g.fillStyle = cor2; g.globalAlpha = 0.2 + r() * 0.35; const s = tam[0] + r() * (tam[1] - tam[0]); g.beginPath(); g.ellipse(r() * n, r() * n, s, s * (0.4 + r() * 0.6), r() * 3, 0, Math.PI * 2); g.fill(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.repeat.set(...rep); return t;
}
function lajotas(cor1, cor2, rep) {
  const n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  const g = c.getContext('2d'); g.fillStyle = cor1; g.fillRect(0, 0, n, n); g.strokeStyle = cor2; g.lineWidth = 5;
  for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(0, i * 64); g.lineTo(n, i * 64); g.stroke(); }
  for (let j = 0; j < 4; j++) for (let i = 0; i <= 4; i++) { const x = i * 64 + (j % 2) * 32; g.beginPath(); g.moveTo(x, j * 64); g.lineTo(x, j * 64 + 64); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.repeat.set(...rep); return t;
}
function semContorno(o) { o.traverse(x => { if (x.material) x.material.userData.outlineParameters = { visible: false }; }); }

function tocha(g, pos, cor = 0xffa040, forca = 2.2) {
  const t = new THREE.Group(); t.position.set(...pos); g.add(t);
  m(new THREE.CylinderGeometry(0.04, 0.03, 0.4, 8), toon(0x4a3020), t, [0, 0, 0]);
  const fogo = m(new THREE.ConeGeometry(0.1, 0.28, 10), new THREE.MeshBasicMaterial({ color: 0xffb23a }), t, [0, 0.3, 0], [0, 0, 0], [1, 1, 1], false);
  semContorno(fogo);
  const luz = new THREE.PointLight(cor, forca, 7, 1.6); luz.position.set(0, 0.4, 0.2); t.add(luz);
  t.userData.fogo = fogo; t.userData.luz = luz;
  (g.userData.chamas = g.userData.chamas || []).push(t);
  return t;
}

function palacio(luz = 'dia') {
  const g = new THREE.Group(); const noite = luz === 'noite';
  const pedra = ruido('#8f877c', '#6f685e', [3, 1.2], 21, 700, [6, 16]);
  const piso = lajotas('#a49a8a', '#7d7466', [8, 8]);
  m(new THREE.PlaneGeometry(30, 30), toon(0xffffff, { map: piso }), g, [0, 0, 0], [-90, 0, 0], [1, 1, 1], false);
  // tapete vermelho até o trono
  m(new THREE.PlaneGeometry(2.2, 14), toon(0x8c1f28), g, [0, 0.005, -2], [-90, 0, 0], [1, 1, 1], false);
  for (const x of [-1.12, 1.12]) m(new THREE.PlaneGeometry(0.12, 14), toon(0xc9a13e), g, [x, 0.006, -2], [-90, 0, 0], [1, 1, 1], false);
  // paredes
  const matP = toon(0xffffff, { map: pedra });
  m(new THREE.BoxGeometry(24, 9, 0.6), matP, g, [0, 4.5, -8]);
  for (const x of [-8, 8]) m(new THREE.BoxGeometry(0.6, 9, 20), matP, g, [x, 4.5, -1]);
  // colunas
  const col = toon(0xb3aa9a);
  for (const x of [-4.2, 4.2]) for (const z of [-6, -2.8, 0.4]) {
    m(new THREE.CylinderGeometry(0.42, 0.48, 7, 16), col, g, [x, 3.5, z]);
    m(new THREE.BoxGeometry(1.1, 0.3, 1.1), col, g, [x, 0.15, z]);
    m(new THREE.BoxGeometry(1.1, 0.3, 1.1), col, g, [x, 6.9, z]);
  }
  // degraus e trono
  for (let i = 0; i < 3; i++) m(new THREE.BoxGeometry(5 - i * 0.8, 0.22, 1.6 - i * 0.3), toon(0x9b917f), g, [0, 0.11 + i * 0.22, -6.6 + i * 0.15]);
  const ouro = toon(0xc9a13e), veludo = toon(0x7a1a26);
  const tr = new THREE.Group(); tr.position.set(0, 0.66, -6.8); g.add(tr);
  m(new THREE.BoxGeometry(1.1, 0.5, 0.9), ouro, tr, [0, 0.25, 0]);
  m(new THREE.BoxGeometry(0.9, 0.12, 0.75), veludo, tr, [0, 0.56, 0.05]);
  m(new THREE.BoxGeometry(1.1, 1.9, 0.18), ouro, tr, [0, 1.3, -0.38]);
  m(new THREE.BoxGeometry(0.85, 1.5, 0.05), veludo, tr, [0, 1.25, -0.28]);
  for (const x of [-0.5, 0.5]) m(new THREE.SphereGeometry(0.1, 10, 8), ouro, tr, [x, 2.3, -0.38]);
  // estandartes
  for (const x of [-2.6, 2.6]) {
    m(new THREE.BoxGeometry(1.2, 3.6, 0.05), toon(0x7a1a26), g, [x, 5.0, -7.65]);
    m(new THREE.BoxGeometry(0.55, 0.55, 0.06), ouro, g, [x, 5.3, -7.6], [0, 0, 45]);
  }
  // vitral ao fundo
  const vit = m(new THREE.CircleGeometry(1.4, 24), new THREE.MeshBasicMaterial({ color: noite ? 0x3b3f8a : 0xf2d9a0 }), g, [0, 6.2, -7.68], [0, 0, 0], [1, 1, 1], false);
  semContorno(vit);
  // tochas nas colunas
  for (const x of [-3.7, 3.7]) for (const z of [-2.8, 0.4]) tocha(g, [x, 2.3, z + 0.5], 0xffa040, noite ? 3.2 : 1.2);
  // luz geral
  g.add(new THREE.HemisphereLight(noite ? 0x6070b0 : 0xfff1dc, noite ? 0x1a1420 : 0x5a4a3a, noite ? 0.55 : 1.15));
  const key = new THREE.DirectionalLight(noite ? 0x9aa6ff : 0xfff0d8, noite ? 0.9 : 2.0);
  key.position.set(-4, 8, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 }); key.shadow.bias = -0.0006; key.shadow.normalBias = 0.02;
  g.add(key);
  g.userData.fundo = noite ? 0x14121c : 0x3a3128;
  g.userData.fog = [noite ? 0x14121c : 0x5a4c3c, 9, 26];
  return g;
}

function quartoGamer() {
  const g = new THREE.Group();
  m(new THREE.PlaneGeometry(20, 20), toon(0x4a3a4a), g, [0, 0, 0], [-90, 0, 0], [1, 1, 1], false);
  m(new THREE.BoxGeometry(12, 5, 0.3), toon(0x2b2840), g, [0, 2.5, -3.5]);
  m(new THREE.BoxGeometry(0.3, 5, 10), toon(0x26233a), g, [-5, 2.5, 0]);
  // mesa, monitor brilhando, cadeira gamer, cama
  m(new THREE.BoxGeometry(2.2, 0.08, 0.9), toon(0x1e1e26), g, [1.4, 0.95, -2.7]);
  for (const x of [0.4, 2.4]) m(new THREE.BoxGeometry(0.06, 0.95, 0.8), toon(0x1e1e26), g, [x, 0.48, -2.7]);
  const tela = m(new THREE.PlaneGeometry(1.2, 0.7), new THREE.MeshBasicMaterial({ color: 0x8a5cff }), g, [1.4, 1.5, -3.0], [0, 0, 0], [1, 1, 1], false);
  semContorno(tela);
  m(new THREE.BoxGeometry(1.28, 0.78, 0.05), toon(0x111118), g, [1.4, 1.5, -3.04]);
  const lt = new THREE.PointLight(0x8a5cff, 3.5, 6, 1.5); lt.position.set(1.4, 1.5, -2.4); g.add(lt);
  const cad = new THREE.Group(); cad.position.set(1.2, 0, -1.7); g.add(cad);
  m(new THREE.BoxGeometry(0.6, 0.1, 0.6), toon(0xb3261e), cad, [0, 0.55, 0]);
  m(new THREE.BoxGeometry(0.6, 0.9, 0.1), toon(0xb3261e), cad, [0, 1.05, 0.3]);
  m(new THREE.CylinderGeometry(0.04, 0.04, 0.5, 8), toon(0x111111), cad, [0, 0.27, 0]);
  m(new THREE.BoxGeometry(1.8, 0.45, 2.4), toon(0x3a3d6a), g, [-3.6, 0.23, -1.6]);
  m(new THREE.BoxGeometry(1.8, 0.12, 2.4), toon(0xdcdce8), g, [-3.6, 0.5, -1.6]);
  // fita de LED
  const led = m(new THREE.BoxGeometry(11.5, 0.05, 0.05), new THREE.MeshBasicMaterial({ color: 0x00e5ff }), g, [0, 4.6, -3.33], [0, 0, 0], [1, 1, 1], false);
  semContorno(led);
  g.add(new THREE.HemisphereLight(0x8070c0, 0x201828, 0.7));
  const key = new THREE.DirectionalLight(0xb8a8ff, 1.0); key.position.set(-3, 6, 5); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); g.add(key);
  g.userData.fundo = 0x15131f; g.userData.fog = [0x15131f, 8, 22];
  return g;
}

function floresta(luz = 'dia') {
  const g = new THREE.Group(); const noite = luz === 'noite';
  ceu(g, noite ? 0x0e1430 : 0x6fa4d8, noite ? 0x2a2a4a : 0xf3e2c4);
  const chao = ruido('#5f7d3a', '#4a6430', [20, 20], 5, 1400);
  m(new THREE.PlaneGeometry(120, 120), toon(0xffffff, { map: chao }), g, [0, 0, 0], [-90, 0, 0], [1, 1, 1], false);
  m(new THREE.PlaneGeometry(2.4, 40), toon(0x9c7a52), g, [0.4, 0.004, -10], [-90, 0, 12], [1, 1, 1], false);
  const r = mulberry(41), tronco = toon(0x5a3e28);
  const folhas = [toon(0x2f5a2a), toon(0x3f6b33), toon(0x2a4a2a)];
  for (let i = 0; i < 70; i++) {
    const x = (r() - 0.5) * 50, z = -3 - r() * 30;
    if (Math.abs(x) < 3 && z > -8) continue;
    const s = 0.8 + r() * 1.1;
    m(new THREE.CylinderGeometry(0.12 * s, 0.2 * s, 2 * s, 8), tronco, g, [x, s, z]);
    for (let j = 0; j < 3; j++) m(new THREE.ConeGeometry((1.3 - j * 0.3) * s, 1.6 * s, 9), folhas[(i + j) % 3], g, [x, (2 + j * 0.9) * s, z]);
  }
  for (const [x, z] of [[-4.5, 1.2], [4.8, 0.8], [-5.5, -1.5], [5.6, -2]]) {
    m(new THREE.CylinderGeometry(0.22, 0.3, 3, 8), tronco, g, [x, 1.5, z]);
    m(new THREE.ConeGeometry(1.6, 2.4, 9), folhas[0], g, [x, 3.6, z]);
  }
  for (let i = 0; i < 12; i++) m(new THREE.DodecahedronGeometry(0.2 + r() * 0.3), toon(0x8a8a86), g, [(r() - 0.5) * 12, 0.1, -1 - r() * 6]);
  if (noite) {
    g.add(new THREE.HemisphereLight(0x5a6aa8, 0x101018, 0.55));
    const lua = new THREE.DirectionalLight(0x9db0ff, 1.0); lua.position.set(-5, 9, 4); lua.castShadow = true; lua.shadow.mapSize.set(2048, 2048);
    Object.assign(lua.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 }); g.add(lua);
    g.userData.fog = [0x10142a, 6, 30];
  } else { luzesDia(g); g.userData.fog = [0xcfe0d0, 12, 50]; }
  return g;
}

function aldeia(luz = 'dia') {
  const g = new THREE.Group(); const noite = luz === 'noite';
  ceu(g, noite ? 0x0e1430 : 0x6fa4d8, noite ? 0x2a2a4a : 0xf3e2c4);
  m(new THREE.PlaneGeometry(120, 120), toon(0xffffff, { map: ruido('#7d9a4e', '#5f7d3a', [30, 30], 3, 1400) }), g, [0, 0, 0], [-90, 0, 0], [1, 1, 1], false);
  m(new THREE.PlaneGeometry(40, 3.2), toon(0xffffff, { map: ruido('#b89466', '#9c7a52', [10, 1], 8) }), g, [0, 0.004, -0.5], [-90, 0, 0], [1, 1, 1], false);
  const r = mulberry(19);
  const paredes = [0xe8dcc0, 0xd9c7a2, 0xcbb592], telhados = [0x8a3a2a, 0x6a3a28, 0x5a4a3a];
  const casas = [[-5, -4.5], [-1.5, -5.2], [2.2, -4.8], [5.6, -4.2], [-7.5, -1.5], [7.8, -1.0]];
  casas.forEach(([x, z], i) => {
    const w = 2 + r() * 1, h = 1.8 + r() * 0.6, d = 2 + r() * 0.6;
    const c = new THREE.Group(); c.position.set(x, 0, z); c.rotation.y = (r() - 0.5) * 0.4; g.add(c);
    m(new THREE.BoxGeometry(w, h, d), toon(paredes[i % 3]), c, [0, h / 2, 0]);
    const tel = m(new THREE.ConeGeometry(Math.max(w, d) * 0.78, 1.3, 4), toon(telhados[i % 3]), c, [0, h + 0.65, 0], [0, 45, 0]);
    m(new THREE.BoxGeometry(0.5, 0.9, 0.05), toon(0x5a3a22), c, [0, 0.45, d / 2 + 0.01]);
    const jan = m(new THREE.BoxGeometry(0.4, 0.35, 0.05), new THREE.MeshBasicMaterial({ color: noite ? 0xffc46a : 0x3a4a5a }), c, [w * 0.28, h * 0.62, d / 2 + 0.01], [0, 0, 0], [1, 1, 1], false);
    semContorno(jan);
  });
  m(new THREE.CylinderGeometry(0.7, 0.75, 0.7, 18), toon(0x8f877c), g, [3.2, 0.35, -1.8]);
  if (noite) {
    g.add(new THREE.HemisphereLight(0x5a6aa8, 0x101018, 0.6));
    const lua = new THREE.DirectionalLight(0x9db0ff, 1.0); lua.position.set(-5, 9, 4); lua.castShadow = true; g.add(lua);
    tocha(g, [-2.6, 1.6, -1.6]); tocha(g, [2.6, 1.6, -1.6]);
    g.userData.fog = [0x10142a, 8, 34];
  } else { luzesDia(g); g.userData.fog = [0xe9dcc2, 14, 60]; }
  return g;
}

function masmorra() {
  const g = new THREE.Group();
  const pedra = ruido('#4a4650', '#34313a', [6, 2], 33, 900, [6, 16]);
  m(new THREE.PlaneGeometry(30, 30), toon(0xffffff, { map: lajotas('#4f4a52', '#2f2c34', [8, 8]) }), g, [0, 0, 0], [-90, 0, 0], [1, 1, 1], false);
  const matP = toon(0xffffff, { map: pedra });
  m(new THREE.BoxGeometry(20, 6, 0.6), matP, g, [0, 3, -5]);
  for (const x of [-6, 6]) m(new THREE.BoxGeometry(0.6, 6, 14), matP, g, [x, 3, 0]);
  // grades
  for (let i = 0; i < 9; i++) m(new THREE.CylinderGeometry(0.035, 0.035, 2.6, 6), toon(0x2a2a30), g, [-5.4 + i * 0.25, 1.3, -3.2]);
  m(new THREE.BoxGeometry(2.3, 0.08, 0.08), toon(0x2a2a30), g, [-4.4, 2.55, -3.2]);
  // correntes e barris
  m(new THREE.CylinderGeometry(0.3, 0.27, 0.75, 14), toon(0x5a3e28), g, [4.2, 0.38, -3.6]);
  tocha(g, [-2.5, 2.2, -4.6], 0xff8a30, 3.5); tocha(g, [2.5, 2.2, -4.6], 0xff8a30, 3.5);
  g.add(new THREE.HemisphereLight(0x50506a, 0x0a0810, 0.45));
  const key = new THREE.DirectionalLight(0x8090c0, 0.6); key.position.set(-3, 7, 5); key.castShadow = true; g.add(key);
  g.userData.fundo = 0x0c0a10; g.userData.fog = [0x0c0a10, 6, 18];
  return g;
}

function templo(luz = 'dia') {
  const g = palacio(luz);
  // troca o trono por um altar com cristal roxo
  const altar = new THREE.Group(); altar.position.set(0, 0, -5.2); g.add(altar);
  m(new THREE.BoxGeometry(1.6, 1, 0.9), toon(0x8f877c), altar, [0, 0.5, 0]);
  const cristal = m(new THREE.OctahedronGeometry(0.4), new THREE.MeshBasicMaterial({ color: 0xa070ff }), altar, [0, 1.6, 0], [0, 0, 0], [1, 1.6, 1], false);
  semContorno(cristal);
  const l = new THREE.PointLight(0xa070ff, 4, 8, 1.4); l.position.set(0, 1.6, 0.4); altar.add(l);
  return g;
}

const MAPA = {
  palacio: palacio, castelo: palacio, sala: palacio, trono: palacio,
  campo: (luz) => { const g = new THREE.Group(); campoDeTreino(g); luzesDia(g); g.userData.fog = [0xe9dcc2, 14, 60]; return g; },
  treino: null, quarto_gamer: quartoGamer, quarto: quartoGamer,
  floresta: floresta, deserto: floresta, aldeia: aldeia, cidade: aldeia, rua_noite: (l) => aldeia('noite'), mar: aldeia,
  porao: masmorra, masmorra: masmorra, caverna: masmorra, templo: templo, escola: palacio, cozinha: aldeia,
};
MAPA.treino = MAPA.campo;

export function criarCenario(nome, luz) {
  const f = MAPA[nome] || MAPA.palacio;
  const g = f(luz || 'dia');
  g.userData.nome = nome;
  return g;
}

// chamas tremendo (chame a cada quadro)
export function animarCenario(g, t) {
  for (const c of g.userData.chamas || []) {
    const k = 1 + 0.12 * Math.sin(t * 23 + c.position.x * 3) + 0.08 * Math.sin(t * 37 + c.position.z);
    c.userData.fogo.scale.set(1, k, 1);
    c.userData.luz.intensity = c.userData.luz.userData.base ?? (c.userData.luz.userData.base = c.userData.luz.intensity);
    c.userData.luz.intensity = c.userData.luz.userData.base * (0.85 + 0.15 * k);
  }
}
