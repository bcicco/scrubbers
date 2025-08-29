import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeadGen } from '../contexts/LeadGenContext';

const GeographicalSelection = () => {
  const { sessionData, updateAreas } = useLeadGen();
  const navigate = useNavigate();
  
  const [csvData, setCsvData] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedSA3s, setSelectedSA3s] = useState([]);
  const [step, setStep] = useState(1); // 1: Select State, 2: Select SA3s
  
  const stateMapping = {
    "VIC": ['2RVIC', '2GMEL'],
    "NSW": ['1GSYD', '1RNSW'],
    "NT": ['7GDAR', '7RNTE'],
    "QLD": ['3RQLD', '3GBRI'],
    "SA": ['4GADE', '4RSAU'],
    "TAS": ['6GHOB', '6RTAS'],
    "WA": ['5RWAU', '5GPER'],
    "ACT": ['8ACTE']
  };

  // Load and parse CSV data
  useEffect(() => {
    const loadCSVData = async () => {
      try {
        const response = await fetch('/areas.csv');
        const text = await response.text();
        
        // Use Papa Parse for robust CSV parsing
        const Papa = await import('papaparse');
        const results = Papa.default.parse(text, {
          header: true,
          skipEmptyLines: true,
          transformHeader: (header) => {
            // Clean up headers and map to our field names
            const cleanHeader = header.trim();
            const headerMap = {
              'GCCSA code': 'gccsa_code',
              'GCCSA name': 'gccsa_name', 
              'SA4 code': 'sa4_code',
              'SA4 name': 'sa4_name',
              'SA3 code': 'sa3_code',
              'SA3 name': 'sa3_name',
              'SA2 code': 'sa2_code',
              'SA2 name': 'sa2_name',
              'Population 2024': 'population'
            };
            return headerMap[cleanHeader] || cleanHeader.toLowerCase().replace(/\s+/g, '_');
          },
          transform: (value) => {
            // Clean up values
            return value ? value.trim() : '';
          }
        });
        
        if (results.errors.length > 0) {
          console.warn('CSV parsing warnings:', results.errors);
        }
        
        console.log('Raw CSV results:', results.data.slice(0, 2)); // See what Papa Parse actually creates
        console.log('Column headers found:', Object.keys(results.data[0] || {}));
        
        // Filter out rows with missing essential data
        const cleanData = results.data.filter(row => {
          const isValid = row.gccsa_code && 
                         row.sa2_name && 
                         row.sa3_name &&
                         row.gccsa_code.length > 0;
          
          // Debug the first few invalid rows
          if (!isValid && results.data.indexOf(row) < 5) {
            console.log('Filtering out row:', row);
          }
          
          return isValid;
        });
        
        console.log('Total rows parsed:', results.data.length);
        console.log('Valid rows after filtering:', cleanData.length);
        console.log('Sample data:', cleanData.slice(0, 3));
        console.log('Available GCCSA codes:', [...new Set(cleanData.map(r => r.gccsa_code))]);
        setCsvData(cleanData);
        
      } catch (error) {
        console.error('Error loading CSV:', error);
      }
    };
    
    loadCSVData();
  }, []);

  // Get available SA3s for the selected state
  const getAvailableSA3s = () => {
    if (!selectedState || !csvData.length) return [];
    
    const stateCodes = stateMapping[selectedState] || [];
    const sa3s = csvData
      .filter(row => stateCodes.includes(row.gccsa_code))
      .reduce((acc, row) => {
        if (row.sa3_name && !acc.some(item => item.code === row.sa3_code)) {
          acc.push({
            code: row.sa3_code,
            name: row.sa3_name
          });
        }
        return acc;
      }, [])
      .sort((a, b) => a.name.localeCompare(b.name));
    
    return sa3s;
  };

  // Get all SA2 areas for selected SA3s
  const getSA2Areas = () => {
    if (!selectedSA3s.length || !csvData.length) return [];
    
    const selectedSA3Codes = selectedSA3s.map(sa3 => sa3.code);
    const sa2Areas = csvData
      .filter(row => selectedSA3Codes.includes(row.sa3_code))
      .map(row => ({
        code: row.sa2_code,
        name: row.sa2_name,
        sa3_name: row.sa3_name,
        population: row.population
      }))
      .filter(area => area.name)
      .sort((a, b) => a.name.localeCompare(b.name));
    
    return sa2Areas;
  };

  const handleStateSelect = (state) => {
    setSelectedState(state);
    setSelectedSA3s([]);
    setStep(2);
  };

  const toggleSA3 = (sa3) => {
    setSelectedSA3s(prev => {
      const exists = prev.some(item => item.code === sa3.code);
      if (exists) {
        return prev.filter(item => item.code !== sa3.code);
      } else {
        return [...prev, sa3];
      }
    });
  };

  const handleSubmit = async () => {
  const sa2Areas = getSA2Areas();
  const areaNames = sa2Areas.map(area => area.name);
  
  try {
    // Save product to database

    console.log(sessionData.customerID)
    const response = await fetch('/api/create_product', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer_id: sessionData.customerID,
        product_name: sessionData.productName,
        product_desc: sessionData.productDescription,
        target_industry: sessionData.targetIndustry,
        selected_areas: areaNames
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to create product');
    }

    const result = await response.json();
    console.log('Product saved to database:', result);
    
    // Store product ID for later use
    sessionData.productId = result.product_id;
    
  } catch (error) {
    console.error('Error saving to database:', error);
    alert(`Error: ${error.message}`);
    return; // Don't continue if database save failed
  }
    
    updateAreas(areaNames);
    navigate('/processing');
  };

  const handleBack = () => {
    if (step === 2) {
      setStep(1);
      setSelectedSA3s([]);
    } else {
      navigate('/');
    }
  };

  const availableSA3s = getAvailableSA3s();
  const finalSA2Areas = getSA2Areas();

  return (
    <div className="form-container">
      <h1>Select Target Areas</h1>
      <p>Researching leads for: <strong>{sessionData.productDescription}</strong></p>
      <p>Target Industry: <strong>{sessionData.targetIndustry}</strong></p>
      
      {step === 1 && (
        <div className="state-selection">
          <h2>Step 1: Select State/Territory</h2>
          <div className="state-grid">
            {Object.keys(stateMapping).map(state => (
              <button
                key={state}
                onClick={() => handleStateSelect(state)}
                className={`state-button ${selectedState === state ? 'selected' : ''}`}
              >
                {state}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="sa3-selection">
          <h2>Step 2: Select Regions in {selectedState}</h2>
          <p className="instruction">
            Select the SA3 regions you want to target. All SA2 areas within these regions will be included.
          </p>
          
          <div className="sa3-grid">
            {availableSA3s.map(sa3 => (
              <label key={sa3.code} className="area-checkbox">
                <input
                  type="checkbox"
                  checked={selectedSA3s.some(item => item.code === sa3.code)}
                  onChange={() => toggleSA3(sa3)}
                />
                <span>{sa3.name}</span>
              </label>
            ))}
          </div>

          {selectedSA3s.length > 0 && (
            <div className="sa2-preview">
              <h3>Selected Areas Summary</h3>
              <p><strong>Regions selected:</strong> {selectedSA3s.length}</p>
              <p><strong>Total SA2 areas:</strong> {finalSA2Areas.length}</p>
              
              <details>
                <summary>View all {finalSA2Areas.length} SA2 areas that will be researched</summary>
                <div className="sa2-list">
                  {selectedSA3s.map(sa3 => (
                    <div key={sa3.code} className="sa3-group">
                      <h4>{sa3.name}</h4>
                      <ul>
                        {finalSA2Areas
                          .filter(area => area.sa3_name === sa3.name)
                          .map((area, index) => (
                            <li key={area.code}>
                              {area.name} {area.population && `(Pop: ${area.population})`}
                            </li>
                          ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          )}
        </div>
      )}

      <div className="button-group">
        <button type="button" onClick={handleBack} className="btn-secondary">
          {step === 1 ? 'Back to Product' : 'Back to States'}
        </button>
        
        {step === 2 && (
          <button 
            onClick={handleSubmit}
            className="btn-primary"
            disabled={selectedSA3s.length === 0}
          >
            Generate Leads ({finalSA2Areas.length} areas)
          </button>
        )}
      </div>
    </div>
  );
};

export default GeographicalSelection;