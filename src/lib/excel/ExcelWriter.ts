import ExcelJS from 'exceljs';
import { OrderRow } from '../types/order';
import { reportTemplateColumns } from '@/config/fieldConfig';

export async function generateExcelReport(rows: OrderRow[], fileName: string): Promise<Blob> {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('出貨報告');

  worksheet.columns = reportTemplateColumns.map((header, index) => ({
    header,
    key: header,
    width: calculateColumnWidth(header),
  }));

  const headerRow = worksheet.getRow(1);
  headerRow.font = { name: '微軟正黑體', size: 11, bold: true };
  headerRow.alignment = { vertical: 'middle', horizontal: 'center', wrapText: true };
  headerRow.height = 60;

  for (const row of rows) {
    const rowData: Record<string, string> = {};
    for (const col of reportTemplateColumns) {
      rowData[col] = (row as Record<string, string>)[col] || '';
    }
    const excelRow = worksheet.addRow(rowData);

    excelRow.eachCell((cell) => {
      cell.font = { name: '微軟正黑體', size: 11 };
      cell.alignment = { vertical: 'middle', horizontal: 'left', wrapText: true };

      const value = String(cell.value || '');
      if (value.includes('ERROR') || value.toLowerCase() === 'nan') {
        cell.font = { name: '微軟正黑體', size: 11, bold: true, color: { argb: 'FFFF0000' } };
      }
    });

    const lineCount = Math.max(
      ...Object.values(rowData).map(v => (String(v).match(/\n/g) || []).length + 1)
    );
    excelRow.height = Math.max(20, lineCount * 15);
  }

  worksheet.columns.forEach((column) => {
    if (column.width && column.width > 50) {
      column.width = 50;
    }
  });

  const buffer = await workbook.xlsx.writeBuffer();
  return new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
}

function calculateColumnWidth(header: string): number {
  const lines = header.split('\n');
  const maxLength = Math.max(...lines.map(line => line.length));
  return Math.min(Math.max(maxLength * 2 + 2, 10), 50);
}

export function downloadBlob(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName.endsWith('.xlsx') ? fileName : `${fileName}.xlsx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
