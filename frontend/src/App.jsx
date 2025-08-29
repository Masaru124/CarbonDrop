import React, {useState, useEffect} from 'react'
import Upload from './components/Upload'
export default function App(){
  const [history, setHistory] = useState([])
  useEffect(()=>{
    fetch('http://localhost:8000/footprint_history')
      .then(r=>r.json())
      .then(d=>setHistory(d.history || []))
      .catch(()=>{})
  }, [])
  return (
    <div className="container">
      <header><h1>EcoBasket</h1><p>Upload receipt → get carbon footprint</p></header>
      <main>
        <Upload onUploaded={()=>{
          fetch('http://localhost:8000/footprint_history').then(r=>r.json()).then(d=>setHistory(d.history || []))
        }} />
        <section className="history">
          <h2>History</h2>
          {history.length===0 && <p>No history yet.</p>}
          <ul>
            {history.map(h=>(
              <li key={h.id}>
                <strong>{new Date(h.date).toLocaleString()}</strong> — {h.total_footprint} kg CO₂
              </li>
            ))}
          </ul>
        </section>
      </main>
      <footer>Built with free tools · Tesseract OCR required for backend.</footer>
    </div>
  )
}
