import { ProductInfo } from '@/config/productConfig';

export type MatchType = 'mixx_name' | 'c2c_code' | 'c2c_name' | 'aoshi_name';

interface MatchResult {
  productCode: string;
  matchType: MatchType;
  matchedValue: string;
}

export class ProductMatcher {
  private mixxNameMap: Map<string, string> = new Map();
  private c2cCodeMap: Map<string, string> = new Map();
  private c2cNameMap: Map<string, string> = new Map();
  private aoshiNameMap: Map<string, string> = new Map();
  private productConfig: Record<string, ProductInfo>;

  constructor(productConfig: Record<string, ProductInfo>) {
    this.productConfig = productConfig;
    this.buildIndexes();
  }

  private buildIndexes(): void {
    this.mixxNameMap.clear();
    this.c2cCodeMap.clear();
    this.c2cNameMap.clear();
    this.aoshiNameMap.clear();

    for (const [productCode, info] of Object.entries(this.productConfig)) {
      for (const name of info.mixx_name) {
        this.mixxNameMap.set(this.normalize(name), productCode);
      }
      for (const code of info.c2c_code) {
        this.c2cCodeMap.set(this.normalize(code), productCode);
      }
      for (const name of info.c2c_name) {
        this.c2cNameMap.set(this.normalize(name), productCode);
      }
      for (const name of info.aoshi_name || []) {
        this.aoshiNameMap.set(this.normalize(name), productCode);
      }
    }
  }

  private normalize(value: string): string {
    return value.trim().toLowerCase();
  }

  public updateConfig(productConfig: Record<string, ProductInfo>): void {
    this.productConfig = productConfig;
    this.buildIndexes();
  }

  public findByMixxName(productName: string): MatchResult | null {
    const normalized = this.normalize(productName);
    const code = this.mixxNameMap.get(normalized);
    if (code) {
      return { productCode: code, matchType: 'mixx_name', matchedValue: productName };
    }

    const entries = Array.from(this.mixxNameMap.entries());
    for (let i = 0; i < entries.length; i++) {
      const [key, productCode] = entries[i];
      if (normalized.includes(key) || key.includes(normalized)) {
        return { productCode, matchType: 'mixx_name', matchedValue: productName };
      }
    }

    return null;
  }

  public findByC2C(productCode: string, productStyle: string): MatchResult | null {
    const normalizedCode = this.normalize(productCode);
    const normalizedStyle = this.normalize(productStyle);

    const codeResult = this.c2cCodeMap.get(normalizedCode);
    if (codeResult) {
      const info = this.productConfig[codeResult];
      if (info && info.c2c_name.some(name => this.normalize(name) === normalizedStyle)) {
        return { productCode: codeResult, matchType: 'c2c_code', matchedValue: `${productCode}|${productStyle}` };
      }
    }

    const codeEntries = Array.from(this.c2cCodeMap.entries());
    for (let i = 0; i < codeEntries.length; i++) {
      const [key, code] = codeEntries[i];
      if (normalizedCode.includes(key) || key.includes(normalizedCode)) {
        const info = this.productConfig[code];
        if (info && info.c2c_name.some(name => normalizedStyle.includes(this.normalize(name)))) {
          return { productCode: code, matchType: 'c2c_code', matchedValue: `${productCode}|${productStyle}` };
        }
      }
    }

    const styleResult = this.c2cNameMap.get(normalizedStyle);
    if (styleResult) {
      return { productCode: styleResult, matchType: 'c2c_name', matchedValue: productStyle };
    }

    return null;
  }

  public findByAoshiName(productName: string): MatchResult | null {
    const normalized = this.normalize(productName);
    const code = this.aoshiNameMap.get(normalized);
    if (code) {
      return { productCode: code, matchType: 'aoshi_name', matchedValue: productName };
    }

    const entries = Array.from(this.aoshiNameMap.entries());
    for (let i = 0; i < entries.length; i++) {
      const [key, productCode] = entries[i];
      if (normalized.includes(key) || key.includes(normalized)) {
        return { productCode, matchType: 'aoshi_name', matchedValue: productName };
      }
    }

    return null;
  }

  public getProductInfo(productCode: string): ProductInfo | null {
    return this.productConfig[productCode] || null;
  }

  public getAllProductCodes(): string[] {
    return Object.keys(this.productConfig);
  }
}

let matcherInstance: ProductMatcher | null = null;

export function getProductMatcher(productConfig: Record<string, ProductInfo>): ProductMatcher {
  if (!matcherInstance) {
    matcherInstance = new ProductMatcher(productConfig);
  } else {
    matcherInstance.updateConfig(productConfig);
  }
  return matcherInstance;
}

export function searchProduct(
  searchValue: string,
  searchType: 'mixx_name' | 'c2c_code' | 'aoshi_name',
  c2cName?: string,
  productConfig?: Record<string, ProductInfo>
): string | null {
  if (!productConfig) return null;

  const matcher = getProductMatcher(productConfig);

  if (searchType === 'mixx_name') {
    const result = matcher.findByMixxName(searchValue);
    return result?.productCode || null;
  }

  if (searchType === 'c2c_code' && c2cName) {
    const result = matcher.findByC2C(searchValue, c2cName);
    return result?.productCode || null;
  }

  if (searchType === 'aoshi_name') {
    const result = matcher.findByAoshiName(searchValue);
    return result?.productCode || null;
  }

  return null;
}
