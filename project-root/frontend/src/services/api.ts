export const calculateRoute = async (
  start: [number, number],
  end: [number, number],
) => {
  const response = await fetch("http://localhost:8000/calculate_distance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end }),
  });
  if (!response.ok) throw new Error("Network response was not ok");
  return response.json();
};
