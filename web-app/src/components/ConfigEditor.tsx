'use client';

import { useState } from 'react';
import { Settings, Plus, Trash2, Download, Upload, RotateCcw, ChevronDown, ChevronRight } from 'lucide-react';
import { ProductInfo } from '@/config/productConfig';

interface ConfigEditorProps {
  productConfig: Record<string, ProductInfo>;
  onUpdate: (code: string, info: ProductInfo) => void;
  onDelete: (code: string) => void;
  onReset: () => void;
  onImport: (json: string) => boolean;
  onExport: () => string;
}

export default function ConfigEditor({
  productConfig,
  onUpdate,
  onDelete,
  onReset,
  onImport,
  onExport,
}: ConfigEditorProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [editingCode, setEditingCode] = useState<string | null>(null);
  const [newCode, setNewCode] = useState('');
  const [newQty, setNewQty] = useState('1');

  const handleExport = () => {
    const json = onExport();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'product_config.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        const success = onImport(content);
        if (!success) {
          alert('匯入失敗：JSON 格式錯誤');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleAddProduct = () => {
    if (!newCode.trim()) return;
    onUpdate(newCode.trim(), {
      qty: parseInt(newQty) || 1,
      mixx_name: [],
      c2c_code: [],
      c2c_name: [],
    });
    setNewCode('');
    setNewQty('1');
  };

  return (
    <div className="card">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Settings className="w-5 h-5 text-gray-500" />
          <span className="font-medium text-gray-800">產品配置管理</span>
          <span className="text-sm text-gray-500">
            ({Object.keys(productConfig).length} 項產品)
          </span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="border-t border-gray-100">
          <div className="p-4 bg-gray-50 flex flex-wrap gap-2">
            <button onClick={handleExport} className="btn-secondary text-sm py-2 px-4 flex items-center gap-2">
              <Download className="w-4 h-4" />
              匯出配置
            </button>
            <label className="btn-secondary text-sm py-2 px-4 flex items-center gap-2 cursor-pointer">
              <Upload className="w-4 h-4" />
              匯入配置
              <input type="file" accept=".json" onChange={handleImport} className="hidden" />
            </label>
            <button onClick={onReset} className="btn-secondary text-sm py-2 px-4 flex items-center gap-2 text-red-600 hover:text-red-700">
              <RotateCcw className="w-4 h-4" />
              重置為預設
            </button>
          </div>

          <div className="p-4 border-t border-gray-100">
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={newCode}
                onChange={(e) => setNewCode(e.target.value)}
                placeholder="產品編號"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <input
                type="number"
                value={newQty}
                onChange={(e) => setNewQty(e.target.value)}
                placeholder="數量"
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <button onClick={handleAddProduct} className="btn-primary py-2 px-4 flex items-center gap-2">
                <Plus className="w-4 h-4" />
                新增
              </button>
            </div>

            <div className="max-h-64 overflow-y-auto">
              <table className="data-table text-sm">
                <thead>
                  <tr>
                    <th>產品編號</th>
                    <th>數量</th>
                    <th>MIXX 名稱</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(productConfig).map(([code, info]) => (
                    <tr key={code}>
                      <td className="font-mono text-xs">{code}</td>
                      <td>{info.qty}</td>
                      <td className="max-w-[200px] truncate text-gray-600">
                        {info.mixx_name.join(', ') || '-'}
                      </td>
                      <td>
                        <button
                          onClick={() => onDelete(code)}
                          className="p-1 text-red-500 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
