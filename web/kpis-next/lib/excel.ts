/**
 * Excel Export Utilities
 * Export KPI data and reports to Excel format
 */

export interface ExcelExportOptions {
  filename?: string;
  sheetName?: string;
}

/**
 * Convert data array to CSV format
 */
export function arrayToCSV(data: any[], headers?: string[]): string {
  if (!data || data.length === 0) {
    return '';
  }

  const keys = headers || Object.keys(data[0]);
  const csvHeaders = keys.join(',');
  
  const csvRows = data.map(row => {
    return keys.map(key => {
      const value = row[key];
      // Escape commas and quotes
      if (value === null || value === undefined) return '';
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    }).join(',');
  });

  return [csvHeaders, ...csvRows].join('\n');
}

/**
 * Generate Excel-compatible TSV (Tab-Separated Values)
 * Better compatibility than CSV for Excel
 */
export function arrayToTSV(data: any[], headers?: string[]): string {
  if (!data || data.length === 0) {
    return '';
  }

  const keys = headers || Object.keys(data[0]);
  const tsvHeaders = keys.join('\t');
  
  const tsvRows = data.map(row => {
    return keys.map(key => {
      const value = row[key];
      if (value === null || value === undefined) return '';
      return String(value).replace(/\t/g, ' ').replace(/\n/g, ' ');
    }).join('\t');
  });

  return [tsvHeaders, ...tsvRows].join('\n');
}

/**
 * Generate Excel file content (XML format - Excel 2003+ compatible)
 */
export function generateExcelXML(data: any[], options: ExcelExportOptions = {}): string {
  const sheetName = options.sheetName || 'Sheet1';
  const keys = data.length > 0 ? Object.keys(data[0]) : [];

  const xmlHeader = `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <Worksheet ss:Name="${sheetName}">
  <Table>`;

  const xmlHeaders = keys.length > 0 
    ? `   <Row>\n${keys.map(key => `    <Cell><Data ss:Type="String">${escapeXML(key)}</Data></Cell>`).join('\n')}\n   </Row>`
    : '';

  const xmlRows = data.map(row => {
    return `   <Row>\n${keys.map(key => {
      const value = row[key];
      if (value === null || value === undefined) {
        return '    <Cell><Data ss:Type="String"></Data></Cell>';
      }
      const numValue = Number(value);
      const type = !isNaN(numValue) && isFinite(value) && numValue.toString() === String(value).trim() 
        ? 'Number' 
        : 'String';
      return `    <Cell><Data ss:Type="${type}">${escapeXML(String(value))}</Data></Cell>`;
    }).join('\n')}\n   </Row>`;
  }).join('\n');

  const xmlFooter = `  </Table>
 </Worksheet>
</Workbook>`;

  return xmlHeader + '\n' + xmlHeaders + '\n' + xmlRows + '\n' + xmlFooter;
}

function escapeXML(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Download data as Excel file (browser-side)
 */
export function downloadExcel(
  data: any[],
  options: ExcelExportOptions = {}
): void {
  if (typeof window === 'undefined') {
    throw new Error('downloadExcel can only be called in the browser');
  }

  const filename = options.filename || `report-${new Date().toISOString().split('T')[0]}.xls`;
  const excelContent = generateExcelXML(data, options);
  const blob = new Blob([excelContent], { type: 'application/vnd.ms-excel' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Download data as CSV file (browser-side)
 */
export function downloadCSV(
  data: any[],
  filename?: string
): void {
  if (typeof window === 'undefined') {
    throw new Error('downloadCSV can only be called in the browser');
  }

  const csvContent = arrayToCSV(data);
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || `report-${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}


