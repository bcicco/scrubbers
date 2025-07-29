import { createContext, useContext, useState } from 'react';

const LeadGenContext = createContext();

export const LeadGenProvider = ({ children }) => {
  const [sessionData, setSessionData] = useState({
    sessionId: null,
    productDescription: '',
    targetIndustry: '',
    selectedAreas: [],
    leadResults: {},
    isProcessing: false,
    currentStep: 1,
    currentArea: ''
  });

  const updateProduct = (product, industry) => {
    setSessionData(prev => ({
      ...prev,
      productDescription: product,
      targetIndustry: industry,
      currentStep: 2
    }));
  };

  const updateAreas = (areas) => {
    setSessionData(prev => ({
      ...prev,
      selectedAreas: areas,
      currentStep: 3
    }));
  };

  const updateLeadResults = (area, leads) => {
    setSessionData(prev => ({
      ...prev,
      leadResults: {
        ...prev.leadResults,
        [area]: leads
      }
    }));
  };

  const setProcessing = (isProcessing, currentArea = '') => {
    setSessionData(prev => ({
      ...prev,
      isProcessing,
      currentArea
    }));
  };

  const value = {
    sessionData,
    updateProduct,
    updateAreas,
    updateLeadResults,
    setProcessing,
    setSessionData
  };

  return (
    <LeadGenContext.Provider value={value}>
      {children}
    </LeadGenContext.Provider>
  );
};

export const useLeadGen = () => {
  const context = useContext(LeadGenContext);
  if (!context) { 
    throw new Error('useLeadGen must be used within LeadGenProvider');
  }
  return context;
};