import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./Map.css";
import polyline from "@mapbox/polyline";

const createIcon = (color: string, symbol: string) => {
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="
      background-color: ${color}; 
      width: 24px; 
      height: 24px; 
      border-radius: 50%; 
      border: 2px solid white; 
      box-shadow: 0 2px 4px rgba(0,0,0,0.4); 
      display: flex; 
      justify-content: center; 
      align-items: center; 
      color: white; 
      font-weight: bold; 
      font-size: 12px;
      font-family: sans-serif;
    ">${symbol}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  });
};

const startIcon = createIcon("#198754", "S");
const endIcon = createIcon("#dc3545", "M");
const chargeIcon = createIcon("#FEFFB5", "⚡");

function ChangeView({ coordinates }: { coordinates: [number, number][] }) {
  const map = useMap();

  useEffect(() => {
    if (coordinates.length > 0) {
      const bounds = L.latLngBounds(coordinates);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coordinates, map]);

  return null;
}

export default function MapView({ routeData }: { routeData: any }) {
  const defaultCenter: [number, number] = [52.0693, 19.4803];

  const leafletCoords: [number, number][] = routeData?.coordinates
    ? polyline.decode(routeData.coordinates)
    : [];

  const leafletChargings: [number, number][] = routeData?.chargings
    ? routeData.chargings.map((c: [number, number]) => [c[1], c[0]])
    : [];

  return (
    <div className="map-wrapper">
      <MapContainer
        center={defaultCenter}
        zoom={6}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {routeData && leafletCoords.length > 0 && (
          <>
            <ChangeView coordinates={leafletCoords} />

            <Polyline positions={leafletCoords} color="#0d6efd" weight={5} />

            {/* Ikona Startu */}
            <Marker position={leafletCoords[0]} icon={startIcon}>
              <Popup>Start</Popup>
            </Marker>

            {/* Ikona Mety */}
            <Marker
              position={leafletCoords[leafletCoords.length - 1]}
              icon={endIcon}
            >
              <Popup>Meta</Popup>
            </Marker>

            {/* Ikony stacji ładowania */}
            {leafletChargings.map((station, index) => (
              <Marker
                key={`charge-${index}`}
                position={station}
                icon={chargeIcon}
              >
                <Popup>Stacja ładowania {index + 1}</Popup>
              </Marker>
            ))}
          </>
        )}
      </MapContainer>
    </div>
  );
}
