import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeadGen } from '../contexts/LeadGenContext';

const ProductForm = () => {
  const { sessionData, updateProduct } = useLeadGen();
  const navigate = useNavigate();
  
  const [productDesc, setProductDesc] = useState(sessionData.productDescription);
  const [industry, setIndustry] = useState(sessionData.targetIndustry);
  const [productName, setProductName] = useState(sessionData.productName);
  const [customerID, setCustomerID] = useState(sessionData.customerID);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Check if all required fields are filled, including customerID
    if (productDesc.trim() && industry.trim() && productName.trim() && customerID.trim()) {
      updateProduct(customerID, productName, productDesc, industry);
      navigate('/select-areas');
    } else {
      alert('Please fill in all required fields');
    }
  };

  return (
    <div className="form-container">
      <h1>Describe Your Product</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="productName">Product:</label>
          <textarea
            id="productName"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            placeholder="Product Name"
            rows={4}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="product-description">Product Description:</label>
          <textarea
            id="product-description"
            value={productDesc}
            onChange={(e) => setProductDesc(e.target.value)}
            placeholder="Describe your product or service..."
            rows={4}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="customerID">Customer ID:</label>
          <input
            id="customerID"
            type="text"
            value={customerID}
            onChange={(e) => setCustomerID(e.target.value)}
            placeholder="Enter customer ID"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="industry">Target Industry:</label>
          <input
            id="industry"
            type="text"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g., Healthcare, Finance, Retail..."
            required
          />
        </div>
        
        <button type="submit" className="btn-primary">
          Next: Select Areas
        </button>
      </form>
    </div>
  );
};

export default ProductForm;