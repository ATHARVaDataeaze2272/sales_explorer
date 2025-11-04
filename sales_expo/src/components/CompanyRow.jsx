import { useState } from 'react';
import { Save, XCircle, Edit2, X } from 'lucide-react';

function CompanyRow({ company, isEven, isEditing, onEdit, onSave, onCancel, onDelete }) {
  const [formData, setFormData] = useState(company);

  const handleSave = () => {
    onSave(formData);
  };

  if (isEditing) {
    return (
      <tr className="bg-blue-50">
        <td className="px-6 py-4">
          <input
            type="text"
            value={formData.company_name || ''}
            onChange={e => setFormData({ ...formData, company_name: e.target.value })}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </td>
        <td className="px-6 py-4">
          <div className="space-y-2">
            <input
              type="text"
              value={formData.first_name || ''}
              onChange={e => setFormData({ ...formData, first_name: e.target.value })}
              placeholder="First name"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              value={formData.last_name || ''}
              onChange={e => setFormData({ ...formData, last_name: e.target.value })}
              placeholder="Last name"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </td>
        <td className="px-6 py-4">
          <input
            type="email"
            value={formData.email || ''}
            onChange={e => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </td>
        <td className="px-6 py-4">
          <input
            type="tel"
            value={formData.phone || ''}
            onChange={e => setFormData({ ...formData, phone: e.target.value })}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </td>
        <td className="px-6 py-4">
          <input
            type="text"
            value={formData.country || ''}
            onChange={e => setFormData({ ...formData, country: e.target.value })}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </td>
        <td className="px-6 py-4">
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              title="Save changes"
            >
              <Save className="w-4 h-4" />
            </button>
            <button
              onClick={onCancel}
              className="p-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              title="Cancel"
            >
              <XCircle className="w-4 h-4" />
            </button>
          </div>
        </td>
      </tr>
    );
  }

  return (
    <tr className={isEven ? 'bg-white' : 'bg-gray-50'}>
      <td className="px-6 py-4 text-sm text-gray-900 font-medium">{company.company_name || '-'}</td>
      <td className="px-6 py-4 text-sm text-gray-900">
        {[company.first_name, company.last_name].filter(Boolean).join(' ') || '-'}
      </td>
      <td className="px-6 py-4 text-sm text-gray-900">{company.email || '-'}</td>
      <td className="px-6 py-4 text-sm text-gray-900">{company.phone || '-'}</td>
      <td className="px-6 py-4 text-sm text-gray-900">{company.country || '-'}</td>
      <td className="px-6 py-4">
        <div className="flex gap-2">
          <button
            onClick={onEdit}
            className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
            title="Edit company"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
            title="Delete company"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </td>
    </tr>
  );
}

export default CompanyRow;