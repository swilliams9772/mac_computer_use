# Performance Improvements for Agent Testing the Burial Allowance Application

## Overview
This document summarizes the key performance improvements implemented based on Anthropic's documentation and best practices for Claude 4, Claude 3.7, and computer use optimization.

## Major Improvements Implemented

### 1. **Tool Version & Beta Flag Optimization**
- **Enhanced model detection**: Improved `get_tool_versions_for_model()` to properly handle Bedrock cross-region inference profiles
- **Base model extraction**: Added logic to correctly parse model names like `us.anthropic.claude-sonnet-4-20250514-v1:0`
- **Tool version mapping**: 
  - Claude 4: Uses `text_editor_20250429` (latest version)
  - Claude 3.7: Uses `text_editor_20250124` for token efficiency
  - Claude 3.5: Uses `text_editor_20241022` (stable version)

### 2. **Enhanced Error Handling & Timeout Management**
- **Specific HTTP status handling**: Added actionable error messages for:
  - 429 (Rate Limit): Includes retry-after header parsing and tier upgrade guidance
  - 413 (Request Too Large): Specific guidance on reducing tokens, images, history
  - 529 (API Overloaded): Exponential backoff recommendations
  - 400/401/403: Clear parameter and authentication guidance
- **Timeout improvements**: Enhanced timeout errors with thinking budget context
- **Batch processing recommendations**: Automatic suggestions for >32k thinking budgets

### 3. **System Prompt Enhancement with Claude 4 Best Practices**
- **Explicit instruction guidelines**: Added Claude 4's preference for clear, explicit instructions
- **Parallel tool execution guidance**: Enhanced prompting for near 100% parallel tool success rate
- **Step-by-step verification patterns**: Integrated "After each step, take a screenshot and carefully evaluate..." guidance
- **M4 MacBook Air optimizations**: Hardware-specific thermal and performance management
- **Sequoia form handling strategies**: Enhanced web form automation for macOS 15.6

#### Key Claude 4 Patterns Added:
```
"Include as many relevant features and interactions as possible"
"Go beyond the basics to create a fully-featured implementation"
"After receiving tool results, carefully reflect on their quality and determine optimal next steps"
```

### 4. **Computer Tool Screenshot Resolution Optimization**
- **Anthropic XGA/WXGA compliance**: Implemented resolution targeting of 1024x768 to 1280x800 range
- **Automatic resizing**: Added `sips` command integration for optimal Claude performance
- **Resolution debugging**: Added logging when resolution optimization is applied
- **Performance comments**: Enhanced coordinate scaling with optimization notes

## Technical Details

### Enhanced Beta Flag Management
```python
def get_beta_flags_for_model(model: str) -> list[str]:
    """Get all appropriate beta flags for a given model."""
    beta_flags = []
    
    # Add token efficiency for Claude 3.7 FIRST (most important for performance)
    if model_supports_token_efficiency(model):
        beta_flags.append("token-efficient-tools-2025-02-19")
    
    # Add interleaved thinking for Claude 4 FIRST (most important for performance)
    if model_supports_interleaved_thinking(model):
        beta_flags.append("interleaved-thinking-2025-05-14")
    
    # Get the primary tool beta flag LAST (required but less performance critical)
    tool_versions = get_tool_versions_for_model(model)
    beta_flags.append(tool_versions["beta_flag"])
    
    return beta_flags
```

### Screenshot Resolution Optimization
```python
def get_optimal_screenshot_resolution(self) -> tuple[int, int]:
    """Get optimal screenshot resolution based on Anthropic recommendations."""
    # Target around 1024x768 to 1280x800 range for better model accuracy and speed
    max_width = 1280
    max_height = 1024
    
    # Calculate scale to fit within recommended bounds
    width_scale = max_width / self.width if self.width > max_width else 1.0
    height_scale = max_height / self.height if self.height > max_height else 1.0
    scale = min(width_scale, height_scale)
    
    optimal_width = int(self.width * scale)
    optimal_height = int(self.height * scale)
    
    return (optimal_width, optimal_height)
```

## Key Benefits for Burial Allowance Testing

### 1. **Improved Form Interaction Reliability**
- Enhanced form field detection and interaction patterns
- Better error recovery with multiple fallback methods
- M4-optimized timing for Sequoia's improved form handling

### 2. **Better Screenshot Analysis**
- Optimal resolution for Claude's computer vision capabilities
- Reduced token usage while maintaining visual quality
- Faster processing and improved accuracy

### 3. **Enhanced Error Recovery**
- Actionable error messages help debug issues faster
- Automatic batch processing recommendations for complex workflows
- Better timeout handling for extended thinking sessions

### 4. **Token Efficiency Gains**
- Claude 3.7: Up to 70% token reduction with token-efficient tools
- Claude 4: Improved reasoning with interleaved thinking
- Better parallel tool execution reduces overall request count

## Performance Monitoring

### M4 Hardware Optimization
- Thermal state monitoring during intensive operations
- Performance core utilization for interactive tasks
- Enhanced timing parameters optimized for Apple Silicon

### Testing Metrics to Track
1. **Success Rate**: Form completion success percentage
2. **Error Recovery**: Time to recover from failed interactions
3. **Token Usage**: Reduction in total tokens per test cycle
4. **Screenshot Quality**: Visual analysis accuracy improvements

## Recommendations for Testing Workflow

### 1. **Use Claude 4 for Complex Test Scenarios**
- Enable interleaved thinking for multi-step validation
- Leverage explicit instruction patterns for consistent results
- Use parallel tool execution for efficiency

### 2. **Use Claude 3.7 for High-Volume Testing**
- Enable token-efficient tools for cost optimization
- Use extended thinking for complex form validation logic
- Batch similar test cases together

### 3. **Monitor Performance Continuously**
- Track thermal state during intensive test runs
- Monitor API usage patterns and adjust timeouts accordingly
- Use screenshot resolution optimization for faster processing

## Implementation Status

✅ **Completed**:
- Tool version detection enhancement
- Error handling improvements
- System prompt Claude 4 optimization
- Screenshot resolution optimization
- Beta flag management enhancement

🔄 **Ongoing**:
- Performance monitoring and metric collection
- Test case optimization based on new capabilities
- Fine-tuning timing parameters for M4 hardware

## Next Steps

1. **Test the improvements** with actual Burial Allowance application workflows
2. **Monitor performance metrics** and adjust parameters as needed
3. **Implement additional optimizations** based on real-world usage patterns
4. **Consider batch processing** for high-volume test scenarios (>32k thinking budgets)

---

*This implementation follows Anthropic's latest best practices documentation and is optimized specifically for Mac M4 hardware with macOS Sequoia 15.6.* 