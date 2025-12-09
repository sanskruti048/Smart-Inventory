import React, { useEffect, useState } from "react";

function StatusBadge({ status }) {
  const color =
    status === "Critical"
      ? "#e11d48" // red
      : status === "Warning"
      ? "#f97316" // orange
      : "#16a34a"; // green

  return (
    <span
      style={{
        padding: "4px 8px",
        borderRadius: "999px",
        backgroundColor: color,
        color: "white",
        fontSize: "12px",
      }}
    >
      {status}
    </span>
  );
}

function SummaryCard({ label, value }) {
  return (
    <div
      style={{
        flex: 1,
        padding: "12px 16px",
        borderRadius: "8px",
        border: "1px solid #eee",
        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
        backgroundColor: "white",
      }}
    >
      <div style={{ fontSize: "12px", color: "#888" }}>{label}</div>
      <div style={{ fontSize: "20px", fontWeight: "bold" }}>{value}</div>
    </div>
  );
}

export default function InventoryHealthPage() {
  const [records, setRecords] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [storeFilter, setStoreFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch(`${API_URL}/latest`);
        const data = await res.json();
        setRecords(data.records || []);
        setFiltered(data.records || []);
        if (data.records && data.records.length > 0) {
          setLastUpdated(data.records[0].last_updated);
        }
      } catch (err) {
        console.error("Failed to fetch inventory data", err);
      }
    }

    fetchData();
  }, []);

  const countCritical = records.filter((r) => r.status === "Critical").length;
  const countWarning = records.filter((r) => r.status === "Warning").length;
  const countSafe = records.filter((r) => r.status === "Safe").length;

  useEffect(() => {
    let data = [...records];

    if (storeFilter !== "ALL") {
      data = data.filter((r) => r.store_id === storeFilter);
    }

    if (search.trim() !== "") {
      const term = search.trim().toLowerCase();
      data = data.filter((r) =>
        r.sku_id.toLowerCase().includes(term)
      );
    }

    setFiltered(data);
  }, [storeFilter, search, records]);

  const storeOptions = [
    "ALL",
    ...Array.from(new Set(records.map((r) => r.store_id))),
  ];

  return (
    <div
      style={{
        padding: "24px",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        backgroundColor: "#f9fafb",
        minHeight: "100vh",
      }}
    >
      <h1>Smart Inventory Health</h1>
      <p style={{ color: "#555" }}>
        Last updated: {lastUpdated ? new Date(lastUpdated).toLocaleString() : "N/A"}
      </p>

      {/* Filters */}
      <div style={{ display: "flex", gap: "16px", margin: "16px 0" }}>
        <div>
          <label>Store: </label>
          <select
            value={storeFilter}
            onChange={(e) => setStoreFilter(e.target.value)}
          >
            {storeOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Search SKU: </label>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="e.g., TSHIRT_RED_M"
          />
        </div>
      </div>

      {/* Summary */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "16px" }}>
        <SummaryCard label="Critical" value={countCritical} />
        <SummaryCard label="Warning" value={countWarning} />
        <SummaryCard label="Safe" value={countSafe} />
      </div>

      {/* Table */}
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          backgroundColor: "white",
        }}
      >
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
            <th style={{ padding: "8px" }}>SKU</th>
            <th style={{ padding: "8px" }}>Store</th>
            <th style={{ padding: "8px", textAlign: "right" }}>Current Stock</th>
            <th style={{ padding: "8px", textAlign: "right" }}>Days to Stockout</th>
            <th style={{ padding: "8px" }}>Status</th>
            <th style={{ padding: "8px", textAlign: "right" }}>Reorder Qty</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((row) => (
            <tr
              key={`${row.store_id}-${row.sku_id}`}
              style={{ borderBottom: "1px solid #f0f0f0" }}
            >
              <td style={{ padding: "8px" }}>{row.sku_id}</td>
              <td style={{ padding: "8px" }}>{row.store_id}</td>
              <td style={{ padding: "8px", textAlign: "right" }}>
                {row.current_stock}
              </td>
              <td style={{ padding: "8px", textAlign: "right" }}>
                {row.days_to_stockout === Infinity
                  ? "∞"
                  : row.days_to_stockout?.toFixed
                  ? row.days_to_stockout.toFixed(1)
                  : row.days_to_stockout}
              </td>
              <td style={{ padding: "8px" }}>
                <StatusBadge status={row.status} />
              </td>
              <td style={{ padding: "8px", textAlign: "right" }}>
                {row.recommended_reorder_quantity ?? "-"}
              </td>
            </tr>
          ))}

          {filtered.length === 0 && (
            <tr>
              <td colSpan="6" style={{ padding: "16px", textAlign: "center" }}>
                No records to display.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
