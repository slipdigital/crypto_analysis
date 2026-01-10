"""
Script to convert Flask templates to Django templates.
Run this from the project root directory.
"""
import os
import re
import shutil

def convert_flask_to_django(content):
    """Convert Flask/Jinja2 template syntax to Django template syntax."""
    
    # Convert url_for patterns
    # url_for('route_name') -> {% url 'route_name' %}
    content = re.sub(r'url_for\([\'"]([^\'"]+)[\'"]\)', r"{% url '\1' %}", content)
    
    # url_for('route_name', param=value) -> {% url 'route_name' value %}
    content = re.sub(r'url_for\([\'"]([^\'"]+)[\'"],\s*(\w+)=([^\)]+)\)', r"{% url '\1' \3 %}", content)
    
    # Convert Flask flash messages
    content = re.sub(
        r'{%\s*with\s+messages\s*=\s*get_flashed_messages\(with_categories=true\)\s*%}',
        '{% if messages %}',
        content
    )
    content = re.sub(r'{%\s*endwith\s*%}', '{% endif %}', content)
    
    # Update message iteration for Django
    content = re.sub(
        r'{%\s*for\s+category,\s*message\s+in\s+messages\s*%}',
        '{% for message in messages %}',
        content
    )
    
    # Update alert category for Django messages
    content = re.sub(
        r'alert-{{\s*category\s*}}',
        'alert-{{ message.tags }}',
        content
    )
    
    # Replace {{ message }} in messages context with {{ message.message }} or just {{ message }}
    # Django messages already contain the message text directly
    
    # Convert date filters
    content = re.sub(r'\.strftime\([\'"]([^\'"]+)[\'"]\)', r'|date:"\1"', content)
    
    # Convert Python format strings to Django filters
    content = re.sub(r'"{:,\.0f}"\.format\(([^\)]+)\)', r'\1|floatformat:0', content)
    content = re.sub(r'"{:,\.2f}"\.format\(([^\)]+)\)', r'\1|floatformat:2', content)
    
    # Add CSRF token to forms
    if '<form' in content and 'method="post"' in content.lower() or 'method="POST"' in content:
        content = re.sub(r'(<form[^>]*>)', r'\1\n                {% csrf_token %}', content)
    
    # Convert Flask's request.path to Django's request.path (same)
    # No changes needed
    
    # Convert variable checks with 'or' to Django's default filter
    content = re.sub(r'{{\s*(\w+)\s+or\s+[\'"]([^\'"]+)[\'"]\s*}}', r'{{ \1|default:"\2" }}', content)
    
    return content

def copy_and_convert_templates():
    """Copy all templates from flask_app to django_app and convert them."""
    
    source_dir = 'flask_app/templates'
    dest_dir = 'django_app/templates'
    
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} not found!")
        return
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Get all HTML templates
    template_files = [f for f in os.listdir(source_dir) if f.endswith('.html')]
    
    print(f"Converting {len(template_files)} templates...")
    
    for filename in template_files:
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        
        try:
            # Read the Flask template
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to Django syntax
            converted_content = convert_flask_to_django(content)
            
            # Write the Django template
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            
            print(f"✓ Converted: {filename}")
            
        except Exception as e:
            print(f"✗ Error converting {filename}: {str(e)}")
    
    print(f"\nConversion complete! Templates saved to {dest_dir}/")

if __name__ == '__main__':
    copy_and_convert_templates()
