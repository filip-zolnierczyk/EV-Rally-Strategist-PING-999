import { Car } from "../types/Car";

const BASE_URL = "http://localhost:8000";

export const calculateRoute = async (
  start: [number, number],
  end: [number, number],
  carId: string,
  dateTime: string,
) => {
  const response = await fetch(`${BASE_URL}/calculate_distance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end, carId, dateTime }),
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
