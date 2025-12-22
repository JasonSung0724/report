'use client';

import { useState, useCallback, useEffect } from 'react';
import { ProductInfo } from '@/config/productConfig';

const STORAGE_KEY = 'orderReportConfig';

interface ConfigState {
  productConfig: Record<string, ProductInfo>;
  lastUpdated: string;
}

function getDefaultConfig(): Record<string, ProductInfo> {
  return {
    "bagel101-1PK-999": { qty: 14, mixx_name: ["減醣貝果14天體驗組 (14入)"], c2c_code: ["L2503F00048"], c2c_name: ["減醣市集 減醣貝果14天體驗組-F"] },
    "bagel101-1PK-1299": { qty: 20, mixx_name: ["減醣貝果14天體驗組 (20入)"], c2c_code: [], c2c_name: [] },
    "bagel101-3PK": { qty: 7, mixx_name: ["貝果全系列綜合禮包 (7入)", "減醣市集 貝果綜合禮包(7入)"], c2c_code: [], c2c_name: [] },
    "bagel001-2EA": { qty: 2, mixx_name: ["低糖草莓乳酪貝果 (2入)"], c2c_code: ["F2500000044-0", "L2503F00172"], c2c_name: ["草莓乳酪2入+藍莓乳酪2入(贈品)-F", "草莓乳酪-2入組"], aoshi_name: ["減醣市集｜低糖草莓乳酪貝果 (2入)"] },
    "bagel002-2EA": { qty: 2, mixx_name: ["日式香醇芝麻乳酪貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["芝麻乳酪-2入組"] },
    "bagel003-2EA": { qty: 2, mixx_name: ["宇治抹茶紅豆貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["抹茶紅豆-2入組"], aoshi_name: ["減醣市集｜宇治抹茶紅豆貝果 (2入)"] },
    "bagel004-2EA": { qty: 2, mixx_name: ["低糖藍莓乳酪貝果 (2入)"], c2c_code: ["F2500000044-1", "L2503F00172"], c2c_name: ["藍莓乳酪-2入組"], aoshi_name: ["減醣市集｜低糖藍莓乳酪貝果 (2入)"] },
    "bagel005-2EA": { qty: 2, mixx_name: ["經典輕盈原味貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["經典原味-2入組"] },
    "bagel006-2EA": { qty: 2, mixx_name: ["濃郁起司乳酪丁貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["起司乳酪-2入組"], aoshi_name: ["減醣市集｜濃郁起司乳酪丁貝果 (2入)"] },
    "bagel007-2EA": { qty: 2, mixx_name: ["法式AOP極致奶油貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["鹹香奶油-2入組"] },
    "bagel008-2EA": { qty: 2, mixx_name: ["開心果乳酪貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["開心果乳酪-2入組"], aoshi_name: ["減醣市集｜西西里開心果乳酪貝果 (2入)"] },
    "bagel009-2EA": { qty: 2, mixx_name: ["伯爵高蛋白奶酥貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["伯爵蛋白奶酥-2入組"], aoshi_name: ["減醣市集｜伯爵高蛋白奶酥能量貝果 (2入)"] },
    "bagel010-2EA": { qty: 2, mixx_name: ["原味高蛋白奶酥貝果 (2入)"], c2c_code: ["L2503F00172"], c2c_name: ["原味蛋白奶酥-2入組"] },
    "box60-EA": { qty: 0, mixx_name: [], c2c_code: [], c2c_name: [] },
    "box90-EA": { qty: 0, mixx_name: [], c2c_code: [], c2c_name: [] },
  };
}

export function useConfig() {
  const [productConfig, setProductConfig] = useState<Record<string, ProductInfo>>(getDefaultConfig);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: ConfigState = JSON.parse(stored);
        setProductConfig(parsed.productConfig);
      }
    } catch (e) {
      console.error('Failed to load config from localStorage');
    }
    setIsLoaded(true);
  }, []);

  const saveConfig = useCallback((newConfig: Record<string, ProductInfo>) => {
    setProductConfig(newConfig);
    const state: ConfigState = {
      productConfig: newConfig,
      lastUpdated: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, []);

  const resetConfig = useCallback(() => {
    const defaultConfig = getDefaultConfig();
    saveConfig(defaultConfig);
  }, [saveConfig]);

  const updateProduct = useCallback((code: string, info: ProductInfo) => {
    saveConfig({ ...productConfig, [code]: info });
  }, [productConfig, saveConfig]);

  const deleteProduct = useCallback((code: string) => {
    const newConfig = { ...productConfig };
    delete newConfig[code];
    saveConfig(newConfig);
  }, [productConfig, saveConfig]);

  const importConfig = useCallback((jsonString: string) => {
    try {
      const imported = JSON.parse(jsonString);
      saveConfig(imported);
      return true;
    } catch {
      return false;
    }
  }, [saveConfig]);

  const exportConfig = useCallback(() => {
    return JSON.stringify(productConfig, null, 2);
  }, [productConfig]);

  return {
    productConfig,
    isLoaded,
    saveConfig,
    resetConfig,
    updateProduct,
    deleteProduct,
    importConfig,
    exportConfig,
  };
}
