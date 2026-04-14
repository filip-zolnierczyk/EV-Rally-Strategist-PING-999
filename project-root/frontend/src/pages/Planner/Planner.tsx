import { useState } from "react";
import MapView from "../../components/Map/MapView";
import Sidebar from "../../components/Sidebar/Sidebar";
import { calculateRoute } from "../../services/api";
import "./Planner.css";

export default function Planner() {
  const [routeData, setRouteData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handlePlanRoute = async (
    startCoords: [number, number],
    endCoords: [number, number],
    carId: string,
  ) => {
    setIsLoading(true);
    try {
      const data = await calculateRoute(startCoords, endCoords, carId);
      setRouteData(data);
    } catch (error) {
      console.error(error);
      alert("Błąd podczas wyznaczania trasy.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="planner-container">
      <Sidebar
        onPlanRoute={handlePlanRoute}
        routeData={routeData}
        isLoading={isLoading}
      />
      <MapView routeData={routeData} />
    </div>
  );
}
