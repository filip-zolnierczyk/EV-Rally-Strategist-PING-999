export interface GeocodeResult {
  display_name: string;
  lat: string;
  lon: string;
}

export const searchAddress = async (
  query: string,
): Promise<GeocodeResult[]> => {
  if (!query || query.length < 3) return [];

  const response = await fetch(
    `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`,
  );

  if (!response.ok) return [];
  return await response.json();
};
