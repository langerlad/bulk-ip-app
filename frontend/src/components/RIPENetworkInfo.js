import React, { useState } from 'react';

const RIPENetworkInfo = ({ ripeData }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Debug log
  console.log('RIPE Data in component:', ripeData);
  
  // If no RIPE data is available, don't render anything
  if (!ripeData || Object.keys(ripeData).length === 0) {
    return null;
  }
  
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  // Extract data
  const { 
    prefix, 
    asn, 
    holder, 
    country, 
    netname, 
    registrar, 
    registry,
    ip_range,
    cidr,
    reg_date,
    abuse_contacts 
  } = ripeData;
  
  // Helper functions for displaying information
  const getDisplayName = () => {
    if (holder) return holder;
    if (registrar) return registrar;
    if (netname) return `Network: ${netname}`;
    return 'Network Information';
  };
  
  const getDisplayRegistrar = () => {
    if (registrar) return registrar;
    if (holder && holder !== netname) return holder;
    if (registry) return `${registry} Registry`;
    return 'Unknown';
  };
  
  // Format ASN with "AS" prefix if exists
  const formattedAsn = asn ? `AS${asn}` : 'Unknown';
  
  // Check if we have any information to display
  const hasDetails = prefix || asn || holder || netname || country || 
                    registrar || registry || ip_range || cidr;
  
  return (
    <div className="ripe-network-section">
      <div className="section-header" onClick={toggleExpanded}>
        <h4>
          <span className="network-indicator">🌐</span>
          {getDisplayName()} 
          {registry && <span className="registry-badge">{registry}</span>}
          <span className="toggle-icon">{expanded ? '▼' : '►'}</span>
        </h4>
      </div>
      
      {expanded && hasDetails && (
        <div className="ripe-details">
          {/* Network Information */}
          <div className="detail-group">
            <div className="detail-group-title">Network Information</div>
            
            <div className="detail-row">
              {ip_range && (
                <div className="detail-item">
                  <span className="detail-label">IP Range:</span> 
                  {ip_range}
                </div>
              )}
              
              {cidr && (
                <div className="detail-item">
                  <span className="detail-label">CIDR:</span> 
                  {cidr}
                </div>
              )}
            </div>
            
            <div className="detail-row">
              {prefix && (
                <div className="detail-item">
                  <span className="detail-label">Network Prefix:</span> 
                  {prefix}
                </div>
              )}
              
              {asn && (
                <div className="detail-item">
                  <span className="detail-label">ASN:</span> 
                  {formattedAsn}
                </div>
              )}
            </div>
          </div>
          
          {/* Registration Information */}
          <div className="detail-group">
            <div className="detail-group-title">Registration Information</div>
            
            <div className="detail-row">
              {(registrar || holder || registry) && (
                <div className="detail-item">
                  <span className="detail-label">Registrar:</span> 
                  {getDisplayRegistrar()}
                </div>
              )}
              
              {netname && (
                <div className="detail-item">
                  <span className="detail-label">Network Name:</span> 
                  {netname}
                </div>
              )}
            </div>
            
            <div className="detail-row">
              {country && (
                <div className="detail-item">
                  <span className="detail-label">Country:</span> 
                  {country}
                </div>
              )}
              
              {reg_date && (
                <div className="detail-item">
                  <span className="detail-label">Registered:</span> 
                  {reg_date}
                </div>
              )}
            </div>
          </div>
          
          {/* Abuse Information */}
          {abuse_contacts && abuse_contacts.length > 0 && (
            <div className="detail-group">
              <div className="detail-group-title">Abuse Information</div>
              
              <div className="detail-row">
                <div className="detail-item full-width">
                  <span className="detail-label">Abuse Contacts:</span>
                  <ul className="contact-list">
                    {abuse_contacts.map((contact, index) => (
                      <li key={index}>
                        <a href={`mailto:${contact}`}>{contact}</a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Show a message if expanded but no details available */}
      {expanded && !hasDetails && (
        <div className="ripe-details">
          <p className="no-details">No additional network information available.</p>
        </div>
      )}
    </div>
  );
};

export default RIPENetworkInfo;