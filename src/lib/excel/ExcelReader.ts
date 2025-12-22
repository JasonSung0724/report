import * as XLSX from 'xlsx';
import { RawOrderData, Platform } from '../types/order';
import { fieldConfig } from '@/config/fieldConfig';

export interface ValidationResult {
  isValid: boolean;
  missingColumns: string[];
  extraColumns: string[];
}

export function readExcelFile(file: File): Promise<RawOrderData[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json<RawOrderData>(worksheet, { raw: false });
        resolve(jsonData);
      } catch (error) {
        reject(new Error('無法讀取 Excel 檔案'));
      }
    };

    reader.onerror = () => reject(new Error('檔案讀取失敗'));
    reader.readAsArrayBuffer(file);
  });
}

export function validateColumns(data: RawOrderData[], platform: Platform): ValidationResult {
  if (data.length === 0) {
    return { isValid: false, missingColumns: ['檔案為空'], extraColumns: [] };
  }

  const expectedColumns: string[] = [...fieldConfig[platform].columns];
  const actualColumns = Object.keys(data[0]).filter(col => !col.startsWith('Unnamed'));

  const missingColumns = expectedColumns.filter(col => !actualColumns.includes(col));
  const extraColumns = actualColumns.filter(col => !expectedColumns.includes(col));

  return {
    isValid: missingColumns.length === 0,
    missingColumns,
    extraColumns,
  };
}

export function sortByOrderId(data: RawOrderData[], platform: Platform): RawOrderData[] {
  const orderIdField = fieldConfig[platform].order_id;
  return [...data].sort((a, b) => {
    const aId = String(a[orderIdField] || '');
    const bId = String(b[orderIdField] || '');
    return aId.localeCompare(bId);
  });
}
