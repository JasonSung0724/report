import { BaseProcessor } from './BaseProcessor';
import { OrderRow, RawOrderData } from '../types/order';
import { searchProduct } from '@/config/productConfig';
import { getCurrentDateYYYYMMDD } from '../utils/dateUtils';
import { safeString, extractAfterSeparator, formatOrderMark, isEmptyOrInvalid } from '../utils/stringUtils';

export class MixxProcessor extends BaseProcessor {
  constructor() {
    super('mixx');
  }

  protected getProductCode(row: RawOrderData): string {
    const productName = safeString(row['品名/規格']);
    const extracted = extractAfterSeparator(productName, '｜');
    const code = searchProduct(extracted, 'mixx_name');
    if (!code) {
      this.addError(safeString(row['*銷售單號']), '商品編號', `找不到商品: ${extracted}`);
    }
    return code || 'ERROR';
  }

  protected getFormattedDate(_row: RawOrderData): string {
    return getCurrentDateYYYYMMDD();
  }

  protected getOrderMark(row: RawOrderData): string {
    return formatOrderMark('減醣市集', safeString(row['備註']), '/');
  }

  protected getDeliveryMethod(_row: RawOrderData): string {
    return 'Tcat';
  }

  protected getReceiverAddress(row: RawOrderData): string {
    return safeString(row['收件地址']);
  }

  public process(data: RawOrderData[]): OrderRow[] {
    const newRows: OrderRow[] = [];
    let personalOrder: OrderRow[] = [];

    for (const row of data) {
      const currentOrderId = safeString(row['*銷售單號']);

      if (personalOrder.length > 0) {
        const prevOrderId = personalOrder[0]['貨主單號\n(不同客戶端、不同溫層要分單)'];
        if (prevOrderId !== currentOrderId) {
          newRows.push(this.createBoxRow(personalOrder[0], this.calculateBox(personalOrder)));
          personalOrder = [];
        }
      }

      if (isEmptyOrInvalid(currentOrderId)) continue;

      const deliveryMethod = this.getDeliveryMethod(row);
      const address = this.getReceiverAddress(row);
      const newRow = this.createBaseOrderRow(row, deliveryMethod, address);

      personalOrder.push(newRow);
      newRows.push(newRow);
    }

    if (personalOrder.length > 0) {
      newRows.push(this.createBoxRow(personalOrder[0], this.calculateBox(personalOrder)));
    }

    return newRows;
  }
}
