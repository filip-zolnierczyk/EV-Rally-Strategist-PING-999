import React, { useState } from 'react';
import './CarForm.css';

interface CarRecommendation {
  make: string;
  model: string;
  price: number;
  range_km: number;
  body_type: string;
  seats: number;
  url: string;
}

const CarForm: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [cars, setCars] = useState<CarRecommendation[]>([]);

  // Ustawiamy puste stringi na start, żeby inputy były puste (Any)
  const [formData, setFormData] = useState({
    min_price: '',
    max_price: '',
    range: '',
    body_type: 'any',
    seats: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Zapisujemy wartość taką, jaka jest (jako string), 
    // żeby dało się łatwo kasować tekst w polu
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Konwersja danych przed wysyłką: jeśli puste -> -1, inaczej -> Number
    const dataToSend = {
      min_price: formData.min_price === '' ? -1 : Number(formData.min_price),
      max_price: formData.max_price === '' ? -1 : Number(formData.max_price),
      range: formData.range === '' ? -1 : Number(formData.range),
      seats: formData.seats === '' ? -1 : Number(formData.seats),
      body_type: formData.body_type, // tu już jest "any" lub konkretna marka
    };

    try {
      const response = await fetch('http://localhost:8000/choose_my_car', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSend),
      });

      if (!response.ok) throw new Error('Błąd pobierania danych');

      const data = await response.json();
      setCars(data);
    } catch (error) {
      console.error("Błąd wysyłki:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="car-page-wrapper">
      <div className="car-form-container">
        <h1>Smart EV Finder</h1>
        <form onSubmit={handleSubmit} className="car-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Minimalna cena (USD)</label>
              <input 
                type="number" 
                name="min_price" 
                placeholder="Any" 
                value={formData.min_price} 
                onChange={handleChange} 
              />
            </div>
            <div className="form-group">
              <label>Maksymalna cena (USD)</label>
              <input 
                type="number" 
                name="max_price" 
                placeholder="Any" 
                value={formData.max_price} 
                onChange={handleChange} 
              />
            </div>
            <div className="form-group">
              <label>Minimalny zasięg (km)</label>
              <input 
                type="number" 
                name="range" 
                placeholder="Any" 
                value={formData.range} 
                onChange={handleChange} 
              />
            </div>
            <div className="form-group">
              <label>Liczba siedzeń</label>
              <input 
                type="number" 
                name="seats" 
                placeholder="Dowolna" 
                value={formData.seats} 
                onChange={handleChange} 
              />
            </div>
          </div>

          <div className="form-group">
            <label>Typ nadwozia</label>
            <select name="body_type" value={formData.body_type} onChange={handleChange}>
              <option value="any">Dowolny</option>
              <option value="SUV">SUV</option>
              <option value="sedan">Sedan</option>
              <option value="hatchback">Hatchback</option>
              <option value="wagon">Wagon</option>
              <option value="pickup">Pickup</option>
            </select>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Searching...' : 'Find Your Perfect EV'}
          </button>
        </form>
      </div>

      <div className="cars-container">
        {cars.map((car, index) => (
          <div key={index} className="car-card">
            <div className="car-badge">{car.body_type}</div>
            <h2>{car.make} {car.model}</h2>
            <div className="car-details">
              <strong>Price:</strong> {car.price === 1 ? "Nieznana" : `${car.price.toLocaleString()} USD`}
              <p><strong>Zasięg:</strong> {car.range_km} km</p>
              <p><strong>Liczba siedzeń:</strong> {car.seats}</p>
            </div>
            <a href={car.url} target="_blank" rel="noreferrer" className="view-link">
              Zobacz stronę producenta
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CarForm;