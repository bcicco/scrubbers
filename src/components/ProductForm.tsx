import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeadGen } from '../contexts/LeadGenContext';

const ProductForm = () => {
  const { sessionData, updateProduct } = useLeadGen();
  const navigate = useNavigate();
  
  const [product, setProduct] = useState(sessionData.productDescription);
  const [industry, setIndustry] = useState(sessionData.targetIndustry);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (product.trim() && industry.trim()) {
      updateProduct(product, industry);
      navigate('/select-areas');
    }
  };

  return (
    <div className="form-container">
      <h1>Describe Your Product</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="product">Product Description:</label>
          <textarea
            id="product"
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="Describe your product or service..."
            rows={4}
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