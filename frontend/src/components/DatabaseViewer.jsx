import { useState, useEffect } from 'react'
import './DatabaseViewer.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function DatabaseViewer({ token }) {
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState('')
  const [tableData, setTableData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTables()
  }, [])

  const fetchTables = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/database/tables`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setTables(data.tables)
        if (data.tables.length > 0) {
          setSelectedTable(data.tables[0])
          fetchTableData(data.tables[0])
        }
      }
    } catch (err) {
      setError('Failed to load tables')
    }
  }

  const fetchTableData = async (tableName) => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE_URL}/api/database/table/${tableName}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setTableData(data.rows)
      } else {
        setError('Failed to load table data')
      }
    } catch (err) {
      setError('Failed to load table data')
    } finally {
      setLoading(false)
    }
  }

  const handleTableChange = (tableName) => {
    setSelectedTable(tableName)
    fetchTableData(tableName)
  }

  return (
    <div className="database-viewer">
      <div className="db-header">
        <h2>🗄️ Database Viewer</h2>
        <p>View your database tables and data</p>
      </div>

      <div className="db-controls">
        <label>Select Table:</label>
        <select value={selectedTable} onChange={(e) => handleTableChange(e.target.value)}>
          {tables.map(table => (
            <option key={table} value={table}>{table}</option>
          ))}
        </select>
        <button onClick={() => fetchTableData(selectedTable)} className="btn-refresh">
          🔄 Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading data...</div>
      ) : (
        <div className="db-table-container">
          {tableData.length > 0 ? (
            <>
              <div className="table-info">
                <span>📊 {tableData.length} rows</span>
              </div>
              <div className="db-table-scroll">
                <table className="db-table">
                  <thead>
                    <tr>
                      {Object.keys(tableData[0]).map(column => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.map((row, idx) => (
                      <tr key={idx}>
                        {Object.values(row).map((value, i) => (
                          <td key={i}>{value !== null ? String(value) : 'NULL'}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>No data in this table</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DatabaseViewer
