import os
import sys
import re
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._n_a_m_e import NameRecord

def is_garbage(text):
    """Check if name string is garbage (empty, single char, dots, etc)"""
    if not text: return True
    s = text.strip()
    return len(s) < 2 or re.match(r'^[\W_]+$', s)

def generate_names(filename):
    """Infer Family, Subfamily from filename like 'costa-bold'"""
    base = os.path.splitext(filename)[0]
    # Remove _installable etc
    base = re.sub(r'_(fixed|installable|clean|rewash)$', '', base, flags=re.IGNORECASE)
    
    # Try splitting by hyphen or underscore
    parts = re.split(r'[-_]', base)
    
    if len(parts) > 1:
        # last part likely style
        style_candidate = parts[-1].lower()
        # common styles
        known_styles = ['regular', 'bold', 'italic', 'light', 'medium', 'black', 'thin', 'heavy']
        
        if style_candidate in known_styles or any(s in style_candidate for s in known_styles):
            style = parts[-1].capitalize()
            family = " ".join([p.capitalize() for p in parts[:-1]])
        else:
            # Maybe just one word name?
            family = base.capitalize()
            style = "Regular"
    else:
        family = base.capitalize()
        style = "Regular"
        
    full_name = f"{family} {style}"
    ps_name = f"{family.replace(' ', '')}-{style}"
    
    return {
        1: family,
        2: style,
        4: full_name,
        6: ps_name
    }

def fix_metadata(font, filename):
    name_table = font['name']
    names = name_table.names
    
    inferred = generate_names(filename)
    # print(f"Inferred names from filename: {inferred}")
    
    # Check if existing names are garbage
    current_fam = ""
    for r in names:
        if r.nameID == 1:
            try:
                current_fam = r.toUnicode()
                break
            except: pass
            
    if is_garbage(current_fam):
        print("Detected garbage internal names. Overwriting with inferred names...")
        # Clear existing critical records to avoid conflicts
        name_table.names = [n for n in names if n.nameID not in [1,2,4,6]]
        
        # Add new records for both Mac (1,0,0) and Windows (3,1,1033)
        for nid, val in inferred.items():
            # Mac
            rec1 = NameRecord()
            rec1.platformID = 1
            rec1.platEncID = 0
            rec1.langID = 0
            rec1.nameID = nid
            rec1.string = val.encode('mac_roman')
            name_table.names.append(rec1)
            
            # Windows
            rec3 = NameRecord()
            rec3.platformID = 3
            rec3.platEncID = 1
            rec3.langID = 1033
            rec3.nameID = nid
            rec3.string = val.encode('utf_16_be')
            name_table.names.append(rec3)

def convert_font(input_path, target_format='ttf'):
    """
    Convert font to target format.
    target_format: 'ttf', 'otf', 'woff', 'woff2'
    """
    try:
        filename = os.path.basename(input_path)
        print(f"Loading {filename}...")
        
        # Load Font
        font = TTFont(input_path)
        
        # Determine internal outline type
        has_cff = 'CFF ' in font
        
        # If target asks for OTF but we have TTF outlines, we can't easily auto-convert outlines 
        # without complex third party tools (tx, cu2qu). 
        # FontTools can wrap existing outlines.
        # However, saving TTF outlines as .otf file is technically "OpenType with TrueType outlines",
        # but the extension .otf usually implies CFF. .ttf implies TrueType.
        # WOFF/WOFF2 can hold either.
        
        # We will respect the user's requested container extension, 
        # but we won't convert outlines (Glyph curves) as that's very error prone.
        
        # Target Extension logic
        if target_format.lower() == 'ttf':
            out_ext = '.ttf'
        elif target_format.lower() == 'otf':
            out_ext = '.otf'
        elif target_format.lower() == 'woff':
            out_ext = '.woff'
        elif target_format.lower() == 'woff2':
            out_ext = '.woff2'
        else:
            out_ext = '.ttf'

        # Decompress first input was web font)
        font.flavor = None
        
        # === PREPARE FOR DESKTOP (TTF/OTF) ===
        if target_format in ['ttf', 'otf']:
            # 1. Reset fsType
            if 'OS/2' in font:
                font['OS/2'].fsType = 0
                
            # 2. Fix Names
            if 'name' not in font:
                font['name'] = newTable('name')
                font['name'].names = []
            
            # We always check/fix metadata for desktop targets to avoid installation errors
            fix_metadata(font, filename)
            
            # 3. Strip hostility
            junk = ['DSIG', 'fpgm', 'prep', 'cvt ', 'hdmx', 'VDMX', 'LTSH']
            for tag in junk:
                if tag in font: del font[tag]

            # 4. Standardize post
            if 'post' in font:
                font['post'].formatType = 2.0
                font['post'].mapping = {}
                font['post'].extraNames = []

            # 5. Reset Checksums
            if 'head' in font:
                font['head'].checkSumAdjustment = 0
                
        # === PREPARE FOR WEB (WOFF/WOFF2) ===
        else:
            # For web, we just want to set the flavor. 
            # We might want to keep hints for web if they existed, but our 'clean' approach 
            # is safer. Let's keep the hostility stripping if the user wants a clean web font too.
            # But let's assume if they convert BACK to web, they might want a functional font.
            # We will perform the same cleaning because 'garbage names' also break things
            # in some CSS contexts if the font metadata is totally empty.
            
            font.flavor = target_format # 'woff' or 'woff2'
            
            # If CFF table exists and we save as WOFF, FontTools handles it.
            
        output_path = os.path.join(os.path.dirname(input_path), os.path.splitext(filename)[0] + out_ext)
        print(f"Saving to {output_path}...")
        font.save(output_path)
        print("Done.")
        return output_path
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
