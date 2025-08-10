import React from 'react';
import type { Contact } from '../lib/api';
import { getContactColorClasses, getContactLabel, getContactDescription } from '../lib/contactsColors';

interface ContactLegendProps {
  contacts: Contact[];
  selectedTypes: Set<string>;
  onTypeToggle: (type: string) => void;
}

export const ContactLegend: React.FC<ContactLegendProps> = ({
  contacts,
  selectedTypes,
  onTypeToggle,
}) => {
  // Count contacts by type
  const contactCounts = contacts.reduce((acc, contact) => {
    acc[contact.type] = (acc[contact.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Get all contact types
  const contactTypes = ['HBOND', 'HYDROPHOBIC', 'PI-PI', 'SALT_BRIDGE', 'METAL'] as const;

  return (
    <div className="card p-4">
      <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">
        Contact Types
      </h3>
      <div className="space-y-2">
        {contactTypes.map((type) => {
          const count = contactCounts[type] || 0;
          const isSelected = selectedTypes.has(type);
          
          return (
            <div
              key={type}
              className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all duration-200 ${
                isSelected 
                  ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              onClick={() => onTypeToggle(type)}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-4 h-4 rounded-full ${getContactColorClasses(type)}`} />
                <div>
                  <span className="font-medium text-gray-800 dark:text-gray-200">
                    {getContactLabel(type)}
                  </span>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {getContactDescription(type)}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                  {count}
                </span>
                <div className={`w-4 h-4 rounded border-2 transition-colors duration-200 ${
                  isSelected 
                    ? 'border-primary-500 bg-primary-500' 
                    : 'border-gray-300 dark:border-gray-600'
                }`}>
                  {isSelected && (
                    <svg className="w-full h-full text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {contacts.length === 0 && (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
          No contacts found. Upload structures and analyze to see interactions.
        </div>
      )}
    </div>
  );
}; 