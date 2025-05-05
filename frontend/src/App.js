import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({ name: '', description: '' });
  
  useEffect(() => {
    fetchItems();
  }, []);
  
  const fetchItems = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/items');
      setItems(response.data);
    } catch (error) {
      console.error('Error fetching items:', error);
    }
  };
  
  const handleInputChange = (e) => {
    setNewItem({
      ...newItem,
      [e.target.name]: e.target.value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/items', newItem);
      setNewItem({ name: '', description: '' });
      fetchItems();
    } catch (error) {
      console.error('Error creating item:', error);
    }
  };
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>Flask + React Web App</h1>
        
        <form onSubmit={handleSubmit}>
          <div>
            <input
              type="text"
              name="name"
              placeholder="Item name"
              value={newItem.name}
              onChange={handleInputChange}
              required
            />
          </div>
          <div>
            <textarea
              name="description"
              placeholder="Item description"
              value={newItem.description}
              onChange={handleInputChange}
            />
          </div>
          <button type="submit">Add Item</button>
        </form>
        
        <div>
          <h2>Items</h2>
          {items.length === 0 ? (
            <p>No items found</p>
          ) : (
            <ul>
              {items.map(item => (
                <li key={item.id}>
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;