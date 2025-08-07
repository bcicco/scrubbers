import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeadGen } from '../contexts/LeadGenContext';

const ProductForm = () => {
  const { sessionData, updateProduct } = useLeadGen();
  const navigate = useNavigate();
  
  const [productDesc, setProduct] = useState(sessionData.productDescription);
  const [industry, setIndustry] = useState(sessionData.targetIndustry);
  const [productName, setName] = useState(sessionData.prodctName)

  const handleSubmit = (e) => {
    e.preventDefault();
    if (productDesc.trim() && industry.trim() && productName.trim()) {
      updateProduct(productName, productDesc, industry);
      navigate('/select-areas');
    }
  };

  return (
    <div className="form-container">
      <h1>Describe Your Product</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="product">Product:</label>
          <textarea
            id="product"
            value={productName}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="Product Name"
            rows={4}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="product">Product Description:</label>
          <textarea
            id="product-description"
            value={productDesc}
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