'use client';

import { CheckCircle, AlertTriangle, AlertCircle, Download } from 'lucide-react';
import { ProcessingError } from '@/lib/types/order';

interface ProcessingResultProps {
  originalCount: number;
  finalCount: number;
  uniqueOrderCount: number;
  errors: ProcessingError[];
  onDownload: () => void;
  isProcessing: boolean;
}

export default function ProcessingResult({
  originalCount,
  finalCount,
  uniqueOrderCount,
  errors,
  onDownload,
  isProcessing,
}: ProcessingResultProps) {
  const hasErrors = errors.some(e => e.severity === 'error');
  const hasWarnings = errors.some(e => e.severity === 'warning');

  return (
    <div className="card">
      <div className="p-4 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center gap-2">
          {hasErrors ? (
            <AlertCircle className="w-5 h-5 text-red-500" />
          ) : hasWarnings ? (
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          ) : (
            <CheckCircle className="w-5 h-5 text-green-500" />
          )}
          <h3 className="font-semibold text-gray-800">處理結果</h3>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">{originalCount}</p>
            <p className="text-sm text-gray-600">原始資料筆數</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{finalCount}</p>
            <p className="text-sm text-gray-600">最終訂單筆數</p>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">{uniqueOrderCount}</p>
            <p className="text-sm text-gray-600">不重複訂單數</p>
          </div>
        </div>

        {errors.length > 0 && (
          <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="font-medium text-yellow-800 mb-2">
              注意事項 ({errors.length} 項)
            </p>
            <div className="max-h-32 overflow-y-auto space-y-1">
              {errors.slice(0, 10).map((error, idx) => (
                <p key={idx} className={`text-sm ${error.severity === 'error' ? 'text-red-600' : 'text-yellow-700'}`}>
                  • 訂單 {error.orderId}: {error.message}
                </p>
              ))}
              {errors.length > 10 && (
                <p className="text-sm text-gray-500">... 還有 {errors.length - 10} 項</p>
              )}
            </div>
          </div>
        )}

        <button
          onClick={onDownload}
          disabled={isProcessing}
          className="w-full btn-primary flex items-center justify-center gap-2"
        >
          <Download className="w-5 h-5" />
          {isProcessing ? '處理中...' : '下載報告'}
        </button>
      </div>
    </div>
  );
}
