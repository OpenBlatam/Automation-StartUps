// Panel combinado – Auto-refresh KPIs cada 6 horas

function refreshPanelCombinado() {
  const ss = SpreadsheetApp.getActive();
  const panelSheetNames = [
    'Panel_Combinado',   // hoja sugerida para panel_combinado.csv
    'Panel',             // por si integran ROI en una sola hoja
    'ROI_Snapshot'       // hoja del snapshot de ROI
  ];

  // Fuerza recálculo suave tocando A1 si existe; luego flush
  panelSheetNames.forEach((name) => {
    const sh = ss.getSheetByName(name);
    if (!sh) return;
    try {
      const a1 = sh.getRange(1, 1);
      a1.setValue(a1.getValue());
    } catch (e) {
      // no-op
    }
  });

  // Opcional: vuelve a aplicar fórmulas en tarjetas si usas posiciones fijas
  // Ejemplo seguro (comenta/ajusta según tu layout):
  // const panel = ss.getSheetByName('Panel_Combinado');
  // if (panel) {
  //   panel.getRange('D2').setFormula('=IFERROR(Resumen!B2,"")');
  // }

  SpreadsheetApp.flush();
}

// Crea un disparador time-driven cada 6 horas
function createRefreshTrigger() {
  deleteRefreshTriggers();
  ScriptApp.newTrigger('refreshPanelCombinado')
    .timeBased()
    .everyHours(6)
    .create();
}

// Elimina disparadores existentes para evitar duplicados
function deleteRefreshTriggers() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'refreshPanelCombinado')
    .forEach(ScriptApp.deleteTrigger);
}

// Ejecuta una vez para probar manualmente
function refreshNow() {
  refreshPanelCombinado();
}

// Menú en la barra de Sheets para acceso rápido
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Panel')
    .addItem('Refrescar ahora', 'refreshNow')
    .addItem('Validar panel combinado', 'validatePanelCombinado')
    .addItem('Exportar PDF (Ejecutivo)', 'exportExecutivePanelPdfNow')
    .addItem('Programar refresh cada 6h', 'createRefreshTrigger')
    .addItem('Programar PDF semanal (Ejecutivo)', 'createWeeklyPdfTrigger')
    .addItem('Eliminar triggers de refresh', 'deleteRefreshTriggers')
    .addToUi();
}

// Valida hojas y referencias mínimas del Panel combinado
function validatePanelCombinado() {
  const ss = SpreadsheetApp.getActive();
  const report = [];

  const requiredSheets = ['Panel_Combinado', 'ROI_Snapshot'];
  requiredSheets.forEach(name => {
    const exists = !!ss.getSheetByName(name);
    report.push(`${exists ? '✅' : '❌'} Hoja "${name}" ${exists ? 'encontrada' : 'no existe'}`);
  });

  // Checks simples de celdas clave (si existen)
  const roiSh = ss.getSheetByName('ROI_Snapshot');
  if (roiSh) {
    try {
      const roiLabel = roiSh.createTextFinder('ROI mensual').matchCase(false).findNext();
      report.push(roiLabel ? '✅ ROI_Snapshot contiene "ROI mensual"' : '❌ Falta métrica "ROI mensual" en ROI_Snapshot');
    } catch (e) {
      report.push('❌ Error inspeccionando ROI_Snapshot');
    }
  }

  const panelSh = ss.getSheetByName('Panel_Combinado');
  if (panelSh) {
    // Heurística: buscar palabras clave esperadas
    const keys = ['Completadas', 'Vencidas'];
    keys.forEach(k => {
      try {
        const found = panelSh.createTextFinder(k).matchCase(false).findNext();
        report.push(found ? `✅ Panel_Combinado contiene "${k}"` : `⚠️ No se encontró "${k}" (verifica etiquetas)`);
      } catch (e) {
        report.push(`❌ Error buscando "${k}" en Panel_Combinado`);
      }
    });
  }

  SpreadsheetApp.getUi().alert('Validación Panel Combinado', report.join('\n'), SpreadsheetApp.getUi().ButtonSet.OK);
}

// Nota: Si deseas llevar un checklist de vistas/slicers, puedes marcar una hoja "Checklist"
// y escribir allí la última validación (fecha/resultado). Ejemplo:
// function logValidation_() {
//   const ss = SpreadsheetApp.getActive();
//   const sh = ss.getSheetByName('Checklist') || ss.insertSheet('Checklist');
//   sh.appendRow(['Validación Panel', new Date(), 'OK']);
// }

// ===== Exportación PDF semanal del Panel Ejecutivo =====
function exportExecutivePanelPdfNow() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName('Ejecutivo') || ss.getSheetByName('Panel_Combinado');
  if (!sheet) {
    SpreadsheetApp.getUi().alert('No se encontró hoja "Ejecutivo" ni "Panel_Combinado" para exportar.');
    return;
  }
  const pdfBlob = _exportSheetToPdfBlob_(ss.getId(), sheet.getSheetId(), 'Panel_Ejecutivo');
  // TODO: Ajusta destinatarios
  const recipients = 'ops@tuempresa.com';
  GmailApp.sendEmail(recipients, 'Panel Ejecutivo – Snapshot semanal', 'Adjunto PDF del panel ejecutivo.', { attachments: [pdfBlob] });
}

function createWeeklyPdfTrigger() {
  // Viernes 9:00 (ajusta si prefieres otro día/hora)
  ScriptApp.newTrigger('exportExecutivePanelPdfNow')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.FRIDAY)
    .atHour(9)
    .create();
}

function _exportSheetToPdfBlob_(spreadsheetId, sheetId, filenamePrefix) {
  const url = 'https://docs.google.com/spreadsheets/d/' + spreadsheetId + '/export?' +
    'format=pdf' +
    '&size=A4' +
    '&portrait=true' +
    '&fitw=true' +
    '&sheetnames=false&printtitle=false&pagenumbers=true' +
    '&gridlines=false' +
    '&fzr=true' +
    '&gid=' + sheetId;
  const token = ScriptApp.getOAuthToken();
  const response = UrlFetchApp.fetch(url, { headers: { Authorization: 'Bearer ' + token } });
  const blob = response.getBlob().setName((filenamePrefix || 'Panel') + '_' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyyMMdd_HHmm') + '.pdf');
  return blob;
}


