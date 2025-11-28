# Video Tagger Revamp - Changelog

## Overview

Complete redesign of both `prompt.txt` and `POC_Video_Tagger.py` based on findings from `ANALYSIS.md`. The changes shift from a "concise" approach to a "search-optimized" approach that maximizes the 250-character filename limit.

---

## 🎯 Core Philosophy Change

### Before:
- Goal: "Concise, searchable filenames"
- Target: Keep it short, avoid redundancy
- Result: 95.8 avg characters (38% capacity)

### After:
- Goal: "Maximize search recall through comprehensive keyword coverage"
- Target: 230-250 characters (92-100% capacity)
- Expected: Much better search findability

---

## 📝 prompt.txt Changes

### Major Additions

1. **Explicit Length Target**
   - Before: "Keep output under 250 characters" (vague)
   - After: "Generate 230-250 characters" + strategy guide

2. **Redundancy is Good**
   - Before: "Never repeat the same word"
   - After: "REDUNDANCY IS GOOD: Multiple ways to say the same thing improves search recall"

3. **Comprehensive Examples**
   - Added 4 complete before/after examples
   - Shows bad (short) vs good (comprehensive) outputs
   - Includes character counts

4. **Morphological Variations Section**
   - Indonesian prefix forms (ter-, di-, me-, ber-)
   - Example: tindih → tertindih ditindih ditimpa tertimpa

5. **Local Abbreviations Guide**
   - mercy/merc (Mercedes-Benz)
   - raibon (Innova Reborn)
   - BBM, SPBU, cumi, tobr

6. **Strategy for Maximizing Length**
   - Step-by-step guide: Start with core (20-40 chars), then expand
   - Helps AI systematically reach 230-250 chars

### Removed Directives

1. ❌ "concise, searchable filenames" → conflicts with length goal
2. ❌ "Never repeat" → conflicts with synonym variations
3. ❌ "Don't translate every single word" → limits bilingual coverage

### Improved Directives

1. ✅ Bilingual coverage emphasized (both EN + ID for all key terms)
2. ✅ Synonym variations encouraged (3-5 ways to say same thing)
3. ✅ Search recall prioritized over brevity

---

## 🐍 POC_Video_Tagger.py Changes

### 1. Removed Deduplication Logic

**Before:**
```python
# Split and remove duplicates while preserving order
words = keys.split()
seen = set()
unique_words = []
for word in words:
    word_lower = word.lower()
    if word_lower not in seen and len(word) > 0:
        seen.add(word_lower)
        unique_words.append(word)
```

**After:**
```python
# IMPORTANT: Do NOT remove "duplicates" - they are intentional search variations
text = re.sub(r'\s+', ' ', text).strip()
return text
```

**Why:** "Duplicates" like `kecelakaan accident tabrakan crash` are search variations, not redundancy.

---

### 2. Length Targeting System

**New Constants:**
```python
TARGET_MIN_LENGTH = 230
TARGET_MAX_LENGTH = 250
ABSOLUTE_MAX_LENGTH = 255  # Filesystem limit
```

**New Feedback System:**
```python
# If too short, warn
if base_length < TARGET_MIN_LENGTH:
    print(f"⚠️  Only {base_length} chars - below target of {TARGET_MIN_LENGTH}")

# If in target range, celebrate!
elif TARGET_MIN_LENGTH <= base_length <= TARGET_MAX_LENGTH:
    print(f"✓ {base_length} chars - optimal length!")
```

**Why:** Provides real-time feedback on whether prompt is generating enough keywords.

---

### 3. Source Attribution Enhancement

**New Function:**
```python
def extract_source_from_content(self, file_path):
    """Use Gemini Vision to extract source/watermark from image content."""
```

**Features:**
- Searches for Instagram handles (@username)
- Looks for watermarks
- Identifies screenshot sources
- Falls back if filename has no source prefix

**Why:** Addresses the critical 0% vs 91% source attribution gap.

---

### 4. Improved MIME Type Handling

**Before:**
```python
mime_type=f"{'video' if file_path.suffix.lower() in ['.mp4', '.avi', '.mov'] else 'image'}/{file_path.suffix[1:]}"
```

**After:**
```python
def _get_mime_type(self, file_path):
    """Generate proper MIME type for the file."""
    ext = file_path.suffix.lower()
    if ext in ['.mp4', '.avi', '.mov', '.webm']:
        return f"video/{ext[1:]}"
    elif ext == '.jpg' or ext == '.jpeg':
        return "image/jpeg"
    # ... proper mapping for each type
```

**Why:** More reliable, handles special cases like .heic, .webp properly.

---

### 5. Better Output Formatting

**New Features:**
- Progress bars with `=====` separators
- Character count feedback (✓ or ⚠️)
- Preview of first 150 chars of keywords
- Success/failure summary at end

**Example Output:**
```
================================================================================
Processing: hujat_otomotiff-20250101.jpg
================================================================================
Analyzing with Gemini...
Keywords generated: 235 chars
Preview: Toyota Innova Zenix innova kijang zenix hybrid hev dashboard konsumsi bbm...
Found source in filename: hujat_otomotiff
✓ 245 chars - optimal length!
✓ Moved to: hujat_otomotiff Toyota Innova Zenix innova kijang...jpg
================================================================================
```

---

### 6. Collision Handling

**New Feature:**
```python
if new_path.exists():
    counter = 1
    while new_path.exists():
        new_filename = f"{base} ({counter}).{ext}"
        counter += 1
```

**Why:** Prevents overwriting when multiple files generate similar filenames.

---

### 7. Better Error Handling

**Improvements:**
- Try/except around source extraction from content
- Graceful fallback if source detection fails
- Per-file error tracking (doesn't crash entire batch)

---

## 📊 Expected Improvements

Based on ANALYSIS.md findings:

| Metric | Old (Predicted) | New (Target) | Improvement |
|--------|-----------------|--------------|-------------|
| Avg Length | 95.8 chars | 240 chars | +150% |
| Capacity Used | 38% | 96% | +152% |
| Source Attribution | 0% | 85-95% | +∞ |
| Search Recall | Low | High | +300%* |

*Estimated based on synonym coverage

---

## 🎯 Testing Recommendations

### Test Cases to Validate

1. **Length Achievement**
   - Run on sample images
   - Check: Are filenames reaching 230-250 chars?

2. **Source Attribution**
   - Test with files that have source in filename (hujat_otomotiff-*.jpg)
   - Test with files that have watermarks
   - Test with files that have no source
   - Check: Source attribution rate should be >85%

3. **Search Coverage**
   - Pick a filename
   - Try searching with different terms:
     - Brand variations (mercy vs mercedes vs merc)
     - Bilingual (accident vs kecelakaan vs tabrakan)
     - Morphological (parkir vs diparkir vs parkiran)
   - Check: Multiple search terms should find same file

4. **No Unwanted Deduplication**
   - Check if synonyms are preserved
   - Look for: kecelakaan accident tabrakan crash (all 4 should appear)
   - Verify: Bilingual pairs aren't being collapsed

5. **Edge Cases**
   - Very long responses (>255 chars) - should trim gracefully
   - Very short responses (<100 chars) - should warn
   - Files with no visible content - should handle gracefully

---

## 🚀 Migration Guide

### For Users

1. **Backup existing output:**
   ```bash
   cp -r output output_backup
   ```

2. **Clear input folder:**
   ```bash
   # Move new files to process into input/
   ```

3. **Run new version:**
   ```bash
   python POC_Video_Tagger.py
   ```

4. **Review output:**
   - Check terminal feedback (✓ or ⚠️ indicators)
   - Verify filenames are 230-250 chars
   - Test search functionality

### For Developers

**No breaking changes to:**
- Input/output folder structure
- File format support
- API credentials setup

**New dependencies:**
- None (still uses same libraries)

**Configuration:**
- Adjust `TARGET_MIN_LENGTH` and `TARGET_MAX_LENGTH` in POC_Video_Tagger.py if needed
- Modify `MAX_WORKERS` for different concurrency

---

## 📈 Success Metrics

After running the new version, check:

1. ✅ Average filename length > 230 characters
2. ✅ Source attribution rate > 85%
3. ✅ No files with length warnings (< 230 chars)
4. ✅ Search test: 10 files, 3 search terms each = 30/30 found
5. ✅ Bilingual coverage: Indonesian and English terms both present

---

## 🐛 Known Limitations

1. **Source extraction from content is AI-based**
   - May occasionally misidentify watermarks
   - Dependent on Gemini's OCR capability
   - Recommend: Use source prefix in filenames when possible

2. **255 character filesystem limit**
   - Windows/NTFS limitation
   - Very comprehensive keywords may get trimmed at 250
   - System will warn and trim gracefully

3. **Gemini API rate limits**
   - Max 10 concurrent requests (MAX_WORKERS=10)
   - May need to reduce for large batches

---

## 💡 Future Enhancements

Potential improvements for next version:

1. **Smart source caching**
   - Remember sources for similar content
   - Reduce redundant source extraction calls

2. **Prompt tuning per model**
   - Detect which car brands appear frequently
   - Emphasize those brands' local terms

3. **Interactive mode**
   - Preview filename before committing
   - Manual source override option

4. **Batch validation**
   - Post-process check for search coverage
   - Identify files with low keyword diversity

5. **Statistics dashboard**
   - Average length over time
   - Most common brands/terms
   - Source attribution rate tracking

---

## 📞 Support

If you encounter issues:

1. Check terminal output for ⚠️ warnings
2. Verify prompt.txt is updated correctly
3. Test with single file first (`MAX_WORKERS=1`)
4. Review ANALYSIS.md for context

---

**Last Updated:** 2025-10-07
**Version:** 2.0.0 (Search-Optimized)
**Breaking Changes:** None (backward compatible with file structure)
