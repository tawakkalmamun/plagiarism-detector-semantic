import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Slider,
  Switch,
  FormControlLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  CloudUpload,
  Assessment,
  Download,
  CheckCircle,
  Warning,
  Info,
  Delete,
  Visibility,
  WifiTethering,
} from '@mui/icons-material';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import axios from 'axios';
import './App.css';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

// API Base URL - auto-detect
const API_URL = (() => {
  const envUrl = process.env.REACT_APP_API_URL;
  if (envUrl) return envUrl.trim();

  if (typeof window !== 'undefined') {
    const { hostname, origin } = window.location;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return '';
    }
    if (origin.includes('-3000.')) return origin.replace('-3000.', '-8000.');
    if (origin.includes(':3000')) return origin.replace(':3000', ':8000');
  }

  return 'http://localhost:8000';
})();
// console.log('[DEBUG] API_URL:', API_URL);

function App() {
  // State Management
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
  const [healthError, setHealthError] = useState(null);

  // File Upload Handler
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Hanya file PDF yang didukung');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError('Ukuran file maksimal 10MB');
        return;
      }
      setSelectedFile(file);
      setError(null);
      setResult(null);
    }
  };

  // Detect Plagiarism
  const handleDetect = async () => {
    if (!selectedFile) {
      setError('Silakan pilih file PDF terlebih dahulu');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('threshold', threshold);
    formData.append('use_search', useSearch);
    formData.append('use_local_corpus', true);
    formData.append('extract_abstract', extractAbstract);
    formData.append('chapters_only', chaptersOnly);
    formData.append('start_chapter', startChapter);
    formData.append('end_chapter', endChapter);

    try {
      const response = await axios.post(`${API_URL}/api/detect`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Terjadi kesalahan saat memproses file');
      setLoading(false);
    }
  };

  const handleHealthCheck = async () => {
    setHealthLoading(true);
    setHealthStatus(null);
    setHealthError(null);
    try {
      const resp = await axios.get(`${API_URL}/health`, { timeout: 10000 });
      setHealthStatus(resp.data);
    } catch (err) {
      let msg = 'Health check gagal';
      if (err.response) msg = `HTTP ${err.response.status}: ${err.response.data?.detail || 'Server error'}`;
      else if (err.request) msg = 'Network/timeout';
      else msg = err.message;
      setHealthError(msg);
    } finally {
      setHealthLoading(false);
    }
  };

  // Download CSV Report
  const handleDownload = async () => {
    if (!result?.task_id) return;

    try {
      const response = await axios.get(`${API_URL}/api/download/${result.task_id}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `laporan_plagiarisme_${result.task_id}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Gagal mengunduh laporan');
    }
  };

  // Reset Application
  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  // View Segment Detail
  const handleViewDetail = (segment) => {
    setSelectedSegment(segment);
    setDetailDialogOpen(true);
  };

  // Chart Data
  const pieChartData = result ? {
    labels: ['Plagiat', 'Original'],
    datasets: [{
      data: [result.plagiarized_segments, result.original_segments],
      backgroundColor: ['#f44336', '#4caf50'],
      borderColor: ['#d32f2f', '#388e3c'],
      borderWidth: 2,
    }],
  } : null;

  const barChartData = result ? {
    labels: result.details.map(d => `Seg ${d.segment_id}`),
    datasets: [{
      label: 'Skor Kemiripan',
      data: result.details.map(d => d.similarity_score),
      backgroundColor: result.details.map(d => 
        d.similarity_score >= threshold ? '#f44336' : '#4caf50'
      ),
      borderColor: '#1976d2',
      borderWidth: 1,
    }],
  } : null;

  return (
    <div className="App">
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <Typography variant="h3" align="center" color="white" gutterBottom>
            🔍 Deteksi Plagiarisme Semantik
          </Typography>
          <Typography variant="h6" align="center" color="white">
            Integrasi Google CSE & Sentence-BERT
          </Typography>
          <Typography variant="body2" align="center" color="white" sx={{ mt: 1 }}>
            Fakultas Teknik UNISMUH Makassar
          </Typography>
        </Paper>

        {/* Main Content */}
        <Grid container spacing={3}>
          {/* Left Panel - Upload & Settings */}
          <Grid item xs={12} md={4}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                📄 Upload Dokumen
              </Typography>

              {/* File Upload */}
              <Box sx={{ my: 2 }}>
                <input
                  accept="application/pdf"
                  style={{ display: 'none' }}
                  id="file-upload"
                  type="file"
                  onChange={handleFileSelect}
                />
                <label htmlFor="file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    fullWidth
                    startIcon={<CloudUpload />}
                    sx={{ py: 2 }}
                  >
                    Pilih File PDF
                  </Button>
                </label>

                {selectedFile && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <strong>{selectedFile.name}</strong>
                    <br />
                    Ukuran: {(selectedFile.size / 1024).toFixed(2)} KB
                  </Alert>
                )}
              </Box>

              {/* Settings */}
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                ⚙️ Pengaturan
              </Typography>

              <Box sx={{ my: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Threshold Kemiripan: {threshold.toFixed(2)}
                </Typography>
                <Slider
                  value={threshold}
                  onChange={(e, val) => setThreshold(val)}
                  min={0.5}
                  max={1.0}
                  step={0.05}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={useSearch}
                    onChange={(e) => setUseSearch(e.target.checked)}
                  />
                }
                label="Gunakan Google Search"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={extractAbstract}
                    onChange={(e) => setExtractAbstract(e.target.checked)}
                    disabled={chaptersOnly}
                  />
                }
                label="Hanya Analisis Abstrak"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={chaptersOnly}
                    onChange={(e) => setChaptersOnly(e.target.checked)}
                  />
                }
                label="Filter Bab (skip sampul/kata pengantar)"
              />

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<WifiTethering />}
                  onClick={handleHealthCheck}
                  disabled={healthLoading}
                >
                  {healthLoading ? 'Mengecek...' : 'Tes Koneksi API'}
                </Button>
                {healthStatus && (
                  <Alert severity="success" sx={{ mt: 1 }}>
                    API OK • Model: {healthStatus.services?.sbert_model} • Google: {healthStatus.services?.google_cse}
                  </Alert>
                )}
                {healthError && (
                  <Alert severity="error" sx={{ mt: 1 }} onClose={() => setHealthError(null)}>
                    {healthError}
                  </Alert>
                )}
              </Box>

              {chaptersOnly && (
                <Box sx={{ mt: 2, pl: 1 }}>
                  <Typography variant="body2" gutterBottom>
                    Bab Awal: {startChapter}
                  </Typography>
                  <Slider
                    value={startChapter}
                    onChange={(e, val) => setStartChapter(val)}
                    min={1}
                    max={10}
                    step={1}
                    marks
                    valueLabelDisplay="auto"
                  />
                  <Typography variant="body2" gutterBottom sx={{ mt: 1 }}>
                    Bab Akhir: {endChapter}
                  </Typography>
                  <Slider
                    value={endChapter}
                    onChange={(e, val) => setEndChapter(val)}
                    min={startChapter}
                    max={10}
                    step={1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Box>
              )}

              {/* Action Buttons */}
              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<Assessment />}
                  onClick={handleDetect}
                  disabled={!selectedFile || loading}
                  sx={{ mb: 1 }}
                >
                  {loading ? 'Memproses...' : 'Deteksi Plagiarisme'}
                </Button>

                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Delete />}
                  onClick={handleReset}
                  disabled={loading}
                >
                  Reset
                </Button>
              </Box>

              {loading && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="caption" align="center" display="block" sx={{ mt: 1 }}>
                    Menganalisis dokumen...
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Right Panel - Results */}
          <Grid item xs={12} md={8}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            {result && (
              <>
                {/* Summary Cards */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4" color="primary">
                          {result.total_segments}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Segmen
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4" color="error">
                          {result.plagiarized_segments}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Terindikasi Plagiat
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4" color="success.main">
                          {result.original_segments}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Original
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4" color={result.plagiarism_percentage > 50 ? 'error' : 'warning.main'}>
                          {result.plagiarism_percentage}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Persentase
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Charts */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={5}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Distribusi Hasil
                      </Typography>
                      {pieChartData && <Pie data={pieChartData} />}
                    </Paper>
                  </Grid>

                  <Grid item xs={12} md={7}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Skor Kemiripan Per Segmen
                      </Typography>
                      {barChartData && <Bar data={barChartData} options={{ maintainAspectRatio: true }} />}
                    </Paper>
                  </Grid>
                </Grid>

                {/* Detail Table */}
                <Paper sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      Detail Analisis Per Segmen
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<Download />}
                      onClick={handleDownload}
                      size="small"
                    >
                      Download CSV
                    </Button>
                  </Box>

                  <TableContainer sx={{ maxHeight: 440 }}>
                    <Table stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>ID</strong></TableCell>
                          <TableCell><strong>Teks Segmen</strong></TableCell>
                          <TableCell align="center"><strong>Skor</strong></TableCell>
                          <TableCell align="center"><strong>Status</strong></TableCell>
                          <TableCell align="center"><strong>Aksi</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {result.details.map((segment) => (
                          <TableRow key={segment.segment_id}>
                            <TableCell>{segment.segment_id}</TableCell>
                            <TableCell>
                              <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                                {segment.segment_text}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                label={segment.similarity_score.toFixed(3)}
                                size="small"
                                color={segment.similarity_score >= threshold ? 'error' : 'success'}
                              />
                            </TableCell>
                            <TableCell align="center">
                              {((segment.label || '').toUpperCase().includes('PLAGIAR')) ? (
                                <Chip
                                  icon={<Warning />}
                                  label="Plagiat"
                                  color="error"
                                  size="small"
                                />
                              ) : (
                                <Chip
                                  icon={<CheckCircle />}
                                  label="Original"
                                  color="success"
                                  size="small"
                                />
                              )}
                            </TableCell>
                            <TableCell align="center">
                              <IconButton
                                size="small"
                                onClick={() => handleViewDetail(segment)}
                              >
                                <Visibility />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <Box sx={{ mt: 2 }}>
                    <Alert severity="info" icon={<Info />}>
                      <strong>Waktu Pemrosesan:</strong> {result.processing_time} detik |{' '}
                      <strong>Rata-rata Kemiripan:</strong> {(result.avg_similarity * 100).toFixed(2)}%
                    </Alert>
                  </Box>
                </Paper>
              </>
            )}

            {!result && !loading && !error && (
              <Paper sx={{ p: 5, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary">
                  📊 Hasil deteksi akan ditampilkan di sini
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Upload file PDF dan klik "Deteksi Plagiarisme"
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>

        {/* Detail Dialog */}
        <Dialog
          open={detailDialogOpen}
          onClose={() => setDetailDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            Detail Segmen #{selectedSegment?.segment_id}
          </DialogTitle>
          <DialogContent dividers>
            {selectedSegment && (
              <>
                <Typography variant="subtitle2" gutterBottom>
                  <strong>Teks Segmen:</strong>
                </Typography>
                <Paper sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}>
                  <Typography variant="body2">
                    {selectedSegment.segment_text}
                  </Typography>
                </Paper>

                {selectedSegment.best_match && (
                  <>
                    <Typography variant="subtitle2" gutterBottom>
                      <strong>Teks Referensi Terdekat:</strong>
                    </Typography>
                    <Paper sx={{ p: 2, mb: 2, bgcolor: '#fff3e0' }}>
                      <Typography variant="body2">
                        {selectedSegment.best_match}
                      </Typography>
                    </Paper>

                    <Typography variant="body2">
                      <strong>Skor Kemiripan:</strong> {(selectedSegment.similarity_score * 100).toFixed(2)}%
                    </Typography>
                    <Typography variant="body2">
                      <strong>Sumber:</strong>{' '}
                      <a href={selectedSegment.source_url} target="_blank" rel="noopener noreferrer">
                        {selectedSegment.source_title || selectedSegment.source_url}
                      </a>
                    </Typography>
                  </>
                )}

                {!selectedSegment.best_match && (
                  <Alert severity="success">
                    Tidak ditemukan kecocokan yang signifikan. Segmen ini kemungkinan original.
                  </Alert>
                )}
              </>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailDialogOpen(false)}>Tutup</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </div>
  );
}

export default App;
