import { useState, useEffect, useRef } from "react";
import { searchAddress, GeocodeResult } from "../../services/geocoding";

interface Props {
  placeholder: string;
  onSelect: (coords: [number, number] | null) => void;
}

export default function AutocompleteInput({ placeholder, onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GeocodeResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false); // Flaga kontrolna
  const timeoutRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isTyping || query.length < 3) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);

    timeoutRef.current = window.setTimeout(async () => {
      const data = await searchAddress(query);
      setResults(data);
      setIsOpen(true);
    }, 500);

    return () => {
      if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    };
  }, [query, isTyping]);

  const handleSelect = (item: GeocodeResult) => {
    setIsTyping(false);
    setQuery(item.display_name);
    setResults([]);
    setIsOpen(false);
    onSelect([parseFloat(item.lon), parseFloat(item.lat)]);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsTyping(true);
    setQuery(e.target.value);
    onSelect(null);
  };

  return (
    <div className="autocomplete-wrapper">
      <input
        type="text"
        placeholder={placeholder}
        value={query}
        onChange={handleChange}
        required
      />
      {isOpen && results.length > 0 && (
        <ul className="suggestions-list">
          {results.map((item, i) => (
            <li key={i} onClick={() => handleSelect(item)}>
              {item.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
