# 🤝 Contributing Guide

## Kontribusi untuk Pengembangan Sistem

Terima kasih atas minat Anda untuk berkontribusi! Sistem ini dikembangkan sebagai bagian dari skripsi, namun terbuka untuk improvement dan enhancement.

---

## 📋 Cara Berkontribusi

### 1. Fork & Clone
```bash
# Fork repository di GitHub
# Clone ke local
git clone <your-fork-url>
cd plagiarism-detector-semantic
```

### 2. Create Branch
```bash
git checkout -b feature/nama-fitur
```

### 3. Make Changes
- Implementasi fitur/fix
- Test perubahan
- Update dokumentasi jika perlu

### 4. Commit
```bash
git add .
git commit -m "feat: deskripsi perubahan"
```

### 5. Push & Pull Request
```bash
git push origin feature/nama-fitur
# Buat Pull Request di GitHub
```

---

## 🎯 Areas for Contribution

### High Priority
- [ ] Optimasi deteksi untuk bahasa Indonesia
- [ ] Implementasi database untuk storage
- [ ] Improve PDF extraction accuracy
- [ ] Add unit tests coverage
- [ ] Performance optimization

### Medium Priority
- [ ] UI/UX improvements
- [ ] Additional export formats (Excel, JSON)
- [ ] Email notification system
- [ ] Batch processing
- [ ] API documentation enhancement

### Low Priority
- [ ] Dark mode theme
- [ ] Mobile responsive improvements
- [ ] Internationalization (i18n)
- [ ] Custom SBERT model training

---

## 💻 Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Text editor (VS Code recommended)

### Setup Development Environment
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Run in Development Mode
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

---

## ✅ Code Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions
- Maximum line length: 100 characters

**Example:**
```python
def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    # Implementation
    pass
```

### JavaScript (Frontend)
- Use ES6+ syntax
- Functional components with hooks
- PropTypes for components
- Consistent naming conventions

**Example:**
```javascript
const DetectionResult = ({ result }) => {
  const [selected, setSelected] = useState(null);
  
  // Component logic
  
  return (
    // JSX
  );
};
```

### Documentation
- Update README if adding features
- Add comments for complex logic
- Update API documentation
- Include examples

---

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python test_system.py
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Test Coverage
Aim for minimum 70% code coverage for new features.

### Test Requirements
- Unit tests for new functions
- Integration tests for API endpoints
- E2E tests for critical user flows

---

## 📝 Commit Message Convention

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(detector): add batch processing support
fix(pdf): handle corrupted PDF files
docs(readme): update installation guide
test(api): add endpoint testing
```

---

## 🐛 Bug Reports

### How to Report
1. Check existing issues first
2. Create new issue with template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, etc.)

### Bug Report Template
```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen.

**Screenshots**
If applicable.

**Environment:**
- OS: [e.g. Windows 10]
- Python: [e.g. 3.9]
- Browser: [e.g. Chrome 95]
```

---

## 💡 Feature Requests

### How to Request
1. Check if feature already requested
2. Create issue with "Feature Request" label
3. Explain:
   - Use case
   - Expected behavior
   - Why it's beneficial
   - Possible implementation approach

---

## 📚 Resources

### Learning Materials
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Documentation](https://react.dev/)
- [Sentence-BERT Paper](https://arxiv.org/abs/1908.10084)
- [Python Best Practices](https://docs.python-guide.org/)

### Tools
- **IDE**: VS Code, PyCharm
- **API Testing**: Postman, Insomnia
- **Version Control**: Git, GitHub Desktop

---

## 👥 Code Review Process

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance impact acceptable
- [ ] Security considerations addressed

### Review Timeline
- Small PRs: 1-2 days
- Medium PRs: 3-5 days
- Large PRs: 1 week

---

## 🎓 For Academic Contributors

### Thesis/Research Use
If you're using this for academic purposes:

1. **Cite this work** appropriately
2. **Document your modifications**
3. **Share improvements** back to community
4. **Acknowledge** original author

### Collaboration
For research collaborations or academic partnerships:
- Contact: [your-email]
- Institution: UNISMUH Makassar

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## ❓ Questions?

- **Technical**: Open an issue on GitHub
- **General**: Email [your-email]
- **Academic**: Contact supervisor

---

## 🙏 Acknowledgments

Contributors will be listed in:
- README.md Contributors section
- CHANGELOG.md for specific versions
- Academic papers (if applicable)

---

**Thank you for contributing! 🎉**

Together we can make plagiarism detection better for academic institutions!
