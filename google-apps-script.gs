/**
 * Recebe os leads da landing page do aulão e grava numa planilha Google.
 *
 * Como usar:
 * 1. Crie uma planilha no Google Sheets.
 * 2. Menu Extensões > Apps Script. Apague o conteúdo e cole este arquivo.
 * 3. Clique em Implantar > Nova implantação > tipo "App da Web".
 *    - Executar como: Eu
 *    - Quem pode acessar: Qualquer pessoa
 * 4. Autorize o acesso e copie a URL gerada (termina em /exec).
 * 5. Cole a URL em CONFIG.webhookUrl, no final do index.html.
 */

const NOME_DA_ABA = 'Leads';

const COLUNAS = [
  'data_envio', 'nome', 'email', 'whatsapp', 'objetivo', 'investimento', 'consentimento',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid',
  'pagina', 'referrer', 'evento'
];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const planilha = SpreadsheetApp.getActiveSpreadsheet();
    const aba = planilha.getSheetByName(NOME_DA_ABA) || planilha.insertSheet(NOME_DA_ABA);

    if (aba.getLastRow() === 0) {
      aba.appendRow(COLUNAS);
      aba.setFrozenRows(1);
    }

    const p = (e && e.parameter) || {};
    const linha = COLUNAS.map(function (coluna) {
      if (coluna === 'data_envio') return new Date();
      return p[coluna] || '';
    });
    aba.appendRow(linha);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
