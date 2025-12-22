import { BaseProcessor } from './BaseProcessor';
import { OrderRow, RawOrderData } from '../types/order';
import { ProductInfo } from '@/config/productConfig';
import { formatDateToYYYYMMDD } from '../utils/dateUtils';
import { safeString, formatOrderMark, isEmptyOrInvalid } from '../utils/stringUtils';

export class AoshiProcessor extends BaseProcessor {
  constructor(productConfig?: Record<string, ProductInfo>) {
    super('aoshi', productConfig);
  }

  protected getProductCode(row: RawOrderData): string {
    const productName = safeString(row['商品名稱']);
    const result = this.productMatcher.findByAoshiName(productName);
    if (!result) {
      this.addError(safeString(row['訂單號碼']), '商品編號', `找不到商品: ${productName}`);
    }
    return result?.productCode || 'ERROR';
  }

  protected getFormattedDate(row: RawOrderData): string {
    return formatDateToYYYYMMDD(row['訂單日期(年月日)'] as string);
  }

  protected getOrderMark(row: RawOrderData): string {
    return formatOrderMark('減醣市集 X 奧世國際', safeString(row['客戶備註']), '/');
  }

  protected getDeliveryMethod(_row: RawOrderData): string {
    return 'Tcat';
  }

  protected getReceiverAddress(row: RawOrderData): string {
    return safeString(row['收件人地址']);
  }

  public process(data: RawOrderData[]): OrderRow[] {
    const newRows: OrderRow[] = [];
    let personalOrder: OrderRow[] = [];

    for (const row of data) {
      const currentOrderId = safeString(row['訂單號碼']);

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
