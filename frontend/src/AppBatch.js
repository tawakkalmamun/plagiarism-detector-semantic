import React, { useState } from 'react';
import {
  Container, Paper, Typography, Button, Box, LinearProgress, Alert, Card, CardContent, Grid, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Slider, Switch, FormControlLabel,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import { CloudUpload, Assessment, Download, CheckCircle, Warning, Info, Delete, Visibility } from '@mui/icons-material';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import axios from 'axios';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const API_URL = (() => {
  const envUrl = process.env.REACT_APP_API_URL;
  if (envUrl && envUrl.trim() !== '') {
    const cleaned = envUrl.trim().replace(/^"|"$/g, '').replace(/^'|'$/g, '');
    return cleaned;
  }
  if (typeof window !== 'undefined') {
    const { origin, hostname } = window.location;
    if (hostname && hostname !== 'localhost') {
      if (origin.includes('-3000.')) return origin.replace('-3000.', '-8000.');
      if (origin.includes(':3000')) return origin.replace(':3000', ':8000');
      return origin.replace(/\/?$/, ':8000');
    }
  }
  return 'http://localhost:8000';
})();

function AppBatch() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [threshold, setThreshold] = useState(0.75);
  const [useSearch, setUseSearch] = useState(true);
  const [extractAbstract, setExtractAbstract] = useState(false);
  const [chaptersOnly, setChaptersOnly] = useState(false);
  const [startChapter, setStartChapter] = useState(1);
  const [endChapter, setEndChapter] = useState(5);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [lastHealthError, setLastHealthError] = useState(null);
  // Batch mode dihapus; hanya single PDF

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.type !== 'application/pdf') { setError('Hanya PDF didukung'); return; }
    if (file.size > 10 * 1024 * 1024) { setError('Maks 10MB'); return; }
    setSelectedFile(file); setError(null); setResult(null);
  };

  const handleDetect = async () => {
    if (!selectedFile) { setError('Pilih file PDF dulu'); return; }
    setLoading(true); setError(null); setResult(null);
    const fd = new FormData();
    fd.append('file', selectedFile);
    fd.append('threshold', threshold);
    fd.append('use_search', useSearch);
    fd.append('extract_abstract', extractAbstract);
    fd.append('chapters_only', chaptersOnly);
    fd.append('start_chapter', startChapter);
    fd.append('end_chapter', endChapter);
    try {
      const resp = await axios.post(`${API_URL}/api/detect`, fd, { headers: { 'Content-Type':'multipart/form-data' }, timeout:300000 });
      setResult(resp.data);
    } catch (err) {
      let msg; if (err.response) { msg = `HTTP ${err.response.status}: ${err.response.data?.detail || 'Server error'}`; }
      else if (err.request) { msg = 'Network/timeout'; } else { msg = err.message; }
      setError(msg);
    } finally { setLoading(false); }
  };

  const handleHealthCheck = async () => {
    setHealthLoading(true); setHealthStatus(null); setLastHealthError(null);
    try { const r = await axios.get(`${API_URL}/health`, { timeout:10000 }); setHealthStatus(r.data); }
    catch (err) { let m; if (err.response) m = `HTTP ${err.response.status}`; else if (err.request) m='Network/timeout'; else m=err.message; setLastHealthError(m); }
    finally { setHealthLoading(false); }
  };

  const handleDownload = async () => {
    if (!result?.task_id) return;
    try { const resp = await axios.get(`${API_URL}/api/download/${result.task_id}`, { responseType:'blob' }); const url = URL.createObjectURL(new Blob([resp.data])); const a=document.createElement('a'); a.href=url; a.download=`laporan_plagiarisme_${result.task_id}.csv`; document.body.appendChild(a); a.click(); a.remove(); } catch { setError('Gagal unduh'); }
  };

  const handleReset = () => {
    setSelectedFile(null); setResult(null); setError(null);
  };

  const handleViewDetail = (seg) => { setSelectedSegment(seg); setDetailDialogOpen(true); };

  const pieChartData = result ? { labels:['Plagiat','Original'], datasets:[{ data:[result.plagiarized_segments,result.original_segments], backgroundColor:['#f44336','#4caf50'], borderColor:['#d32f2f','#388e3c'], borderWidth:2 }] } : null;
  const barChartData = result ? { labels: result.details.map(d=>`Seg ${d.segment_id}`), datasets:[{ label:'Skor Kemiripan', data:result.details.map(d=>d.similarity_score), backgroundColor: result.details.map(d=> d.similarity_score >= threshold ? '#f44336' : '#4caf50'), borderColor:'#1976d2', borderWidth:1 }] } : null;

  return (
    <div className="App">
      <Container maxWidth="lg" sx={{ py:4 }}>
        <Paper elevation={3} sx={{ p:3, mb:3, background:'linear-gradient(135deg,#667eea 0%,#764ba2 100%)' }}>
          <Typography variant="h3" align="center" color="white" gutterBottom>🔍 Deteksi Plagiarisme Semantik</Typography>
          <Typography variant="h6" align="center" color="white">Integrasi Google CSE & Sentence-BERT</Typography>
          <Typography variant="body2" align="center" color="white" sx={{ mt:1 }}>Fakultas Teknik UNISMUH Makassar</Typography>
          <Typography variant="caption" align="center" color="white" sx={{ display:'block', mt:1, opacity:0.8 }}>API Base: {API_URL}</Typography>
        </Paper>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper elevation={2} sx={{ p:3 }}>
              <Typography variant="h6" gutterBottom>📄 Upload Dokumen</Typography>
              <Box sx={{ my:2 }}>
                <input accept="application/pdf,text/plain,.txt" style={{ display:'none' }} id="file-upload" type="file" onChange={handleFileSelect} />
                <label htmlFor="file-upload"><Button variant="outlined" component="span" fullWidth startIcon={<CloudUpload />} sx={{ py:2 }}>Pilih File PDF</Button></label>
                {selectedFile && <Alert severity="info" sx={{ mt:2 }}><strong>{selectedFile.name}</strong><br/>Ukuran: {(selectedFile.size/1024).toFixed(2)} KB</Alert>}
              </Box>
              <Typography variant="subtitle2" gutterBottom sx={{ mt:3 }}>⚙️ Pengaturan</Typography>
              <Box sx={{ my:2 }}>
                <Typography variant="body2" gutterBottom>Threshold Kemiripan: {threshold.toFixed(2)}</Typography>
                <Slider value={threshold} onChange={(e,v)=>setThreshold(v)} min={0.5} max={1.0} step={0.05} marks valueLabelDisplay="auto" />
              </Box>
              <FormControlLabel control={<Switch checked={useSearch} onChange={(e)=>setUseSearch(e.target.checked)} />} label="Gunakan Google Search" />
              <FormControlLabel control={<Switch checked={extractAbstract} onChange={(e)=>setExtractAbstract(e.target.checked)} disabled={chaptersOnly} />} label="Hanya Analisis Abstrak" />
              <FormControlLabel control={<Switch checked={chaptersOnly} onChange={(e)=>setChaptersOnly(e.target.checked)} />} label="Filter Bab (skip sampul, kata pengantar, dll)" />
              {chaptersOnly && (
                <Box sx={{ mt: 2, pl: 2 }}>
                  <Typography variant="body2" gutterBottom>Bab Awal: {startChapter}</Typography>
                  <Slider value={startChapter} onChange={(e, val)=>setStartChapter(val)} min={1} max={10} marks valueLabelDisplay="auto" sx={{ width:'200px' }} />
                  <Typography variant="body2" gutterBottom sx={{ mt: 1 }}>Bab Akhir: {endChapter}</Typography>
                  <Slider value={endChapter} onChange={(e, val)=>setEndChapter(val)} min={startChapter} max={10} marks valueLabelDisplay="auto" sx={{ width:'200px' }} />
                </Box>
              )}
              <Box sx={{ mt:2 }}>
                <Button variant="outlined" size="small" onClick={handleHealthCheck} disabled={healthLoading}>{healthLoading ? 'Mengecek...' : 'Tes Koneksi API'}</Button>
                {healthStatus && <Alert severity="success" sx={{ mt:1 }}>API OK • Model: {healthStatus.services?.sbert_model} • Google: {healthStatus.services?.google_cse}</Alert>}
                {lastHealthError && <Alert severity="error" sx={{ mt:1 }}>Health gagal: {lastHealthError}</Alert>}
              </Box>
              <Box sx={{ mt:3 }}>
                <Button variant="contained" fullWidth startIcon={<Assessment />} onClick={handleDetect} disabled={!selectedFile || loading} sx={{ mb:1 }}>{loading ? 'Memproses...' : 'Deteksi Plagiarisme'}</Button>
                <Button variant="outlined" fullWidth startIcon={<Delete />} onClick={handleReset} disabled={loading}>Reset</Button>
              </Box>
              {loading && <Box sx={{ mt:2 }}><LinearProgress /><Typography variant="caption" align="center" display="block" sx={{ mt:1 }}>Menganalisis dokumen...</Typography></Box>}
            </Paper>
          </Grid>
          <Grid item xs={12} md={8}>
            {error && <Alert severity="error" sx={{ mb:2 }} onClose={()=>setError(null)}>{error}</Alert>}
            {result && (
              <>
                <Grid container spacing={2} sx={{ mb:3 }}>
                  <Grid item xs={6} md={3}><Card><CardContent><Typography variant="h4" color="primary">{result.total_segments}</Typography><Typography variant="body2" color="text.secondary">Total Segmen</Typography></CardContent></Card></Grid>
                  <Grid item xs={6} md={3}><Card><CardContent><Typography variant="h4" color="error">{result.plagiarized_segments}</Typography><Typography variant="body2" color="text.secondary">Terindikasi Plagiat</Typography></CardContent></Card></Grid>
                  <Grid item xs={6} md={3}><Card><CardContent><Typography variant="h4" color="success.main">{result.original_segments}</Typography><Typography variant="body2" color="text.secondary">Original</Typography></CardContent></Card></Grid>
                  <Grid item xs={6} md={3}><Card><CardContent><Typography variant="h4" color={result.plagiarism_percentage>50?'error':'warning.main'}>{result.plagiarism_percentage}%</Typography><Typography variant="body2" color="text.secondary">Persentase</Typography></CardContent></Card></Grid>
                </Grid>
                <Grid container spacing={2} sx={{ mb:3 }}>
                  <Grid item xs={12} md={5}><Paper sx={{ p:2 }}><Typography variant="h6" gutterBottom>Distribusi Hasil</Typography>{pieChartData && <Pie data={pieChartData} />}</Paper></Grid>
                  <Grid item xs={12} md={7}><Paper sx={{ p:2 }}><Typography variant="h6" gutterBottom>Skor Kemiripan Per Segmen</Typography>{barChartData && <Bar data={barChartData} options={{ maintainAspectRatio:true }} />}</Paper></Grid>
                </Grid>
                <Paper sx={{ p:2 }}>
                  <Box sx={{ display:'flex', justifyContent:'space-between', alignItems:'center', mb:2 }}>
                    <Typography variant="h6">Detail Analisis Per Segmen</Typography>
                    <Button variant="contained" startIcon={<Download />} onClick={handleDownload} size="small">Download CSV</Button>
                  </Box>
                  <TableContainer sx={{ maxHeight:440 }}>
                    <Table stickyHeader size="small"><TableHead><TableRow><TableCell><strong>ID</strong></TableCell><TableCell><strong>Teks Segmen</strong></TableCell><TableCell align="center"><strong>Skor</strong></TableCell><TableCell align="center"><strong>Status</strong></TableCell><TableCell align="center"><strong>Aksi</strong></TableCell></TableRow></TableHead><TableBody>{result.details.map(seg => (<TableRow key={seg.segment_id}><TableCell>{seg.segment_id}</TableCell><TableCell><Typography variant="body2" noWrap sx={{ maxWidth:300 }}>{seg.segment_text}</Typography></TableCell><TableCell align="center"><Chip label={seg.similarity_score.toFixed(3)} size="small" color={seg.similarity_score >= threshold ? 'error' : 'success'} /></TableCell><TableCell align="center">{seg.label === 'Plagiat' || seg.label === 'PLAGIARIZED' ? (<Chip icon={<Warning />} label="Plagiat" color="error" size="small" />) : (<Chip icon={<CheckCircle />} label="Original" color="success" size="small" />)}</TableCell><TableCell align="center"><IconButton size="small" onClick={()=>handleViewDetail(seg)}><Visibility /></IconButton></TableCell></TableRow>))}</TableBody></Table></TableContainer>
                  <Box sx={{ mt:2 }}><Alert severity="info" icon={<Info />}>Waktu: {result.processing_time} detik • Rata-rata Kemiripan: {(result.avg_similarity*100).toFixed(2)}%</Alert></Box>
                </Paper>
              </>
            )}
            {!result && !loading && !error && (
              <Paper sx={{ p:5, textAlign:'center' }}>
                <Typography variant="h6" color="text.secondary">📊 Hasil deteksi akan ditampilkan di sini</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt:1 }}>Upload satu PDF lalu jalankan deteksi.</Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
        <Dialog open={detailDialogOpen} onClose={()=>setDetailDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Detail Segmen #{selectedSegment?.segment_id}</DialogTitle>
          <DialogContent dividers>
            {selectedSegment && (
              <>
                <Typography variant="subtitle2" gutterBottom><strong>Teks Segmen:</strong></Typography>
                <Paper sx={{ p:2, mb:2, bgcolor:'#f5f5f5' }}><Typography variant="body2">{selectedSegment.segment_text}</Typography></Paper>
                {selectedSegment.best_match ? (
                  <>
                    <Typography variant="subtitle2" gutterBottom><strong>Teks Referensi Terdekat:</strong></Typography>
                    <Paper sx={{ p:2, mb:2, bgcolor:'#fff3e0' }}><Typography variant="body2">{selectedSegment.best_match}</Typography></Paper>
                    <Typography variant="body2"><strong>Skor Kemiripan:</strong> {(selectedSegment.similarity_score*100).toFixed(2)}%</Typography>
                    {selectedSegment.source_url ? (
                      <Typography variant="body2">
                        <strong>Sumber:</strong>{' '}
                        <a href={selectedSegment.source_url} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2' }}>
                          {selectedSegment.source_title || selectedSegment.source_url}
                        </a>
                      </Typography>
                    ) : selectedSegment.source_title || selectedSegment.source_domain ? (
                      <Typography variant="body2">
                        <strong>Sumber:</strong>{' '}
                        <span style={{ color: '#666', fontStyle: 'italic' }}>
                          {selectedSegment.source_title || selectedSegment.source_domain || 'Korpus Lokal'}
                        </span>
                      </Typography>
                    ) : null}
                  </>
                ) : <Alert severity="success">Tidak ada kecocokan signifikan (Original).</Alert>}
              </>
            )}
          </DialogContent>
          <DialogActions><Button onClick={()=>setDetailDialogOpen(false)}>Tutup</Button></DialogActions>
        </Dialog>
      </Container>
    </div>
  );
}

export default AppBatch;
