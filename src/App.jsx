import { Routes, Route } from 'react-router-dom';
import { LeadGenProvider } from './contexts/LeadGenContext';
import ProductForm from './components/ProductForm';
import GeographicalSelection from './components/GeographicalSelection';
import './App.css';

function App() {
  return (
    <LeadGenProvider>
      <div className="App">
        <header className="app-header">
          <h1>Business Lead Generator</h1>
        </header>
        
        <main className="app-main">
          <Routes>
            <Route path="/" element={<ProductForm />} />
            <Route path="select-areas" element={<GeographicalSelection />} />
          </Routes>
        </main>
      </div>
    </LeadGenProvider>
  );
}

export default App;