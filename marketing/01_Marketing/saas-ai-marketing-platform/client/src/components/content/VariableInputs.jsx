import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, HelpCircle } from 'lucide-react';

const VariableInputs = ({ variables, values, onChange }) => {
  const renderInput = (variable) => {
    const value = values[variable.name] || '';
    const hasError = variable.required && !value;

    const commonProps = {
      id: variable.name,
      value: value,
      onChange: (e) => onChange(variable.name, e.target.value),
      className: `w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
        hasError 
          ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20' 
          : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'
      } text-gray-900 dark:text-white`,
      placeholder: variable.placeholder || `Enter ${variable.label.toLowerCase()}...`
    };

    switch (variable.type) {
      case 'textarea':
        return (
          <textarea
            {...commonProps}
            rows={4}
            className={`${commonProps.className} resize-none`}
          />
        );

      case 'select':
        return (
          <select {...commonProps}>
            <option value="">Select {variable.label.toLowerCase()}...</option>
            {variable.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'number':
        return (
          <input
            {...commonProps}
            type="number"
            min={variable.validation?.min}
            max={variable.validation?.max}
          />
        );

      case 'boolean':
        return (
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id={variable.name}
              checked={value === 'true' || value === true}
              onChange={(e) => onChange(variable.name, e.target.checked.toString())}
              className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <label htmlFor={variable.name} className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {variable.label}
            </label>
          </div>
        );

      case 'date':
        return (
          <input
            {...commonProps}
            type="date"
          />
        );

      default:
        return (
          <input
            {...commonProps}
            type="text"
            minLength={variable.validation?.minLength}
            maxLength={variable.validation?.maxLength}
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      {variables.map((variable, index) => (
        <motion.div
          key={variable.name}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="space-y-2"
        >
          {/* Label */}
          <div className="flex items-center justify-between">
            <label
              htmlFor={variable.name}
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              {variable.label}
              {variable.required && (
                <span className="text-red-500 ml-1">*</span>
              )}
            </label>
            
            {variable.placeholder && (
              <div className="group relative">
                <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" />
                <div className="absolute right-0 top-6 w-64 p-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10">
                  {variable.placeholder}
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="relative">
            {renderInput(variable)}
            
            {/* Error Message */}
            {variable.required && !values[variable.name] && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center mt-2 text-sm text-red-600 dark:text-red-400"
              >
                <AlertCircle className="w-4 h-4 mr-1" />
                This field is required
              </motion.div>
            )}
          </div>

          {/* Validation Info */}
          {variable.validation && (
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {variable.validation.minLength && variable.validation.maxLength && (
                <span>
                  {variable.validation.minLength}-{variable.validation.maxLength} characters
                </span>
              )}
              {variable.validation.min && variable.validation.max && (
                <span>
                  Range: {variable.validation.min}-{variable.validation.max}
                </span>
              )}
              {variable.validation.pattern && (
                <span>Must match pattern: {variable.validation.pattern}</span>
              )}
            </div>
          )}
        </motion.div>
      ))}

      {/* Summary */}
      {variables.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: variables.length * 0.1 }}
          className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
        >
          <h4 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
            Template Variables Summary
          </h4>
          <div className="text-sm text-blue-700 dark:text-blue-400">
            <p>• {variables.filter(v => v.required).length} required fields</p>
            <p>• {variables.filter(v => !v.required).length} optional fields</p>
            <p>• {Object.keys(values).filter(key => values[key]).length} fields completed</p>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default VariableInputs;









