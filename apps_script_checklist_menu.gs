function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Checklist')
    .addItem('Ir a HOY', 'goToTodayView')
    .addItem('Marcar Due Date = HOY', 'setDueToday')
    .addToUi();
}

function goToTodayView() {
  const ss = SpreadsheetApp.getActive();
  const todaySheet = ss.getSheetByName('Hoy');
  if (todaySheet) {
    ss.setActiveSheet(todaySheet);
    return;
  }
  const source = ss.getSheetByName('Origen');
  if (!source) {
    SpreadsheetApp.getUi().alert('No existe hoja Origen. Renombra tu hoja de datos a "Origen" o ajusta el script.');
    return;
  }
  const sheet = ss.insertSheet('Hoy');
  const headers = source.getRange(1, 1, 1, source.getLastColumn()).getValues();
  sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
  const formula = '=FILTER(Origen!A2:I, (Origen!F:F = TODAY()) + ((Origen!F:F < TODAY()) * (Origen!D:D <> "Done")))';
  sheet.getRange(2, 1).setFormula(formula);
}

function setDueToday() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  if (!range) return;
  const values = range.getValues();
  const today = new Date();
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[0].length; c++) {
      // Busca la columna due_date por encabezado en la fila 1
      const header = sheet.getRange(1, c + 1).getValue();
      if (header === 'due_date') {
        sheet.getRange(range.getRow() + r, c + 1).setValue(today);
      }
    }
  }
}
