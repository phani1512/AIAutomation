"""
Add fallback selectors to all common patterns across all categories.
Similar to email/password consolidation, but for clicks, getText, wait, dropdown, etc.
"""
import json
import re
from collections import defaultdict

# Define fallback templates for common patterns
FALLBACK_TEMPLATES = {
    "click": {
        "submit_button": {
            "keywords": ["submit", "save", "confirm"],
            "fallbacks": [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Submit')",
                "button:contains('Save')",
                "button:contains('Confirm')",
                "button[name='submit']",
                "button[id*='submit']",
                "a:contains('Submit')",
                ".btn-submit",
                ".submit-btn"
            ]
        },
        "cancel_button": {
            "keywords": ["cancel", "close", "dismiss"],
            "fallbacks": [
                "button:contains('Cancel')",
                "button:contains('Close')",
                "button[class*='close']",
                "button[class*='cancel']",
                "a:contains('Cancel')",
                ".close",
                ".modal-close",
                ".btn-cancel",
                "[data-dismiss='modal']",
                "button[type='button']:contains('Cancel')"
            ]
        },
        "delete_button": {
            "keywords": ["delete", "remove"],
            "fallbacks": [
                "button:contains('Delete')",
                "button:contains('Remove')",
                "button[class*='delete']",
                "button[id*='delete']",
                "a:contains('Delete')",
                ".btn-delete",
                ".delete-btn",
                "button[data-action='delete']"
            ]
        },
        "edit_button": {
            "keywords": ["edit", "modify", "update"],
            "fallbacks": [
                "button:contains('Edit')",
                "button:contains('Update')",
                "button[class*='edit']",
                "button[id*='edit']",
                "a:contains('Edit')",
                ".btn-edit",
                ".edit-btn",
                "button[data-action='edit']"
            ]
        },
        "add_button": {
            "keywords": ["add", "new", "create"],
            "fallbacks": [
                "button:contains('Add')",
                "button:contains('New')",
                "button:contains('Create')",
                "button[class*='add']",
                "button[id*='add']",
                "a:contains('Add')",
                ".btn-add",
                ".add-btn",
                "button[data-action='add']"
            ]
        },
        "link": {
            "keywords": ["link"],
            "fallbacks": [
                "a[href]",
                "a.link",
                "[role='link']",
                ".nav-link",
                "a[class*='link']"
            ]
        },
        "button_generic": {
            "keywords": ["button", "btn"],
            "fallbacks": [
                "button",
                "input[type='button']",
                "[role='button']",
                ".btn",
                "a.button"
            ]
        }
    },
    
    "getText": {
        "success_message": {
            "keywords": ["success", "successfully"],
            "fallbacks": [
                ".alert-success",
                ".success-message",
                ".message-success",
                "[role='alert'].success",
                ".notification.success",
                ".toast-success",
                "[class*='success-message']",
                "[class*='alert'][class*='success']"
            ]
        },
        "error_message": {
            "keywords": ["error", "invalid", "failed"],
            "fallbacks": [
                ".alert-error",
                ".error-message",
                ".message-error",
                "[role='alert'].error",
                ".notification.error",
                ".toast-error",
                "[class*='error-message']",
                "[class*='alert'][class*='error']",
                ".alert-danger",
                ".text-danger"
            ]
        },
        "header": {
            "keywords": ["header", "heading", "title"],
            "fallbacks": [
                "h1",
                "h2",
                "h3",
                ".header",
                ".heading",
                ".title",
                "[role='heading']",
                ".page-header",
                ".section-header"
            ]
        },
        "label": {
            "keywords": ["label"],
            "fallbacks": [
                "label",
                ".label",
                "[role='label']",
                "span.label",
                ".form-label"
            ]
        },
        "text_generic": {
            "keywords": ["text", "content"],
            "fallbacks": [
                "p",
                "span",
                "div",
                ".text",
                "[role='text']"
            ]
        }
    },
    
    "wait": {
        "loading_spinner": {
            "keywords": ["loading", "spinner", "wait"],
            "fallbacks": [
                ".spinner",
                ".loading",
                ".loader",
                "[class*='loading']",
                "[class*='spinner']",
                "[role='progressbar']",
                ".progress",
                ".loading-overlay"
            ]
        },
        "modal": {
            "keywords": ["modal", "dialog", "popup"],
            "fallbacks": [
                ".modal",
                "[role='dialog']",
                ".dialog",
                ".popup",
                "[class*='modal']",
                ".overlay"
            ]
        }
    },
    
    "dropdown": {
        "select": {
            "keywords": ["select", "dropdown"],
            "fallbacks": [
                "select",
                "[role='combobox']",
                ".select",
                ".dropdown",
                "[class*='select']",
                "[class*='dropdown']"
            ]
        }
    }
}

def find_template_match(prompt, category):
    """Find which template best matches the prompt."""
    prompt_lower = prompt.lower()
    
    if category not in FALLBACK_TEMPLATES:
        return None
    
    # Check each template for keyword matches
    for template_name, template_data in FALLBACK_TEMPLATES[category].items():
        for keyword in template_data["keywords"]:
            if keyword in prompt_lower:
                return template_data["fallbacks"]
    
    return None

def add_fallbacks_to_dataset(input_file, output_file):
    """Add fallback selectors to entries that don't have them."""
    
    print(f"Loading dataset from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"Total entries: {len(dataset)}")
    
    # Track statistics
    stats = {
        "total": len(dataset),
        "already_has_fallbacks": 0,
        "fallbacks_added": 0,
        "no_template_match": 0
    }
    
    # Process each entry
    for entry in dataset:
        prompt = entry.get('prompt', '')
        category = entry.get('category', '')
        current_fallbacks = entry.get('fallback_selectors', [])
        
        # Skip if already has multiple fallbacks
        if len(current_fallbacks) > 1:
            stats["already_has_fallbacks"] += 1
            continue
        
        # Try to find a matching template
        template_fallbacks = find_template_match(prompt, category)
        
        if template_fallbacks:
            # Add the original xpath as first fallback
            original_xpath = entry.get('xpath', '')
            if original_xpath:
                entry['fallback_selectors'] = [original_xpath] + template_fallbacks
            else:
                entry['fallback_selectors'] = template_fallbacks
            
            # Mark as enhanced
            if 'metadata' not in entry:
                entry['metadata'] = {}
            if 'entry_type' not in entry['metadata']:
                entry['metadata']['entry_type'] = 'enhanced'
            
            stats["fallbacks_added"] += 1
        else:
            stats["no_template_match"] += 1
    
    # Save enhanced dataset
    print(f"\nSaving enhanced dataset to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("\n" + "="*80)
    print("FALLBACK ADDITION SUMMARY")
    print("="*80)
    print(f"Total entries: {stats['total']}")
    print(f"Already had fallbacks: {stats['already_has_fallbacks']}")
    print(f"Fallbacks added: {stats['fallbacks_added']}")
    print(f"No template match: {stats['no_template_match']}")
    print(f"\nEnhanced entries: {stats['fallbacks_added'] + stats['already_has_fallbacks']}")
    print(f"Percentage enhanced: {((stats['fallbacks_added'] + stats['already_has_fallbacks']) / stats['total'] * 100):.1f}%")
    print("="*80)

if __name__ == "__main__":
    input_file = "src/resources/combined-training-dataset-final-consolidated-v2.json"
    output_file = "src/resources/combined-training-dataset-final-enhanced-v3.json"
    
    add_fallbacks_to_dataset(input_file, output_file)
    print("\n✓ Done! Enhanced dataset saved.")
