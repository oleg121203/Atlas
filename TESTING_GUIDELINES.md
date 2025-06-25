# Atlas Testing Guidelines

## Plugin System Testing Methodology

### Dependency Testing
1. **Satisfied Dependencies**:
   - Verify plugins activate when all dependencies are present and active
   - Test with multiple dependency levels (nested dependencies)

2. **Missing Dependencies**:
   - Ensure plugins fail to activate when dependencies are missing
   - Verify proper error messages are returned

3. **Circular Dependencies**:
   - Detect and prevent activation of plugins with circular dependencies
   - Log appropriate warnings

### Performance Benchmarks
### Measured Performance (2025-06-25)
| Test Case | Metric | Target | Actual |
|-----------|--------|--------|--------|
| Dependency Resolution (100 plugins) | Execution Time | <100ms | 85.58μs |
| Mass Activation (1000 plugins) | Memory Usage | <100MB | 42.7MB |

### Benchmark Methodology
1. Use `pytest-benchmark` for timing measurements
2. Use `tracemalloc` for memory profiling
3. Run tests on clean environment
4. Average results over multiple runs

### Optimization Guidelines
- Keep dependency graphs shallow (<3 levels)
- Limit plugins to <50 direct dependencies
- Use lazy loading for heavy plugins

### Test Structure
```python
# Example test structure
def test_feature():
    # Setup
    registry = PluginRegistry()
    
    # Exercise
    result = registry.activate_plugin("test_plugin")
    
    # Verify
    assert result is True
    assert registry.get_plugin("test_plugin").is_active()
```

## Version Compatibility Testing

### Version Constraint Rules
1. **Format**: Must follow semantic versioning (major.minor.patch)
2. **Minimum Version**: Plugin won't load if app version is older
3. **Maximum Version**: Plugin won't load if app version is newer
4. **Wildcards**: Not currently supported (exact version matching)

### Test Cases
```python
# Example version test
@pytest.mark.version
def test_version_constraints():
    # Plugin requires app version between 1.2.0 and 2.0.0
    plugin = VersionTestPlugin("test", "1.0.0", "1.2.0", "2.0.0")
    
    # Should work with compatible version
    assert registry.activate_plugin("test", "1.5.0") is True
    
    # Should fail with older version
    assert registry.activate_plugin("test", "1.1.0") is False
    
    # Should fail with newer version
    assert registry.activate_plugin("test", "2.1.0") is False
```

### Edge Cases to Test
- Empty version strings
- Malformed version numbers
- Pre-release versions (1.0.0-alpha)
- Build metadata (1.0.0+build)

## Cross-Platform Compatibility Testing

### Platform Support Rules
1. **Supported Platforms**: macOS (darwin), Linux (linux), Windows (win32)
2. **Single Platform**: Plugins can be restricted to one platform
3. **Multi-Platform**: Plugins can support multiple platforms
4. **Validation**: Activation fails if current platform is unsupported

### Test Cases
```python
# Example platform test
@pytest.mark.platform
def test_platform_support():
    registry = MockPluginRegistry()
    plugin = PlatformTestPlugin("test", ["darwin", "linux"])
    
    with patch('sys.platform', 'darwin'):
        assert registry.activate_plugin("test") is True
    plugin.deactivate()
    
    with patch('sys.platform', 'win32'):
        assert registry.activate_plugin("test") is False
```

### Edge Cases to Test
- Platform-specific dependencies
- Case sensitivity in platform names
- Unknown platform identifiers
- Platform-specific UI behaviors

## CI/CD Integration
- All tests run on push to main branch
- Performance benchmarks compared against baseline
- Coverage reports generated automatically

## Writing New Tests
1. Follow Arrange-Act-Assert pattern
2. Include edge cases
3. Document test purpose in docstring
4. Keep tests isolated and independent
