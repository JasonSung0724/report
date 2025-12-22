import { ProductInfo } from '@/config/productConfig';

export function searchProduct(
  searchValue: string,
  searchType: 'mixx_name' | 'c2c_code' | 'aoshi_name',
  productConfig: Record<string, ProductInfo>,
  c2cName?: string
): string | null {
  for (const [productCode, productInfo] of Object.entries(productConfig)) {
    if (searchType === 'mixx_name' && productInfo.mixx_name.includes(searchValue)) {
      return productCode;
    }
    if (searchType === 'c2c_code' && c2cName && productInfo.c2c_name.includes(c2cName)) {
      const c2cCodeList = productInfo.c2c_code;
      for (const code of c2cCodeList) {
        if (searchValue.includes(code)) {
          return productCode;
        }
      }
    }
    if (searchType === 'aoshi_name' && productInfo.aoshi_name?.includes(searchValue)) {
      return productCode;
    }
  }
  return null;
}
