// API client for Azure Function backend
export const generateLeadsForArea = async (productDescription, targetIndustry, area) => {
  try {
    // Extract product name from description (first few words)
    const productName = productDescription.split(' ').slice(0, 3).join(' ');
    
    const url = `/api/get_business_leads_openai?${new URLSearchParams({
      locality: area,
      product: productName,
      product_description: productDescription,
      target_industry: targetIndustry
    })}`;
    
    console.log('🔗 Making API request to:', url);
    
    const response = await fetch(url);
    
    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));
    
    // Get the raw response text first to see what we're actually getting
    const responseText = await response.text();
    console.log('📄 Raw response (first 200 chars):', responseText.substring(0, 200));
    
    if (!response.ok) {
      console.error('❌ Response not OK:', response.status, response.statusText);
      console.error('❌ Full response text:', responseText);
      throw new Error(`API error: ${response.status} - ${response.statusText}`);
    }
    
    // Try to parse as JSON
    let data;
    try {
      data = JSON.parse(responseText);
      console.log('✅ Successfully parsed JSON:', data);
    } catch (parseError) {
      console.error('❌ JSON parse error:', parseError);
      console.error('❌ Response was:', responseText);
      throw new Error(`Invalid JSON response: ${parseError.message}`);
    }
    
    // Transform Azure Function response to frontend format
    const transformedLeads = data.businesses.map(business => ({
      companyName: business.name,
      industry: business.industry,
      size: business.size || 'Unknown',
      contact: business.contact_email,
      website: business.website,
      phone: business.phone,
      location: business.location,
      reasoning: business.description || `Potential fit for ${productDescription} in ${targetIndustry}`
    }));
    
    console.log(`✅ Successfully transformed ${transformedLeads.length} leads for ${area}`);
    return transformedLeads;
    
  } catch (error) {
    console.error(`❌ Error generating leads for ${area}:`, error);
    throw error;
  }
};