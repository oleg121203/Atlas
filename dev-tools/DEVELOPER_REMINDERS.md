# НАГАДУВАННЯ ДЛЯ РОЗРОБНИКІВ ATLAS

## СТРУКТУРА ФАЙЛІВ

**ОБОВ'ЯЗКОВО** дотримуйтесь структури файлів відповідно до `platform-info.instructions.md`:

```
Atlas/
├── utils/                      # Cross-platform utilities
│   ├── platform_utils.py      # Platform detection
│   ├── macos_utils.py         # macOS-specific utilities
│   └── linux_utils.py         # Linux development utilities
├── dev-tools/                  # Development utilities
│   ├── testing/               # Tests (NOT in root!)
│   ├── analysis/              # Analysis tools
│   ├── setup/                 # Setup tools
│   └── documentation/         # Developer documentation
├── docs/                       # Documentation
│   ├── reports/               # Reports (NOT in root!)
│   └── macos/                 # macOS documentation
├── requirements-linux.txt     # Linux (Python 3.12) deps
├── requirements-macos.txt     # macOS (Python 3.13) deps
└── launch_macos.sh           # Native macOS launcher
```

## ПЕРЕВІРКА СТРУКТУРИ

Використовуйте:
```bash
python dev-tools/check_file_structure.py
```

## ПЛАТФОРМИ

- **Linux**: Розробка (Python 3.12, headless)
- **macOS**: Цільова платформа (Python 3.13, GUI)

## НЕ КЛАДІТЬ ФАЙЛИ В КОРІНЬ!

❌ `test_*.py` в корені  
❌ `*_report.md` в корені  
❌ `analysis_*.py` в корені  

✅ `dev-tools/testing/test_*.py`  
✅ `docs/reports/*_report.md`  
✅ `dev-tools/analysis/analysis_*.py`  
