import { Car } from "../types/Car";

const BASE_URL = "http://localhost:8000";

export const calculateRoute = async (
  start: [number, number],
  end: [number, number],
  carId: string,
  dateTime: string,
  chargingTo100: boolean = false,
) => {
  const response = await fetch(`${BASE_URL}/calculate_distance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end, carId, dateTime, charging_to_100: chargingTo100}),
  });
  if (!response.ok)
    throw new Error(`Network response was not ok: ${response.status}`);
  return response.json();
};

export const getCars = async (): Promise<Car[]> => {
  const response = await fetch(`${BASE_URL}/cars`);

  if (!response.ok)
    throw new Error(`Network response was not ok: ${response.status}`);

  return await response.json();
};



export const getElectricityPrice = async (lat: number, lon: number): Promise<number> => {
  const apiKey = import.meta.env.VITE_ELECTRICITY_MAPS_API_KEY;

  if (!apiKey) throw new Error("Brak klucza VITE_ELECTRICITY_MAPS_API_KEY");

  const url = `https://api.electricitymaps.com/v3/price-day-ahead/latest?lat=${lat}&lon=${lon}`;

  const response = await fetch(url, {
    method: "GET",
    headers: { "auth-token": apiKey }
  });

  if (!response.ok) throw new Error(`Błąd API prądu: ${response.status}`);

  const data = await response.json();
  // API zwraca EUR/MWh, dzielimy przez 1000 aby uzyskać EUR/kWh
  return data.value / 1000;
};

export const getGasolinePrice = async (lat: number, lon: number): Promise<number> => {
  const authValue = import.meta.env.VITE_OIL_PRICE_API_KEY;

  if (!authValue) throw new Error("Brak klucza VITE_OIL_PRICE_API_KEY");

  const url = `https://api.collectapi.com/gasPrice/fromCoordinates?lat=${lat}&lng=${lon}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "content-type": "application/json",
      "authorization": authValue 
    }
  });

  if (!response.ok) throw new Error(`Błąd API paliw: ${response.status}`);

  const data = await response.json();

  if (data.success && data.result?.length > 0) {
    const res = data.result[0];
    const price = parseFloat(res.gasoline);
    
    // Przelicznik walut: jeśli API zwróci USD, zamieniamy na EUR (kurs ok. 0.92)
    const isUSD = res.currency?.toLowerCase() === 'usd';
    const finalPrice = isUSD ? price * 0.92 : price;

    return Number(finalPrice.toFixed(2));
  }

  throw new Error("Nie znaleziono danych paliwowych");
};
