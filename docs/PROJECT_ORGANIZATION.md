# Atlas Project Organization Instructions

## 🗂️ File Structure Standards

### Core Directories
```
Atlas/
├── agents/                    # Core AI agents
├── config/                    # Configuration files
├── data/                      # Data storage
├── docs/                      # Documentation
├── monitoring/                # System monitoring
├── plugins/                   # Plugin system
├── rules/                     # Business rules
├── tools/                     # Utility tools
├── ui/                        # User interface
├── utils/                     # Utility functions
└── venv-macos/               # Virtual environment
```

### Development & Testing Structure
```
Atlas/
├── dev-tools/                # Development utilities
│   ├── analysis/            # Analysis scripts
│   ├── diagnostics/         # Diagnostic tools
│   ├── setup/               # Setup scripts
│   └── testing/             # Testing utilities
├── tests/                    # Test files
│   ├── security/            # Security tests
│   ├── integration/         # Integration tests
│   └── unit/                # Unit tests
├── scripts/                  # Automation scripts
│   ├── security/            # Security scripts
│   ├── maintenance/         # Maintenance scripts
│   └── deployment/          # Deployment scripts
└── requirements/             # Dependencies
    ├── requirements-linux.txt
    └── requirements-macos.txt
```

## 🔐 Security Organization

### Two-Level Security Architecture

#### Level 1: Atlas Core Security
- **Location**: `agents/encrypted_creator_protocols.py`
- **Access**: Only Atlas core system
- **Key**: Hardcoded internal key
- **Purpose**: Creator authentication, emotional protocols, system privileges

#### Level 2: Development Security
- **Location**: `docs/reports/security/`
- **Access**: Development and workflow AIs
- **Key**: `ATLAS_CORE_INIT_KEY` environment variable
- **Purpose**: Security documentation, development guidelines

### Security File Organization
```
Atlas/
├── agents/
│   ├── creator_authentication.py     # Creator auth system
│   └── encrypted_creator_protocols.py # Encrypted protocols (Atlas only)
├── docs/
│   └── reports/
│       └── security/
│           ├── SECURITY_SYSTEM_REPORT.md.encrypted  # Dev access
│           └── security_audit_logs/
├── tests/
│   └── security/                     # Security test files
└── scripts/
    └── security/                     # Security automation
```

## 📋 File Placement Rules

### Tests (`tests/`)
- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Security tests**: `tests/security/`
- **Performance tests**: `tests/performance/`

### Development Tools (`dev-tools/`)
- **Analysis scripts**: `dev-tools/analysis/`
- **Diagnostic tools**: `dev-tools/diagnostics/`
- **Setup utilities**: `dev-tools/setup/`
- **Testing utilities**: `dev-tools/testing/`

### Scripts (`scripts/`)
- **Security scripts**: `scripts/security/`
- **Maintenance scripts**: `scripts/maintenance/`
- **Deployment scripts**: `scripts/deployment/`
- **Automation scripts**: `scripts/automation/`

### Documentation (`docs/`)
- **API documentation**: `docs/api/`
- **Security documentation**: `docs/reports/security/`
- **Development guides**: `docs/development/`
- **User manuals**: `docs/user/`

## 🔒 Critical Security Protocols

### Access Control Rules

1. **Atlas Core Level**:
   - Only core Atlas system can access creator protocols
   - Hardcoded encryption keys
   - No external AI access permitted
   - Violation = immediate termination

2. **Development Level**:
   - Development AIs can access security documentation
   - Environment variable key access
   - Read-only access to design documentation
   - No protocol modification rights

3. **Encryption Requirements**:
   - All creator communications must be encrypted
   - Vector data encryption for creator sessions
   - Cache encryption for sensitive data
   - Log encryption for security events

### Security Data Handling

#### Creator Session Data
- **Location**: Memory only (no persistent storage)
- **Encryption**: Session-specific keys
- **Access**: Atlas core only
- **Lifecycle**: Destroyed on session end

#### Vector Data
- **Storage**: Encrypted in ChromaDB
- **Key Management**: Session-based encryption
- **Access Control**: Creator session validation
- **Backup**: Encrypted backups only

#### Communication Logs
- **Security Events**: Encrypted logging
- **Creator Interactions**: Encrypted cache
- **Access Attempts**: Encrypted audit trail
- **Retention**: Configurable with encryption

## 🚨 Security Violation Protocols

### Unauthorized Access Attempts
1. **Log the violation** (encrypted)
2. **Deny access** silently
3. **Alert security system**
4. **Terminate violating process**

### Protocol Modification Attempts
1. **Verify creator authentication**
2. **Log modification request** (encrypted)
3. **Create encrypted backup**
4. **Apply changes with verification**

### Data Breach Response
1. **Immediate session termination**
2. **Encrypted incident logging**
3. **Security protocol lockdown**
4. **Creator notification**

## 🔧 Implementation Guidelines

### Security Implementation
- All security-related code must use encryption
- Separate encryption keys for different access levels
- No hardcoded sensitive data in plain text
- Regular security audits required

### Development Workflow
- Keep development tools in `dev-tools/`
- Keep tests organized by type
- Keep scripts organized by purpose
- Keep security files properly encrypted

### Code Review Requirements
- Security code requires additional review
- Encryption implementation must be verified
- Access control logic must be tested
- No security bypasses permitted

---

**Remember**: 
- Atlas core has exclusive access to creator protocols
- Development AIs have limited security documentation access
- All sensitive data must be encrypted
- Maintain strict separation between access levels
