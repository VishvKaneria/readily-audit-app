import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_URL = "https://readily-audit-app-production.up.railway.app";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error("Error uploading file:", err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="title">📑 Readily Audit Tool</h1>

      <div className="upload-box">
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Processing..." : "Upload & Analyze"}
        </button>
      </div>

      {results && (
        <div className="results-box">
          <h2>Analysis Results</h2>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Requirement</th>
                <th>Requirement Met</th>
                <th>Policy</th>
                <th>Page</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {results.questions.map((q) => (
                <tr key={q.id}>
                  <td>{q.id}</td>
                  <td>{q.question}</td>
                  <td
                    style={{
                      color: q.requirement_met ? "green" : "red",
                      fontWeight: "bold",
                    }}
                  >
                    {q.requirement_met ? "✅ Yes" : "❌ No"}
                  </td>
                  <td>{q.policy || "-"}</td>
                  <td>{q.page || "-"}</td>
                  <td>{q.evidence || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
