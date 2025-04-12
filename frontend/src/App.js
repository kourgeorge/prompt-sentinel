import React, { useState, useEffect } from 'react';

function App() {
  const [reports, setReports] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch('/api/reports');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setReports(data.reports);
      } catch (error) {
        console.error('Error fetching reports:', error);
        setReports([]); // Set to empty array if there's an error to prevent map error
      }
    };

    fetchReports();
  }, []);

  // Check if reports is null before rendering the table
  if (reports === null) {
    return <div>Loading...</div>; // Or some other loading indicator
  }

  return (
    <div className="App">
      <h1>Prompt Sentinel Reports</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Prompt</th>
            <th>Secrets</th>
              <th>Sanitized Output</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {reports.length === 0 ? (
            <tr><td colSpan="5">No data available</td></tr>
          ) : (
            reports.map((report) => (

            <tr key={report.id}>

              <td>{report.id}</td>
              <td>{report.prompt}</td>
              <td>{report.secrets}</td>
              <td>{report.sanitized_output}</td>
              <td>{report.timestamp}</td>
            </tr>
          )))}

        </tbody>
      </table>
    </div>
  );
}

export default App;
