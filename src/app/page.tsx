'use client';

import { useState, useCallback } from 'react';
import { FileSpreadsheet, Loader2 } from 'lucide-react';
import FileUploader from '@/components/FileUploader';
import PlatformSelector from '@/components/PlatformSelector';
import DataPreview from '@/components/DataPreview';
import ConfigEditor from '@/components/ConfigEditor';
import ProcessingResult from '@/components/ProcessingResult';
import { useConfig } from '@/lib/hooks/useConfig';
import { Platform, RawOrderData, ProcessingError } from '@/lib/types/order';
import { readExcelFile, validateColumns, sortByOrderId } from '@/lib/excel/ExcelReader';
import { generateAndDownloadReport } from '@/lib/excel/ExcelWriter';
import { createProcessor } from '@/lib/processors';

export default function Home() {
  const [platform, setPlatform] = useState<Platform>('shopline');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [rawData, setRawData] = useState<RawOrderData[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [outputFileName, setOutputFileName] = useState('');
  const [processingResult, setProcessingResult] = useState<{
    originalCount: number;
    finalCount: number;
    uniqueOrderCount: number;
    errors: ProcessingError[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    productConfig,
    isLoaded,
    updateProduct,
    deleteProduct,
    resetConfig,
    importConfig,
    exportConfig,
  } = useConfig();

  const handleFileSelect = useCallback(async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setProcessingResult(null);

    try {
      const data = await readExcelFile(file);
      const validation = validateColumns(data, platform);

      if (!validation.isValid) {
        setError(`欄位驗證失敗。缺少欄位: ${validation.missingColumns.join(', ')}`);
        return;
      }

      const sortedData = sortByOrderId(data, platform);
      setRawData(sortedData);
      setOutputFileName(file.name.replace(/\.(xlsx|xls)$/, '_output'));
    } catch (err) {
      setError('檔案讀取失敗，請確認檔案格式正確');
    }
  }, [platform]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    setRawData([]);
    setProcessingResult(null);
    setError(null);
    setOutputFileName('');
  }, []);

  const handleProcess = useCallback(async () => {
    if (rawData.length === 0) return;

    setIsProcessing(true);
    setError(null);

    try {
      const processor = createProcessor(platform, productConfig);
      const rows = processor.process(rawData);
      const errors = processor.getErrors();

      const uniqueOrderIds = new Set(
        rows.map(r => r['貨主單號\n(不同客戶端、不同溫層要分單)'])
      );

      setProcessingResult({
        originalCount: rawData.length,
        finalCount: rows.length,
        uniqueOrderCount: uniqueOrderIds.size,
        errors,
      });

      await generateAndDownloadReport(rows, outputFileName);
    } catch (err) {
      setError('處理過程發生錯誤');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  }, [rawData, platform, outputFileName, productConfig]);

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-green-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
              <FileSpreadsheet className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800">
              減醣市集 訂單報告生成器
            </h1>
          </div>
          <p className="text-gray-500">
            快速整合多平台訂單，一鍵生成出貨報告
          </p>
        </header>

        <div className="space-y-6">
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              1. 選擇電商平台
            </h2>
            <PlatformSelector selected={platform} onChange={setPlatform} />
          </section>

          <section className="card p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              2. 上傳訂單檔案
            </h2>
            <FileUploader
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onClear={handleClear}
            />
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}
          </section>

          {rawData.length > 0 && (
            <>
              <DataPreview data={rawData} />

              <section className="card p-6">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">
                  3. 設定輸出檔名
                </h2>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={outputFileName}
                    onChange={(e) => setOutputFileName(e.target.value)}
                    placeholder="輸出檔案名稱"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  />
                  <span className="flex items-center text-gray-500">.xlsx</span>
                </div>
              </section>

              <section className="card p-6">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">
                  4. 生成報告
                </h2>
                <button
                  onClick={handleProcess}
                  disabled={isProcessing || !outputFileName.trim()}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      處理中...
                    </>
                  ) : (
                    '生成並下載報告'
                  )}
                </button>

                {processingResult && (
                  <ProcessingResult
                    originalCount={processingResult.originalCount}
                    finalCount={processingResult.finalCount}
                    uniqueOrderCount={processingResult.uniqueOrderCount}
                    errors={processingResult.errors}
                  />
                )}
              </section>
            </>
          )}

          <ConfigEditor
            productConfig={productConfig}
            onUpdate={updateProduct}
            onDelete={deleteProduct}
            onReset={resetConfig}
            onImport={importConfig}
            onExport={exportConfig}
          />
        </div>

        <footer className="mt-12 text-center text-sm text-gray-400">
          <p>減醣市集 訂單報告生成器 v2.0</p>
          <p className="mt-1">Made with Next.js • 部署於 Vercel</p>
        </footer>
      </div>
    </div>
  );
}
