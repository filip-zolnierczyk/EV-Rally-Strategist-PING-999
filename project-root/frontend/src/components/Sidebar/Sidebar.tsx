import { useState, useEffect } from "react";
import AutocompleteInput from "./AutocompleteInput";
import { Car } from "../../types/Car";
import { getCars } from "../../services/api";
import "./Sidebar.css";

interface SidebarProps {
  onPlanRoute: (
    startCoords: [number, number],
    endCoords: [number, number],
    carId: string,
    departureDateTime: string,
  ) => void;
  routeData: any;
  isLoading: boolean;
}

export default function Sidebar({
  onPlanRoute,
  routeData,
  isLoading,
}: SidebarProps) {
  const [startCoords, setStartCoords] = useState<[number, number] | null>(null);
  const [endCoords, setEndCoords] = useState<[number, number] | null>(null);

  const [cars, setCars] = useState<Car[]>([]);
  const [selectedCar, setSelectedCar] = useState<string | null>(null);
  const [departureDateTime, setDepartureDateTime] = useState<string>(() => {
    const now = new Date();
    const tzOffset = now.getTimezoneOffset() * 60000;
    return new Date(now.getTime() - tzOffset).toISOString().slice(0, 16);
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedYear, setSelectedYear] = useState("");

  useEffect(() => {
    const fetchCarsData = async () => {
      try {
        const data = await getCars();
        setCars(data);
      } catch (error) {
        console.error("Error loading cars:", error);
      }
    };

    fetchCarsData();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (startCoords && endCoords && selectedCar) {
      onPlanRoute(startCoords, endCoords, selectedCar, departureDateTime);
    } else {
      alert("Wybierz dokładny adres z listy podpowiedzi.");
    }
  };

  const formatTime = (minutes: number) => {
    const hrs = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hrs}h ${mins}min`;
  };

  const filteredCars = cars.filter((car) => {
    const fullName = `${car.brand} ${car.model}`.toLowerCase();
    const matchesSearch = fullName.includes(searchQuery.toLowerCase());
    const matchesBrand = selectedBrand ? car.brand === selectedBrand : true;
    const matchesYear = selectedYear
      ? String(car.release_year) === selectedYear
      : true;
    return matchesSearch && matchesBrand && matchesYear;
  });

  const uniqueBrands = Array.from(new Set(cars.map((c) => c.brand))).sort();
  const uniqueYears = Array.from(
    new Set(cars.map((c) => c.release_year).filter(Boolean)),
  ).sort();

  // Helper function to get charger name from charger_info
  const getChargerName = (chargerInfo: any): string => {
    if (!chargerInfo) return "Nieznana stacja";
    // Try various possible name fields from the API response
    return chargerInfo.name ||
           chargerInfo.title ||
           chargerInfo.station_name ||
           "Nieznana stacja";
  };

  return (
    <div className="sidebar">
      <h2>EV Route Planner</h2>

      <section className="car-selection">
        <h3>Wybierz pojazd</h3>

        <div className="filters">
          <input
            type="text"
            placeholder="Szukaj auta..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="filter-row">
            <select
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
            >
              <option value="">Wszystkie marki</option>
              {uniqueBrands.map((brand) => (
                <option key={brand} value={brand}>
                  {brand}
                </option>
              ))}
            </select>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
            >
              <option value="">Wszystkie roczniki</option>
              {uniqueYears.map((year) => (
                <option key={year} value={String(year)}>
                  {year}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="car-list">
          {filteredCars.map((car) => (
            <div
              key={car.id}
              className={`car-card ${selectedCar === car.id ? "selected" : ""}`}
              onClick={() => setSelectedCar(car.id)}
            >
              <div className="car-name">
                {car.brand} {car.model}
              </div>
              <div className="car-specs">
                Bateria: {car.battery_capacity} kWh • Śr. zużycie:{" "}
                {car.avg_consumption} kWh/100km
                <br />
                Rocznik: {car.release_year || "Brak danych"}
              </div>
            </div>
          ))}
          {filteredCars.length === 0 && (
            <div className="car-specs">Nie znaleziono pojazdów.</div>
          )}
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
          <div className="datetime-wrapper">
            <label htmlFor="departure-time">Data i czas wyjazdu</label>
            <input
              id="departure-time"
              type="datetime-local"
              value={departureDateTime}
              onChange={(e) => setDepartureDateTime(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !startCoords || !endCoords || !selectedCar}
            title={!selectedCar ? "Wybierz najpierw pojazd" : ""}
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
            <div>
              Łączny czas: <strong>{formatTime(routeData.total_time)}</strong>
            </div>
          </div>

          <h3>Stacje ładowania ({routeData.chargings.length})</h3>
          <div className="charging-list">
            {routeData.chargings.map(
              (station: [number, number], index: number) => {
                const chargerInfo = routeData.charger_info?.[index];
                const chargerName = getChargerName(chargerInfo);

                return (
                  <div key={index} className="charging-stop">
                    <div className="stop-number">{index + 1}</div>
                    <div className="stop-details">
                      <div className="charger-name">{chargerName}</div>
                      <div className="coords">
                        Współrzędne: {station[1].toFixed(4)},{" "}
                        {station[0].toFixed(4)}
                      </div>
                      {routeData.charging_time?.[index] && (
                        <div className="charging-duration">
                          Czas ładowania: {formatTime(routeData.charging_time[index])}
                        </div>
                      )}
                      {routeData.plugs?.[index] && (
                        <div className="plug-type">
                          {routeData.plugs[index].plug_name || "Nieznany typ złącza"}
                        </div>
                      )}
                    </div>
                  </div>
                );
              },
            )}
          </div>
        </section>
      )}
    </div>
  );
}