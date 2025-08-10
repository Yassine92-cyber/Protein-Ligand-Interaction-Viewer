import type { Contact } from './api';

// Color scheme for different contact types
export const CONTACT_COLORS = {
  HBOND: '#FF6B6B',        // Red
  HYDROPHOBIC: '#4ECDC4',  // Teal
  'PI-PI': '#45B7D1',      // Blue
  SALT_BRIDGE: '#96CEB4',  // Green
  METAL: '#FFEAA7',        // Yellow
} as const;

// Get color for a contact type
export function getContactColor(type: Contact['type']): string {
  return CONTACT_COLORS[type];
}

// Get color for a contact
export function getContactColorByContact(contact: Contact): string {
  return getContactColor(contact.type);
}

// CSS color classes for Tailwind
export const CONTACT_COLOR_CLASSES = {
  HBOND: 'text-red-500 bg-red-100 dark:bg-red-900/20',
  HYDROPHOBIC: 'text-teal-500 bg-teal-100 dark:bg-teal-900/20',
  'PI-PI': 'text-blue-500 bg-blue-100 dark:bg-blue-900/20',
  SALT_BRIDGE: 'text-green-500 bg-green-100 dark:bg-green-900/20',
  METAL: 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900/20',
} as const;

// Get CSS classes for a contact type
export function getContactColorClasses(type: Contact['type']): string {
  return CONTACT_COLOR_CLASSES[type];
}

// Contact type labels
export const CONTACT_LABELS = {
  HBOND: 'Hydrogen Bond',
  HYDROPHOBIC: 'Hydrophobic',
  'PI-PI': 'π-π Stacking',
  SALT_BRIDGE: 'Salt Bridge',
  METAL: 'Metal Coordination',
} as const;

// Get label for a contact type
export function getContactLabel(type: Contact['type']): string {
  return CONTACT_LABELS[type];
}

// Contact type descriptions
export const CONTACT_DESCRIPTIONS = {
  HBOND: 'Electrostatic attraction between hydrogen and electronegative atoms',
  HYDROPHOBIC: 'Non-polar interactions between hydrophobic groups',
  'PI-PI': 'Stacking interactions between aromatic rings',
  SALT_BRIDGE: 'Electrostatic interactions between charged groups',
  METAL: 'Coordination bonds with metal ions',
} as const;

// Get description for a contact type
export function getContactDescription(type: Contact['type']): string {
  return CONTACT_DESCRIPTIONS[type];
} 