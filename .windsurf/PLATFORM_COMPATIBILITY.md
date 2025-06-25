# ATLAS PLATFORM COMPATIBILITY

## Target Platform Specification

Atlas is exclusively developed and optimized for:

- **Hardware**: Mac Studio M1 Max with 32GB unified memory
- **Processor**: Apple M1 Max (10-core CPU: 8 performance cores + 2 efficiency cores)
- **Memory**: 32GB unified memory with high bandwidth
- **Operating System**: macOS
- **Architecture**: ARM64 (Apple Silicon)
- **Python Version**: 3.9.6

## Compatibility Status

| Platform | Status | Notes |
|----------|--------|-------|
| **Mac Studio M1 Max 32GB** | ✅ Fully Supported | Optimized for performance and memory usage |
| Other Apple Silicon Macs | ⚠️ Not Optimized | May work but not optimized for memory or performance |
| Intel Macs | ❌ Not Supported | Will not work correctly due to ARM64-specific optimizations |
| Linux | ❌ Not Supported | Development focus is exclusively on macOS |
| Windows | ❌ Not Supported | Not compatible |

## Mac Studio M1 Max Optimization

The application leverages specific hardware features of Mac Studio M1 Max:

- **Unified Memory Architecture**: Optimized memory usage patterns
- **Neural Engine**: Hardware acceleration for ML tasks
- **Metal Performance Shaders**: GPU acceleration
- **Performance Cores**: Workload distribution across the 8 performance cores
- **Native Frameworks**: Integration with macOS-specific frameworks

## Development Requirements

All development work must be performed on Mac Studio M1 Max 32GB to ensure compatibility and performance optimization. Code must be tested on the target platform before being committed.

## Language Requirements

- **Code**: All code, comments, and documentation must be in English
- **User Interface**: Must support Ukrainian, Russian, and English languages
- **Default Language**: Ukrainian is the default UI language

This document serves as the definitive specification for Atlas platform compatibility and should be consulted for all development decisions.
