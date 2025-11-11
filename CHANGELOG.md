# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-01-16

### ✨ Initial Release

#### Added
- ✅ Core plagiarism detection engine with SBERT
- ✅ Google Custom Search Engine integration
- ✅ PDF text extraction (PyPDF2 & pdfplumber)
- ✅ Sliding window text segmentation
- ✅ Semantic similarity calculation with cosine similarity
- ✅ FastAPI backend with RESTful endpoints
- ✅ React frontend with Material-UI
- ✅ Real-time detection dashboard
- ✅ Visualization with charts (Pie & Bar)
- ✅ CSV report export
- ✅ Adjustable similarity threshold
- ✅ Multi-language support (Indonesian & English)
- ✅ Comprehensive documentation
- ✅ Testing suite
- ✅ Sample data for testing

#### Features
- **Backend API Endpoints**:
  - `POST /api/detect` - Detect from PDF file
  - `POST /api/detect-text` - Detect from raw text
  - `GET /api/result/{task_id}` - Get detection result
  - `GET /api/download/{task_id}` - Download CSV report
  - `GET /api/tasks` - List all tasks
  - `DELETE /api/task/{task_id}` - Delete task
  - `GET /health` - Health check

- **Frontend Features**:
  - File upload with drag & drop
  - Real-time progress indicator
  - Interactive charts and statistics
  - Detailed segment analysis
  - Source URL linking
  - Responsive design
  - Dark/Light mode support

#### Documentation
- README.md - Project overview
- QUICKSTART.md - 5-minute setup guide
- INSTALLATION.md - Complete installation guide
- METHODOLOGY.md - Research methodology
- PROJECT_STRUCTURE.md - Project organization

#### Technical Specifications
- **SBERT Model**: paraphrase-multilingual-mpnet-base-v2
- **Segment Size**: 25 words
- **Overlap**: 5 words
- **Default Threshold**: 0.75
- **API Rate Limit**: 100 requests/day (Google CSE free tier)

---

## [Planned] - Future Versions

### [1.1.0] - Q2 2025 (Planned)
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication system
- [ ] History tracking
- [ ] Batch processing for multiple files
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] API rate limiting
- [ ] Caching mechanism

### [1.2.0] - Q3 2025 (Planned)
- [ ] Mobile app (React Native)
- [ ] Integration with UNISMUH academic system
- [ ] Internal database for past thesis
- [ ] Comparison with internal database
- [ ] Advanced reporting
- [ ] Multi-user support with roles
- [ ] Department-level analytics

### [2.0.0] - Q4 2025 (Planned)
- [ ] Full paper analysis (not just abstract)
- [ ] Custom model fine-tuning for Indonesian
- [ ] Real-time collaboration detection
- [ ] Plagiarism prevention suggestions
- [ ] AI-powered paraphrase detection improvement
- [ ] Integration with Turnitin/iThenticate
- [ ] Machine learning model updates

---

## Version History

| Version | Release Date | Changes | Status |
|---------|--------------|---------|--------|
| 1.0.0 | 2025-01-16 | Initial Release | ✅ Released |
| 1.1.0 | Q2 2025 | Database & Auth | 📋 Planned |
| 1.2.0 | Q3 2025 | Mobile & Integration | 📋 Planned |
| 2.0.0 | Q4 2025 | Advanced Features | 📋 Planned |

---

## Contributing

Untuk kontribusi atau bug reports, silakan hubungi:
- Email: [your-email]
- GitHub: [repository-url]

---

## Maintenance Notes

### Known Issues (v1.0.0)
- Google API quota limitation (100/day free tier)
- Large PDF files (>10MB) may timeout
- Some PDF formats may not extract correctly
- SBERT model download requires stable internet (~500MB)

### Performance Notes
- Average detection time: 30-60 seconds per document
- Optimal segment size: 20-30 words
- Best threshold range: 0.70-0.80
- Recommended RAM: 8GB minimum

---

**Maintained by**: Mahasiswa Teknik Informatika UNISMUH Makassar  
**License**: MIT
