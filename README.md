# ReconX - Comprehensive Security Recon Tool

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
</p>

## 📋 Overview

**ReconX** is an advanced and comprehensive security reconnaissance tool written in Python, designed to gather information and discover vulnerabilities in web infrastructures.  
Developed by **NullSpecter (AbdUlrahman Elsayed)** to provide a reliable and easy-to-use tool for authorized security testing.

## ✨ Features

- 🔍 Subdomain discovery using multiple techniques  
- 🚪 Fast port scanning with common and custom ports  
- 🔬 Fingerprinting to identify servers and technologies  
- 🛡️ Security headers analysis  
- 📊 Export results to JSON, CSV, HTML, TXT  
- ⚡ High performance with Async/Await support  
- 🌐 Interactive CLI with colorized output  
- 📝 Full logging system  

## 📋 Requirements

- Python 3.8+  
- Windows / Linux / macOS  
- Disk: 50MB+  
- RAM: 512MB+

## 🚀 Installation

```bash
git clone https://github.com/abdelrhman445/reconx
cd reconx
pip install -r requirements.txt
pip install -e .
```

### (Coming soon) PyPI installation
```bash
pip install reconx
```

### (Coming soon) Docker
```bash
docker pull nullspecter/reconx:latest
docker run -it nullspecter/reconx --help
```

## 🎯 Usage Examples

### Subdomain Enumeration
```bash
reconx enum example.com
reconx enum example.com --wordlist words.txt
reconx enum example.com --threads 100 --timeout 10
reconx enum example.com --output subs.json
```

### Port Scanning
```bash
reconx scan example.com
reconx scan example.com --ports 80,443,8080
reconx scan example.com --ports 1-1000
reconx scan example.com --threads 200 --output ports.csv
```

### Fingerprinting
```bash
reconx fingerprint https://example.com
reconx fingerprint https://example.com --detailed
reconx fingerprint https://example.com --output fp.html
```

### Security Headers Analysis
```bash
reconx headers https://example.com
reconx headers https://example.com --output headers.json
```

### Full Recon Pipeline
```bash
reconx run example.com
reconx run example.com --pipeline "enum,scan,fingerprint,headers"
reconx run example.com --threads 100 --output final.json
```

### Exporting Data
```bash
reconx export results.json --format html --output report.html
reconx export results.json --format csv --output data.csv
```

## 🗂 Project Structure

```
reconx/
├── pyproject.toml
├── setup.py
├── requirements.txt
├── README.md
├── reconx/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── enumerator.py
│   │   ├── scanner.py
│   │   ├── fingerprint.py
│   │   ├── headers.py
│   │   └── exporter.py
│   └── utils/
│       ├── logger.py
│       └── helpers.py
└── tests/
```

## 🔧 Advanced Configuration

### Logger Level
```bash
export RECONX_LOG_LEVEL=DEBUG
```

### Using Proxy
```bash
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
```

## 🧪 Testing

```bash
pytest tests/test_enumerator.py
pytest tests/test_scanner.py
pytest tests/test_exporter.py
```

## ⚠️ Important Notes

1. Use responsibly and ethically  
2. Obtain prior permission before scanning  
3. Any misuse is your responsibility  
4. Educational and authorized security testing only  

## 🤝 Contribution

- Fork the repo  
- Create a new branch  
- Implement features  
- Open a Pull Request  
- Ensure code is clean and tests are added  

## 📄 License

MIT License – © 2024 NullSpecter

## 👤 Author

**NullSpecter — AbdUlrahman Elsayed**  
- Email: boodapro540@gmail.com  
- GitHub: https://github.com/nullspecter  
- YouTube: https://www.youtube.com/@gamotek175  
- LinkedIn: https://www.linkedin.com/in/abdulrahman-elsayed-59a664313  

## 🙏 Acknowledgments

- Open-source security community  
- Inspiration from other recon tools  
- All contributors and users  

## 📈 Roadmap

- [ ] Add vulnerability scanning  
- [ ] Integrate external recon sources  
- [ ] Web interface  
- [ ] CI/CD integration  
- [ ] Python library  
- [ ] Publish on PyPI  
- [ ] Official Docker images  

⭐ **If you like this project, give it a star on GitHub!**
