#!/usr/bin/env python3
"""Gera o app instalável (PWA) do SnowField Tech a partir do arquivo do app no Claude.

Uso: python3 build.py [caminho/do/snowtech-campo.html]
Saída: index.html, sw.js e manifest.webmanifest nesta pasta.
"""
import hashlib, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/snow/snowtech-campo.html'
src = open(FONTE, encoding='utf-8').read()

# 1) conteúdo da página (tudo depois do <body> do esqueleto do Claude)
corpo = src.split('<body>', 1)[1] if '<body>' in src else src
corpo = corpo.replace('</body></html>', '')
corpo = re.sub(r'<title>.*?</title>\n?', '', corpo, count=1)
corpo = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', '', corpo)
corpo = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com/[^"]*">\n?', '', corpo)
assert 'cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js' in corpo, 'script do jsPDF não encontrado'
corpo = corpo.replace('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js', 'vendor/jspdf.umd.min.js')

FONTES = ''.join(
    f"@font-face{{font-family:'Inter';font-style:normal;font-weight:{w};font-display:swap;"
    f"src:url(fonts/inter-latin-{w}-normal.woff2) format('woff2')}}"
    for w in (400, 500, 600, 700))

# 2) instalação, atualização e modo sem internet (só no app próprio)
PWA_JS = r"""<script>
(function(){
'use strict';
var $=function(s){return document.querySelector(s)};
var guardado=function(k){try{return localStorage.getItem(k)}catch(e){return null}};
var guardar=function(k,v){try{localStorage.setItem(k,v)}catch(e){}};
var instalado=matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
var ios=/iphone|ipad|ipod/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
var pedido=null;

/* cartão "Instale o app" no topo da tela inicial */
function pintar(){
  var c=$('#instalar');
  if(instalado||guardado('sf-instalar-dispensado')||(!pedido&&!ios)){if(c)c.remove();return}
  var main=$('.home .hm-main');if(!main||c)return;
  var s=document.createElement('section');s.id='instalar';s.className='space';
  s.innerHTML='<div><b>Instale o SnowField Tech</b><span>Abre como app, funciona sem internet e guarda seus dados com segurança.</span></div>'+
    '<button class="btn primary" id="btnInstalar">Instalar</button>'+
    '<button class="ck-x" id="btnInstalarX" aria-label="Agora não"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>';
  main.insertBefore(s,main.firstChild);
}
document.addEventListener('click',function(e){
  if(e.target.closest('#btnInstalarX')){guardar('sf-instalar-dispensado','1');pintar();return}
  if(!e.target.closest('#btnInstalar'))return;
  if(pedido){pedido.prompt();pedido.userChoice.then(function(r){if(r&&r.outcome==='accepted'){pedido=null;pintar()}});return}
  var m=$('#modal');
  m.innerHTML='<div class="glass" role="dialog" aria-modal="true" aria-labelledby="it"><h2 id="it" class="h2">Instalar no iPhone</h2>'+
    '<ol class="passos"><li>Abra este endereço no <b>Safari</b>.</li><li>Toque em <b>Compartilhar</b>, o quadrado com a seta para cima.</li><li>Role e toque em <b>Adicionar à Tela de Início</b>.</li><li>Toque em <b>Adicionar</b>. O ícone do floco aparece na tela inicial.</li></ol>'+
    '<p class="note">Instalado, o iPhone não apaga os dados do app por falta de uso.</p><div class="acts"><button class="btn primary" data-m="no">Entendi</button></div></div>';
  m.hidden=false;m.onclick=function(ev){if(ev.target===m||ev.target.closest('[data-m]'))m.hidden=true};
});
window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();pedido=e;pintar()});
window.addEventListener('appinstalled',function(){instalado=true;pedido=null;pintar()});
new MutationObserver(pintar).observe($('#app'),{childList:true});

/* nova versão: avisa e atualiza quando o técnico tocar */
if('serviceWorker' in navigator&&location.protocol!=='file:'){
  var recarregando=false;
  navigator.serviceWorker.addEventListener('controllerchange',function(){if(recarregando)return;recarregando=true;location.reload()});
  function aviso(reg){
    if($('#novaVersao'))return;
    var d=document.createElement('div');d.id='novaVersao';d.className='nova-versao';d.setAttribute('role','status');
    d.innerHTML='<span>Nova versão do app disponível.</span><button class="btn primary">Atualizar</button>';
    d.querySelector('button').onclick=function(){this.disabled=true;this.textContent='Atualizando…';setTimeout(function(){if(reg.waiting)reg.waiting.postMessage('atualizar')},700)};
    document.body.appendChild(d);
  }
  window.addEventListener('load',function(){
    navigator.serviceWorker.register('./sw.js').then(function(reg){
      if(reg.waiting&&navigator.serviceWorker.controller)aviso(reg);
      reg.addEventListener('updatefound',function(){var w=reg.installing;if(!w)return;w.addEventListener('statechange',function(){if(w.state==='installed'&&navigator.serviceWorker.controller)aviso(reg)})});
      setInterval(function(){reg.update()},60*60*1000);
      document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')reg.update()});
    }).catch(function(){});
  });
}
})();
</script>"""

PWA_CSS = """<style>
.nova-versao{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:35;width:min(440px,calc(100% - 32px));display:flex;align-items:center;gap:12px;padding:10px 10px 10px 16px;border-radius:18px;background:#14272F;border:1px solid var(--accent-line);box-shadow:0 10px 30px rgba(0,0,0,.4);font-size:14px;font-weight:500}
.nova-versao span{flex:1}
.nova-versao .btn{min-height:42px;padding:0 16px;font-size:14px}
#instalar .btn{min-height:42px;padding:0 16px;font-size:14px;flex:none}
#instalar .ck-x{margin:0}
.passos{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:8px;color:var(--soft)}
</style>"""

HEAD = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>SnowField Tech</title>
<meta name="description" content="Comissionamento, preventiva e manutenção de refrigeração e climatização, com relatórios em PDF.">
<meta name="theme-color" content="#0C1A21">
<meta name="color-scheme" content="dark">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="SnowField">
<link rel="preload" href="fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/inter-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>:root{{color-scheme:dark;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}html{{scroll-padding-top:env(safe-area-inset-top,0px);background:#0C1A21}}body{{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#0C1A21;color:#EEF5F8}}img{{max-width:100%}}[hidden]:not([hidden=until-found i]){{display:none!important}}{FONTES}</style>
</head>
<body>
"""

html = HEAD + corpo.strip() + '\n' + PWA_CSS + '\n' + PWA_JS + '\n</body>\n</html>\n'
open(os.path.join(AQUI, 'index.html'), 'w', encoding='utf-8').write(html)

# 3) manifesto
manifest = {
    "name": "SnowField Tech",
    "short_name": "SnowField",
    "description": "Comissionamento, preventiva e manutenção de refrigeração e climatização, com relatórios em PDF.",
    "lang": "pt-BR",
    "id": "./",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0C1A21",
    "theme_color": "#0C1A21",
    "categories": ["business", "productivity", "utilities"],
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
open(os.path.join(AQUI, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

# 4) service worker: a versão muda sempre que algum arquivo do app muda
ARQS = ['index.html', 'manifest.webmanifest', 'vendor/jspdf.umd.min.js',
        'fonts/inter-latin-400-normal.woff2', 'fonts/inter-latin-500-normal.woff2',
        'fonts/inter-latin-600-normal.woff2', 'fonts/inter-latin-700-normal.woff2',
        'icons/icon-192.png', 'icons/icon-512.png', 'icons/maskable-512.png',
        'icons/apple-touch-icon.png', 'icons/favicon-32.png']
h = hashlib.sha256()
for a in ARQS:
    h.update(open(os.path.join(AQUI, a), 'rb').read())
versao = h.hexdigest()[:10]
sw = """/* SnowField Tech: guarda o app no aparelho para abrir sem internet. Versão gerada pelo build.py */
const VERSAO = 'snowfield-%s';
const ARQUIVOS = ['./', %s];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSAO).then(c => c.addAll(ARQUIVOS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('snowfield-') && k !== VERSAO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('message', e => { if (e.data === 'atualizar') self.skipWaiting(); });

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    /* página: usa a versão guardada desta instalação; a nova chega pelo aviso "Atualizar" */
    e.respondWith(caches.match('./index.html').then(r => r || fetch(req)));
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(r => r || fetch(req)));
});
""" % (versao, ', '.join("'./%s'" % a for a in ARQS))
open(os.path.join(AQUI, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('ok · versão', versao, '·', round(len(html) / 1024), 'KB de index.html')
