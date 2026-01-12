# File Upload Path Resolution - Quick Guide

## 🎯 Overview

The file upload system now uses **smart path resolution** with `src/resources/uploads/` as the default directory. This makes tests portable across environments and perfect for CI/CD pipelines.

## 📍 Default Upload Location

```
src/resources/uploads/
```

All test files should be placed here, organized by module/feature.

## 🔧 How It Works

### Path Resolution Order

When you specify a file path, the system checks in this order:

1. **`src/resources/uploads/[your-path]`** ← Default
2. **`src/resources/[your-path]`**
3. **`[project-root]/[your-path]`**
4. **Absolute path as-is**

### Examples

#### Example 1: Filename Only
**File location:** `src/resources/uploads/resume.pdf`
**You enter:** `resume.pdf`
**Resolved to:** `C:/Users/.../WebAutomation/src/resources/uploads/resume.pdf`

#### Example 2: Module Subdirectory
**File location:** `src/resources/uploads/documents/contract.pdf`
**You enter:** `documents/contract.pdf`
**Resolved to:** `C:/Users/.../WebAutomation/src/resources/uploads/documents/contract.pdf`

#### Example 3: With "uploads/" Prefix
**File location:** `src/resources/uploads/images/photo.jpg`
**You enter:** `uploads/images/photo.jpg`
**Resolved to:** `C:/Users/.../WebAutomation/src/resources/uploads/images/photo.jpg`

#### Example 4: Absolute Path (Not Recommended)
**You enter:** `C:\Users\John\Downloads\file.pdf`
**Resolved to:** `C:/Users/John/Downloads/file.pdf`

## 📂 Recommended Directory Structure

```
src/resources/uploads/
├── auth/                    # Authentication related files
│   ├── profile_photo.jpg
│   └── id_document.pdf
├── documents/               # Document uploads
│   ├── contract.pdf
│   ├── invoice.xlsx
│   └── report.docx
├── images/                  # Image files
│   ├── banner.png
│   └── logo.svg
└── general/                 # Miscellaneous files
    └── sample.txt
```

## 🎬 Recording a Test

### Step-by-Step

1. **Prepare Files**
   ```bash
   # Place your test file
   src/resources/uploads/documents/resume.pdf
   ```

2. **Record Test**
   - Start recording
   - Navigate to upload page
   - Click file input
   - Select any file (actual file doesn't matter during recording)

3. **Execute Test**
   - Modal appears asking for file path
   - **💡 Helper shown:** "Place files in `src/resources/uploads/` and use filename only"
   - **Enter:** `documents/resume.pdf` or just `resume.pdf`
   - Click Continue

4. **System Resolves**
   ```
   [PATH RESOLVE] Found in uploads: C:/Users/.../src/resources/uploads/documents/resume.pdf
   [FILE UPLOAD] File exists, uploading: C:/Users/.../src/resources/uploads/documents/resume.pdf
   ```

## 🌟 Benefits

### ✅ Portability
- No hardcoded paths
- Works on any developer's machine
- Works in CI/CD without changes

### ✅ Organization
- Files organized by module
- Easy to find and maintain
- Clean project structure

### ✅ CI/CD Ready
- Consistent paths across environments
- Docker-friendly
- Easy to version control

### ✅ User-Friendly
- Just use filename: `file.pdf`
- Or module path: `documents/file.pdf`
- Helper text in UI guides users

## 🚀 CI/CD Integration

### Docker Example
```dockerfile
# Dockerfile
COPY src/resources/uploads /app/src/resources/uploads
```

### GitHub Actions
```yaml
- name: Setup test files
  run: |
    mkdir -p src/resources/uploads/documents
    cp test-files/* src/resources/uploads/documents/
```

### Jenkins
```groovy
stage('Prepare Test Files') {
    steps {
        sh 'cp $WORKSPACE/test-data/* src/resources/uploads/'
    }
}
```

## 💾 Version Control

The `.gitignore` in `uploads/` ignores all files by default but keeps directory structure:

```gitignore
# Ignore all files
*

# Keep subdirectories
!*/

# Keep README
!README.md
!.gitkeep

# Optionally commit sample files
# !documents/sample.pdf
```

## 🎨 UI Updates

### File Path Modal Now Shows:
```
┌─────────────────────────────────────────────┐
│ 💡 Tip: Place files in src/resources/       │
│    uploads/ and use filename only           │
│    (e.g., file.pdf)                         │
├─────────────────────────────────────────────┤
│ File Path:                                  │
│ [uploads/file.pdf or C:\full\path\file.pdf] │
└─────────────────────────────────────────────┘
```

## 📊 Before vs After

### Before
```
❌ Absolute paths: C:\Users\John\Downloads\file.pdf
❌ Not portable
❌ Breaks in CI/CD
❌ Hardcoded in tests
```

### After
```
✅ Relative paths: documents/file.pdf
✅ Fully portable
✅ CI/CD ready
✅ Clean and organized
```

## 🔍 Path Resolution Logs

Enable logging to see path resolution in action:

```
[PATH RESOLVE] Found in uploads: C:/Users/.../src/resources/uploads/documents/file.pdf
[FILE UPLOAD] File exists, uploading: C:/Users/.../src/resources/uploads/documents/file.pdf
```

If file not found:
```
[PATH RESOLVE] File not found in any location: wrong.pdf
[PATH RESOLVE] Checked: C:/Users/.../src/resources/uploads/wrong.pdf, C:/Users/.../wrong.pdf, and absolute path
```

## 📝 Best Practices

1. **Always use relative paths** from uploads directory
2. **Organize by module**: `auth/`, `documents/`, `images/`
3. **Use descriptive names**: `valid_resume.pdf`, `invalid_image.txt`
4. **Keep files small**: Use test/sample files, not real data
5. **Commit structure**: Commit `.gitkeep` and subdirectories, not actual files
6. **Document requirements**: Note file format/size requirements in module README

## ❓ FAQ

**Q: Can I still use absolute paths?**
A: Yes, but not recommended. Relative paths are portable.

**Q: What if file is in a different location?**
A: System checks 4 locations in order. If not in uploads/, put full path.

**Q: How do I organize 50+ test files?**
A: Create subdirectories: `uploads/module1/`, `uploads/module2/`, etc.

**Q: Does this work with multiple files?**
A: Yes! Use pipe separator: `file1.pdf|file2.pdf` or `docs/file1.pdf|docs/file2.pdf`

**Q: What about Windows vs Linux paths?**
A: System normalizes all paths to forward slashes for Selenium compatibility.

---

**🎉 Your tests are now portable, organized, and CI/CD ready!**
