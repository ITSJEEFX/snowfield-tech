# SnowField Tech

App de campo para técnicos de refrigeração e climatização: comissionamento com cálculo de superaquecimento e sub-resfriamento, manutenção preventiva com checklist, manutenção corretiva, cadastro de clientes e equipamentos, relatório em PDF e envio pelo WhatsApp.

É um app web instalável (PWA): abre pelo navegador, instala na tela inicial do Android e do iPhone e funciona sem internet.

## Como instalar no celular

- **Android (Chrome):** abra o endereço do app e toque em **Instalar** no cartão da tela inicial, ou no menu ⋮ › *Instalar app*.
- **iPhone (Safari):** abra o endereço, toque em **Compartilhar** › **Adicionar à Tela de Início** › **Adicionar**.

## Onde ficam os dados

Ordens, clientes, fotos e configurações ficam salvos **somente no aparelho** do técnico. Nada é enviado a servidores. Os relatórios saem em PDF e podem ser enviados para o Google Drive ou o iCloud pela tela de compartilhar do celular.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `index.html` | O app inteiro |
| `sw.js` | Guarda o app no aparelho para abrir sem internet e avisa quando há versão nova |
| `manifest.webmanifest` | Nome, ícone e cores do app instalado |
| `vendor/jspdf.umd.min.js` | Gerador de PDF ([jsPDF](https://github.com/parallax/jsPDF), licença MIT) |
| `fonts/` | Fonte Inter ([licença SIL Open Font](https://github.com/rsms/inter/blob/master/LICENSE.txt)) |
| `icons/` | Ícones do app |
| `build.py` | Gera `index.html`, `sw.js` e o manifesto a partir do arquivo do app |

## Publicar uma versão nova

1. Rode `python3 build.py caminho/do/app.html`.
2. Envie os arquivos para a branch `main`. O GitHub Pages publica sozinho.
3. Quem já tem o app instalado vê o aviso **Nova versão do app disponível** e toca em **Atualizar**.
