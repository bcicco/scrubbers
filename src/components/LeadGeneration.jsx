import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLeadGen } from "../contexts/LeadGenContext";

const LeadGeneration = () => {
  const { sessionData, updateLeadResults, setProcessing } = useLeadGen();
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [currentArea, setCurrentArea] = useState("");
  const [completedAreas, setCompletedAreas] = useState([]);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    const processAreas = async () => {
      if (sessionData.selectedAreas.length === 0) {
        navigate("/select-areas");
        return;
      }

      setProcessing(true);
      const totalAreas = sessionData.selectedAreas.length;

      for (let i = 0; i < sessionData.selectedAreas.length; i++) {
        const area = sessionData.selectedAreas[i];
        setCurrentArea(area);
        print("Customer ID: ", sessionData.customerID)
        try {
          console.log(`Generating leads for ${area}...`);
          console.log(`product: ${sessionData.productName}`);
          console.log(`customerID: ${sessionData.customerID}`)
          const OpenAIurl = `/api/get_business_leads_openai?${new URLSearchParams({
            locality: area,
            product: sessionData.productName,
            product_description: sessionData.productDescription,
            customer_id: sessionData.customerID,
            target_industry: sessionData.targetIndustry,
          })}`;
          const leads = await fetch(OpenAIurl);
          console.log(leads)
          updateLeadResults(area, leads);
          setCompletedAreas((prev) => [...prev, area]);
          setProgress(((i + 1) / totalAreas) * 100);
        } catch (error) {
          console.error(`Error generating leads for ${area}:`, error);
          setErrors((prev) => [...prev, { area, error: error.message }]);
          // Continue with other areas even if one fails
        }
      }

      setProcessing(false);
      setCurrentArea("");

      // Navigate to results after a short delay
      setTimeout(() => {
        navigate("/results");
      }, 1000);
    };

    processAreas();
  }, []);

  const handleCancel = () => {
    setProcessing(false);
    navigate("/select-areas");
  };

  return (
    <div className="processing-container">
      <h1>Generating Business Leads</h1>

      <div className="progress-info">
        <p>
          <strong>CustomerID:</strong> {sessionData.customerID}
        </p>
        <p>
          <strong>Product Name:</strong>
          {sessionData.productName}
        </p>
        <p>
          <strong>Description:</strong> {sessionData.productDescription}
        </p>
        <p>
          <strong>Industry:</strong> {sessionData.targetIndustry}
        </p>
        <p>
          <strong>Total Areas:</strong> {sessionData.selectedAreas.length}
        </p>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="progress-text">{Math.round(progress)}% Complete</div>
      </div>

      {currentArea && (
        <div className="current-processing">
          <p>
            🔍 Currently researching: <strong>{currentArea}</strong>
          </p>
        </div>
      )}

      <div className="completed-areas">
        <h3>Completed Areas ({completedAreas.length}):</h3>
        <ul>
          {completedAreas.map((area) => (
            <li key={area}>✅ {area}</li>
          ))}
        </ul>
      </div>

      {errors.length > 0 && (
        <div className="errors">
          <h3>Errors:</h3>
          <ul>
            {errors.map((error, index) => (
              <li key={index}>
                ❌ {error.area}: {error.error}
              </li>
            ))}
          </ul>
        </div>
      )}

      <button onClick={handleCancel} className="btn-secondary">
        Cancel Process
      </button>
    </div>
  );
};

export default LeadGeneration;
