import React from "react";

export const ReturnsLogTable: React.FC = () => {
  return (
    <div className="returns-log-table-container">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID Операции</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Серийный номер</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr className="payment-form-active">
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#0501-MOCK</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">SN-MOCK-777</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">IN_STORE</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};
