// Renderiza uma página do motor 3D quadro a quadro. Uso:
//   node servidor.js pagina.html saida_dir inicio fim [fps]   -> PNGs (ou "-" em saida_dir para mandar para o ffmpeg via stdout)
//   node servidor.js pagina.html still t arquivo.png
const { chromium } = require('playwright'); const http = require('http'); const fs = require('fs'); const path = require('path');
const raiz = __dirname;
const tipos = { '.js': 'application/javascript', '.html': 'text/html', '.png': 'image/png', '.json': 'application/json', '.glb': 'model/gltf-binary', '.jpg': 'image/jpeg' };
function servir() {
  return new Promise(ok => {
    const srv = http.createServer((q, res) => {
      const f = path.join(raiz, decodeURIComponent(q.url.split('?')[0]));
      fs.readFile(f, (e, d) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'Content-Type': tipos[path.extname(f)] || 'application/octet-stream' }); res.end(d); });
    }).listen(0, () => ok(srv));
  });
}
(async () => {
  const [pagina, modo, a, b, fpsArg] = process.argv.slice(2);
  const srv = await servir();
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await br.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('console', m => { if (!m.text().includes('GPU stall')) console.error('[pag]', m.text()); });
  p.on('pageerror', e => console.error('[erro]', e.message));
  await p.goto(`http://localhost:${srv.address().port}/${pagina}`);
  await p.waitForFunction('window.pronto === true', null, { timeout: 120000 });
  if (modo === 'still') {
    await p.evaluate(t => window.quadro(t), parseFloat(a));
    fs.writeFileSync(b, await p.screenshot({ type: 'png' }));
  } else {
    const fps = parseFloat(fpsArg || '30');
    const i0 = Math.round(parseFloat(a) * fps), i1 = Math.round(parseFloat(b) * fps);
    if (modo !== '-') fs.mkdirSync(modo, { recursive: true });
    const t0 = Date.now();
    for (let i = i0; i < i1; i++) {
      await p.evaluate(t => window.quadro(t), i / fps);
      const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
      if (modo === '-') { if (!process.stdout.write(buf)) await new Promise(r => process.stdout.once('drain', r)); }
      else fs.writeFileSync(path.join(modo, `q${String(i).padStart(5, '0')}.jpg`), buf);
      if (i % 30 === 0) console.error(`quadro ${i} (${((Date.now() - t0) / (i - i0 + 1)).toFixed(0)} ms/quadro)`);
    }
  }
  await br.close(); srv.close();
})();
