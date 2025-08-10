import React, { useRef, useState } from 'react';
import type { ContactParams, VisualizationParams } from '../lib/api';
import { DEFAULT_PARAMS, DEFAULT_VIZ_PARAMS, validateContactParams } from '../lib/api';

interface ControlsProps {
  onAnalyze: (pdbText: string, sdfText: string, params: ContactParams, vizParams: VisualizationParams) => void;
  onResetView: () => void;
  onExportPNG: () => void;
  isAnalyzing: boolean;
  hasContacts: boolean;
}

export const Controls: React.FC<ControlsProps> = ({
  onAnalyze,
  onResetView,
  onExportPNG,
  isAnalyzing,
  hasContacts,
}) => {
  const pdbFileRef = useRef<HTMLInputElement>(null);
  const sdfFileRef = useRef<HTMLInputElement>(null);
  
  const [pdbText, setPdbText] = useState('');
  const [sdfText, setSdfText] = useState('');
  const [params, setParams] = useState<ContactParams>(DEFAULT_PARAMS);
  const [vizParams, setVizParams] = useState<VisualizationParams>(DEFAULT_VIZ_PARAMS);
  const [showSurface, setShowSurface] = useState(false);
  const [style, setStyle] = useState({ cartoon: true, sticks: false });

  const handleFileRead = (file: File, setter: (text: string) => void) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setter(text);
    };
    reader.readAsText(file);
  };

  const handlePDBFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileRead(file, setPdbText);
    }
  };

  const handleSDFFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileRead(file, setSdfText);
    }
  };

  const handleLoadSample = async () => {
    try {
      // Fetch sample files from public directory
      const [pdbResponse, sdfResponse] = await Promise.all([
        fetch('/samples/sample.pdb'),
        fetch('/samples/sample.sdf')
      ]);
      
      if (!pdbResponse.ok || !sdfResponse.ok) {
        throw new Error('Failed to fetch sample files');
      }
      
      // Extract the text content
      const pdbText = await pdbResponse.text();
      const sdfText = await sdfResponse.text();
      
      // Set the sample data
      setPdbText(pdbText);
      setSdfText(sdfText);
      
      // Clear file inputs
      if (pdbFileRef.current) pdbFileRef.current.value = '';
      if (sdfFileRef.current) sdfFileRef.current.value = '';
      
    } catch (error) {
      console.error('Failed to load sample data:', error);
      alert('Failed to load sample data. Please check the console for details.');
    }
  };

  const handleAnalyze = () => {
    if (pdbText && sdfText) {
      // Validate and clamp parameters before sending
      const validatedParams = validateContactParams(params);
      onAnalyze(pdbText, sdfText, validatedParams, vizParams);
    }
  };

  const handleReset = () => {
    setPdbText('');
    setSdfText('');
    setParams(DEFAULT_PARAMS);
    setVizParams(DEFAULT_VIZ_PARAMS);
    setShowSurface(false);
    setStyle({ cartoon: true, sticks: false });
    if (pdbFileRef.current) pdbFileRef.current.value = '';
    if (sdfFileRef.current) sdfFileRef.current.value = '';
  };

  const canAnalyze = pdbText.trim() && sdfText.trim();

  return (
    <div className="card p-6 space-y-6">
      <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">
        Structure Analysis Controls
      </h2>

      {/* File Uploads */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Protein Structure (PDB)
          </label>
          <input
            ref={pdbFileRef}
            type="file"
            accept=".pdb,.ent"
            onChange={handlePDBFileChange}
            className="input-field"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ligand Structure (SDF)
          </label>
          <input
            ref={sdfFileRef}
            type="file"
            accept=".sdf,.mol"
            onChange={handleSDFFileChange}
            className="input-field"
          />
        </div>

        {/* Sample Data Button */}
        <div className="pt-2">
          <button
            onClick={handleLoadSample}
            className="btn-secondary w-full"
          >
            📁 Load Sample Data
          </button>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-center">
            Load a sample protein-ligand complex to get started
          </p>
        </div>
      </div>

      {/* Analysis Parameters */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          Analysis Parameters
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              H-bond Max Distance (Å)
            </label>
            <input
              type="number"
              step="0.1"
              min="0.5"
              max="10.0"
              value={params.hbond_max_dist}
              onChange={(e) => setParams({ ...params, hbond_max_dist: parseFloat(e.target.value) })}
              className="input-field"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Range: 0.5 - 10.0 Å
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              H-bond Min Angle (°)
            </label>
            <input
              type="number"
              step="1"
              min="90"
              max="180"
              value={params.hbond_min_angle}
              onChange={(e) => setParams({ ...params, hbond_min_angle: parseFloat(e.target.value) })}
              className="input-field"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Range: 90° - 180°
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Hydrophobic Max Distance (Å)
            </label>
            <input
              type="number"
              step="0.1"
              min="1.0"
              max="10.0"
              value={params.hydrophobic_max_dist}
              onChange={(e) => setParams({ ...params, hydrophobic_max_dist: parseFloat(e.target.value) })}
              className="input-field"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Range: 1.0 - 10.0 Å
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Salt Bridge Max Distance (Å)
            </label>
            <input
              type="number"
              step="0.1"
              min="1.0"
              max="10.0"
              value={params.salt_bridge_max_dist}
              onChange={(e) => setParams({ ...params, salt_bridge_max_dist: parseFloat(e.target.value) })}
              className="input-field"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Range: 1.0 - 10.0 Å
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Metal Max Distance (Å)
            </label>
            <input
              type="number"
              step="0.1"
              min="1.0"
              max="5.0"
              value={params.metal_max_dist}
              onChange={(e) => setParams({ ...params, metal_max_dist: parseFloat(e.target.value) })}
              className="input-field"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Range: 1.0 - 5.0 Å
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="pi_stack"
              checked={params.pi_stack}
              onChange={(e) => setParams({ ...params, pi_stack: e.target.checked })}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label htmlFor="pi_stack" className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Enable π-π Stacking
            </label>
          </div>
        </div>
      </div>

      {/* Visualization Options */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          Visualization Options
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Protein Style
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="protein_style"
                  checked={style.cartoon}
                  onChange={() => setStyle({ cartoon: true, sticks: false })}
                  className="mr-2"
                />
                Cartoon
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="protein_style"
                  checked={style.sticks}
                  onChange={() => setStyle({ cartoon: false, sticks: true })}
                  className="mr-2"
                />
                Sticks
              </label>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="show_surface"
              checked={showSurface}
              onChange={(e) => setShowSurface(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label htmlFor="show_surface" className="text-sm font-medium text-gray-700 dark:text-gray-400">
              Show Molecular Surface
            </label>
          </div>
        </div>

        {/* Contact Visualization Toggles */}
        <div className="space-y-3">
          <h4 className="text-md font-medium text-gray-700 dark:text-gray-300">
            Contact Visualization
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="color_contact_residues"
                checked={vizParams.color_contact_residues}
                onChange={(e) => setVizParams({ ...vizParams, color_contact_residues: e.target.checked })}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="color_contact_residues" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Color Contact Residues
              </label>
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="highlight_ligand_contacts"
                checked={vizParams.highlight_ligand_contacts}
                onChange={(e) => setVizParams({ ...vizParams, highlight_ligand_contacts: e.target.checked })}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="highlight_ligand_contacts" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Highlight Ligand Contacts
              </label>
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="show_contact_labels"
                checked={vizParams.show_contact_labels}
                onChange={(e) => setVizParams({ ...vizParams, show_contact_labels: e.target.checked })}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="show_contact_labels" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Show Contact Labels
              </label>
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="hide_waters_ions"
                checked={vizParams.hide_waters_ions}
                onChange={(e) => setVizParams({ ...vizParams, hide_waters_ions: e.target.checked })}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="hide_waters_ions" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Hide Waters/Ions
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <button
          onClick={handleAnalyze}
          disabled={!canAnalyze || isAnalyzing}
          className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Interactions'}
        </button>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleReset}
            className="btn-secondary"
          >
            Reset
          </button>
          
          <button
            onClick={onResetView}
            className="btn-secondary"
          >
            Reset View
          </button>
        </div>

        {hasContacts && (
          <button
            onClick={onExportPNG}
            className="btn-secondary w-full"
          >
            Export PNG
          </button>
        )}
      </div>
    </div>
  );
}; 