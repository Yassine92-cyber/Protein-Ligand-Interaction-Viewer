import { useState } from 'react';
import type { ContactParams, VisualizationParams, Contact, AnalyzeRequest, AnalyzeResponse } from './lib/api';
import { postAnalyze } from './lib/api';
import { Controls } from './components/Controls';
import { ContactLegend } from './components/ContactLegend';
import { ErrorBoundary } from './components/ErrorBoundary';
import './App.css';

function App() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedContactTypes, setSelectedContactTypes] = useState<Set<string>>(new Set(['HBOND', 'HYDROPHOBIC', 'PI-PI', 'SALT_BRIDGE', 'METAL']));
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null);

  const handleAnalyze = async (pdbText: string, sdfText: string, params: ContactParams, vizParams: VisualizationParams) => {
    setIsAnalyzing(true);
    try {
      const request: AnalyzeRequest = {
        pdb_text: pdbText,
        sdf_text: sdfText,
        params,
        viz_params: vizParams
      };

      const response = await postAnalyze(request);
      setContacts(response.contacts);
      setAnalysisResult(response);
      
      // Update selected contact types to include all found types
      const foundTypes = new Set(response.contacts.map(c => c.type));
      setSelectedContactTypes(foundTypes);
      
    } catch (error) {
      console.error('Analysis failed:', error);
      alert(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleResetView = () => {
    setContacts([]);
    setAnalysisResult(null);
    setSelectedContactTypes(new Set(['HBOND', 'HYDROPHOBIC', 'PI-PI', 'SALT_BRIDGE', 'METAL']));
  };

  const handleExportPNG = () => {
    // TODO: Implement PNG export functionality
    alert('PNG export functionality coming soon!');
  };

  const handleContactTypeToggle = (type: string) => {
    const newSelected = new Set(selectedContactTypes);
    if (newSelected.has(type)) {
      newSelected.delete(type);
    } else {
      newSelected.add(type);
    }
    setSelectedContactTypes(newSelected);
  };

  const filteredContacts = contacts.filter(contact => selectedContactTypes.has(contact.type));

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Protein-Ligand Interaction Viewer
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Analyze molecular interactions between proteins and ligands
            </p>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Controls */}
            <div className="lg:col-span-2">
              <Controls
                onAnalyze={handleAnalyze}
                onResetView={handleResetView}
                onExportPNG={handleExportPNG}
                isAnalyzing={isAnalyzing}
                hasContacts={contacts.length > 0}
              />
            </div>

            {/* Right Column - Contact Legend */}
            <div className="lg:col-span-1">
              <ContactLegend
                contacts={contacts}
                selectedTypes={selectedContactTypes}
                onTypeToggle={handleContactTypeToggle}
              />
            </div>
          </div>

          {/* Results Section */}
          {analysisResult && (
            <div className="mt-8">
              <div className="card p-6">
                <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
                
                {/* Summary Statistics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-blue-900">Protein</h3>
                    <p className="text-2xl font-bold text-blue-600">{analysisResult.protein_summary.residues}</p>
                    <p className="text-sm text-blue-700">Residues</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-green-900">Ligand</h3>
                    <p className="text-2xl font-bold text-green-600">{analysisResult.ligand_summary.atoms}</p>
                    <p className="text-sm text-green-700">Atoms</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-purple-900">Contacts</h3>
                    <p className="text-2xl font-bold text-purple-600">{analysisResult.contacts.length}</p>
                    <p className="text-sm text-purple-700">Total</p>
                  </div>
                </div>

                {/* Contact Details */}
                {filteredContacts.length > 0 ? (
                  <div>
                    <h3 className="text-xl font-semibold mb-3">Contact Details</h3>
                    <div className="space-y-2">
                      {filteredContacts.map((contact, index) => (
                        <div key={index} className="bg-gray-50 p-3 rounded border-l-4 border-blue-500">
                          <div className="flex justify-between items-center">
                            <span className="font-medium text-gray-900">
                              {contact.type} - {contact.protein_resn}{contact.protein_resi}
                            </span>
                            <span className="text-sm text-gray-600">
                              Distance: {contact.distance.toFixed(2)}Å
                              {contact.angle && `, Angle: ${contact.angle.toFixed(1)}°`}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No contacts found with current filters
                  </p>
                )}

                {/* Warnings */}
                {analysisResult.warnings && analysisResult.warnings.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-lg font-semibold text-yellow-800 mb-2">Warnings</h3>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <ul className="list-disc list-inside space-y-1">
                        {analysisResult.warnings.map((warning, index) => (
                          <li key={index} className="text-yellow-800">{warning}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
