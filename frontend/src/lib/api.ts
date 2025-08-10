// Types matching backend schemas
export interface ContactParams {
  hbond_max_dist: number;
  hbond_min_angle: number;
  hydrophobic_max_dist: number;
  pi_stack: boolean;
  salt_bridge_max_dist: number;
  metal_max_dist: number;
}

export interface VisualizationParams {
  color_contact_residues: boolean;
  highlight_ligand_contacts: boolean;
  show_contact_labels: boolean;
  hide_waters_ions: boolean;
}

export interface Contact {
  type: "HBOND" | "HYDROPHOBIC" | "PI-PI" | "SALT_BRIDGE" | "METAL";
  ligand_atom: number;
  protein_resi: number;
  protein_resn: string;
  protein_atom: string;
  distance: number;
  angle: number | null;
}

export interface AnalyzeRequest {
  pdb_text: string;
  sdf_text: string;
  params: ContactParams;
  viz_params?: VisualizationParams;
}

export interface AnalyzeResponse {
  contacts: Contact[];
  ligand_summary: {
    atoms: number;
    bonds: number;
  };
  protein_summary: {
    chains: number;
    residues: number;
  };
  warnings: string[];
  filtered_pdb?: string;
}

// API client
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let csrfToken: string | null = null;

async function getCSRFToken(): Promise<string> {
  if (!csrfToken) {
    const response = await fetch(`${API_BASE_URL}/csrf-token`);
    if (response.ok) {
      const data = await response.json();
      csrfToken = data.csrf_token;
    }
  }
  return csrfToken || '';
}

export class APIError extends Error {
  status?: number;
  details?: unknown;

  constructor(message: string, status?: number, details?: unknown) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.details = details;
  }
}

export async function postAnalyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  try {
    const token = await getCSRFToken();
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': token,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : 'Network error occurred',
      undefined,
      error
    );
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

// Parameter validation and clamping functions
export function clampValue(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export function validateContactParams(params: ContactParams): ContactParams {
  return {
    hbond_max_dist: clampValue(params.hbond_max_dist, 0.5, 10.0),
    hbond_min_angle: clampValue(params.hbond_min_angle, 90.0, 180.0),
    hydrophobic_max_dist: clampValue(params.hydrophobic_max_dist, 1.0, 10.0),
    pi_stack: params.pi_stack,
    salt_bridge_max_dist: clampValue(params.salt_bridge_max_dist, 1.0, 10.0),
    metal_max_dist: clampValue(params.metal_max_dist, 1.0, 5.0),
  };
}

// Default parameters with validation
export const DEFAULT_PARAMS: ContactParams = {
  hbond_max_dist: 3.5,
  hbond_min_angle: 120.0,
  hydrophobic_max_dist: 4.0,
  pi_stack: true,
  salt_bridge_max_dist: 4.0,
  metal_max_dist: 2.8,
};

export const DEFAULT_VIZ_PARAMS: VisualizationParams = {
  color_contact_residues: true,
  highlight_ligand_contacts: true,
  show_contact_labels: true,
  hide_waters_ions: true,
}; 