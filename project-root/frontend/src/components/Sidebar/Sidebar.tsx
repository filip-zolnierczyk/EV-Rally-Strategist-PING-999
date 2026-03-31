import { useState } from "react";
import AutocompleteInput from "./AutocompleteInput";
import "./Sidebar.css";

interface SidebarProps {
  onPlanRoute: (
    startCoords: [number, number],
    endCoords: [number, number],
  ) => void;
  routeData: any;
  isLoading: boolean;
}

const MOCK_CARS = [
  { id: 1, name: "Tesla Model 3", battery: "60 kWh", range: "491 km" },
  { id: 2, name: "Tesla Model Y", battery: "75 kWh", range: "533 km" },
  { id: 3, name: "BMW iX3", battery: "80 kWh", range: "460 km" },
];

export default function Sidebar({
  onPlanRoute,
  routeData,
  isLoading,
}: SidebarProps) {
  const [startCoords, setStartCoords] = useState<[number, number] | null>(null);
  const [endCoords, setEndCoords] = useState<[number, number] | null>(null);
  const [selectedCar, setSelectedCar] = useState<number | null>(1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (startCoords && endCoords) {
      onPlanRoute(startCoords, endCoords);
    } else {
      alert("Wybierz dokładny adres z listy podpowiedzi.");
    }
  };

  const formatTime = (minutes: number) => {
    const hrs = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hrs}h ${mins}min`;
  };

  return (
    <div className="sidebar">
      <h2>EV Route Planner</h2>

      <section className="car-selection">
        <h3>Wybierz pojazd (Mock)</h3>
        <div className="car-list">
          {MOCK_CARS.map((car) => (
            <div
              key={car.id}
              className={`car-card ${selectedCar === car.id ? "selected" : ""}`}
              onClick={() => setSelectedCar(car.id)}
            >
              <div className="car-name">{car.name}</div>
              <div className="car-specs">
                {car.battery} • Zasięg: {car.range}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="route-form-section">
        <h3>Zaplanuj trasę</h3>
        <form onSubmit={handleSubmit} className="route-form">
          <AutocompleteInput
            placeholder="Skąd (np. ulica, miasto)"
            onSelect={setStartCoords}
          />
          <AutocompleteInput
            placeholder="Dokąd (np. ulica, miasto)"
            onSelect={setEndCoords}
          />
          <button
            type="submit"
            disabled={isLoading || !startCoords || !endCoords}
          >
            {isLoading ? "Szukanie..." : "Wyznacz trasę"}
          </button>
        </form>
      </section>

      {routeData && (
        <section className="route-results">
          <h3>Podsumowanie trasy</h3>
          <div className="summary-stats">
            <div>
              Dystans: <strong>{routeData.distance.toFixed(1)} km</strong>
            </div>
            <div>
              Czas jazdy: <strong>{formatTime(routeData.time)}</strong>
            </div>
          </div>

          <h3>Stacje ładowania ({routeData.chargings.length})</h3>
          <div className="charging-list">
            {routeData.chargings.map(
              (station: [number, number], index: number) => (
                <div key={index} className="charging-stop">
                  <div className="stop-number">{index + 1}</div>
                  <div className="stop-details">
                    <div>Ładowarka {index + 1}</div>
                    <div className="coords">
                      Współrzędne: {station[1].toFixed(4)},{" "}
                      {station[0].toFixed(4)}
                    </div>
                  </div>
                </div>
              ),
            )}
          </div>
        </section>
      )}
    </div>
  );
}
